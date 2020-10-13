import os
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_caching import Cache
from werkzeug.utils import secure_filename
import requests
from subprocess import Popen, DEVNULL
from uuid import uuid4

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
UPLOAD_FORM_IMAGE_PARAM = 'image'
UPLOAD_DIR = 'assets/uploads'
WEB_REL_UPLOAD_DIR = '/' + UPLOAD_DIR
ABS_UPLOAD_DIR = os.path.join(APP_ROOT, UPLOAD_DIR)

tasks = {}

app = Flask(__name__)

# Configure Bootstrap with Python
Bootstrap(app)

# clear Cache whenever re-run the server
cache = Cache()

cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    # Fall back to simple in memory cache (development)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
else:
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(app,
    config={'CACHE_TYPE': 'saslmemcached',
            'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
            'CACHE_MEMCACHED_USERNAME': cache_user,
            'CACHE_MEMCACHED_PASSWORD': cache_pass,
            'CACHE_OPTIONS': { 'behaviors': {
                # Faster IO
                'tcp_nodelay': True,
                # Keep connection alive
                'tcp_keepalive': True,
                # Timeout for set/get requests
                'connect_timeout': 2000, # ms
                'send_timeout': 750 * 1000, # us
                'receive_timeout': 750 * 1000, # us
                '_poll_timeout': 2000, # ms
                # Better failover
                'ketama': True,
                'remove_failed': 1,
                'retry_timeout': 2,
                'dead_timeout': 30}}})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/assets/<path:path>')
def send_js(path):
    return send_from_directory('assets', path)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/upload-file', methods=['POST'])
def upload_file():
    if UPLOAD_FORM_IMAGE_PARAM not in request.files:
        return redirect(request.url)

    file = request.files[UPLOAD_FORM_IMAGE_PARAM]

    # if user does not select file, browser also submit an empty part without filename
    if file.filename == '' and not file or not allowed_file(file.filename):
        return redirect(request.url)

    filename = secure_filename(file.filename)
    absolute_filepath = os.path.join(ABS_UPLOAD_DIR, filename)

    input_file  = f'{WEB_REL_UPLOAD_DIR}/{filename}'
    result_file = cache.get(input_file)
    if result_file is not None:
        return render_template('result.html', input_file=input_file, result_file=result_file, in_cache=True)

    file.save(absolute_filepath)

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


@app.route('/get-results/<string:pid>')
def get_results(pid):

    if pid not in tasks:
        return jsonify({"err": "No such task."})
    task = tasks[pid]

    input_file  = os.path.join(WEB_REL_UPLOAD_DIR, task['filename'])
    result_file = cache.get(input_file)

    process: Popen = task['process']
    if process.poll() is None:
        return jsonify({
            'running': True
        })

    # !Future Improvement: Use to retrieve the file faster
    result_file = f'/assets/segmentingData/{task["filename"]}'
    cache.set(input_file, result_file)

    return jsonify({
        'running': False,
        'html': render_template('result.html', input_file=input_file, result_file=result_file)
    })


if __name__ == '__main__':
    with app.app_context():
        cache.clear()

    # Create upload folder called /uploads
    if not os.path.isdir(ABS_UPLOAD_DIR):
        os.mkdir(ABS_UPLOAD_DIR)

    app.run(port=5000, debug=True)
