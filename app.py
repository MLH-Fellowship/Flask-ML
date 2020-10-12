import os
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_caching import Cache
from werkzeug.utils import secure_filename
import requests
from subprocess import Popen
from uuid import uuid4

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
UPLOAD_FORM_IMAGE_PARAM = 'image'
UPLOAD_DIR = 'assets/uploads'
WEB_REL_UPLOAD_DIR = '/' + UPLOAD_DIR
ABS_UPLOAD_DIR = os.path.join(APP_ROOT, UPLOAD_DIR)

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

tasks = {}

app = Flask(__name__)
app.config.from_mapping(config)

# Configure Bootstrap with Python
Bootstrap(app)

# clear Cache whenever re-run the server
cache = Cache(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/assets/<path:path>')
def send_js(path):
    return send_from_directory('assets', path)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/upload-file', methods=['POST'])
# @cache.cached(timeout=300)  # cache this image result for 5 minutes
def upload_file():
    if UPLOAD_FORM_IMAGE_PARAM not in request.files:
        print('redirect 1')
        return redirect(request.url)

    file = request.files[UPLOAD_FORM_IMAGE_PARAM]

    # if user does not select file, browser also submit an empty part without filename
    if file.filename == '':
        print('redirect 2')
        return redirect(request.url)

    if not file or not allowed_file(file.filename):
        print('redirect 3')
        return redirect(request.url)

    filename = secure_filename(file.filename)
    absolute_filepath = os.path.join(ABS_UPLOAD_DIR, filename)
    file.save(absolute_filepath)

    # TODO: Need to integrate with @Yida's BentoML Services. Call BentoML API

    pid = str(uuid4())

    process = Popen(['bentoml', 'run', 'PytorchImageSegment:latest',
                     'predict',  f'--input-file={absolute_filepath}'], cwd=os.path.join(APP_ROOT, 'img_process_backend'))

    tasks[pid] = {
        'filename': filename,
        'process': process
    }

    return redirect(f'/processing/{pid}')


@app.route('/processing/<string:pid>', methods=['GET'])
def processing(pid):
    return render_template('processing.html', pid=pid)


@app.route('/get-results/<string:pid>', methods=['GET'])
# @cache.cached(timeout=300)  # cache this image result for 5 minutes
def get_results(pid):
    if pid not in tasks:
        return jsonify({"err": "No such task."})
    task = tasks[pid]
    process: Popen = task['process']

    # !Ping the client when it's done

    if process.poll() is None:
        print('running')
        return jsonify({
            'running': True
        })
    else:
        print('done')
        return jsonify({
            'running': False,
            'html': render_template('result.html', input_file=os.path.join(WEB_REL_UPLOAD_DIR, task['filename']), result_file=f'/assets/segmentingData/{task["filename"]}')
        })


if __name__ == '__main__':
    with app.app_context():
        cache.clear()

    # Create upload folder called /uploads
    if not os.path.isdir(ABS_UPLOAD_DIR):
        os.mkdir(ABS_UPLOAD_DIR)

    app.run(port=5000, debug=True)
