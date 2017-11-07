"""
页面跳转及接口配置
"""
from django.conf.urls import url

from hub_migrate import views
from hub_migrate.interface import common, index, result

urlpatterns = [
    # 页面跳转
    url(r'^index.html$', views.index, name='index'),
    url(r'^new.html$', views.new, name='new'),
    url(r'^copy.html$', views.new, name='copy'),
    url(r'^progress.html$', views.progress, name='progress'),
    url(r'^result.html$', views.result, name='result'),
    
    # index.html页面数据接口
    url(r'^index.html/get_job/$', index.get_job, name="get job"),
    url(r'^index.html/copy/$', index.copy, name="copy"),
    
    # new.html页面数据接口
    url(r'^test/$', common.test, name='test'),
    url(r'^submit/$', common.submit, name='submit'),
    url(r'^create/$', common.create, name='create'),
    
    # result.html页面数据接口
    url(r'^result.html/get_job_info/$', result.get_job_info, name='get job info'),
    url(r'^result.html/get_table_info/$', result.get_table_info, name='get table info'),
    url(r'^result.html/get_nextPage_info/$', result.get_nextPage_info, name='get nextPage info'),
    url(r'^result.html/get_previousPage_info/$', result.get_previousPage_info, name='get previous info'),
]
