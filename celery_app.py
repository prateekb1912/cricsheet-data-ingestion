from celery import Celery
from redis_resource import connection_link

app = Celery(
    'cricbit',
    broker=connection_link,
    backend=connection_link
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    imports=('services.queue.tasks',),
)