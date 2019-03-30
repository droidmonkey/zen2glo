#!/usr/bin/python3
from flup.server.fcgi import WSGIServer
from app import create_app

if __name__ == '__main__':
    WSGIServer(create_app()).run()
