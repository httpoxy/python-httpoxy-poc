FROM eboraas/apache:latest

RUN mkdir -p /usr/local/share/httpoxy
WORKDIR /usr/local/share/httpoxy

RUN apt-get update && apt-get install -y \
    python \
    python-pip \
 && rm -rf /var/lib/apt/lists/*

RUN pip install requests
RUN a2enmod cgid
COPY apache2.conf /etc/apache2/apache2.conf

COPY server.cgi ./httpoxy
