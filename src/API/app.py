from flask import Flask, send_from_directory
from asgiref.wsgi import WsgiToAsgi
from asyncio import run
from hypercorn.config import Config
from hypercorn.asyncio import serve
from dotenv import load_dotenv
from os import getenv
from api import api

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv('SECRET')
app.register_blueprint(api, url_prefix='/api')
app_async = WsgiToAsgi(app)
app.config['UPLOAD_FOLDER'] = getenv('UPLOAD_FOLDER')


@app.route('/<path:path>', methods=['GET'])
async def main(path): return send_from_directory('../../html', path)


@app.route('/attachment/<name>')
def get_video(name): return send_from_directory('{}/attachments/'.format(app.config['UPLOAD_FOLDER']), name)


if __name__ == '__main__': run(serve(app_async, Config()))
