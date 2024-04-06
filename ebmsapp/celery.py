from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE','newebsystem.settings')

app = Celery('newebsystem')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object(settings,namespace='CELERY')


app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request : {self.request!r}')


@app.task(bind=True)
def debug_task2(self):
    print(f'Request : {self.request!r}')

@app.task(bind=True)
def debug_task3(self):
    print(f'Request : {self.request!r}')