#!/bin/bash

mkdir /tmp/panosteal/ -p
gunicorn -c gunicorn.cfg server.daemon

