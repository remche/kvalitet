import djcelery
djcelery.setup_loader()

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis'

