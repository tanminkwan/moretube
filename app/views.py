from flask import g, render_template, request, Response, send_from_directory, send_file, jsonify
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import BaseView, ModelView, ModelRestApi, has_access
from flask_appbuilder.filemanager import FileManager, uuid_namegen
from flask_appbuilder.api import BaseApi, expose, protect
from flask_appbuilder.actions import action
from .models import Dictionary, Mp4ContentMaster, UTubeContentMaster, UTubeContentCaption\
  , ContentMaster, TestTable, EcamFile, Program, SplitCaption
from . import appbuilder, db, app
from .scheduled_jobs import job_create_job
from .queries import selectRow, selectRows, selectDict, applyDicts
from .common import VerifyYaml, getAlNumCnt, getStrfile, getUtubeCap, getUtubeCapYamlFile
from .batchs import transVideo

import os
import re
import json
import yaml
import traceback

REPMAP = [
  ('(s(','<span class="w_subject">'),
  ('(v(','<span class="w_verb">'),
  ('(<(','<span class="p_relative">'),
  ('(t(','<span class="p_title">'),
  ('(d(','<span class="w_dict">'),
  ('))','</span>'),
]

def _setDeco(text):
    for tup in REPMAP:
      text = text.replace(tup[0], tup[1])
    
    return text

def _removeDeco(text):
    for tup in REPMAP:
      text = text.replace(tup[0], '')
    
    return text

def _addEnd(jlist):
    return [ j | {'end':round(jlist[i+1 if i+1!=len(jlist) else i]['start']+0.1,2)} for i, j in enumerate(jlist)]

def _removeEmpty(jlist):
    return [ j for j in jlist if j.get('text')]

def _addID(jlist):
    return [ j | {'id':i} for i, j in enumerate(jlist)]

def _addLen(jlist):
    return [ j | {'len':getAlNumCnt(re.sub(r'<[^>]*>','',(j['text'] if j.get('text') else '')))} for j in jlist]

def _getTotLen(jlist):
    return sum([j['len'] for j in jlist])

def addIdNStart(jlist):

    jlist2 = _addEnd(jlist)
    return _addID(jlist2)

def convertYcap2Jcap(ycap):
    decoed_ycap = _setDeco(ycap)
    jlist =  yaml.safe_load(decoed_ycap)
    jlist2 = _addEnd(jlist)
    jlist3 =_removeEmpty(jlist2)
    jlist4 = _addLen(jlist3)
    return _addID(jlist4)

def _getDivision(data, split_type, split_value):

    division = []
    match split_type:
      case "CUSTOM_DEFINED":
        division = list(map(int, split_value.split(',')))
      case "SAME_WEIGHT":
        pass
      case "FIXED_WEIGHT":
        pass
      case "BY_TITLE":
        pass
      case _:
        pass

    return division

def _getCaptions(utube_content_caption):

    data = []
    division = []
    division_title = ""

    row = next((r for r in utube_content_caption if r.picked_yn.name == 'YES'), "")

    if row:
      data = row.captions['data']

      for s in row.split_caption:
        for ss in s.ab_user:
          if g.user.username == ss.username:
            division = _getDivision(data, s.split_type.name, s.split_value)
            division_title = s.split_title
            break

        if division:
          break

    return dict(
            data = data ,
            division = division ,
            division_title = division_title ,
          )


@db.event.listens_for(Mp4ContentMaster, 'before_insert')
def transecode_mp4(mapper, connection, target):
    
    filename = str(target.file)
    fileId   = filename[:-4]
    inputFile = app.config['UPLOAD_FOLDER'] + filename
    outputPath = app.config['HLS_STREAM_FOLDER'] + fileId

    outputFile = 'playlist.m3u8'

    transVideo(inputFile, outputPath, outputFile)

    target.manifest_path = '/api/v1/mytube/hls/' + fileId + '/' + outputFile

