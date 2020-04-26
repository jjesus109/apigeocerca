import os
import json
import logging
from io import StringIO
from io import BytesIO

import unittest

from app import app
 
 
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, 
    level=logging.INFO, 
    datefmt="[%Y-%m-%d %H:%M:%S]")


class TestCase(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        

    def tearDown(self):
        pass
    
    def deteccion(self,lat,lng):
        data = {
                'lat': lat,
                'lng': lng
        }
        print(f"data send {data}")
        return self.app.post(
            '/api/v1/deteccion',
            data=json.dumps(data),
            content_type='application/json'
            )
    def enviar_archivo(self):
        with open("./../Recursos/Coyoacan.kml",'rb') as archivo:
            kmlfile = archivo

        return self.app.post(
            '/api/v1/geocerca',
            data={"file":(BytesIO(bytes(kmlfile)))},
            content_type='multipart/form-data'
            )
    def pretest_insertar_geocerca(self):
        
        lat = 19.35775
        lng = -99.146383 
        # Verify geofence in db before push new data
        logging.info("INFO: Lista de Geocercas antes de insertar datos")
        self.app.get('/api/v1/geocerca')
        response = self.enviar_archivo()
        logging.info("INFO: Lista de Geocercas despues de insertar datos")
        self.app.get('/api/v1/geocerca')
        # Verify geofence in db after push new data
        self.assertEqual(response.status_code, 200)
    
    def test_dentro_geocerca(self):
        
        lat = 19.350205
        lng = -99.158217 
        response = self.deteccion(lat,lng)
        self.assertEqual(response.status_code, 200)
    def test_fuera_geocerca(self):
        
        lat = 19.35775
        lng = -99.146383 
        response = self.deteccion(lat,lng)
        self.assertEqual(response.status_code, 200)
    
 
if __name__ == "__main__":
    unittest.main()