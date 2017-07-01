import datetime, csv, json 
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User, Group
from asset.models import *
from supplier.models import *
from department.models import *

from django.db import transaction, IntegrityError
from django.db.models import Q, Max 

from helper_functions import convert_epoch_to_date


def create_department_stock(stock_item_id,department_id,quantity=0):
    print(stock_item_id)
    stock_item=StockItem.objects.get(id=stock_item_id)
    department=Department.objects.get(id=department_id)
    
    dept_stock=DepartmentStock()
    dept_stock.stock_item=stock_item       
    dept_stock.department=department
    dept_stock.quantity=quantity
    dept_stock.save()
    return dept_stock

def get_or_create_department_stock(stock_item_id,department_id):
    try:
        dept_stock=DepartmentStock.objects.get(stock_item=stock_item_id,department=department_id)
    except Exception as e:
        print(e)
        dept_stock=create_department_stock(stock_item_id,department_id)

    return dept_stock

def transfer_stock_between_departments(source_dept_id,dest_dept_id,stock_items):
# stock_items = [{"stock_item_id": 4,"quantity": 3}]
#     source_dept = KITCHEN_ID=1
#     dest_dept = STORE_ID=2
    for stock in stock_items:
        print('stock: ', stock)
        source_dept_info=get_or_create_department_stock(stock['stock_item_id'],source_dept_id)
        dest_dept_info=get_or_create_department_stock(stock['stock_item_id'],dest_dept_id)
        print('source_dept_info: ', source_dept_info)
        print('dest_dept_info: ', dest_dept_info)
                
        print('stock: ', stock)
        source_dept_info.quantity -= stock['quantity']
        
        dest_dept_info.quantity += stock['quantity']
        
        source_dept_info.save()
        
        dest_dept_info.save()

def consume_item_from_department(stock_items_to_consume, dept_id):
# dept_id = KITCHEN_ID
#     stock_items_to_consume = [{"stock_item_id": TEA,"quantity": 1}]        
    for stock in stock_items_to_consume:
        stock_detail=get_or_create_department_stock(stock["stock_item_id"],dept_id)
        stock_detail.quantity -= stock["quantity"]
        stock_detail.save()

def add_item_to_department(stock_items_to_add, dept_id):
    # dept_id = KITCHEN_ID
    # stock_items_to_add = [{"stock_item_id": TEA,"quantity": 5}]
    for stock in stock_items_to_add:
        stock_detail=get_or_create_department_stock(stock["stock_item_id"],dept_id)
        stock_detail.quantity += stock["quantity"]
        stock_detail.save()

def produce_items_with_recipe(produced_stock_items, department_id):
    # department_id = KITCHEN_ID
    # produced_stock_items = [{"produced_stock_item_id": TEA,"produced_quantity": 15}]        
    for stock in produced_stock_items:
        produced_recipe=get_or_create_department_stock(stock["produced_stock_item_id"],department_id)
        produced_recipe.quantity += stock["produced_quantity"]        
        print(produced_recipe)
        produced_recipe.save()
        get_recipe=Recipe.objects.get(produced_item=stock["produced_stock_item_id"])
        print(get_recipe)
        ingidient=json.loads(get_recipe.ingredients_json)
        print(ingidient)
        # [{'quantity': 2, 'stock_item_id': 1}]
        for item in ingidient:
           get_item=get_or_create_department_stock(item["stock_item_id"]) 
           get_item.quantity -= item["quantity"]
           get_item.save()

def get_all_stock_items(request):
    if request.method == "OPTIONS":
        return JsonResponse({"status": False})
        
    # {"usage_types":[1,2]}
    params=json.loads(str(request.body, 'utf-8'))
    usage_types=params.get('usage_types')
    stock_item_list=[]
    kwargs={}
    kwargs["is_active"]=True
    kwargs["usage_type__in"]=usage_types
    stock_get_items=StockItem.objects.filter(**kwargs)
    for stocks in stock_get_items:
        stock_item_list.append(stocks.get_json())

    return JsonResponse({"data": stock_item_list, "status": True})

def stock_total_quantity(department_stock_item_list):
    total_quantity=0
    for item in department_stock_item_list:
        total_quantity =total_quantity+float(item['quantity'])
    return total_quantity    
    
def get_total_stock_quantity_from_all_department(request):        
# [{'stock_name': 'Aaloo Paratha', 'total_quantity': 35.0, 
# 'department_stock_item_list': [{'department': 'Store', 'quantity': 12.0},
# {'department': 'Kitchen', 'quantity': 23.0}]
    get_all_stock=StockItem.objects.all()
    final_list=[]
    for stock in get_all_stock:
        Dict={}
        stock_name=stock.name
        Dict["stock_name"]=stock_name
        stock_dept=DepartmentStock.objects.filter(stock_item=stock)
        department_stock_item_list=[]
        for stock_item in stock_dept:
            department_stock_item_list.append({"department":stock_item.department.name,"quantity":stock_item.quantity})
        Dict["department_stock_item_list"]=department_stock_item_list
        total_quantity=stock_total_quantity(department_stock_item_list)
        Dict["total_quantity"]=total_quantity
        final_list.append(Dict)    
    print("total_quantity: ",total_quantity)   
    print(final_list)
    return HttpResponse(final_list)

def save_stock_item(request):
    input_data= json.loads(str(request.body, 'utf-8'))
    print("input_data: ",input_data)
    data,massage,status=validate_stock_item(input_data)
    if status:
        stock_item=StockItem.objects.create(**data)
    return JsonResponse({"validation": massage, "status": status})

def validate_stock_item(input_data):
    kwargs={}
    code = params.get("code")
    name = params.get("name")
    regional_name = params.get("regional_name")
    brand = params.get("brand")
    sale_price = params.get("sale_price")
    usage_type = params.get("usage_type")
    nature = params.get("nature")
    quantity_unit = params.get("quantity_unit")
    tax_rate = params.get("tax_rate")
    description = params.get("description")
    shelf_life = params.get("shelf_life")
    notes = params.get("notes")
    is_active = params.get("is_active")

    if (not code)or (not name)or (not regional_name):
        return kwargs, "Invalid data", False

    if StockItem.objects.filter(code=code).exists():
        return kwargs, "Item already exists", False

    kwargs = {
                "code": code,
                "name": name,
                "regional_name": regional_name,
                "brand": brand,
                "sale_price": sale_price,
                "usage_type": usage_type,
                "nature": nature,
                "quantity_unit": quantity_unit,
                "tax_rate": tax_rate,
                "description": description,
                "shelf_life": shelf_life,
                "notes": notes,
                "is_active": is_active
            }            

    return kwargs, "Stock item saved", True  


def create_purchase_order_draft(item_list, supplier_id, dest_department_id):
    purchase_order_draft=PurchaseOrder()
    purchase_order_draft.placed_date=datetime.datetime.now()
    purchase_order_draft.status=PURCHASE_ORDER_STATUS[0][0]
    purchase_order_draft.supplier=Supplier.objects.get(id=supplier_id)
    purchase_order_draft.dest_department=Department.objects.get(id=department_id)
    purchase_order_draft.save()
    for item in item_list:
        if float(item['requested_quantity']) > 0.0:
            purchase_order_item=PurchaseOrderItem()
            purchase_order_item.purchase_order=purchase_order_draft
            purchase_order_item.item=StockItem.objects.get(id=item['stock_item_id'])
            purchase_order_item.requested_quantity=item["requested_quantity"]
            purchase_order_item.received_unit_price=item["received_unit_price"]
            purchase_order_item.save()