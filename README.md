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

* Test HTML RFC generation
```
curl localhost:5000/api/render/html -X POST -F "file=@<xml2rfc draft | Karmadown draft>"
```
