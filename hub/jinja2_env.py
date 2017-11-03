import datetime

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment


# index页面运行时间格式化显示
def runtime(dt):
    run_time = datetime.datetime.now() - dt
    run_time = datetime.timedelta(seconds=run_time.seconds)
    return run_time


# 页面时间格式互显示
def datetime_format(dt, format='%Y-%m-%d %H:%M:%S'):
    return dt.strftime(format)

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    env.filters["runtime"] = runtime
    env.filters["datetime_format"] = datetime_format
    return env
