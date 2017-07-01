import datetime, csv, json 
from django.contrib.auth.models import User, Group
from asset.models import *
from supplier.models import *
from department.models import *

from django.db import transaction, IntegrityError
from django.db.models import Q, Max
from asset.helper_functions import *
from asset.my_views import *

# Department Ids
STORE_ID = 2
KITCHEN_ID = 3

# Stock item Ids
CHAPATI = 3
TEA = 2
SUGAR = 1
AALOO_PARATHA = 4
PITH = 5

def test_transfer_stock_between_departments():
    stock_items = [
        {
            "stock_item_id":3,
            "quantity": 3
        }
        # {
        #     "stock_item_id": 6542,
        #     "quantity": 2
        # }
    ]

    source_dept = STORE_ID
    dest_dept = KITCHEN_ID

    transfer_stock_between_departments(source_dept, dest_dept, stock_items)

def test_consume_item_from_department():

    dept_id = KITCHEN_ID

    stock_items_to_consume = [
        {
            "stock_item_id": TEA,
            "quantity": 5
        }
    ]
    consume_item_from_department(stock_items_to_consume, dept_id)

def test_add_item_to_department():

    dept_id = KITCHEN_ID

    stock_items_to_add = [
        {
            "stock_item_id": TEA,
            "quantity": 5
        }
    ]
    add_item_to_department(stock_items_to_add, dept_id)

def test_overwrite_department_stock():

    dept_id = KITCHEN_ID

    stock_items_in_department = [
        {
            "stock_item_id": TEA,
            "quantity": 50
        }
    ]
    overwrite_department_stock(stock_items_in_department, dept_id)

def test_produce_items_with_recipe():
    department_id = KITCHEN_ID

    produced_stock_items = [
        {
            "produced_stock_item_id": TEA,
            "produced_quantity": 15
        }
    ]

    produce_items_with_recipe(produced_stock_items, department_id)

def test_create_purchase_order_draft():
    supplier_id = 1
    dest_department_id = 3
    item_list = [
        {
            "stock_item_id": 1,
            "requested_quantity": 50,
            "requested_unit_price": 10
        }
    ]
    create_purchase_order_draft(item_list, supplier_id, dest_department_id)

def test_purchase_order_honoured():
    purchase_order_id = 2
    item_list = [
        {
            "stock_item_id": 1,
            "received_quantity": 45,
            "received_unit_price": 9
        }
    ]
    purchase_order_honoured(purchase_order_id, item_list)

def test_create_stock_transfer_request_draft():
    source_department_id = 1
    dest_department_id = 2
    item_list = [
        {
            "stock_item_id": 1,
            "requested_quantity": 50
        }
    ]
    create_stock_transfer_request_draft(source_department_id, dest_department_id, item_list)

def test_stock_transfer_request_honoured():
    stock_transfer_request_id = 2
    item_list = [
        {
            "stock_item_id": 1,
            "received_quantity": 45
        }
    ]
    stock_transfer_request_honoured(stock_transfer_request_id, item_list)

# ----------------------------------------------------------------------------------------------

def test_get_total_stock_quantity_from_all_department():

    get_total_stock_quantity_from_all_department()


def test_create_system_checkpoint_for_all_stock_items():

    create_system_checkpoint_for_all_stock_items()


def test_create_manual_checkpoint_for_stock_item():

    dept_stock = 1
    manual_checkpoint_ts = 1
    create_manual_checkpoint_for_stock_item(dept_stock, manual_checkpoint_ts)


def test_create_sale_order_draft():
    item_dict ={
                "from_department_id": 3,
                "order_code": "DCF1254",
                "item_list": [{"stock_item_id": 3, "quantity": 2}, {"stock_item_id": 4, "quantity": 4}]
               }

    create_sale_order_draft(item_dict["item_list"], item_dict["order_code"], item_dict["from_department_id"])

def test_purchase_order_honoured():
    item_dict ={
                "sale_order_id": 4,
                "item_list": [{"stock_item_id": 3, "quantity": 2}, {"stock_item_id": 4, "quantity": 4}]
               }
    sale_order_honoured(item_dict["sale_order_id"], item_dict["item_list"])
