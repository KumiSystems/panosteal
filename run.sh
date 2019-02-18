#!/bin/bash

mkdir /tmp/panosteal/youtube -p
gunicorn -c gunicorn.cfg server.daemon

