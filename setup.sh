#!binbash

echo Running database initialization...
python3 database.py

echo Running database initialization...
python3 import_data.py

echo Starting Flask application...
python3 app.py