@db.event.listens_for(ContentMaster, 'after_insert')
def update_stream_info(mapper, connection, target):
    
    job_create_job(target)

@db.event.listens_for(UTubeContentCaption, 'before_update')
def update_stream_info(mapper, connection, target):
    
    jdata = convertYcap2Jcap(target.captions_yaml)
    target.captions = {'data':jdata}
    target.caption_len = _getTotLen(jdata)

    print('UTubeContentCaption update!!')

@db.event.listens_for(UTubeContentCaption, 'before_insert')
def update_stream_info(mapper, connection, target):
    
    jdata = convertYcap2Jcap(target.captions_yaml)
    target.captions = {'data':jdata}
    target.caption_len = _getTotLen(jdata)

    print('UTubeContentCaption insert!!')

class DictionaryView(ModelView):
    datamodel = SQLAInterface(Dictionary)
    list_title = 'Dictionary'
    list_columns = ['tags','value1']
    #label_columns = {'id':'SEQ','name':'이름','description':'메세지','create_on':'생성일지'}
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

class SplitCaptionView(ModelView):
    datamodel = SQLAInterface(SplitCaption)
    add_template = 'add_simulation.html'
    edit_template = 'edit_simulation.html'
    
    list_title = 'Split Caption'
    list_columns = ['utube_content_caption','split_caption_id','ab_user','split_type','split_value','create_on']
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

    description_columns = {
      'split_type':'[Fixed size : 고정길이로 분할, split value에 고정길이(byte)입력]'
          +' [Same size : 동일한 길이로 분할, split value에 분할 개수 입력]'
          +' [Classified by title : 특정 문자열 기준으로 분할, split value에 특정 문자열 입력]'
          +' [Custom Defined : 분할기준 직접입력, split value에 각 분할단위의 마지막 id를 ","를 구분자로 순차적으로 입력(ex : 5,8,13,22)]' ,
    }

class UTubeContentCaptionView(ModelView):
    datamodel = SQLAInterface(UTubeContentCaption)
    list_title = 'YouTube Content Captions'
    list_columns = ['utube_content_master','show_html','caption_id','caption_len','picked_yn','create_on']
    edit_exclude_columns = ['captions','caption_len', 'id','create_on']
    add_exclude_columns = ['captions','caption_len','id','create_on']
    search_exclude_columns = ['captions']

    label_columns = {
      'captions_yaml':'자막(yaml type)',
    }

    description_columns = {
      'captions_yaml':'yaml 형식을 준수하세요.',
    }

    validators_columns = {
      'captions_yaml':[VerifyYaml()],
    }

    related_views = [SplitCaptionView]
    
    @action("download_subtitles", "Download Subtitles", "", "fa-rocket", single=True)
    def download_subtitles(self, item):

      data_s = item[0].captions_yaml
      output = getStrfile(data_s)

      return send_file(output, attachment_filename=str(item[0].id)+'_caption.yaml', as_attachment=True)

class Mp4ContentMasterView(ModelView):
    datamodel = SQLAInterface(Mp4ContentMaster)
    list_title = 'Mp4 Contents'
    list_columns = ['show_html','get_filename','description','difficulty','picked_yn','download','create_on']
    edit_exclude_columns = ['id','file','create_on']
    add_exclude_columns = ['id','manifest_path','create_on']

class UTubeContentMasterView(ModelView):
    datamodel = SQLAInterface(UTubeContentMaster)
    list_title = 'YouTube Contents'
    list_columns = ['show_html','content_description','content_id','utube_content_caption','difficulty','picked_yn','create_on']
    #label_columns = {'id':'SEQ','name':'이름','description':'메세지','create_on':'생성일지'}
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

    related_views = [UTubeContentCaptionView]

    @action("download_utubecaps", "Download Utube Captions", "", "fa-rocket", single=True)
    def download_utubecaps(self, item):

      output = getUtubeCapYamlFile(item[0].content_id)
      return send_file(output, attachment_filename=str(item[0].content_id)+'_utube_cap.yaml', as_attachment=True)

