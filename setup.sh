#!/bin/bash

echo Running database initialization...
python3 database.py

echo Running database initialization...
python3 import_data.py

echo Starting Flask application...
gunicorn -b 0.0.0.0:5000 app:app
