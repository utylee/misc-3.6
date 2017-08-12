from sanic import Sanic
from sanic.response import text, html, file


app = Sanic()

@app.route('/')
def index(request):
    return text('하하')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='7777')