class UTubeContentMasterAPI(ModelRestApi):

    resource_name = 'utubecontentmaster'

    allow_browser_login = True

    datamodel = SQLAInterface(UTubeContentMaster)

    list_columns = ['show_html','content_description','content_id','play_from','play_to','user_id','create_on']

class Mp4ContentMasterAPI(ModelRestApi):

    resource_name = 'mp4contentmaster'

    allow_browser_login = True

    datamodel = SQLAInterface(Mp4ContentMaster)

    list_columns = ['show_html','get_filename','description','download','user_id','create_on']

class TestTableView(ModelView):
    datamodel = SQLAInterface(TestTable)
    list_title = 'CRUD TEST'
    list_columns = ['id','name','description','create_on']
    label_columns = {'id':'SEQ','name':'이름','description':'메세지','create_on':'생성일지'}
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

class TestTableApi(ModelRestApi):
    
    datamodel = SQLAInterface(TestTable)

class EcamFileView(ModelView):
    datamodel = SQLAInterface(EcamFile)
    list_title = 'File Upload TEST'
    list_columns = ['id','type_t', 'name','description','download','create_on']
    label_columns = {'id':'SEQ','type_t':'파일Type','name':'이름','description':'메세지','create_on':'생성일지'}
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

class ContentMasterView(ModelView):
    datamodel = SQLAInterface(ContentMaster)
    list_title = 'Content Master'
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

class ContentMasterApi(ModelRestApi):

    resource_name = 'contentmaster'
    
    datamodel = SQLAInterface(ContentMaster)
    add_columns = ['filename', 'description', 'stored_filename', 'ref_stored_filename']
    edit_columns = ['filename', 'description', 'ref_stored_filename']
    list_columns = ['content_type','filename','file_type','description','valid_yn','stream_url','manifest_path','stored_filename','ref_stored_filename'\
        ,'thumbnail_path','user_id','create_on','hostname']
    show_columns = ['content_type','filename','file_type','description','valid_yn','stream_url','manifest_path','stored_filename','ref_stored_filename'\
        ,'thumbnail_path','user_id','create_on','hostname']
    
    def post_add(self, item):
        """
            Override this, will be called before add.
        """
        pass

class ProgramView(ModelView):
    datamodel = SQLAInterface(Program)
    list_title = 'Program'
    list_columns = ['program_name','description','author','content_master','user_id','create_on','hostname']
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

class ProgramApi(ModelRestApi):
    
    resource_name = 'program'

    datamodel = SQLAInterface(Program)
    add_columns = ['program_name', 'description', 'author']
    edit_columns = ['description', 'author']
    list_columns = ['program_name','description','author','contentmaster','user_id','create_on','hostname']
    show_columns = ['program_name','description','author','contentmaster','user_id','create_on','hostname']

