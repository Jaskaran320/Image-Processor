from celery import Celery

celery_app = Celery(
    "image_processor_api",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks.image_tasks"],
)

celery_app.conf.task_routes = {
    'app.tasks.image_tasks.*': 'image-processing-queue',
}
celery_app.conf.task_default_queue = 'default'
