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

* Build docker image
```sh
docker build -f dev.Dockerfile -t author-tools:dev .
```

* Run the docker image
```sh
docker run -it author-tools:dev
```

* Run unit tests.
```sh
python3 -m unittest discover tests
```
