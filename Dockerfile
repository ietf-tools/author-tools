FROM ubuntu:latest

WORKDIR /usr/src/app

COPY . .

RUN apt-get update
RUN apt-get install -y software-properties-common gcc
RUN apt-get install -y ruby python3.8 python3-pip
# xml2rfc (Weasyprint) dependencies
RUN apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

RUN pip3 install -r requirements.txt
RUN gem install bundler
RUN bundle install


RUN mkdir -p tmp
RUN echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py

# host with waitress
RUN pip install waitress
CMD waitress-serve --port=8888 --call 'at:create_app'
