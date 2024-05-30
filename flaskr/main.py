from flaskr import app
from flask import render_template

@app.route('/') #topのURLを示す
def index(): #top画面にアクセスした時実行される
    return render_template(
        'index.html'
    )
