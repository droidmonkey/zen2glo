#!/usr/bin/env python3.7
from flup.server.fcgi import WSGIServer
from app import create_app

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = ''
       return self.app(environ, start_response)

app = ScriptNameStripper(create_app())

if __name__ == '__main__':
    WSGIServer(app).run()
