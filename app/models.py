from flask import Markup, url_for
from flask_appbuilder import Model
from flask_appbuilder.filemanager import get_file_original_name
from flask_appbuilder.models.mixins import FileColumn
from sqlalchemy import Table, Column, Integer, Float, String, Text, ForeignKey\
    , DateTime, Enum, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .common import get_user, get_now, get_hostname, YnEnum, DifficultyEnum, SplitTypeEnum
from .queries import get_thumbnailpath
from . import app

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who

"""
class Dictionary(Model):
    __tablename__ = "dictionary"

    id = Column(Integer, primary_key=True)
    tags         = Column(String(1000), nullable=False, comment='유사단어묶음')
    description  = Column(Text, comment='설명')
    value1       = Column(String(100), comment='부가정보1')
    value2       = Column(String(100), comment='부가정보2')
    user_id      = Column(String(100), default=get_user, nullable=False, comment='입력 user')
    create_on    = Column(DateTime(), default=get_now, nullable=False, comment='입력 일시')
    
    UniqueConstraint(tags)

    __table_args__ = (
        Index('ix_dictionary_gin'
            , func.string_to_array(tags, ',')
            , postgresql_using='gin'
        ),
        {"comment":"사전"}
    )

    def __repr__(self) -> str:
        return self.tags

assoc_mp4_caption = Table('ref_mp4_caption', Model.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('id_of_mp4', Integer, ForeignKey('mp4_content_master.id', ondelete='CASCADE')),
                            Column('id_of_caption', Integer, ForeignKey('utube_content_caption.id', ondelete='CASCADE'))
                        )

class Mp4ContentMaster(Model):
    __tablename__ = "mp4_content_master"
    __table_args__ = {"comment":"mp4 Content file"}
    
    id = Column(Integer, primary_key=True)
    filename        = Column(String(100), nullable=False, comment='컨텐츠 파일 이름')
    file            = Column(FileColumn, nullable=False)
    description     = Column(String(500), nullable=True, comment='설명')
    manifest_path   = Column(String(500), nullable=True, comment='m8u3 파일 url path')
    difficulty   = Column(Enum(DifficultyEnum), info={'enum_class':DifficultyEnum}, comment='난이도')
    user_id      = Column(String(100), default=get_user, nullable=False, comment='입력 user')
    create_on    = Column(DateTime(), default=get_now, nullable=False, comment='입력 일시')

    utube_content_caption  = relationship('UTubeContentCaption', secondary=assoc_mp4_caption, backref='mp4_content_master')

    def __repr__(self) -> str:
        return get_file_original_name(str(self.file))

    def download(self):
        return Markup(
            '<a href="'
            + url_for('Mp4ContentMasterView.download', filename=str(self.file))
            + '">Download</a>'
        )

    def get_filename(self):
        return get_file_original_name(str(self.file))

    def show_html(self):
        return Markup('<a href="/hls/view/'+str(self.id)+'">VIEW</a>')

assoc_utube_caption = Table('ref_utube_caption', Model.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('id_of_utube', Integer, ForeignKey('utube_content_master.id', ondelete='CASCADE')),
                            Column('id_of_caption', Integer, ForeignKey('utube_content_caption.id', ondelete='CASCADE'))
                        )

class UTubeContentMaster(Model):
    __tablename__ = "utube_content_master"
    __table_args__ = {"comment":"Youtube Content 정보"}
    
    id = Column(Integer, primary_key=True)
    content_id  = Column(String(100), nullable=False, comment='YouTube Contents URL')
    play_from    = Column(Integer, nullable=False, comment='')
    play_to      = Column(Integer, nullable=False, comment='')
    content_description  = Column(String(500), nullable=True, comment='설명')
    difficulty   = Column(Enum(DifficultyEnum), info={'enum_class':DifficultyEnum}, comment='난이도')
    user_id      = Column(String(100), default=get_user, nullable=False, comment='입력 user')
    create_on    = Column(DateTime(), default=get_now, nullable=False, comment='입력 일시')
    
    UniqueConstraint(content_id)

    utube_content_caption  = relationship('UTubeContentCaption', secondary=assoc_utube_caption, backref='utube_content_master')

    def __repr__(self) -> str:
        return '['+ self.content_id +']'+ self.content_description[0:30]

    def show_html(self):
        return Markup('<a href="/utube/view/'+str(self.id)+'">VIEW</a>')

class UTubeContentCaption(Model):

    __tablename__ = "utube_content_caption"
    __table_args__ = {"comment":"Youtube Content 자막 정보"}
    
    id = Column(Integer, primary_key=True)
    caption_id   = Column(String(100), nullable=False, comment='YouTube Contents caption info')
    captions     = Column(JSONB, comment='자막(JSON)')
    picked_yn    = Column(Enum(YnEnum), info={'enum_class':YnEnum}, comment='대표 자막 여부')
    captions_yaml = Column(Text, comment='자막(YAML)')
    caption_len  = Column(Integer, comment='자막 전체 길이')
    user_id      = Column(String(100), default=get_user, nullable=False, comment='입력 user')
    create_on    = Column(DateTime(), default=get_now, nullable=False, comment='입력 일시')

    UniqueConstraint(caption_id)

    def __repr__(self) -> str:
        return self.caption_id

    def show_html(self):
        return Markup('<a href="/utube/textview/'+str(self.id)+'">VIEW</a>')

class SplitCaption(Model):

    __tablename__ = "split_caption"
    __table_args__ = {"comment":"학습량 분할 정보"}
    
    id = Column(Integer, primary_key=True)
    split_caption_id  = Column(String(100), nullable=False, comment='학습량 분할 정보')
    contentcaption_id = Column(Integer, ForeignKey('utube_content_caption.id'), nullable=False)
    split_type   = Column(Enum(SplitTypeEnum), info={'enum_class':SplitTypeEnum}, nullable=False, comment='분할 기준')
    split_value  = Column(String(300), nullable=False)
    split_title  = Column(String(300))
    user_id      = Column(String(100), default=get_user, nullable=False, comment='입력 user')
    create_on    = Column(DateTime(), default=get_now, nullable=False, comment='입력 일시')

    utube_content_caption = relationship('UTubeContentCaption')

    UniqueConstraint(split_caption_id)

    def __repr__(self) -> str:
        return self.split_caption_id

class ContentMaster(Model):

    __tablename__ = "content_master"
    __table_args__ = {"comment":"Content 정보"}
    
    id = Column(Integer, primary_key=True)
    filename        = Column(String(100), nullable=False, comment='컨텐츠 파일 이름')
    stored_filename = Column(String(500), nullable=False, comment='등록된 파일 이름')
    description     = Column(String(500), nullable=True, comment='설명')
    content_type    = Column(String(50), nullable=True, comment='컨텐츠 Type')
    file_type       = Column(String(50), nullable=True, comment='파일 Type')
    manifest_path   = Column(String(500), nullable=True, comment='m8u3 파일 url path')
    ref_stored_filename = Column(String(500), nullable=True, comment='참조하는 파일 이름')
    valid_yn        = Column(Enum(YnEnum), info={'enum_class':YnEnum}, comment='파일 유효성 여부')
    hostname        = Column(String(200), default=get_hostname, nullable=False, comment='입력 서버')
    user_id         = Column(String(100), default=get_user, nullable=False, comment='입력 user')
    create_on       = Column(DateTime(), default=datetime.now, nullable=False, comment='입력 일시')
    
    UniqueConstraint(stored_filename)
    
    def stream_url(self):
        return app.config['STREAM_URL'] if self.valid_yn is not None and self.valid_yn.name == 'YES' else ''
    
    def thumbnail_path(self):
        return get_thumbnailpath(self.stored_filename)

    def __repr__(self):
        return self.filename

assoc_program_contentmaster = Table('ref_program_contentmaster', Model.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('id_of_program', Integer, ForeignKey('program.id', ondelete='CASCADE')),
                                    Column('id_of_contentmaster', Integer, ForeignKey('content_master.id', ondelete='CASCADE'))
                                    )

class Program(Model):

    __tablename__ = "program"
    __table_args__ = {"comment":"교육 과정"}
    
    id = Column(Integer, primary_key=True)
    program_name    = Column(String(200), nullable=False, comment='교육 과정 이름')
    description     = Column(Text, nullable=True, comment='설명')
    author          = Column(String(100), nullable=True, comment='작성자')
    hostname        = Column(String(200), default=get_hostname, nullable=False, comment='입력 서버')
    user_id         = Column(String(100), default=get_user, nullable=False, comment='입력 user')
    create_on       = Column(DateTime(), default=datetime.now, nullable=False, comment='입력 일시')

    content_master  = relationship('ContentMaster', secondary=assoc_program_contentmaster, backref='program')
    
    def contentmaster(self):
        contents = []
        for row in self.content_master:
            contents.append(row.id)
        return contents
        
    def __repr__(self):
        return self.program_name

class TestTable(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    create_on = Column(DateTime(), default=datetime.now, nullable=False)

    def __repr__(self):
        return self.name

class EcamFile(Model):
    __tablename__ = "ecam_file"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    file = Column(FileColumn, nullable=False)
    create_on = Column(DateTime(), default=datetime.now, nullable=False)

    def type_t(self):

        file_type = str(self.file).split('.')[-1:][0].upper()

        if file_type == 'MP4':
            html_t = "<button type=\"button\" onclick=\"location.href=\'"
            html_t = html_t + '/teststream/stream/' + str(self.file)
            html_t = html_t + "\'\">" + file_type + "</button>"
        elif file_type == 'JPG':
            html_t = "<button type=\"button\" onclick=\"location.href=\'"
            html_t = html_t + '/teststream/image/' + str(self.file)
            html_t = html_t + "\'\">" + file_type + "</button>"
        else:
            html_t = "<p>" + file_type + "</p>"

        return Markup(html_t)

    def download(self):
        return Markup(
                '<a href="'
                + url_for("EcamFileView.download", filename=str(self.file))
                + '">Download</a>'
                )

    def __repr__(self):
        return self.name
