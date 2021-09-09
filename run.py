from datetime import time
import logging
import subprocess
import threading
import time
from flask.helpers import make_response
#import matplotlib
import os
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
import numpy
#from sklearn.linear_model import LinearRegression
import pandas
from flask.json import jsonify
from flask import (Flask, json, redirect, render_template, request, session,
                   url_for)
from flask_bootstrap import Bootstrap
from pandas.io.parsers import TextParser

import sqlite3
from sqlite3 import Error

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
    return redirect(url_for('home'))
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
    return redirect(url_for('home'))


@app.route('/loadData')
def loadData():
    try:
        name = request.args.get('name')        
        if name == 'simples':    
            base = pandas.read_csv('./static/cars.csv')
            logging.error('name: {}'.format(base.head().to_json()))
        return base.head().to_json()        
    except Exception as e:
        return redirect(url_for('main'))


# Seção 22 - Regressão linear simples
@app.route('/linearRegression', methods=['POST'])
def linearRegression():
    try:        
        distancia = request.form.get('distancia')        
        response = dict([('distancia', distancia)])

        #Carrega planilha de dados
        base = pandas.read_csv('./static/cars.csv')
        base = base.drop(['Unnamed: 0'], axis = 1)
        x = base.iloc[:, 1].values #distância
        y = base.iloc[:, 0].values #velocidade

        #Correlação
        #Correlações próximas de 1 são fortes. Podem ser positivas ou negativas
        correlacao = numpy.corrcoef(x, y)
        response['correlacao'] = correlacao[0][1]        

        dirname = os.path.dirname(__file__)
    
        #Regressão
        x = x.reshape(-1, 1)
        ##modelo = LinearRegression()
        ##modelo.fit(x, y)

        #Criação do gráfico para visualização        
        filename = r'./{}'.format(url_for('static', filename='scatter.png'))             
        # plt.scatter(x, y)
        # plt.plot(x, modelo.predict(x), color = "gray")
        # plt.savefig(filename, bbox_inches='tight')
        response['scatter'] = filename

        #Regressão com predição                
        filename = r'./{}'.format(url_for('static', filename='scatterpred.png'))
        x = x.reshape(-1, 1)
        ##modelo = LinearRegression()
        ##modelo.fit(x, y) 

        #Transforma m em ft
        feet = float(distancia) / 0.3048

        ##p = modelo.predict([[feet]])
        ##convertido = numpy.array(p, dtype=numpy.float32)
        ##response['predicao'] = str(convertido[0])
        response['predicao'] = 'sem predição'
      
        # plt.scatter(x, y)
        # plt.plot(x, modelo.predict(x), color = "gray")
        # plt.savefig(filename, bbox_inches='tight')
        response['scatter1'] = filename

        #print(response)

        return render_template("linearRegression.html", data=response)
        
    except Exception as e:
        return 'Mensagem: {}'.format(e)


@app.route('/gps', methods=['GET'])
def gps():
    try:
        
        # return render_template('gps.html', data=MyOut)
        global getDataGps
        getDataGps=True
        global x
        x=threading.Thread(target=getLocation, args=(1,))        
        x.start()
        return render_template('gps.html', data='Thread ativada')

    except Exception as e:
        return 'Erro: {}'.format(e)        

@app.route('/gpsStop', methods=['GET'])
def gpsStop():
    try:
        global getDataGps
        getDataGps=False
        global x
        x.join()
        return render_template('gps.html', data='Thread desativada')
    except Exception as e:
        return 'Erro: {}'.format(e)

def getLocation(param):
    try:
        c = createConnection('location.db')
        while True:            
            myOut = subprocess.call(f'''termux-location''', shell=True)
            myOut = 'Accessing GPS'
            print(myOut)
            time.sleep(5)
            if not getDataGps:
                break

    except Exception as e:
        print('Erro: {}'.format(e))


def createConnection(dbFile):
    """create a SQLite database connection"""
    conn=None
    try:
        conn=sqlite3.connect(dbFile)
        print("Conectado a Sqlite3 {}".format(sqlite3.version))
    except Error as e:
        print(e)
    # finally:
    #     if conn:
    #         conn.close()
    return conn


if __name__ =='__main__':
    app.run(debug=True)
