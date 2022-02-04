FROM ubuntu:latest

WORKDIR /usr/src/app

COPY . .

RUN apt-get update
RUN apt-get install -y software-properties-common gcc wget
RUN apt-get install -y ruby python3.8 python3-pip

# xml2rfc (Weasyprint) dependencies
RUN apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libcairo2-dev libpangocairo-1.0-0

# install Go lang
RUN apt-get install -y golang git
ENV GOPATH=/

# install mmark
RUN go get github.com/mmarkdown/mmark
# install goat (kramdown-rfc2629 dependency)
RUN go get github.com/blampe/goat

# install npm dependencies
RUN apt-get install -y npm
RUN npm install
ENV PATH=$PATH:./node_modules/.bin

# install idnits
RUN apt-get install -y gawk
RUN wget https://raw.githubusercontent.com/ietf-tools/idnits-mirror/main/idnits
RUN cp idnits /bin
RUN chmod +x /bin/idnits

RUN pip3 install -r requirements.txt
RUN gem install bundler
RUN bundle install

# install required fonts
RUN mkdir -p ~/.fonts/opentype
RUN wget -q https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip
RUN unzip -q Noto-unhinted.zip -d ~/.fonts/opentype/
RUN wget -q https://fonts.google.com/download?family=Roboto%20Mono -O roboto-mono.zip
RUN unzip -q roboto-mono.zip -d ~/.fonts/opentype/

RUN mkdir -p tmp
RUN echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py
RUN echo "VERSION = '0.3.2'" >> at/config.py
RUN echo "DT_APPAUTH_URL = 'https://datatracker.ietf.org/api/appauth/authortools'" >> at/config.py
RUN echo "DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/doc/rfcdiff-latest-json'" >> at/config.py
RUN echo "IDDIFF_ALLOWED_DOMAINS = ['ietf.org', 'rfc-editor.org', 'githubusercontent.com', 'github.io', 'gitlab.com']" >> at/config.py

# host with waitress
RUN pip3 install waitress
CMD python3 serve.py
