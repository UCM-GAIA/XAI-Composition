Instrucciones para utilizar API Flask Restful

•	Para lanzar el script en el servidor:

1.	Crear un virtual environment para poder instalar las librerías requeridas sin que se produzcan conflictos. Se puede crear con:
	```
	python -m venv <ruta deseada>
	```
2.	Desde el virtualenv, instalar las dependencias que vienen en el fichero “requirements.txt”con pip. Ejemplo:
	```
	python pip -r /Flask_apirest/requirements.txt
	```
3.	(Para versión con Autenticación) Antes de poder ejecutar el script, hay que iniciar el servicio “mysql”. Se puede descargar e instalar la versión lightweight de MySQLServer si no se tiene. Para que el programa pueda acceder a la base de datos, hay que definir primero las credenciales de administrador. Una vez iniciado MySQL, se puede hacer:
	```
	ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';
	```
Con esto le asignamos la contraseña “password” al usuario “root”, que viene por defecto. Por último, hace falta crear una nueva base de datos llamada “jwt_auth” que será la utilizada para almacenar los usuarios y el hash de la contraseña. Para esto se puede hacer:
	```
	CREATE DATABASE jwt_auth;
	```
IMPORTANTE: Para que poder acceder a la base de datos, se especifica en el script “flask_apirest.py” en la línea 27:
	```
	app.config['SQLALCHEMY_DATABASE_URI'] = 	'mysql://root:password@localhost/jwt_auth'
	```
Se recomienda cambiar las credenciales de MySQL para mayor seguridad, pero también hace falta cambiarlas en esta línea de código respectivamente.

4.	Ahora si se puede ejecutar el script con:
	```
	python flask_apirest.py
	```

Nota: Por defecto, se usa la dirección IP de localhost en el puerto 5444, pero esto se puede cambiar en la última línea del script, por ejemplo, habilitando todas las direcciones con:
	```
	app.run(host='0.0.0.0', port=63630)
	```
•	Uso desde el cliente sin interfaz gráfica:

1.	(Para versión con Autenticación) Antes de poder utilizar los métodos, es necesario obtener primero un token de autenticación, ya se a través de la función de register o de login, si ya hemos creado un usuario anteriormente. Se puede hacer utilizando curl de la siguiente manera, por ejemplo:
	```
	curl -H "Content-Type: application/json" -d @login.json 	http://localhost:5444/login
	```
Se usa el fichero “login.json” que contiene las credenciales (username y password) en un diccionario 	JSON 	por facilidad, pero también se puede proporcionar directamente el objeto JSON sustituyendo “@login.json” por el diccionario con las credenciales. Si las credenciales son correctas, debería aparecer un mensaje de esta forma:
```
{"message": "Logged in as <username>", 
"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYzMjkyOTQ1OCwianRpIjoiZjliYzNhNzUtMDUzYy00YjMxLTg3OTAtZTJjNTNmNWJhZjgzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ikplc3VzIiwibmJmIjoxNjMyOTI5NDU4LCJleHAiOjE2MzI5MzAzNTh9.Fpl7ynTZ0keL09GWWfdWd2v44zCxpjmA1h6KZHPXjGo"}
```
El valor de access_token es un JWT que debemos utilizar para hacer las llamadas, por lo que es conveniente guardarlo en una variable. En Windows se puede hacer con:
	```
	set TOKEN="token.example.xyz"
	```
	
Nota: los JWTs expiran cada cierto tiempo, por lo que es necesario volver a hacer login para obtener un nuevo token.

2.	Para hacer llamadas a los métodos, hay acceder a la dirección y puerto del servidor y especificar para cada parámetro la ruta del archivo correspondiente. Para esto se puede utilizar la herramienta curl. Para ver los parámetros en detalle, consultar “apirest_specification”.  Además, hay que pasar el Token a la llamada (Ignorar sin Autenticación). Con “%TOKEN%” se vuelca el valor de la variable definida en el paso anterior. En Bash, se utlizaría “$TOKEN” en su lugar. Un ejemplo de llamada: 
```
curl -F "params=<sklearn/depr_public_params.json" -F "model=@ sklearn/depr_mlp_model.pkl" -F "data=@sklearn/depr_data.pkl" -H "Authorization: Bearer %TOKEN%" http://localhost:5444/DicePublic
```

