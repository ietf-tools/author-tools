# Contributing

This repository relates to activities in the Internet Engineering Task Force
([IETF](https://www.ietf.org/)). All material in this repository is considered
Contributions to the IETF Standards Process, as defined in the intellectual
property policies of IETF currently designated as
[BCP 78](https://www.rfc-editor.org/info/bcp78),
[BCP 79](https://www.rfc-editor.org/info/bcp79) and the
[IETF Trust Legal Provisions (TLP) Relating to IETF Documents](http://trustee.ietf.org/trust-legal-provisions.html).

Any edit, commit, pull request, issue, comment or other change made to this
repository constitutes Contributions to the IETF Standards Process
(https://www.ietf.org/).

You agree to comply with all applicable IETF policies and procedures, including,
BCP 78, 79, the TLP, and the TLP rules regarding code components (e.g. being
subject to a Simplified BSD License) in Contributions.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[Setting up development environment](#setting-up-development-environment)

[Running tests](#running-tests)

## Code of Conduct

See [Code of Conduct](CODE_OF_CONDUCT.md).

## Setting up development environment

* Set up Python 3.8+ environment.
```
python3.8 -m venv venv
. venv/bin/activate
```

* Install required dependencies.
```
pip install -r requirements.txt
```

> **NOTE:** Known issue with Jinja conflict.

* Set up other dependencies for [xml2rfc](https://pypi.org/project/xml2rfc/).

* To use kramdown-rfc2629 and mmark, you need to have
[ruby](https://www.ruby-lang.org/) and [go](https://golang.org/) installed.

* Install kramdown-rfc2629 dependencies

    Install [GoAT](https://github.com/blampe/goat).
    ```
    go get github.com/blampe/goat
    ```

* Install npm dependencies
```
npm install
```

* Install [kramdown-rfc2629](https://github.com/cabo/kramdown-rfc2629).
```
bundle install
```

* Install [mmark](https://github.com/mmarkdown/mmark).
```
go get github.com/mmarkdown/mmark
```

* Create a tmp directory.
```
mkdir tmp
```

* Create a configuration file.
```
echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py
echo "VERSION = '9.9.9'" >> at/config.py
echo "DT_APPAUTH_URL = 'https://datatracker.ietf.org/api/appauth/authortools'" >> at/config.py
echo "DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/doc/rfcdiff-latest-json'" >> at/config.py
echo "IDDIFF_ALLOWED_DOMAINS = ['ietf.org', 'ietf.org', 'rfc-editor.org']" >> at/config.py
```

* Run flask server.
```
FLASK_APP=at FLASK_ENV=development flask run
```

## Running tests
* Install required dependencies for testing.
```
pip install -r requirements.dev.txt
```

* Run unit tests.
```
python -m unittest discover tests
```
