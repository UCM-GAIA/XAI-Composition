FROM ubuntu
RUN apt-get update && apt-get install -y python3.8
RUN apt-get install -y python3-pip
RUN apt-get install -y default-libmysqlclient-dev
RUN apt-get install -y mysql-server
COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt
RUN pip3 install numpy==1.19.5
RUN pip3 install pandas==1.2.4
RUN pip3 install joblib==0.16.0
RUN pip3 install dice_ml==0.7.1
RUN pip3 install mysqlclient==2.0.3
RUN pip3 install json5==0.9.5
RUN pip3 install jsonpickle==2.0.0
RUN pip3 install jsonschema==3.2.0
RUN pip3 install Werkzeug==2.0
RUN pip3 install h5py==3.1.0
RUN pip3 install flask==2.0.1
RUN pip3 install flask-jwt-extended==4.3.1
RUN pip3 install Flask-SQLAlchemy==2.5.1
RUN pip3 install flask-restful==0.3.9
RUN pip3 install passlib==1.7.4
RUN pip3 install lime==0.2.0.1
RUN pip3 install shap==0.40.0
RUN pip3 install alibi==0.6.1
RUN pip3 install dalex==1.4.1
RUN pip3 install passlib==1.7.4
RUN pip3 install tensorflow==2.6.2
RUN pip3 install torch==1.9.0
COPY . .
CMD ["python3.8","app.py"]
