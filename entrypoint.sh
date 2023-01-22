#!/bin/bash
#exec gunicorn --config gunicorn_config.py main:app
exec gunicorn --bind=0.0.0.0:3001 --workers=3 --threads=4 --worker-class=gevent --log-level=debug --timeout=1000 main:app