class ContentsInfo(BaseApi):
  
    resource_name = 'mytube'

    @expose('/hls/<dir>/<filename>', methods=['GET'])
    @has_access
    def getM3u8File(self, dir, filename):
      
      return send_from_directory(app.config['HLS_STREAM_FOLDER'] + dir + '/', filename)

    @expose('/dictionary/<word>', methods=['GET'])
    @has_access
    def getDictionary(self, word):
      
      recs, _ = selectDict(word)

      rlist = []
      if recs:
        rlist = [ r.description for r in recs ]
      
      return jsonify({'data':rlist})

    @expose('/hls_caption/<id>', methods=['GET'])
    @has_access
    def getHlsCaption(self, id):
      
      result = dict()
      content, _ = selectRow('mp4_content_master',{'id':id})

      if content.utube_content_caption:
        result = _getCaptions(content.utube_content_caption)
      else:
        result = {'data':[]}

      return jsonify(result)

    @expose('/mytube_caption/<id>', methods=['GET'])
    @has_access
    def getMytubeCaption(self, id):
      
      result = dict()
      data = []
      content, _ = selectRow('utube_content_master',{'id':id})

      if content.utube_content_caption:
        for row in content.utube_content_caption:
          if row.picked_yn.name == 'YES':
            data = row.captions['data']
            break    
      
      result.update({'data':data})

      return jsonify(result)

    @expose('/caption/<id>', methods=['GET'])
    @has_access
    def getCaption(self, id):
      
      result = dict()
      data = []
      content, _ = selectRow('utube_content_master',{'content_id':id})

      if content.utube_content_caption:
        result = _getCaptions(content.utube_content_caption)
        """
        for row in content.utube_content_caption:
          if row.picked_yn.name == 'YES':
            data = row.captions['data']
            break    
        """
      if not result.get('data'):
        jlist = getUtubeCap(id)
        data = addIdNStart(jlist)
        result = {'data':data}

      return jsonify(result)

    @expose('/caption_yaml/<id>', methods=['GET'])
    @has_access
    def getCaptionYaml(self, id):
      
      output = getUtubeCapYamlFile(id)
      return send_file(output, attachment_filename=id+'_utube_cap.yaml', as_attachment=True)    

    @expose('/dictionary_yaml', methods=['GET'])
    @has_access
    def getDictionaryYaml(self):
      
      jlist, _ = selectRows('dictionary',{})

      data = []
      for j in jlist:
        r_dict = dict(
          tags       =j.tags,
          description=j.description,
        )
        r_dict = r_dict | ({'value1':j.value1} if j.value1 else {}) | ({'value2':j.value2} if j.value2 else {})
        data.append(r_dict)

      data_y = yaml.dump(data, sort_keys=False, allow_unicode=True)
      
      output = getStrfile(str(data_y))

      return send_file(output, attachment_filename='_dictionary.yaml', as_attachment=True)    

    @expose('/upload_dict', methods=['POST'])
    @protect()
    def upload_dict(self, **kwargs):
        """POST Dictionary file Upload
        ---
        post:
          description: Upload a dictionary file
          requestBody:
            description: yaml file
            required: true
            content:
              multipart/form-data:
                schema:
                  type: object
                  properties:
                    file:
                      type: string
                      format: binary
          responses:
            201:
              description: File Uploaded
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      return_code:
                        type: integer
                      stored_file_name:
                        type: string
                      message:
                        type: string
                    example:
                      return_code: 1
                      stored_file_name: dict.yaml
                      message: Well done
            415:
              description: Invalid Yaml Type
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      return_code:
                        type: integer
                      message:
                        type: string
                    example:
                      return_code: -1
                      message: jpg is not a yaml type.
        """
        file = request.files['file']
        file_name = file.filename 
        filetype = file_name.split('.')[-1]
        
        if filetype.lower() in ['yaml']:

          try:

            d_list = yaml.safe_load(file)
            rtn, message = applyDicts(d_list)            
            db.session.commit()

          except yaml.parser.ParserError as e:
            return jsonify({'return_code':-2, 'message':traceback.format_exc()}), 415
          except Exception as e:
            return jsonify({'return_code':-3, 'message':traceback.format_exc()}), 415

        else:

          return jsonify({'return_code':-1, 'message':filetype+' is not yaml type.'}), 415
        
        return jsonify({'return_code':rtn, 'file_name':file_name, 'message':message}), 201

