#!/usr/bin/python

import requests
import os
import sys
from wsgiref.handlers import CGIHandler

if sys.version_info < (3,):
    def b(x):
        return x
else:
    import codecs

    def b(x):
        return codecs.latin_1_encode(x)[0]


def application(environ, start_response):
    status = '200 OK'

    r = requests.get("http://example.com/")

    output = """
    Made internal subrequest to http://example.com/ and got:
      os.environ[HTTP_PROXY]: %(proxy)s
      os.getenv('HTTP_PROXY'): %(getenv-proxy)s
      wsgi Proxy header: %(wsgi-env-proxy)s
      status code: %(status)d
      text: %(text)s
    """ % {
        'proxy': os.environ['HTTP_PROXY'] if 'HTTP_PROXY' in os.environ else 'none',
        'getenv-proxy': os.getenv('HTTP_PROXY', 'none'),
        'wsgi-env-proxy': environ['HTTP_PROXY'] if 'HTTP_PROXY' in environ else 'none',
        'status': r.status_code,
        'text': r.text
    }

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(b(output))))]

    start_response(status, response_headers)

    return [b(output)]

if __name__ == '__main__':
    CGIHandler().run(application)
