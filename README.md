Pre-requirements:
- Docker version 18.03.1
- Docker-compose version 1.21.2

Installation:
1. Set up in `settings.py` `WIT_AI_ACCESS_TOKEN` and `SALT`
   Also, you can set up `PRIVATE_KEY_FILENAME` which will be specified you private key
2. `docker-compose build`
3. `docker-compose up -d`
   Wait some time and the site will be available in `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/admin` URL addresses

4. For shutting down your Docker containers type: `docker-compose down`


To add new URL into the DB use `http://127.0.0.1:8000/`
To get a list of all words entered into the DB and list of all the URLs use `http://127.0.0.1:8000/admin`