class UserManager(BaseApi):
    
    resource_name = 'user'
    
    @expose('/myprofile', methods=['GET'])
    @protect()
    def myprofile(self):
        """Get My Profile
        ---
        get:
          description: >-
            Get My Profile
          responses:
            200:
              description: Connected user information
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      return_code:
                        type: integer
                      username:
                        type: string
                      first_name:
                        type: string
                      last_name:
                        type: string
                      email:
                        type: string
                      created_on:
                        type: string
                        format: date-time                        
                      last_login:
                        type: string
                        format: date-time                        
                    example:
                      return_code: 1
                      username: tiffanie
                      first_name: Hennry
                      last_name: Kim
                      email: tiffanie@gmail.com
                      created_on: Mon, 27 Dec 2021 16:35:52 GMT
                      last_login: Wed, 12 Jan 2022 15:55:14 GMT
        """
        resp = dict(return_code = 1
                  , username    = g.user.username
                  , first_name  = g.user.first_name
                  , last_name   = g.user.last_name
                  , email       = g.user.email
                  , created_on  = g.user.created_on
                  , last_login  = g.user.last_login)
        
        return jsonify(resp), 201

class HlsContent(BaseApi):

    route_base = '/hls'

    @expose('/view/<id>', methods=['GET'])
    @has_access
    def view(self, id=None):

      row, _ = selectRow('mp4_content_master',{'id':int(id)})

      if row:
        return render_template('hls_show.html',\
                id    = row.id,
                content_description = row.description,
                manifest_path = row.manifest_path,
                base_template = appbuilder.base_template,
                appbuilder    = appbuilder,
          )

class UTubeContent(BaseApi):

    route_base = '/utube'

    @expose('/view/<id>', methods=['GET'])
    @has_access
    def view(self, id=None):

      row, _ = selectRow('utube_content_master',{'id':int(id)})

      if row:
        return render_template('utube_show.html',\
                content_id  = row.content_id,
                play_from   = row.play_from if row.play_from else 0,
                play_to     = row.play_to,
                content_description = row.content_description,
                base_template=appbuilder.base_template,
                appbuilder=appbuilder,
          )

    @expose('/textview/<id>', methods=['GET'])
    @has_access
    def textview(self, id=None):

      row, _ = selectRow('utube_content_caption',{'id':int(id)})

      if row:

        title = row.caption_id

        jlist = convertYcap2Jcap(row.captions_yaml)

        return render_template('text_show.html',\
                title          = title,
                jcontents_list = jlist,
                base_template  = appbuilder.base_template,
                appbuilder     = appbuilder,
          )

class ContentsManager(BaseApi):
    
    resource_name = 'contents'
    
    @expose('/upload', methods=['POST'])
    @protect()
    def upload_content(self, **kwargs):
        """POST Vidoe Upload
        ---
        post:
          description: Upload a video file
          requestBody:
            description: Video file
            required: true
            content:
              multipart/form-data:
                schema:
                  type: object
                  properties:
                    file:
                      type: string
                      format: binary
          responses:
            201:
              description: File Uploaded
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      return_code:
                        type: integer
                      stored_file_name:
                        type: string
                      message:
                        type: string
                    example:
                      return_code: 1
                      stored_file_name: f70c9a39-6f88-11ec-9c34-00505694d9ee_sep_file_example.mp4
                      message: Well done
            415:
              description: Invalid Video Type
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      return_code:
                        type: integer
                      message:
                        type: string
                    example:
                      return_code: -1
                      message: jpg is not a video type.
        """
        file = request.files['file']
        filetype = file.filename.split('.')[-1]
        
        if filetype.lower() in ['mp4','mov']:
            base_path = None
        elif filetype.lower() in ['jpg','jpeg','png','gif']:
            base_path = app.config['IMG_UPLOAD_FOLDER']
        else:
            return jsonify({'return_code':-1, 'message':filetype+' is not a video type.'}), 415
        
        fm = FileManager(base_path=base_path)      
        
        sfilename = fm.save_file(file, uuid_namegen(file))
        
        return jsonify({'return_code':1, 'stored_file_name':sfilename, 'message':'well done'}), 201
        
    
