FROM ubuntu:jammy
LABEL maintainer="Kesara Rathnayake <kesara@staff.ietf.org>"

ARG VERSION=6.6.6

ENV DEBIAN_FRONTEND noninteractive
ENV PATH=$PATH:./node_modules/.bin
# Disable local file read for kramdown-rfc
ENV KRAMDOWN_SAFE=1

WORKDIR /usr/src/app

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Add nodejs 18.x
RUN apt-get update && \
    apt-get install -y curl gpg && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

RUN apt-get update && \
    apt-get install -y \
        software-properties-common \
        gcc \
        wget \
        ruby \
        python3.10 \
        python3-pip \
        libpango-1.0-0 \
        libpango1.0-dev \
        wdiff \
        rfcdiff \
        nodejs \
        gawk \
        bison \
        flex \
        nginx \
        supervisor && \
    rm -rf /var/lib/apt/lists/* /var/log/dpkg.log && \
    apt-get autoremove -y && \
    apt-get clean -y

# Install required fonts
RUN mkdir -p ~/.fonts/opentype /tmp/fonts && \
    wget -q -O /tmp/fonts.tar.gz https://github.com/ietf-tools/xml2rfc-fonts/archive/refs/tags/3.20.0.tar.gz && \
    tar zxf /tmp/fonts.tar.gz -C /tmp/fonts && \
    mv /tmp/fonts/*/noto/* ~/.fonts/opentype/ && \
    mv /tmp/fonts/*/roboto_mono/* ~/.fonts/opentype/ && \
    rm -rf /tmp/fonts.tar.gz /tmp/fonts/

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
    wget "https://github.com/mmarkdown/mmark/releases/download/v2.2.43/mmark_2.2.43_linux_$arch.tgz" && \
    tar zxf mmark_*.tgz -C /bin/ && \
    rm mmark_*.tgz

COPY Gemfile Gemfile.lock LICENSE README.md api.yml constraints.txt package-lock.json package.json requirements.txt docker/version.py .
COPY at ./at

# Install JavaScript dependencies
RUN npm install

# Rename idnits v3 binary
RUN mv ./node_modules/.bin/idnits ./node_modules/.bin/idnits3

# Install Python dependencies
RUN apt-get remove -y python3-blinker
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt -c constraints.txt

# Install Ruby dependencies
RUN gem install bundler && bundle install

RUN mkdir -p tmp && \
    echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py && \
    echo "VERSION = '${VERSION}'" >> at/config.py && \
    echo "REQUIRE_AUTH = False" >> at/config.py && \
    echo "DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/api/rfcdiff-latest-json'" >> at/config.py && \
    echo "ALLOWED_DOMAINS = ['ietf.org', 'rfc-editor.org', 'github.com', 'githubusercontent.com', 'github.io', 'gitlab.com', 'gitlab.io', 'codeberg.page']" >> at/config.py && \
    python3 version.py >> at/config.py


# COPY required files
COPY static /usr/share/nginx/html/
COPY api.yml /usr/share/nginx/html/
COPY docker/gunicorn.py /usr/src/app/
COPY docker/nginx-default-site.conf /etc/nginx/sites-available/default
COPY docker/supervisord.conf /etc/supervisor/conf.d/

CMD ["supervisord"]
