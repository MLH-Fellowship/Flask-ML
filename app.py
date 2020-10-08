import os
from flask import Flask, render_template, request, send_from_directory, redirect
from flask_bootstrap import Bootstrap

from werkzeug.utils import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
UPLOAD_FORM_IMAGE_PARAM = 'image'
UPLOAD_DIR = os.path.join(APP_ROOT, 'upload')


app = Flask(__name__)
Bootstrap(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/assets/<path:path>')
def send_js(path):
    return send_from_directory('assets', path)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/upload-file', methods=['POST'])
def upload_file():
    if UPLOAD_FORM_IMAGE_PARAM not in request.files:
        # flash('No file part')
        return redirect(request.url)

    file = request.files[UPLOAD_FORM_IMAGE_PARAM]

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        # flash('No selected file')
        return redirect(request.url)

    if not file or not allowed_file(file.filename):
        # flash('No selected file')
        return redirect(request.url)

    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_DIR, filename))

    # TODO: Need to integrate with @Yida's BentoML Services

    return render_template('result.html')


def app_setup():
    # If folder does not exist, mkdir the folder

    if not os.path.isdir(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)


if __name__ == '__main__':
    app_setup()
    app.run()
