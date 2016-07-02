FROM grahamdumpleton/mod-wsgi-docker:python-3.5-onbuild
MAINTAINER Dominic Scheirlinck <dominic@vendhq.com>

COPY . .

CMD [ "server.wsgi" ]
