import subprocess
import logging
from flask import Flask,request, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def home() :                                        
    return render_template("index.html")

@app.route('/voz',methods=["GET","POST"])
def playsound():
    #if request.method == 'GET':
    #    return render_template('voz.html')
    logging.warning('Requisição: {}'.format(request.form))    
    text = request.form.get("control-msg")    
    MyOut1 = subprocess.call(f'''termux-volume music 15''', shell=True)
    MyOut = subprocess.call(f'''termux-tts-speak {text}''', shell=True)
    #return render_template("index.html")
    return home()
    #return welcome('Marlon')

@app.route('/sms', methods=['GET','POST'])
def sendsms():
    if request.method == 'GET':
        return render_template('index.html')
    number = request.form.get('fonenumber')
    text = request.form.get('message')
    logging.warning('SMS: {}'.format(request.form)) 
    logging.warning('SMS: {}'.format(number))
    logging.warning('SMS: {}'.format(text))
    
    MyOut = subprocess.call(f'''termux-sms-send -n {number} {text}''', shell=True)  
    
    return home()

if __name__ =='__main__':
    app.run(debug=True)
