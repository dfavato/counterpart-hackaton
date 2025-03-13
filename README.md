Before running `docker compose up` you'll need to create the data folders:

`docker volume create n8n_data`
`docker volume create traefik_data`
`docker compose up -d`

Create .env file and add your credentials.
`cp .env-example .env`

For running the basic.py file you'll need to:
`pipenv sync`
`pipenv run python basic.py`
