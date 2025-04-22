import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from celery import Celery

from app.core.config import config

celery_app = Celery(
    'worker',
    broker=f"amqp://{config.rabbitmq.user}:{config.rabbitmq.password}@{config.rabbitmq.host}:{config.rabbitmq.port}/",
    backend="rpc://"
)

celery_app.conf.task_routes = {
    "app.tasks.email.send_registration_email": {"queue": "email"},
}
