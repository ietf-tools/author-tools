FROM ubuntu:jammy
LABEL maintainer="Kesara Rathnayake <kesara@staff.ietf.org>"

ARG VERSION=6.6.6

ENV DEBIAN_FRONTEND=noninteractive
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
RUN mkdir -p /var/www/.fonts/opentype /tmp/fonts && \
    wget -q -O /tmp/fonts.tar.gz https://github.com/ietf-tools/xml2rfc-fonts/archive/refs/tags/3.22.0.tar.gz && \
    tar zxf /tmp/fonts.tar.gz -C /tmp/fonts && \
    mv /tmp/fonts/*/noto/* /var/www/.fonts/opentype/ && \
    mv /tmp/fonts/*/roboto_mono/* /var/www/.fonts/opentype/ && \
    chown -R www-data:0 /var/www/.fonts && \
    rm -rf /tmp/fonts.tar.gz /tmp/fonts/ && \
    fc-cache -f

# Install rfcdiff
RUN wget https://github.com/ietf-tools/rfcdiff/archive/refs/tags/1.49.tar.gz && \
    tar zxf 1.49.tar.gz -C /tmp/ && \
    mv /tmp/rfcdiff-1.49/rfcdiff /bin && \
    chmod +x /bin/rfcdiff && \
    rm -rf 1.49.tar.gz /tmp/rfcdiff-1.49

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
    wget "https://github.com/mmarkdown/mmark/releases/download/v2.2.45/mmark_2.2.45_linux_$arch.tgz" && \
    tar zxf mmark_*.tgz -C /bin/ && \
    rm mmark_*.tgz

COPY Gemfile Gemfile.lock LICENSE README.md api.yml constraints.txt package-lock.json package.json requirements.txt docker/version.py ./
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

# nginx unprivileged setup
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    sed -i '/user www-data;/d' /etc/nginx/nginx.conf && \
    sed -i 's,/run/nginx.pid,/tmp/nginx.pid,' /etc/nginx/nginx.conf && \
    sed -i "/^http {/a \    proxy_temp_path /tmp/proxy_temp;\n    client_body_temp_path /tmp/client_temp;\n    fastcgi_temp_path /tmp/fastcgi_temp;\n    uwsgi_temp_path /tmp/uwsgi_temp;\n    scgi_temp_path /tmp/scgi_temp;\n" /etc/nginx/nginx.conf && \
    mkdir -p /var/cache/nginx && \
    chown -R www-data:0 /var/cache/nginx && \
    chmod -R g+w /var/cache/nginx

RUN mkdir -p tmp && \
    echo "UPLOAD_DIR = '$PWD/tmp'" > at/config.py && \
    echo "VERSION = '${VERSION}'" >> at/config.py && \
    echo "REQUIRE_AUTH = False" >> at/config.py && \
    echo "DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/api/rfcdiff-latest-json'" >> at/config.py && \
    echo "ALLOWED_DOMAINS = ['ietf.org', 'rfc-editor.org', 'github.com', 'githubusercontent.com', 'github.io', 'gitlab.com', 'gitlab.io', 'codeberg.page']" >> at/config.py && \
    python3 version.py >> at/config.py && \
    chown -R www-data:0 /usr/src/app/tmp

# cache configuration
RUN mkdir -p /tmp/cache/xml2rfc && \
    mkdir -p /tmp/cache/refcache && \
    ln -sf /tmp/cache/xml2rfc /var/cache/xml2rfc && \
    chown -R www-data:0 /tmp/cache
ENV KRAMDOWN_REFCACHEDIR=/tmp/cache/refcache


# COPY required files
COPY static /usr/share/nginx/html/
COPY api.yml /usr/share/nginx/html/
COPY docker/gunicorn.py /usr/src/app/
COPY docker/nginx-default-site.conf /etc/nginx/sites-available/default
COPY docker/supervisord.conf /etc/supervisor/

USER www-data
EXPOSE 8080
WORKDIR /usr/src/app/

CMD ["supervisord"]
