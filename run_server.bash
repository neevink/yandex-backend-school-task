#!/bin/bash
cd src
export FLASK_APP=api.py
gunicorn -b 0.0.0.0:8080 -w 5 api:app
cd ..