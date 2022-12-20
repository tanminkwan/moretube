from flask import g
from wtforms.validators import ValidationError
import enum
import uuid
import socket
from datetime import datetime
import yaml
import traceback

def get_user():
    return g.user.username

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_hostname():
    return socket.gethostname()

def get_uuid():
    return str(uuid.uuid4())[-12:]

def getAlNumCnt(text):
    return len([le for le in text if le.isalnum()])

class YnEnum(enum.Enum):
    YES = 'YES'
    NO  = 'NO'

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