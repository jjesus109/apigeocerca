import logging
import time
import re

import numpy as np
from fastkml import kml
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
from flask import Flask, jsonify, abort
from flask import request, make_response
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, 
    level=logging.INFO, 
    datefmt="[%Y-%m-%d %H:%M:%S]")




cred = credentials.Certificate("./../Recursos/firecargamos-firebase-adminsdk-uwn8s-9eb9c1f934.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://firecargamos.firebaseio.com/'
})
intentos = 1

# establish connection to parent
while True:
    try:
        geocercas = db.reference(path="geocerca",url='https://firecargamos.firebaseio.com/')
        geocercas.get()
        logging.info("INFO: Connected to database succesfully")
        break
    except:
        logging.info("INFO: Could not connect to database")
        logging.info("INFO: Retrying . . .")
        time.sleep(3)
        intentos += 1
    if intentos>3:
        logging.info("INFO: Exiting")
        exit(0)

# Create kml object 
k = kml.KML()

app = Flask(__name__)

@app.route('/api/v1/geocerca', methods=['POST'])
def set_geocerca():
    # Obtain recevied data
    try:
        kml = request.files
    except:
        response = {"errorMessage":"No se pudo leer el archivo"}
        logging.info("INFO: Cannot read file")
        return make_response(jsonify(response),400)   
        
    kml = kml["archivokml"]
    datakml  =kml.read()

    k.from_string(datakml)
    #print(k.to_string(prettyprint=True))
    # features of primary tree
    features = list(k.features())
    # features of secondary tree
    featureofF = list(features[0].features())
    # GObtain name of placemark
    alias = featureofF[0].name 
    # push data in db
    elementpushed = geocercas.push({"alias":alias}) 
    idAlias = elementpushed.key
    # Obtain data from Polygon
    tree = featureofF[0].geometry
    # Convert into str 
    dataPolygon = tree.wkt
    # search for parenthesis for remove from string
    parentesis = re.search(r'[(]',dataPolygon)
    # formatted data 
    dataPolygon = dataPolygon[parentesis.start()+2:-2]
    # Separate str int list
    coordinates = dataPolygon.split(', ') 
    
    # in lat and long attributes
    newCoordinates = []
    for co in coordinates:
        # Avoid altitude the last 4 elements
        coordinate= co.split(' ') 
        newCoordinates.append(coordinate[:-1])
    logging.info(f"INFO: Coordinates pushed: \n{newCoordinates}")

    # push data in db
    for coordinate in newCoordinates:
        puntos ={"lng":coordinate[0],
                 "lat":coordinate[1]}
        try:
            geocercas.child(idAlias).child("puntos").push(puntos) 
        except ValueError as ve:
            logging.info(f"ERROR: {ve}")    
        except FirebaseError as fe:
            logging.info(f"ERROR: {fe}")    

    logging.info("OUTPUT: Coordinates pushed on database")    
    return make_response(jsonify({}),201)

@app.route('/api/v1/deteccion', methods=['POST'])
def get_deteccion():
    # Obtain data from incoming json
    data = request.json
    try:
        lt = data["lat"]
        lg = data["lng"]
    except:
        response = {"errorMessage":"Empty body"}
        return make_response(jsonify(response),400)
    logging.info(f"INPUT: lat: {lt}, lng: {lg}")
    nombres  = geocercas.get()
    idAliasGeocercas = list(nombres.keys())
    results = []
    # Obtain data from each geocerca
    for idAl in idAliasGeocercas:
        # Get json from each document
        datosArea = nombres[idAl]
        # obtain puntos and alias data
        coordenadas = datosArea["puntos"]
        aliasActual = datosArea["alias"]
        # Gt keys for iterate over puntos dict
        idcoordenadas = list(coordenadas.keys())
        puntosArea = []
        lngs = []
        lats = []
        # obtain points from area
        for puntos in idcoordenadas:
            punto = coordenadas[puntos]
            lngs.append(punto["lng"])
            lats.append(punto["lat"])
        # Convert to vector 
        lats = np.asarray(lats)
        lngs = np.asarray(lngs)
        # Convert to 2D matrix rotating vector to columns
        lng_lat = np.column_stack((lngs, lats)) 
        # Creae polygon an point
        polygon = Polygon(lng_lat) 
        point = Point(lg,lt) 
        # Evaluate points on shapely
        contains = polygon.contains(point)
        if contains:
            results.append({
                "id":idAl,
                "alias":aliasActual
                })
    logging.info(f"OUTPUT: {results}")        
    # Get data from dicts in list
    return make_response(jsonify({"results":results}),200)

@app.route('/api/v1/geocerca', methods=['GET'])
def get_geocercas():
    nombres  = geocercas.get()
    idAliasGeocercas = list(nombres.keys())
    logging.info(f"INFO: Lista de Areas en db\n------\n")
    results = []
    for idAl in idAliasGeocercas:
        # Get json from each document
        datosArea = nombres[idAl]
        aliasActual = datosArea["alias"]
        logging.info(f"INFO: ID Alias {idAl}")        
        logging.info(f"INFO: Alias {aliasActual}")
        results.append({
                "id":idAl,
                "alias":aliasActual
                })        
    return make_response(jsonify({"GeocercasDB":results}),200)
if __name__ == '__main__':
    app.run(debug=True)