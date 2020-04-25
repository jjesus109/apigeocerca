#!/bin/bash
cd Codigo
export GOOGLE_APPLICATION_CREDENTIALS="./../Recursos/firecargamos-firebase-adminsdk-uwn8s-9eb9c1f934.json"
gunicorn --workers 1 --worker-class gevent --timeout 21 -b 0.0.0.0:8080 app:app
