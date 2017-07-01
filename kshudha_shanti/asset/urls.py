from django.conf.urls import url
from django.contrib import admin
from .views import *
from asset.my_views import *


urlpatterns = [
    url(r'^get/all/stock/items/$', get_all_stock_items),
    url(r'^save/stock/item/$', save_stock_item),
    url(r'^save/sell/order/$', save_sell_order),
]
