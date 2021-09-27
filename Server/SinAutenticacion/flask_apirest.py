import tensorflow as tf
import torch
import numpy as np
import pandas as pd
import joblib
import dice_ml
import json
#import sys
import werkzeug
import h5py
#from flask_jwt_extended import JWTManager
#from flask_jwt_extended import (
#    create_access_token,
#    jwt_required,
#    get_jwt_identity
#)
from flask import Flask, jsonify, request, g, url_for, abort, make_response
from flask_restful import reqparse, abort, Api, Resource
#from flask_sqlalchemy import SQLAlchemy


#cli = sys.modules['flask.cli']
#cli.show_server_banner = lambda *x: None
app = Flask(__name__)
parser = reqparse.RequestParser()

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/jwt_auth'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = ';vM$9A[N'

#jwt = JWTManager(app)
api = Api(app)
#db = SQLAlchemy(app)

#from passlib.hash import pbkdf2_sha256 as sha256


"""class UserModel(db.Model):
    \"""
    User Model Class
    \"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(120), nullable=False)

    \"""
    Save user details in Database
    \"""
    def save_to_db(self):

        db.session.add(self)

        db.session.commit()

    \"""
    Find user by username
    \"""
    @classmethod
    def find_by_username(cls, username):

        return cls.query.filter_by(username=username).first()

    \"""
    return all the user data in json form available in DB
    \"""
    @classmethod
    def return_all(cls):

        def to_json(x):

            return {

                'username': x.username,

                'password': x.password

            }

        return {'users': [to_json(user) for user in UserModel.query.all()]}

    \"""
    Delete user data
    \"""
    @classmethod
    def delete_all(cls):

        try:

            num_rows_deleted = db.session.query(cls).delete()

            db.session.commit()

            return {'message': f'{num_rows_deleted} row(s) deleted'}

        except:

            return {'message': 'Something went wrong'}

    \"""
    generate hash from password by encryption using sha256
    \"""
    @staticmethod
    def generate_hash(password):

        return sha256.hash(password)

    \"""
    Verify hash and password
    \"""
    @staticmethod
    def verify_hash(password, hash_):

        return sha256.verify(password, hash_)


@app.before_first_request
def create_tables():

    db.create_all()

class UserRegistration(Resource):
    def post(self):
        
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        # Checking that user is already exist or not
        if UserModel.find_by_username(username):
            return {'message': f'User {username} already exists'}
        # create new user
        new_user = UserModel(
            username=username,
            password=UserModel.generate_hash(password)
        )

        try:
            
            new_user.save_to_db()
            access_token = create_access_token(identity=username)
           
            return {

                'message': f'User {username} was created',

                'access_token': access_token

            }
        except Exception as e:
            return {'message': str(e)}, 500

    def get(self):

        return {
        "_method_description": "Allows registration of an user and authentication through Json Web Tokens. Requires a JSON containing two string fields, the username and password.",

        "_params_example": {
                            "username": "test_user",
                            "password": "test_password"
                            }

        }

api.add_resource(UserRegistration, '/register')

class UserLogin(Resource):
    def post(self):
       
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        # Searching user by username
        current_user = UserModel.find_by_username(username)
        # user does not exists
        if not current_user:
            return {'message': f'User {username} doesn\'t exist'}
        # user exists, comparing password and hash
        if UserModel.verify_hash(password, current_user.password):
            # generating access token 
            access_token = create_access_token(identity=username)
            return {

                'message': f'Logged in as {username}',

                'access_token': access_token

            }

        else:
            return {'message': "Wrong credentials"}

    def get(self):

        return {
        "_method_description": "Allows an user to login and access the API methods. Requires a JSON containing two string fields, the username and password of the user.",

        "_params_example": {
                            "username": "test_user",
                            "password": "test_password"
                            }

        }

api.add_resource(UserLogin, '/login')"""

#class Predict(Resource):
 #   decorators=[jwt_required()]
  #  def post(self):
        
   #     parser.add_argument("model", type=werkzeug.datastructures.FileStorage, location='files')
    #    parser.add_argument('params')
     #   args = parser.parse_args()
      #  model = args.get("model")
       # params_json = json.loads(args.get("params"))
        #instances=params_json["instances"]
        
        #mlp = joblib.load(model)

        #result =[]

        #for instance in instances:
         #   dict1 = {"predicted_class": int(mlp.predict([instance])[0]),
		  #  "probabilities":list(mlp.predict_proba([instance])[0])}
           # result.append(dict1)

        # return result

# api.add_resource(Predict, '/predict')


class DicePublic(Resource):
    #decorators=[jwt_required()]
    def post(self):
        
        parser.add_argument("model", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument("data", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('params')
        args = parser.parse_args()
        
        data = args.get("data")
        dataframe = joblib.load(data)
        params_json = json.loads(args.get("params"))
        instances=params_json["instances"]
        cont_features = params_json["cont_features"]
        backend = params_json["backend"]
        num_cfs = params_json["num_cfs"]
        desired_class = params_json["desired_class"]
        method = params_json["method"]
        features_to_vary = params_json["features_to_vary"]

        model = args.get("model")
        
        if backend=="TF1" or backend=="TF2":
            model=h5py.File(model, 'w')
            mlp = tf.keras.models.load_model(model)
        elif backend=="sklearn":
            mlp = joblib.load(model)
        else:
            mlp = torch.load(model)
      
        kwargsData = dict(continuous_features=cont_features, outcome_name=dataframe.columns[-1], permitted_range=None, continuous_features_precision=None, data_name=None)

        if "permitted_range" in params_json:
            kwargsData["permitted_range"] = params_json["permitted_range"]
        if "continuous_features_precision" in params_json:
            kwargsData["continuous_features_precision"] = params_json["continuous_features_precision"]
        if "data_name" in params_json:
            kwargsData["data_name"] = params_json["data_name"]

        # Create data
        d = dice_ml.Data(dataframe=dataframe, **{k: v for k, v in kwargsData.items() if v is not None})
  
        # Create model
        m = dice_ml.Model(model=mlp, backend=backend)

        # Create CFs generator using random
        exp = dice_ml.Dice(d, m, method=method)

        columns = list(dataframe.columns)
        columns.remove(dataframe.columns[-1])

        instances = pd.DataFrame(instances, columns=columns)
       
        # Generate counterfactuals
        if backend=="sklearn":
            e1 = exp.generate_counterfactuals(query_instances=instances, total_CFs=num_cfs, desired_class=desired_class, features_to_vary=features_to_vary)
        else:
            e1 = exp.generate_counterfactuals(instances, total_CFs=num_cfs, desired_class=desired_class, features_to_vary=features_to_vary)
        
        return e1.to_json() 

    def get(self):
        return {
        "_method_description": "Generates counterfactuals using the training data as a baseline. Requires 3 arguments: " 
                           "the 'params' string, the 'model' which is a file containing the trained model, and " 
                           "the 'data', containing the training data used for the model. These arguments are described below.",

        "params": { "_description": "STRING representing a JSON object containing the following fields:",
                "instances": "Array of arrays, where each one represents a row with the feature values of an instance including the target class.",
                "backend": "A string containing the backend of the prediction model. The supported values are: 'sklearn' (Scikit-learn), 'TF1' "
                "(TensorFlow 1.0), 'TF2' (TensorFlow 2.0), 'PYT' (PyTorch).",
                "method": "The method used for counterfactual generation. The supported methods are: 'random' (random sampling), 'genetic' (genetic algorithms), 'kdtrees'.",
                "cont_features": "Array of strings containing the name of the continuous features. Features not included here are considered categorical.",
                "features_to_vary": "Either a string 'all' or a list of strings representing the feature names to vary.",
                "desired_class": "Integer representing the index of the desired counterfactual class, or 'opposite' in the case of binary classification.",
                "num_cfs": "number of counterfactuals to be generated for each instance.",
                "permitted_range": "(optional) JSON object with feature names as keys and permitted range in array as values.",
                "continuous_features_precision": "(optional) JSON object with feature names as keys and precisions as values.",
                "data_name": "(optional) name of the dataset."
                },

        "params_example":{
                "backend": "sklearn",
                "cont_features": ["Height", "Weight"],
                "continuous_features_precision": {"Height": 1, "Weight":3},
                "data_name": "datasetName",
                "desired_class": 0,
                "features_to_vary": "all",
                "instances": [ ["X1", "X2", "Xn"], ["Y1", "Y2", "Yn"]],
                "method": "random",
                "num_cfs": 3,
                "permitted_range": {"Height": [ 0, 250]}
               },

        "model": "The trained prediction model given as a file. The extension must match the backend being used i.e.  a .pkl " 
             "file for Scikit-learn (use Joblib library), .pt for PyTorch or .h5 for TensorFlow models.",

        "data": "Pandas DataFrame containing the training data given as a .pkl file (use Joblib library). The target class must be the last column of the DataFrame"
        }
    


api.add_resource(DicePublic, '/DicePublic')

class DicePrivate(Resource):
    #decorators=[jwt_required()]
    def post(self):
        
        parser.add_argument("model", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('params')
        args = parser.parse_args()
        params_json = json.loads(args.get("params"))
        instance=params_json["instance"]
        features = params_json["features"]
        backend = params_json["backend"]
        num_cfs = params_json["num_cfs"]
        desired_class = params_json["desired_class"]
        method = params_json["method"]
        outcome_name = params_json["outcome_name"]
        features_to_vary = params_json["features_to_vary"]
        model = args.get("model")
      
        if backend=="TF1" or backend=="TF2":
            model =h5py.File(model, 'w')
            mlp = tf.keras.models.load_model(model)
        elif backend=="sklearn":
            mlp = joblib.load(model)
        else:
            mlp = torch.load(model)

        kwargsData = dict(features=features, outcome_name=outcome_name, type_and_precision=None, mad=None, data_name=None)

        if "type_and_precision" in params_json:
            kwargsData["type_and_precision"] = params_json["type_and_precision"]
        if "mad" in params_json:
            kwargsData["mad"] = params_json["mad"]
        if "data_name" in params_json:
            kwargsData["data_name"] = params_json["data_name"]

        # Create data
        d = dice_ml.Data(**{k: v for k, v in kwargsData.items() if v is not None})
  
        # Create model
        m = dice_ml.Model(model=mlp, backend=backend)

        # Create CFs generator using random
        exp = dice_ml.Dice(d, m, method=method)
        
     
       
        # Generate counterfactuals
        e1 = exp.generate_counterfactuals(instance, total_CFs=num_cfs, desired_class=desired_class, features_to_vary=features_to_vary)
        
        return json.loads(e1.cf_examples_list[0].final_cfs_df.to_json(orient='records'))

    def get(self):
        return {
        "_method_description": "Generates counterfactuals without the training data. However, it requires the format and ranges of the data. Requires 2 arguments: " 
                           "the 'params' string, and the 'model' which is a file containing the trained model.",

        "params": { "_description": "STRING representing a JSON object containing the following fields:",
                "instance": "JSON object representing the instance of interest with attribute names as keys, and feature values as values.",
                "backend": "A string containing the backend of the prediction model. Currently, the only supported backend for private data is 'TF2' (TensorFlow 2.0).",
                "method": "The method used for counterfactual generation. The supported methods for private data are: 'random' (random sampling) and 'genetic' (genetic algorithms).",
                "features": "JSON Object with feature names as keys and arrays containing the ranges of continuous features, or strings with the categories for categorical features.",
                "features_to_vary": "Either a string 'all' or a list of strings representing the feature names to vary.",
                "desired_class": "Integer representing the index of the desired counterfactual class, or 'opposite' in the case of binary classification.",
                "num_cfs": "number of counterfactuals to be generated for each instance.",
                "outcome_name": "name of the target column.",
                "type_and _precision": "(optional) JSON object with continuous feature names as keys. If the feature is of type int, the value should be the string 'int'. If the feature is of type float, an array of two values is expected, containing the string 'float', and the precision.",
                "mad": "(optional) JSON with feature names as keys and corresponding Median Absolute Deviation.",
                "data_name": "(optional) name of the dataset."
                },

        "params_example":{
                "backend": "TF2",
                "data_name": "datasetName",
                "features": {"Gender":["male", "female"], "Height": [ 0, 250], "Weight":[ 0, 250]},
                "features_to_vary": "all",
                "outcome_name": "Target",
                "desired_class": 0,
                "instances": [ ["X1", "X2", "Xn"], ["Y1", "Y2", "Yn"]],
                "method": "random",
                "num_cfs": 3,
                "type_and_precision": {"Height": ["float",1], "Weight": "int"}

               },

        "model": "The trained prediction model given as a file. The extension must match the backend being used i.e.  a .pkl " 
             "file for Scikit-learn (use Joblib library), .pt for PyTorch or .h5 for TensorFlow models. Currently, only TensorFlow models are allowed for DicePrivate"
        }

api.add_resource(DicePrivate, '/DicePrivate')


if __name__ == '__main__':
    app.run(host='localhost', port=5444)