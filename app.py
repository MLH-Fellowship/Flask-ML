from flask import Flask, render_template, request, send_from_directory
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route('/assets/<path:path>')
def send_js(path):
    return send_from_directory('assets', path)


@app.route('/')
def hello():
    return render_template('index.html', client_ip=request.remote_addr)


if __name__ == '__main__':
    app.run()
