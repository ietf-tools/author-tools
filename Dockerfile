FROM ubuntu:jammy
LABEL maintainer="Kesara Rathnayake <kesara@staff.ietf.org>"

ENV DEBIAN_FRONTEND noninteractive
ENV PATH=$PATH:./node_modules/.bin
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
# Disable local file read for kramdown-rfc
ENV KRAMDOWN_SAFE=1

WORKDIR /usr/src/app

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y \
        autoconf \
        software-properties-common \
        gcc \
        wget \
        ruby \
        python3.10 \
        python3-pip \
        pkg-config \
        libtool \
        libpango-1.0-0 \
        wdiff \
        rfcdiff \
        npm \
        gawk \
        bison \
        flex && \
    rm -rf /var/lib/apt/lists/* /var/log/dpkg.log && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    ldconfig

# Install required fonts
RUN mkdir -p ~/.fonts/opentype && \
    wget -q https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip && \
    unzip -q Noto-unhinted.zip -d ~/.fonts/opentype/ && \
    rm Noto-unhinted.zip && \
    wget -q https://fonts.google.com/download?family=Roboto%20Mono -O roboto-mono.zip && \
    unzip -q roboto-mono.zip -d ~/.fonts/opentype/ && \
    rm roboto-mono.zip && \
    wget -q https://fonts.google.com/download?family=Noto+Sans+Math -O noto-sans-math.zip && \
    unzip -q noto-sans-math.zip -d ~/.fonts/opentype/ && \
    rm noto-sans-math.zip

# Install bap
RUN wget https://github.com/ietf-tools/bap/archive/refs/heads/master.zip && \
    unzip -q master.zip -d /tmp/bap && \
    cd /tmp/bap/bap-master/ && \
    ./configure && \
    make && \
    cp aex bap /bin && \
    rm -rf /tmp/bap master.zip

# Install idnits
RUN wget https://github.com/ietf-tools/idnits/archive/refs/tags/2.17.1.zip && \
    unzip -q 2.17.1.zip -d ~/idnits && \
    cp ~/idnits/idnits-2.17.1/idnits /bin && \
    chmod +x /bin/idnits && \
    rm -rf ~/idnits/idnits-2.17.1/idnits idnit 2.17.1.zip

# Install mmark
RUN arch=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) && \
    wget "https://github.com/mmarkdown/mmark/releases/download/v2.2.31/mmark_2.2.31_linux_$arch.tgz" && \
    tar zxf mmark_*.tgz -C /bin/ && \
    rm mmark_*.tgz

# Install utftex
RUN export UTFTEX=libtexprintf-1.25 && \
    wget -q https://github.com/bartp5/libtexprintf/archive/refs/tags/v1.25.zip && \
    unzip -q v1.25.zip -d /tmp/ && \
    cd /tmp/$UTFTEX && \
    ./autogen.sh && \
    ./configure && \
    make install && \
    rm -r /tmp/$UTFTEX /usr/src/app/v1.25.zip

COPY Gemfile Gemfile.lock LICENSE README.md api.yml constraints.txt package-lock.json package.json requirements.txt .
COPY at ./at

# Install JavaScript dependencies
RUN npm install

# Install Python dependencies
RUN apt-get remove -y python3-blinker
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt -c constraints.txt gunicorn

# Install Ruby dependencies
RUN gem install bundler && bundle install

RUN mkdir -p tmp && \
    echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py && \
    echo "VERSION = '0.17.6'" >> at/config.py && \
    echo "REQUIRE_AUTH = False" >> at/config.py && \
    echo "DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/api/rfcdiff-latest-json'" >> at/config.py && \
    echo "ALLOWED_DOMAINS = ['ietf.org', 'rfc-editor.org', 'github.com', 'githubusercontent.com', 'github.io', 'gitlab.com', 'gitlab.io', 'codeberg.page']" >> at/config.py

# host with gunicorn
CMD gunicorn --workers=16 -b 0.0.0.0:80 'at:create_app()'
