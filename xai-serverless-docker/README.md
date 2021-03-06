# Docker

Se puede crear una Docker Image para despues lanzar el servidor localmente a partir del fichero `Dockerfile`. Para esto es necesario tener Docker instalado. 

Primero se contruye la imagen, ejecutando este comando desde el directorio donde se encuentren los archivos `requirements.txt`, `app.py` y `Dockerfile`

```bash
docker build -t <nombre del tag> .
```
Con el tag que asignemos nos podemos referir a la imagen una vez que se haya creado. **Nota:** En el fichero `Dockerfile` se instalan todas las librerías de forma individual con pip para poder depurar en caso de producirse un error, pero también se puede hacer un único pip con `requirements.txt`.
Una vez creada la imagen, podemos ejecutar desde el mismo directorio anterior:

```bash
docker run -p 5000:5000 <nombre del tag asignado>
```
Con esto debería lanzarse el servidor en local en un contenedor. Se hace el mapeo del puerto 5000 con la opción -p. Para realizar las llamadas con curl o Postman (ver ejemplos con curl en la carpeta Client de este repo), podemos utilizar la dirección https:localhost:5000.


# Serverless

Ejecutar este comando para instalar serverless en MacOS o Linux:
```bash
curl -o- -L https://slss.io/install | bash
```

Es recomendable crearse una cuenta para poder utilizar el Dashboard de Serverless. Desde aquí es mucho más sencillo crear una nueva aplicación clicando en `create app`. Desde ahí se escoge un nombre para la aplicación y el tipo de framework a utilizar. Para poder lanzar `app.py`, seleccionamos la opción de `python flask API` y ejecutamos los comandos que nos muestran en el directorio que queramos. Todo esto se puede hacer de igual manera desde la CLI con el comando:

```bash
serverless
```
Este comando nos guía a través de la creación de una nueva aplicación. Una vez se haya generado la plantilla, habría que cambiar el fichero `app.py` por el que se encuentra aquí y modificar `serverless.yml` en caso de que queramos utilizar Docker para la instalación de los paquetes. Esto se muestra a continuación.

### Importante

Para lanzar una aplicación con serverless, es necesario definir un proveedor en el archivo `serverless.yml` y asegurarnos de que nuestras credenciales del proveedor están configuradas en nuestra máquina. La configuración del las credenciales va a depender de cada proveedor. De todas formas, si no hemos configurado las credenciales, se nos informará a la hora de desplegar el servicio.

## Serverless Python Requirements

Este plugin se utiliza para empaquetar las dependencias de `requirements.txt`, Para instalarlo, ejecutar:

```shell
sls plugin install -n serverless-python-requirements
```
Este plugin nos permite utilizar docker para la instalación de los módulos de python.
Para activar el uso de Dockers, se añade lo siguiente a `serverless.yml`:

```yaml
custom:
  pythonRequirements:
    dockerizePip: true
```

The dockerizePip option supports a special case in addition to booleans of `'non-linux'` which makes
it dockerize only on non-linux environments.

Se utiliza un Docker por defecto que se basa en el fichero `requirements.txt`, pero se puede utilizar un docker propio modificando `serverless.yml`:

```yaml
custom:
  pythonRequirements:
    dockerImage: <nombre de la imagen>:tag
```

En lugar de pasar la imagen directamente, se puede pasar la ruta al Dockerfile en `serverless.yml`:

```yaml
custom:
  pythonRequirements:
    dockerFile: ./ruta/a/Dockerfile
```
Lógicamente, hace falta tener Docker instalado para utilizar estas funciones.

## Serverless-wsgi

Este plugin permite desplegar aplicaciones WSGI de python con serverless. Para instalarlo, ejecutar:

```bash
sls plugin install -n serverless-wsgi
```
Particularmente, `Serverless-wsgi` permite desplegar localmente durante el desarrollo con el comando:

```bash
serverless wsgi serve
```

Sin embargo, **primero es necesario instalar las dependencias** en `requirements.txt`. Para esto podemos crear un `venv`: 

```bash
python3.8 -m venv ./venv
source ./venv/bin/activate
pip install werkzeug
pip install -r requirements.txt
```
