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

[Note Well](#note-well)

[Setting up development environment](#setting-up-development-environment)

## Note Well

This is a reminder of IETF policies in effect on various topics such as patents
or code of conduct. It is only meant to point you in the right direction.
Exceptions may apply. The IETF's patent policy and the definition of an IETF
"contribution" and "participation" are set forth in BCP 79; please read it
carefully.

As a reminder:
 * By participating in the IETF, you agree to follow IETF processes and
policies.
 * If you are aware that any IETF contribution is covered by patents or patent
applications that are owned or controlled by you or your sponsor, you must
disclose that fact, or not participate in the discussion.
 * As a participant in or attendee to any IETF activity you acknowledge that
written, audio, video, and photographic records of meetings may be made public.
 * Personal information that you provide to IETF will be handled in accordance
with the IETF Privacy Statement.
 * As a participant or attendee, you agree to work respectfully with other
participants; please contact the ombudsteam
(https://www.ietf.org/contact/ombudsteam/) if you have questions or concerns
about this.

Definitive information is in the documents listed below and other IETF BCPs.
For advice, please talk to WG chairs or ADs:

* [BCP 9](https://www.rfc-editor.org/info/bcp9) (Internet Standards Process)
* [BCP 25](https://www.rfc-editor.org/info/bcp25) (Working Group processes)
* [BCP 25](https://www.rfc-editor.org/info/bcp25) (Anti-Harassment Procedures)
* [BCP 54](https://www.rfc-editor.org/info/bcp54) (Code of Conduct)
* [BCP 78](https://www.rfc-editor.org/info/bcp78) (Copyright)
* [BCP 79](https://www.rfc-editor.org/info/bcp79) (Patents, Participation)
* https://www.ietf.org/privacy-policy/ (Privacy Policy)

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

* Install [kramdown-rfc2629](https://github.com/cabo/kramdown-rfc2629).
```
bundle install
```

* Create a tmp directory.
```
mkdir tmp
```

* Create a configuration file.
```
echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py
```

* Run flask server.
```
FLASK_APP=at FLASK_ENV=development flask run
```
