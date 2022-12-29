from flask import g
from wtforms.validators import ValidationError
import enum
import uuid
import socket
from datetime import datetime
import yaml
import traceback
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO, StringIO

def get_user():
    return g.user.username

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_hostname():
    return socket.gethostname()

def get_uuid():
    return str(uuid.uuid4())[-12:]

def getStrfile(text):
    output = BytesIO(bytes(text,'utf-8'))
    output.seek(0)
    return output

def getAlNumCnt(text):
    return len([le for le in text if le.isalnum()])

def getUtubeCap(id):
    return YouTubeTranscriptApi.get_transcript(id, languages=['en'])

def getUtubeCapYaml(id):

    jlist = getUtubeCap(id)
    
    data = []
    for j in jlist:
      del j['duration']
      data.append(j)

    return str(yaml.dump(data))

def getUtubeCapYamlFile(id):

    data_s = getUtubeCapYaml(id)

    return getStrfile(data_s)

class YnEnum(enum.Enum):
    YES = 'YES'
    NO  = 'NO'

class DifficultyEnum(enum.Enum):
    LEVEL1 = 'Level 1'
    LEVEL2 = 'Level 2'
    LEVEL3 = 'Level 3'
    LEVEL4 = 'Level 4'
    LEVEL5 = 'Level 5'
    LEVEL6 = 'Level 6'
    LEVEL7 = 'Level 7'

class SplitTypeEnum(enum.Enum):
    FIXED_WEIGHT = 'Fixed size'
    SAME_WEIGHT  = 'Same size'
    BY_TITLE     = 'Classified by title'
    CUSTOM_DEFINED = 'Custom defined'

class VerifyYaml(object):

    def __init__(self) -> None:
        pass

    def __call__(self, form, field):
        
        if not field.data:
            raise ValidationError(field.gettext("자막 정보가 공백입니다."))

        try:
            jlist =  yaml.safe_load(field.data)
        except yaml.parser.ParserError as e:
            message = field.gettext('Yaml Parsing Error. ' + traceback.format_exc())
            raise ValidationError(message)