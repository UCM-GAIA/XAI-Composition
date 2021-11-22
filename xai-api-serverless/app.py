import tensorflow as tf
import torch
import numpy as np
import pandas as pd
import joblib
import dice_ml
import json
import sys
import werkzeug
import h5py
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask import Flask, jsonify, request, g, url_for, abort, make_response
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy

import lime.lime_tabular
import shap
from alibi.explainers import AnchorTabular
from alibi.explainers.ale import ALE
import dalex as dx

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__)
parser = reqparse.RequestParser()

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/jwt_auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = ';vM$9A[N'

jwt = JWTManager(app)
api = Api(app)
db = SQLAlchemy(app)

from passlib.hash import pbkdf2_sha256 as sha256



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
        
        return json.loads(e1.to_json())

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

class Lime(Resource):
    #decorators=[jwt_required()]
    def post(self):
        
        parser.add_argument("model", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument("data", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('params')
        args = parser.parse_args()
        
        data = args.get("data")
        dataframe = joblib.load(data)
        params_json = json.loads(args.get("params"))
        instance=params_json["instance"]

        backend = params_json["backend"]
       
        model = args.get("model")
        
        if backend=="TF1" or backend=="TF2":
            model=h5py.File(model, 'w')
            mlp = tf.keras.models.load_model(model)
            predic_func=mlp.predict
            mlp = tf.keras.models.load_model(model)
        elif backend=="sklearn":
            mlp = joblib.load(model)
            predic_func =mlp.predict_proba
        else:
            mlp = torch.load(model)
            predic_func=mlp.predict
      
        kwargsData = dict(training_labels=None, feature_names=None, categorical_features=None,  class_names=None)

        if "training_labels" in params_json:
            kwargsData["training_labels"] = params_json["training_labels"]
        if "feature_names" in params_json:
            kwargsData["feature_names"] = params_json["feature_names"]
        if "categorical_features" in params_json:
            kwargsData["categorical_features"] = params_json["categorical_features"]
        if "class_names" in params_json:
            kwargsData["class_names"] = params_json["class_names"]

        # Create data
        explainer = lime.lime_tabular.LimeTabularExplainer(dataframe.drop(dataframe.columns[len(dataframe.columns)-1], axis=1, inplace=False).to_numpy(),
                                                            **{k: v for k, v in kwargsData.items() if v is not None})

        kwargsData2 = dict(labels=(1,), top_labels=None, num_features=None)

        if "output_classes" in params_json:
            kwargsData2["labels"] = params_json["output_classes"]  #labels
        if "top_classes" in params_json:
            kwargsData2["top_labels"] = params_json["top_classes"]   #top labels
        if "num_features" in params_json:
            kwargsData2["num_features"] = params_json["num_features"]

        explanation = explainer.explain_instance(np.array(instance, dtype='f'), predic_func, **{k: v for k, v in kwargsData2.items() if v is not None}) 
        
        ret = explanation.as_map()

        
     
        ret = {str(k):[(int(i),float(j)) for (i,j) in v] for k,v in ret.items()}

        if kwargsData["class_names"]!=None:
            ret = {kwargsData["class_names"][int(k)]:v for k,v in ret.items()}
        if kwargsData["feature_names"]!=None:
            ret = {k:[(kwargsData["feature_names"][i],j) for (i,j) in v] for k,v in ret.items()}
        return json.loads(json.dumps(ret)) ## intentar convertir a json

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
    


api.add_resource(Lime, '/LIME')

class Shap(Resource):
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

        backend = params_json["backend"]
       
        model = args.get("model")
        
        if backend=="TF1" or backend=="TF2":
            model=h5py.File(model, 'w')
            mlp = tf.keras.models.load_model(model)
            predic_func=mlp.predict
            mlp = tf.keras.models.load_model(model)
        elif backend=="sklearn":
            mlp = joblib.load(model)
            predic_func =mlp.predict_proba
        else:
            mlp = torch.load(model)
            predic_func=mlp.predict
      
        kwargsData = dict(feature_names=None, output_names=None)

        if "feature_names" in params_json:
            kwargsData["feature_names"] = params_json["feature_names"]
        if "output_names" in params_json:
            kwargsData["output_names"] = params_json["output_names"]

        # Create data
        explainer = shap.KernelExplainer(predic_func, dataframe.drop(dataframe.columns[len(dataframe.columns)-1], axis=1, inplace=False),**{k: v for k, v in kwargsData.items()})

        shap_values = explainer.shap_values(np.array(instances))

        shap_values = [x.tolist() for x in shap_values]
        
        return json.loads(json.dumps(shap_values))


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
    


api.add_resource(Shap, '/SHAP')

class Anchor(Resource):
    #decorators=[jwt_required()]
    def post(self):
        
        parser.add_argument("model", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument("data", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('params')
        args = parser.parse_args()
        
        data = args.get("data")
        dataframe = joblib.load(data)
        params_json = json.loads(args.get("params"))
        instance=params_json["instance"]

        backend = params_json["backend"]
        feature_names = params_json["feature_names"]
       
        model = args.get("model")
        
        if backend=="TF1" or backend=="TF2":
            model=h5py.File(model, 'w')
            mlp = tf.keras.models.load_model(model)
            predic_func=mlp.predict
         
        elif backend=="sklearn":
            mlp = joblib.load(model)
            predic_func =mlp.predict_proba
        else:
            mlp = torch.load(model)
            predic_func=mlp.predict
      
        kwargsData = dict(categorical_names=None, ohe=False)
        kwargsData2 = dict(threshold=0.95)
            
        if "categorical_names" in params_json:
            cat_names = params_json["categorical_names"]
            kwargsData["categorical_names"] = {int(k):v for k,v in cat_names.items()}

        if "ohe" in params_json:
            kwargsData["ohe"] = params_json["ohe"]
        if "threshold" in params_json:
            kwargsData2["threshold"] = params_json["threshold"]

        # Create data
        explainer = AnchorTabular(predic_func, feature_names,**{k: v for k, v in kwargsData.items()})

        explainer.fit(dataframe.drop(dataframe.columns[len(dataframe.columns)-1], axis=1, inplace=False).to_numpy(), disc_perc=(25, 50, 75))
        
        explanation = explainer.explain(np.array(instance), **{k: v for k, v in kwargsData2.items()})
        
        ret = dict(anchor=(' AND '.join(explanation.anchor)),precision=explanation.precision, coverage=explanation.coverage)
        return json.loads(json.dumps(ret))


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
    


api.add_resource(Anchor, '/Anchors')

class Ale(Resource):
    #decorators=[jwt_required()]
    def post(self):
        
        parser.add_argument("model", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument("data", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('params')
        args = parser.parse_args()
        
        data = args.get("data")
        dataframe = joblib.load(data)
        params_json = json.loads(args.get("params"))
       

        backend = params_json["backend"]
        
       
        model = args.get("model")
        
        if backend=="TF1" or backend=="TF2":
            model=h5py.File(model, 'w')
            mlp = tf.keras.models.load_model(model)
            predic_func=mlp.predict
         
        elif backend=="sklearn":
            mlp = joblib.load(model)
            predic_func =mlp.predict_proba
        else:
            mlp = torch.load(model)
            predic_func=mlp.predict
      
        kwargsData = dict(feature_names = None, target_names=None)
        kwargsData2 = dict(features=None)
            
        if "feature_names" in params_json:
            kwargsData["feature_names"] = params_json["feature_names"]
        if "target_names" in params_json:
            kwargsData["target_names"] = params_json["target_names"]
        if "features_to_show" in params_json:
            kwargsData2["features"] = params_json["features_to_show"]


        proba_ale_lr = ALE(predic_func, **{k: v for k, v in kwargsData.items()})
        proba_exp_lr = proba_ale_lr.explain(dataframe.drop(dataframe.columns[len(dataframe.columns)-1], axis=1, inplace=False).to_numpy(),**{k: v for k, v in kwargsData2.items()})
        
        return json.loads(proba_exp_lr.to_json())


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
    


api.add_resource(Ale, '/ALE')


class Importance(Resource):
    #decorators=[jwt_required()]
    def post(self):
        
        parser.add_argument("model", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument("data", type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('params')
        args = parser.parse_args()
        
        data = args.get("data")
        dataframe = joblib.load(data)
        params_json = json.loads(args.get("params"))
       

        backend = params_json["backend"]
        
       
        model = args.get("model")
        
        if backend=="TF1" or backend=="TF2":
            model=h5py.File(model, 'w')
            mlp = tf.keras.models.load_model(model)
          
         
        elif backend=="sklearn":
            mlp = joblib.load(model)
         
        else:
            mlp = torch.load(model)
          
      
        kwargsData = dict(feature_names = None, target_names=None)
            
        if "variables" in params_json:
            kwargsData["variables"] = params_json["variables"]

        

        explainer = dx.Explainer(mlp, dataframe.drop(dataframe.columns[len(dataframe.columns)-1], axis=1, inplace=False), dataframe.iloc[:,-1:],model_type="classification")
        parts = explainer.model_parts(**{k: v for k, v in kwargsData.items()})
        
        print(dataframe.iloc[:,-1:])
        return json.loads(parts.result.to_json())#drop(parts.result.columns[len(parts.result.columns)-1], axis=1, inplace=False).to_json()


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
    


api.add_resource(Importance, '/importance')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)