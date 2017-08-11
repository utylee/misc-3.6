from flask import Flask, render_template 
from flask_socketio import *


app = Flask(__name__)
sock =  SocketIO(app)

@app.route('/')
@app.route('/index')
def index():
    #return 'hello world'
    return render_template('index.html')

if __name__ == "__main__":
    sock.run(app, host="0.0.0.0", port="5000")

