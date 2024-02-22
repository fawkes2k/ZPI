from flask import Flask
from datetime import timedelta
from waitress import serve
from dotenv import load_dotenv
from os import getenv
from api import api

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET")
app.permanent_session_lifetime = timedelta(days=100)
app.register_blueprint(api, url_prefix='/api')

if __name__ == "__main__": serve(app, host="0.0.0.0", port=5000)
