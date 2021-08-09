# IETF @
IETF @ (IETF Author Tools)

## Installation

* Set up Python 3.8+ environment.
```
python3.8 -m venv venv
. venv/bin/activate
```

* Install required dependencies
```
pip install -r requirements.txt -c constraints.txt
```

NOTE: Known issue with Jinja conflict.

* Set up other dependencies for [xml2rfc](https://pypi.org/project/xml2rfc/).

* Install [kramdown-rfc2629](https://github.com/cabo/kramdown-rfc2629).

```
bundle install
```

## Configuration

* Create a instance directory and tmp directory
```
mkdir instance
mkdir tmp
```

* Add instance config

```
echo "UPLOAD_DIR = '$PWD/tmp'" > instance/config.py
```

## Testing

* Run server

```
FLASK_APP=at FLASK_ENV=development flask run
```

* Test XML RFC generation
```
curl localhost:5000/api/render/xml -X POST -F "file=@<xml2rfc draft | Kramdown draft>"
```

* Test HTML RFC generation
```
curl localhost:5000/api/render/html -X POST -F "file=@<xml2rfc draft | Kramdown draft>"
```

* Test text RFC generation
```
curl localhost:5000/api/render/text -X POST -F "file=@<xml2rfc draft | Kramdown draft>"
```

* Test PDF RFC generation
```
curl localhost:5000/api/render/pdf -X POST -F "file=@<xml2rfc draft | Kramdown draft>" -o draft-output.pdf
```

## License

* [IETF @ - License](LICENSE)
* [Swagger UI - License](api-doc/LICENSE)
