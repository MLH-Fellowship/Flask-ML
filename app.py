from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def hello():
    return render_template('index.html', client_ip=request.remote_addr)


if __name__ == '__main__':
    app.run()
