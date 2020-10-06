from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html', client_ip=request.remote_addr)


if __name__ == '__main__':
    app.run()
