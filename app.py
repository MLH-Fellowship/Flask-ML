import os
from flask import Flask, render_template, request, send_from_directory, redirect
from flask_bootstrap import Bootstrap

from werkzeug.utils import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
UPLOAD_FORM_IMAGE_PARAM = 'image'


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


@app.route('/upload-file', methods=['POST', 'GET'])
def upload_file():
    target = os.path.join(APP_ROOT, 'uploads/')

    # If folder does not exist, mkdir the folder
    if not os.path.isdir(target):
        os.mkdir(target)

    if request.method == 'POST':
        if UPLOAD_FORM_IMAGE_PARAM not in request.files:
            # flash('No file part')
            return redirect(request.url)

        file = request.files[UPLOAD_FORM_IMAGE_PARAM]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(target, filename))

            # TODO: Need to integrate with @Yida's BentoML Services

            return redirect('/upload-file')
    return render_template('result.html')


if __name__ == '__main__':
    app.run()
