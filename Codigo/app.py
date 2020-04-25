from flask import Flask, jsonify
from flask import request, make_response
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from fastkml import kml
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
"""
print(f"geocercas {geon.get()}")


puntos = db.reference(path="geocerca/Area5",url='https://firecargamos.firebaseio.com/')
lat=9
lng=45

for i in range(2):
    lat += 7
    lng += 14
    puntos.push({
        "lat":lat,
        "lng":lng
        })

n = puntos.get()

print(f"puntos {n}")
print(f"geocercas ahora{geocercas.get()}")
"""
app = Flask(__name__)


@app.route('/api/v1/geocerca', methods=['POST'])
def set_geocerca():
    #alias = request.json["alias"]
    alias = ""
    kml = request.files
    kml = kml["archivokml"]
    datakml  =kml.read()

    k.from_string(datakml)
    print(k.to_string(prettyprint=True))
    features = list(k.features())
    featureofF = list(features[0].features())
    alias = featureofF[0].name
    data = featureofF[0].features()

    print(f"Alias: {featureofF[0]}")
    print(f"Cooridnate: {alias}")

    """
    # push data in db
    geon = geocercas.child(alias).push({"lat":100,
                                      "lng":900}) 
    lat=32
    lng=23
    for i in range(2):
        lat +=11
        lng += 22
        puntos ={"lat":lat,
                 "lng":lng}
        geocercas.child(alias).push(puntos) 
    puntos = db.reference(path="geocerca/"+alias,
        url='https://firecargamos.firebaseio.com/')
    print(f"puntos {puntos.get()}")
    print(f"geocercas {geocercas.get()}")
    """
    return make_response(jsonify({"ALL":"GOOD"}),201)

@app.route('/api/v1/deteccion', methods=['POST'])
def get_deteccion():
    return jsonify({'tasks': "No"})

if __name__ == '__main__':
    app.run(debug=True)