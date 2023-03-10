# Crypto alert
The application is designed to monitor the price of cryptocurrencies and send alerts.

## Dependences:
### With Docker:
- Docker (docker compose)
- WSL (only for Windows)

### Without Docker:
- Python 3.10+
- installed python depandences from requirements.txt
- Redis
- Postgres
- Nginx (or other proxy) for the application
- minimum 3 terminals for running the app, celery-worker, and celery-beat at the same time

## Install (Docker compose):
1. Clone the repository
2. Make .env file (copy .env-example) and fill it right
3. Run the app:
```
docker-compose -f docker-compose-deploy.yml up -d
```
4. Create superuser:
```
docker-compose -f docker-compose-deploy.yml run --rm app sh -c "python manage.py wait_for_db && python manage.py createsuperuser"
```
and fill e-mail and password

## Usage:
### Administer alerts:
via admin panel http://app-url/admin/:

![Alt text](docs/admin.png?raw=true "Admin panel")

or via REST API http://app-url/api/docs

![Alt text](docs/docs.png?raw=true "API Docks")

### Control tasks via Flower dashboard (http://app-url/flower/)

![Alt text](docs/flower.png?raw=true "Flower dashboard")
