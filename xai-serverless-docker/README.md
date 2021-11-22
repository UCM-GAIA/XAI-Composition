# Docker

Se puede crear una Docker Image para despues lanzar el servidor localmente a partir del fichero `Dockerfile`. Para esto es necesario tener Docker instalado. 

Primero se contruye la imagen, ejecutando este comando desde el directorio donde se encuentren los archivos `requirements.txt` y `Dockerfile`

```
docker build -t <nombre del tag> .
```
Con el tag que asignemos nos podemos referir a la imagen una vez que se haya creado. **Nota:** En el fichero `Dockerfile` se instalan todas las librerías de forma individual con pip para poder depurar en caso de producirse un error, pero también se puede hacer un único pip con `requirements.txt`.
Una vez creada la imagen, podemos ejecutar:

```
bash
docker run -p 5000:5000 <nombre del tag asignado>
```
Con esto debería lanzarse el servidor en local en un contenedor. Se hace el mapeo al puerto 5000 con la opción -p. Para realizar las llamadas con curl o Postman (ver ejemplos con curl el directorio Server de este repo), podemos utilizar la dirección https:localhost:5000.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
