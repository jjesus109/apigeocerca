from flask import Flask, jsonify, abort
from flask import request, make_response
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from fastkml import kml
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

#export GOOGLE_APPLICATION_CREDENTIALS="./../Recursos/firecargamos-firebase-adminsdk-uwn8s-9eb9c1f934.json"
#cred = credentials.Certificate("./../Recursos/firecargamos-firebase-adminsdk-uwn8s-9eb9c1f934.json")
#firebase_admin.initialize_app(cred,{
#    'databaseURL': 'https://firecargamos.firebaseio.com/'
#}
# Init database
firebase_admin.initialize_app()
# establish connection to parent
geocercas = db.reference(path="geocerca",url='https://firecargamos.firebaseio.com/')
# Create kml object 
k = kml.KML()

app = Flask(__name__)

from pykml import parser
@app.route('/api/v1/geocerca', methods=['POST'])
def set_geocerca():
    # Obtain recevied data
    try:
        kml = request.files
    except:
        response = {"errorMessage":"No se pudo leer el archivo"}
        return make_response(jsonify(response),400)   
        
    kml = kml["archivokml"]
    datakml  =kml.read()

    k.from_string(datakml)
    #print(k.to_string(prettyprint=True))
    # features of primary tree
    features = list(k.features())
    # features of secondary tree
    featureofF = list(features[0].features())
    alias = featureofF[0].name 
    nombres  = geocercas.get()
    """
    if alias in nombres:
        print("Ya esta en la database nombre de area")
        response = {"errorMessage":
                    "Nombre de area ya se encuentra en la base de datos"}
        return make_response(jsonify(response),400)   
    """
    print(f"alias : {alias}")
    print(f"alias : {type(alias)}")

    # sobtain data from Polygon
    tree = featureofF[0].geometry
    # Convert into str 
    dataPolygon = tree.wkt
    # formatted data 
    # TODO definir nombr de geometria para tomar datos
    # de esa figura y filtrarlo en el string
    dataPolygon = dataPolygon[9:-2]
    # Separate str int list
    coordinates = dataPolygon.split(', ') 
    # split each element of lists 
    # in lat and long attributes
    newCoordinates = []
    for co in coordinates:
        # Avoid altitude 
        coordinate= co[:-4].split(' ') 
        newCoordinates.append(coordinate)
    print(f"coor {newCoordinates}")

    # push data in db
    for coordinate in newCoordinates:
        puntos ={"lng":coordinate[0],
                 "lat":coordinate[1]}
        geocercas.child(alias).push(puntos) 
    puntos = db.reference(path="geocerca/"+alias,
        url='https://firecargamos.firebaseio.com/')
    print(f"puntos {puntos.get()}")
    print(f"geocercas {geocercas.get()}")

    return make_response(jsonify({"ALL":"GOOD"}),201)

@app.route('/api/v1/deteccion', methods=['GET'])
def get_deteccion():
    data = request.json
    lt = data["lat"]
    lg = data["lng"]
    nombres  = geocercas.get()
    print(f"Nombres : {nombres}")
    print(f"Nombres TYPE: {type(nombres)}")

    aliasGeocercas = list(nombres.keys())
    print(f"aliasGeocercas : {aliasGeocercas}")
    results = []
    # Obtain data from each geocerca
    for ngeo in aliasGeocercas:
        coordenadas = nombres[ngeo]
        idcoordenadas = list(coordenadas.keys())
        puntosArea = []
        lngs = []
        lats = []
        # obtain points from area
        for puntos in idcoordenadas:
            punto = coordenadas[puntos]
            x_y = [punto["lng"],punto["lat"]]
            lngs.append(punto["lng"])
            lats.append(punto["lat"])
            puntosArea.append(x_y)
        lats = np.asarray(lats)
        lngs = np.asarray(lngs)
        print(f"Puntos de {ngeo}")
        print(puntosArea)
        # evaluate pints on shapely
        lons_lats_vect = np.column_stack((lngs, lats)) # Reshape coordinates
        polygon = Polygon(lons_lats_vect) # create polygon

        point = Point(lt,lg) # create point
        contains = polygon.contains(point)
        print(f"polygon contains: {contains}") 
        if contains:
            results.append()
        print("********************")
    # Get data from dicts in list
    return make_response(jsonify({"results":results}),200)
    

if __name__ == '__main__':
    app.run(debug=True)