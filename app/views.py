from flask import g, render_template, request, Response, send_file, jsonify
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import BaseView, ModelView, ModelRestApi, has_access
from flask_appbuilder.filemanager import FileManager, uuid_namegen
from flask_appbuilder.api import BaseApi, expose, protect
from .models import Dictionary, UTubeContentMaster, UTubeContentCaption\
  , ContentMaster, TestTable, EcamFile, Program
from . import appbuilder, db, app
from .scheduled_jobs import job_create_job
from .queries import selectRow, selectDict
from .common import VerifyYaml

from io import BytesIO
import os
import re
import json
import yaml
from youtube_transcript_api import YouTubeTranscriptApi

REPMAP = [
  ('(s(','<span class="w_subject">'),
  ('(v(','<span class="w_verb">'),
  ('(<(','<span class="p_relative">'),
  ('(t(','<span class="p_title">'),
  ('(d(','<span class="w_dict" onclick="viewDict(this)">'),
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

def addIdNStart(jlist):

    jlist2 = _addEnd(jlist)
    return _addID(jlist2)

def convertYcap2Jcap(ycap):
    decoed_ycap = _setDeco(ycap)
    jlist =  yaml.safe_load(decoed_ycap)
    jlist2 = _addEnd(jlist)
    jlist3 =_removeEmpty(jlist2)
    return _addID(jlist3)

@db.event.listens_for(ContentMaster, 'after_insert')
def update_stream_info(mapper, connection, target):
    
    job_create_job(target)

@db.event.listens_for(UTubeContentCaption, 'before_update')
def update_stream_info(mapper, connection, target):
    
    jdata = convertYcap2Jcap(target.captions_yaml)
    target.captions = {'data':jdata}

    print('UTubeContentCaption update!!')

@db.event.listens_for(UTubeContentCaption, 'before_insert')
def update_stream_info(mapper, connection, target):
    
    jdata = convertYcap2Jcap(target.captions_yaml)
    target.captions = {'data':jdata}

    print('UTubeContentCaption insert!!')

class DictionaryView(ModelView):
    datamodel = SQLAInterface(Dictionary)
    list_title = 'Dictionary'
    list_columns = ['tags','value1']
    #label_columns = {'id':'SEQ','name':'이름','description':'메세지','create_on':'생성일지'}
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

class UTubeContentCaptionView(ModelView):
    datamodel = SQLAInterface(UTubeContentCaption)
    list_title = 'YouTube Content Captions'
    list_columns = ['utube_content_master','show_html','caption_id','picked_yn','create_on']
    edit_exclude_columns = ['captions','id','create_on']
    add_exclude_columns = ['captions','id','create_on']
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

class UTubeContentMasterView(ModelView):
    datamodel = SQLAInterface(UTubeContentMaster)
    list_title = 'YouTube Contents'
    list_columns = ['show_html','content_description','content_id','download_yaml','play_from','play_to','create_on']
    #label_columns = {'id':'SEQ','name':'이름','description':'메세지','create_on':'생성일지'}
    edit_exclude_columns = ['id','create_on']
    add_exclude_columns = ['id','create_on']

    related_views = [UTubeContentCaptionView]

class UTubeContentMasterAPI(ModelRestApi):

    resource_name = 'utubecontentmaster'

    datamodel = SQLAInterface(UTubeContentMaster)

    list_columns = ['show_html','content_description','content_id','download_yaml','play_from','play_to','user_id','create_on']


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

    @expose('/dictionary/<word>', methods=['GET'])
    @has_access
    def getDictionary(self, word):
      
      recs, _ = selectDict(word)

      rlist = []
      if recs:
        rlist = [ r.description for r in recs ]
      
      return jsonify({'data':rlist})

    @expose('/caption/<id>', methods=['GET'])
    @has_access
    def getCaption(self, id):
      
      data = []
      content, _ = selectRow('utube_content_master',{'content_id':id})

      row, _ = selectRow('utube_content_caption',{'content_master_id':content.id,'picked_yn':'YES'})

      if row:
        data = row.captions['data']
        #jlist =  yaml.safe_load(row.captions_yaml)
        #data = [ j | {'id':i} for i, j in enumerate(jlist)]
      else:
        jlist = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
        data = addIdNStart(jlist)
      
      return jsonify(data)

    @expose('/caption_yaml/<id>', methods=['GET'])
    @has_access
    def getCaptionYaml(self, id):
      
      jlist = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
      #data = [ j | {'id':i,'end':round(j['start']+j['duration'],2)} for i, j in enumerate(jlist)]
      #data = [ j | {'id':i,'end':round(jlist[i+1 if i+1!=len(jlist) else i]['start']+0.1,2)} for i, j in enumerate(jlist)]
      #data = [ j | {'text':j['text']} for j in jlist]
      data = []
      for j in jlist:
        del j['duration']
        data.append(j)

      data_y = yaml.dump(data)
      
      data_s = str(data_y)
      output = BytesIO(bytes(data_s,'utf-8'))
      output.seek(0)

      return send_file(output, attachment_filename=id+'_test.yaml', as_attachment=True)    
  
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

class UTubeContent(BaseApi):

    route_base = '/utube'

    @expose('/view/<id>', methods=['GET'])
    @has_access
    def view(self, id=None):

      row, _ = selectRow('utube_content_master',{'id':int(id)})

      if row:
        return render_template('utube_show.html',\
                content_id  = row.content_id,
                play_from   = row.play_from,
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

        title = row.utube_content_master.content_description

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
    DictionaryView,
    "Dictionary",
    icon = "fa-folder-open-o",
    category = "Contents",
    category_icon = "fa-envelope"
)

appbuilder.add_api(ContentsInfo)
appbuilder.add_api(UTubeContent)
appbuilder.add_api(UTubeContentMasterAPI)