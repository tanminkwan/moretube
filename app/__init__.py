import logging

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_appbuilder import AppBuilder, SQLA, IndexView

"""
 Logging configuration
"""
class MyIndexView(IndexView):
    index_template = 'my_index.html'

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)

migrate = Migrate(app, db)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

CORS(app)
appbuilder = AppBuilder(app, db.session, indexview=MyIndexView)

"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

from . import views, scheduled_jobs
