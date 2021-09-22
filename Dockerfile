FROM ubuntu:latest

WORKDIR /usr/src/app

COPY . .

RUN apt-get update
RUN apt-get install -y software-properties-common gcc
RUN apt-get install -y ruby python3.8 python3-pip
# xml2rfc (Weasyprint) dependencies
RUN apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
# install kramdown-rfc2629 dependencies
RUN apt-get install -y golang git
ENV GOPATH=/
RUN go get github.com/blampe/goat

RUN pip3 install -r requirements.txt
RUN gem install bundler
RUN bundle install


RUN mkdir -p tmp
RUN echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py
RUN echo "VERSION = '0.0.1'" >> at/config.py
RUN echo "DT_APPAUTH_URL = 'https://datatracker.ietf.org/api/appauth/authortools'" >> at/config.py

# host with waitress
RUN pip3 install waitress
CMD waitress-serve --port=80 --call 'at:create_app'
