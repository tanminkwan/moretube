import os
import redis

from flask_appbuilder.security.manager import (
    AUTH_OID,
    AUTH_REMOTE_USER,
    AUTH_DB,
    AUTH_LDAP,
    AUTH_OAUTH,
)

basedir = os.path.abspath(os.path.dirname(__file__))

# Your App secret key
SECRET_KEY = "\2\1thisismyscretkey\1\2\e\y\y\h"

# The SQLAlchemy connection string.
# SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
# SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'

if os.environ.get('DATABASE_URI'):
  SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']
elif os.environ.get('DATABASE_HOST'):
  db_host = os.environ['DATABASE_HOST']
  db_port = os.environ['DATABASE_PORT']
  db_name = os.environ['DATABASE_NAME']
  db_user = os.environ['DATABASE_USER']
  db_pw   = os.environ['DATABASE_PASSWD']
  SQLALCHEMY_DATABASE_URI = 'postgresql://'+db_user+':'+db_pw+'@'+db_host+':'+db_port+'/'+db_name
else:
  SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1q2w3e4r!!@localhost/more'

STREAM_URL = os.environ['STREAM_URL'] if os.environ.get('STREAM_URL') else ''

if os.environ.get('REDIS_URI'):
  SESSION_TYPE = 'redis'
  SESSION_PERMANENT = False
  SESSION_USE_SIGNER = True
  SESSION_REDIS = redis.from_url(os.environ['REDIS_URI'])

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# ------------------------------
# GLOBALS FOR APP Builder
# ------------------------------
# Uncomment to setup Your App name
APP_NAME = "Study 4 MaMa "

# Uncomment to setup Setup an App icon
# APP_ICON = "static/img/logo.jpg"

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# The authentication type
# AUTH_OID : Is for OpenID
# AUTH_DB : Is for database (username/password()
# AUTH_LDAP : Is for LDAP
# AUTH_REMOTE_USER : Is for using REMOTE_USER from web server
AUTH_TYPE = AUTH_DB

# Uncomment to setup Full admin role name
# AUTH_ROLE_ADMIN = 'Admin'

# Uncomment to setup Public role name, no authentication needed
# AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
# AUTH_USER_REGISTRATION = True

# The default user self registration role
# AUTH_USER_REGISTRATION_ROLE = "Public"

# When using LDAP Auth, setup the ldap server
# AUTH_LDAP_SERVER = "ldap://ldapserver.new"

# Uncomment to setup OpenID providers example for OpenID authentication
# OPENID_PROVIDERS = [
#    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
#    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
#    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
#    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
# ---------------------------------------------------
# Babel config for translations
# ---------------------------------------------------
# Setup default language
BABEL_DEFAULT_LOCALE = "ko"
# Your application default translation path
BABEL_DEFAULT_FOLDER = "translations"
# The allowed translation for you app
LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
    "es": {"flag": "es", "name": "Spanish"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
    "pl": {"flag": "pl", "name": "Polish"},
    "ko": {"flag": "ko", "name": "Coree"},
}
# ---------------------------------------------------
# Image and file configuration
# Modified by Hennry
# ---------------------------------------------------
if os.name == 'nt':
    UPLOAD_FOLDER = "C:/static/uploads/"
    IMG_UPLOAD_FOLDER = "C:/static/uploads/images/"
    HLS_STREAM_FOLDER = "C:/static/hls/"
else:
    # The file upload folder, when using models with files
    UPLOAD_FOLDER = "/static/uploads/"

    # The image upload folder, when using models with images
    IMG_UPLOAD_FOLDER = "/static/uploads/images/"
    HLS_STREAM_FOLDER = "/static/hls/"

# The image upload url, when using models with images
IMG_UPLOAD_URL = "/static/uploads/"
# Setup image size default is (300, 200, True)
# IMG_SIZE = (300, 200, True)

# Added by Hennry
FAB_API_SWAGGER_UI = True

# Added by Hennry
SCHEDULER_API_ENABLED = True

# Theme configuration
# these are located on static/appbuilder/css/themes
# you can create your own and easily use them placing them on the same dir structure to override
# APP_THEME = "bootstrap-theme.css"  # default bootstrap
# APP_THEME = "cerulean.css"
# APP_THEME = "amelia.css"
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "readable.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"
# APP_THEME = "spacelab.css"
# APP_THEME = "united.css"
# APP_THEME = "yeti.css"

