from datetime import datetime
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
import json
import sqlite3
from sqlite3 import Error
import math
import copy

app = Flask(__name__)
Bootstrap(app)

local = 'celular'

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
        return 'Erro em gps: {}'.format(e)        

@app.route('/gpsStop', methods=['GET'])
def gpsStop():
    try:
        global getDataGps
        getDataGps=False
        global x
        x.join()
        return render_template('gps.html', data='Thread desativada')
    except Exception as e:
        return 'Erro em gpsStop: {}'.format(e)

def getLocation(param):    
    try:
        
        while True:            
            if local == 'celular':
                myOut = subprocess.check_output(f'''termux-location -p network''', shell=True).strip()
            else:
                myOut = {'latitude':-25.2809042,'longitude':-54.0720255,'altitude': 789,'speed': 321,'data':f'{datetime.now()}'}
            logging.warning(f"{datetime.now()} termux-location: {myOut}")
            try:
                if local == 'celular':
                    transformed=myOut.decode('utf-8')
                else:
                    transformed=json.dumps(myOut)
                myJson=json.loads(transformed)
                insertData(myJson)
            except Error as e:
                pass

            time.sleep(5)

            if not getDataGps:
                break

    except Exception as e:
        print('Erro em getLocation: {}'.format(e))


def createConnection(dbFile):
    """create a SQLite database connection"""
    conn=None
    try:
        conn=sqlite3.connect(dbFile
            ,detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        print("Conectado a Sqlite3 {}".format(sqlite3.version))

        # sql criação de tabelas
        sql = '''CREATE TABLE IF NOT EXISTS LOCATION(
            LATITUDE TEXT NOT NULL
            ,LONGITUDE TEXT NOT NULL
            ,ALTITUDE REAL
            ,SPEED REAL
            ,DATA TIMESTAMP NOT NULL);'''
        if conn is not None:
            createTable(conn, sql)
        
    except Error as e:
        print("Erro em createConnection: {}".format(e))
    # finally:
    #     if conn:
    #         conn.close()
    return conn

def createTable(conn, sql):
    '''Create table in Sqlite database file
    :param conn: Connection oject
    :param sql: DDL sql command
    '''
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print("Erro em createTable: {}".format(e))

def insertData(gpsData):
    '''Insert data from gps to a Sqlite database file
    :param conn: Connection object
    :param gpsData: Json data from GPS
    '''
    try:

        # Verifica se existe diferença de 1km entre locais
        ultima = retrievLastLocation()
        atual = {gpsData['latitude'], gpsData['longitude']}
        distancia = haversine(ultima, atual)
        if distancia <= 1:
            return
        
        conn = createConnection('location.db')
        sql='''INSERT INTO LOCATION(LATITUDE,LONGITUDE,ALTITUDE,SPEED,DATA)
            VALUES(?,?,?,?,?)'''
        loc=(gpsData['latitude'],gpsData['longitude'],gpsData['altitude'],gpsData['speed'],datetime.now())
        cur=conn.cursor()
        cur.execute(sql,loc)
        conn.commit()
        logging.warning(f"{datetime.now()} Inserção de dados finalizada")

    except Error as e:
        print("Erro em insertData {}".format(e))


@app.route('/retrievData', methods=['GET'])
def retrievData():
    '''Retriev data from Sqlite database file
    '''

    data = datetime.now()
    try:
        sql=f'''SELECT * FROM LOCATION WHERE DATA >= {data.strftime('%d-%m-%Y')} ORDER BY DATA'''
        conn=createConnection('location.db')
        cur=conn.cursor()
        cur.execute(sql)
        result=cur.fetchall()
        conn.close()

        # r=[row[i] for row in result for i in [0,1]]

        latitude=''
        longitude=''
        trajeto = []        
        for res in result:
            latitude=res[0]
            longitude=res[1]
            trajeto.append([latitude,longitude])
        
        i = 0
        trajetoaux = copy.deepcopy(trajeto)        
        while i < len(trajeto) - 1:
            dist = haversine(trajeto[i],trajeto[i+1])
            if dist > 1:
                trajetoaux[i+1].append(dist)
            i+=1

        return render_template('gps.html', data=trajetoaux)

        
    except Error as e:
        print("Erro em retrievData {}".format(e))

def haversine(coord1, coord2):
    
    # Earth radius in meters
    R = 6372800  
    #R = 6371

    la1, lo1 = coord1
    la2, lo2 = coord2

    lat1 = float(la1)
    lon1 = float(lo1)
    lat2 = float(la2)
    lon2 = float(lo2)

    logging.warning(f'haversine lat1 {lat1}')
    logging.warning(f'haversine lon1 {lon1}')
    logging.warning(f'haversine lat2 {lat2}')
    logging.warning(f'haversine lon2 {lon2}')
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    res = 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    res = res / 1000
    logging.warning(f"{datetime.now()} Distância em km: {res * 1.609}")
    return res * 1.609

def retrievLastLocation():
    '''Retriev last location from database
    '''
    try:
        sql = f'''SELECT * FROM LOCATION ORDER BY DATA DESC LIMIT 1 '''
        conn = createConnection('location.db')
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()

        latitude=''
        longitude=''
        ultimo = []
        for res in result:
            latitude=res[0]
            longitude=res[1]
            ultimo = {latitude, longitude}
        return ultimo
    except Error as e:
        print (f'Erro em retrievLastLocation: {e}')

if __name__ =='__main__':
    app.run(debug=True)
