from flask import *
import sqlite3
from db.queries import *
from decorators import verifylogged
from config import dbbasepath,nosqldbpath
from hashlib import sha256
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = "1234567890"


from routes.main import mainblueprint
app.register_blueprint(mainblueprint)
from routes.oauth import authblueprint
app.register_blueprint(authblueprint)
from routes.api import apiblueprint
app.register_blueprint(apiblueprint)




if __name__ == "__main__":
    app.run(debug=True)