class TestStream(BaseView):

    default_view = 'stream'

    def get_chunk(self, file_name, byte1=None, byte2=None):
        print("HHH : ", app.root_path, file_name)
        full_path = "/static/uploads/" + file_name
        file_size = os.stat(full_path).st_size
        start = 0

        if byte1 < file_size:
            start = byte1
        if byte2:
            length = byte2 + 1 - byte1
        else:
            length = file_size - start

        with open(full_path, 'rb') as f:
            f.seek(start)
            chunk = f.read(length)

        return chunk, start, length, file_size

    @expose('/stream/')
    def stream(self):
        return 'Hello'

    @expose('/video/<string:param1>')
    @has_access
    def video(self, param1):
        range_header = request.headers.get('Range', None)
        byte1, byte2 = 0, None
        #byte1, byte2 = 0, 1024
        if range_header:
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()

            if groups[0]:
                byte1 = int(groups[0])
            if groups[1]:
                byte2 = int(groups[1])

        chunk, start, length, file_size = self.get_chunk(param1, byte1, byte2)
        resp = Response(chunk, 206, mimetype='video/mp4',
                      content_type='video/mp4', direct_passthrough=True)
        resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
        resp.headers.add('Accept-Ranges', 'bytes')
        return resp

    @expose('/stream/<string:param1>')
    @has_access
    def stream2(self, param1):
        #file_name = "0a81e91c-3307-11ec-b8cf-005056a50b96_sep_20210613_154319.mp4"
        return render_template('my_list.html',file_name='/teststream/video/'+param1, base_template=appbuilder.base_template, appbuilder=appbuilder)

    @expose('/photo/<string:param1>')
    @has_access
    def photo(self, param1):
        full_path = "/static/uploads/" + param1
        return send_file(full_path, mimetype='image/jpg')

    @expose('/image/<string:param1>')
    @has_access
    def image2(self, param1):
        return render_template('my_list2.html',file_name='/teststream/photo/'+param1, base_template=appbuilder.base_template, appbuilder=appbuilder)

"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )

db.create_all()
"""
appbuilder.add_view(
    TestTableView,
    "CRUD Test",
    icon = "fa-folder-open-o",
    category = "TEST MENU",
    category_icon = "fa-envelope"
)
appbuilder.add_view(
    ContentMasterView,
    "Content Master",
    icon = "fa-folder-open-o",
    category = "TEST MENU"
)
appbuilder.add_view(
    ProgramView,
    "Program",
    icon = "fa-folder-open-o",
    category = "TEST MENU"
)
appbuilder.add_view(
    EcamFileView,
    "File Up/Down",
    icon = "fa-folder-open-o",
    category = "TEST MENU"
)
appbuilder.add_view_no_menu(TestStream, "stream")
appbuilder.add_api(ContentsManager)
appbuilder.add_api(UserManager)
appbuilder.add_api(ContentMasterApi)
appbuilder.add_api(ProgramApi)
"""
appbuilder.add_view(
    Mp4ContentMasterView,
    "Mp4 Contents",
    icon = "fa-folder-open-o",
    category = "Contents",
    category_icon = "fa-envelope"
)
appbuilder.add_view(
    UTubeContentMasterView,
    "YouTube Contents",
    icon = "fa-folder-open-o",
    category = "Contents",
    category_icon = "fa-envelope"
)
appbuilder.add_view(
    UTubeContentCaptionView,
    "Captions",
    icon = "fa-folder-open-o",
    category = "Contents",
    category_icon = "fa-envelope"
)
appbuilder.add_view(
    SplitCaptionView,
    "Caption 분할",
    icon = "fa-folder-open-o",
    category = "Contents",
    category_icon = "fa-envelope"
)
appbuilder.add_view(
    DictionaryView,
    "Dictionary",
    icon = "fa-folder-open-o",
    category = "Contents",
    category_icon = "fa-envelope"
)

appbuilder.add_api(ContentsInfo)
appbuilder.add_api(UTubeContent)
appbuilder.add_api(HlsContent)
appbuilder.add_api(UTubeContentMasterAPI)
appbuilder.add_api(Mp4ContentMasterAPI)