import os
import sys

# Добавим корень проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from celery import Celery

from app.core.config_file import config

celery_app = Celery(
    'worker',
    broker=f"amqp://{config.rabbitmq.user}:{config.rabbitmq.password}@{config.rabbitmq.host}:{config.rabbitmq.port}/",
    backend="rpc://"
)

celery_app.conf.task_routes = {
    "app.tasks.email.send_email_task": {"queue": "email"},
}

print("[CELERY] Celery worker initialized with RabbitMQ")
