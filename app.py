import os
from flask import Flask, render_template, request, send_from_directory, redirect
from flask_bootstrap import Bootstrap
from flask_caching import Cache
from werkzeug.utils import secure_filename
import requests

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
UPLOAD_FORM_IMAGE_PARAM = 'image'
UPLOAD_DIR = os.path.join(APP_ROOT, 'assets/uploads')

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

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
@cache.cached(timeout=300) # cache this image result for 5 minutes
def upload_file():
    if UPLOAD_FORM_IMAGE_PARAM not in request.files:
        return redirect(request.url)

    file = request.files[UPLOAD_FORM_IMAGE_PARAM]

    # if user does not select file, browser also submit an empty part without filename
    if file.filename == '':
        return redirect(request.url)

    if not file or not allowed_file(file.filename):
        return redirect(request.url)

    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_DIR, filename))

    # TODO: Need to integrate with @Yida's BentoML Services. Call BentoML API
    fileToUpload = {'file': file.read()}
    r = requests.post('http://localhost:5000/predict', fileToUpload)

    if r.ok:
        return render_template('result.html')
    else:
        return "Error Uploading file!"



if __name__ == '__main__':
    with app.app_context():
        cache.clear()

    # Create upload folder called /uploads
    if not os.path.isdir(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)

    app.run(port=8080, debug=True)


