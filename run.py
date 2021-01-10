import subprocess
from flask import Flask,request, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def home() :                                        return render_template("index.html")

@app.route('/voz',methods=["GET","POST"])
def playsound():
    if request.method == 'GET':
        return render_template('voz.html')

    #text = request.values.get("control_msg")
    #text = request.form.get("control_msg")
    text = request.values.get("text")
    MyOut1 = subprocess.call(f'''termux-volume music 15''', shell=True)
    MyOut = subprocess.call(f'''termux-tts-speak {text}''', shell=True)
    return render_template("index.html")

@app.route('/welcome/<name>')
def welcome(name=None):
    return render_template('welcome.html', name=name)

if __name__ =='__main__':
    app.run(debug=True)
