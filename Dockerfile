FROM python:3.6-slim
WORKDIR api
RUN pip install firebase_admin flask fastkml numpy shapely gunicorn  && pip install gunicorn[gevent]
COPY ./Recursos ./Recursos
COPY ./Codigo ./Codigo
COPY exe.sh .
CMD ["sh","exe.sh"]
