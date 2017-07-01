from django.conf.urls import url
from django.contrib import admin
from .views import *


urlpatterns = [
    url(r'^get/all/departments/$', get_all_departments),
]
