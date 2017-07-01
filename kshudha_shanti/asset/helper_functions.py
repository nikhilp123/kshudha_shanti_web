import datetime, csv, json 
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User, Group
from asset.models import *
from supplier.models import *
from department.models import *

from django.db import transaction, IntegrityError
from django.db.models import Q, Max 

from helper_functions import convert_epoch_to_date


def get_usage_type_id(usage_types):
    usage_type_list = []
    for usage_type in usage_types:
        usage_type = usage_type.strip()

        if str(usage_type) == 'RAW_MATERIAL':
            usage_type_list.append(1)
        elif str(usage_type) == 'FINISHED_PRODUCT':
            usage_type_list.append(2)
        elif str(usage_type) == 'APPLIANCE':
            usage_type_list.append(3)

    return list(set(usage_type_list))

# def transfer_stock_between_departments(source_dept_id, dest_dept_id, stock_items):
#     print('============================ transfer_stock_between_departments ============================')
#     try:
#         with transaction.atomic():
#             for stock_item in stock_items:
#                 print('')
#                 source_department_stock = get_or_create_new_department_stock(stock_item['stock_item_id'], source_dept_id)
#                 if not source_department_stock:
#                     raise Exception('Failed to create source department stock entry')

#                 dest_department_stock = get_or_create_new_department_stock(stock_item['stock_item_id'], dest_dept_id)
#                 if not dest_department_stock:
#                     raise Exception('Failed to create dest department stock entry')

#                 source_department_stock.quantity -= stock_item['quantity']
#                 dest_department_stock.quantity += stock_item['quantity']

#                 source_department_stock.save()
#                 dest_department_stock.save()
#                 print('success: transfered ', source_department_stock, 'to', dest_department_stock, 'quantity:', stock_item['quantity'])
#                 print('------------------------------')
#             # End of for loop
#             print ('Success transfer_stock_between_departments')
#             return True
#     except Exception as e:
#         print ('Error in transfer_stock_between_departments: ', e)
#         print ('Rolling back stock transfer trancation')
#         return False


# def create_department_stock(stock_item_id, department_id, quantity=0):
#     try:
#         with transaction.atomic():
#             stock_item = StockItem.objects.get(id=stock_item_id)
#             department = Department.objects.get(id=department_id)

#             department_stock = DepartmentStock()
#             department_stock.stock_item = stock_item
#             department_stock.department = department
#             department_stock.quantity = quantity
#             department_stock.quantity_unit = stock_item.quantity_unit
#             department_stock.save()
#             return department_stock
#     except Exception as e:
#         print(e)
#         return None

# def produce_items_with_recipe(produced_stock_items, department_id):
#     for produced_stock_item in produced_stock_items:
#         produced_stock_item_id = produced_stock_item['produced_stock_item_id']
#         produced_quantity = produced_stock_item['produced_quantity']

#         # Increase produced item quantity
#         produced_department_stock = get_or_create_new_department_stock(produced_stock_item_id, department_id)
#         if not produced_department_stock:
#             raise Exception('Failed to create department stock entry')

#         produced_department_stock.quantity += produced_quantity
#         produced_department_stock.save()

#         # Get recipe and ingredients
#         recipe = Recipe.objects.get(produced_item=produced_stock_item_id)
#         ingredients = json.loads(recipe.ingredients_json)

#         # Decrease ingredient item quantity
#         for ingredient in ingredients:
#             ingredient_department_stock = get_or_create_new_department_stock(ingredient['stock_item_id'], department_id)
#             if not ingredient_department_stock:
#                 raise Exception('Failed to create department stock entry')

#             consumed_qty = (float(produced_quantity)/float(recipe.produced_item_quantity)) * ingredient['quantity']

#             ingredient_department_stock.quantity -= consumed_qty
#             ingredient_department_stock.save()
#             print('success produce_item_with_recipe: ', ingredient_department_stock)
#     # End of for loop
#     return "success"

def get_conversion_factor(from_unit, to_unit):
    return 1

# def overwrite_department_stock(stock_items_in_department, department_id):
#     try:
#         with transaction.atomic():
#             for stock_item in stock_items_in_department:
#                 stock_item_id = stock_item['stock_item_id']
#                 quantity = stock_item['quantity']

#                 department_stock = get_or_create_new_department_stock(stock_item_id, department_id)
#                 if not department_stock:
#                     return None

#                 department_stock.quantity = quantity
#                 department_stock.save()
#                 print('department stock overwritten', department_stock)
#             # End of for loop
#             return True
#     except Exception as e:
#         print('Error: ', e)
#         return False

# def add_item_to_department(stock_items_to_add, dept_id):
#     try:
#         with transaction.atomic():
#             for stock_item in stock_items_to_add:
#                 stock_item_id = stock_item['stock_item_id']
#                 quantity = stock_item['quantity']

#                 department_stock = get_or_create_new_department_stock(stock_item_id, dept_id)
#                 if not department_stock:
#                     raise Exception('Failed to add department stock')

#                 department_stock.quantity += quantity
#                 department_stock.save()
#                 print('added item to department', department_stock)
#             # End of for loop
#             return True
#     except Exception as e:
#         print('Error: ', e)
#         return False

# def consume_item_from_department(stock_items_to_consume, dept_id):
#     try:
#         with transaction.atomic():
#             for stock_item in stock_items_to_consume:
#                 stock_item_id = stock_item['stock_item_id']
#                 quantity = stock_item['quantity']

#                 department_stock = get_or_create_new_department_stock(stock_item_id, dept_id)
#                 if not department_stock:
#                     raise Exception('Failed to consume department stock')

#                 department_stock.quantity -= quantity
#                 department_stock.save()
#                 print('Consumed item from department', department_stock)
#             # End of for loop
#             return True
#     except Exception as e:
#         print('Error: ', e)
#         return False

# def get_or_create_new_department_stock(stock_item_id,dept_id):
#     try:
#         department_stock = DepartmentStock.objects.get(stock_item=stock_item_id, \
#                                     department=dept_id)
#         return department_stock
#     except Exception as e:
#         print('Error dest dept: ', e)
#         print('creating new department stock with quantity 0')
#         department_stock = create_department_stock(stock_item_id, dept_id)
#         if department_stock:
#             print('Created department stock')
#             return department_stock
#         else:
#             return None

# def create_purchase_order_draft(item_list, supplier_id, dest_department_id):
#     try:
#         with transaction.atomic():
#             purchase_order = PurchaseOrder()
#             purchase_order.placed_date = datetime.datetime.now()
#             purchase_order.status = PURCHASE_ORDER_STATUS[0][0] # Draft

#             purchase_order.supplier = Supplier.objects.get(id=supplier_id)
#             purchase_order.dest_department = Department.objects.get(id=dest_department_id)
#             purchase_order.save()

#             for item in item_list:
#                 if float(item['requested_quantity']) > 0.0:
#                     purchase_order_item = PurchaseOrderItem()
#                     purchase_order_item.purchase_order = purchase_order
#                     purchase_order_item.item = StockItem.objects.get(id=item['stock_item_id'])
#                     purchase_order_item.requested_quantity = item['requested_quantity']
#                     purchase_order_item.requested_unit_price = item['requested_unit_price']
#                     purchase_order_item.save()
#             # End of for loop

#             print('Success create_purchase_order_draft', purchase_order)
#             return True
#     except Exception as e:
#         print('Error in create_purchase_order_draft: ', e)
#         return False

def purchase_order_honoured(purchase_order_id, item_list):
    try:
        with transaction.atomic():
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
            if purchase_order.status == PURCHASE_ORDER_STATUS[1][0]: # Canceled
                print('Purchase order is Canceled')
                return None

            if purchase_order.status == PURCHASE_ORDER_STATUS[3][0]: # Complete
                print('Purchase order is already completed')
                return None

            purchase_order.status = PURCHASE_ORDER_STATUS[3][0] # Complete
            purchase_order.honoured_date_ts = datetime.datetime.now()
            purchase_order.save()

            stock_items_to_add = []
            for item in item_list:
                purchase_order_item = PurchaseOrderItem.objects.get(purchase_order=purchase_order, item=item['stock_item_id'])
                purchase_order_item.received_quantity = item['received_quantity']
                purchase_order_item.received_unit_price = item['received_unit_price']
                purchase_order_item.save()
                stock_items_to_add.append({"stock_item_id": item['stock_item_id'], "quantity": item['received_quantity']})
            # End of for loop

            res = add_item_to_department(stock_items_to_add, purchase_order.dest_department)
            if not res:
                raise Exception('Failed to add stock in department')
            print('Success purchase_order_honoured', purchase_order)
            return True
    except Exception as e:
        print('Error in purchase_order_honoured: ', e)
        return False

def create_stock_transfer_request_draft(source_department_id, dest_department_id, item_list):
    try:
        with transaction.atomic():
            stock_transfer_request = StockTransferRequest()
            stock_transfer_request.placed_date = datetime.datetime.now()
            stock_transfer_request.status = STOCK_TRANSFER_REQUEST_STATUS[0][0] # Draft

            stock_transfer_request.source_department = Department.objects.get(id=source_department_id)
            stock_transfer_request.dest_department = Department.objects.get(id=dest_department_id)
            stock_transfer_request.save()

            for item in item_list:
                if float(item['requested_quantity']) > 0.0:
                    stock_transfer_request_item = StockTransferRequestItem()
                    stock_transfer_request_item.stock_transfer_request = stock_transfer_request
                    stock_transfer_request_item.item = StockItem.objects.get(id=item['stock_item_id'])
                    stock_transfer_request_item.requested_quantity = item['requested_quantity']
                    stock_transfer_request_item.save()
            # End of for loop

            print('Success create_stock_transfer_request_draft', stock_transfer_request_item)
            return True
    except Exception as e:
        print('Error in create_stock_transfer_request_draft: ', e)
        return False

# def stock_transfer_request_honoured(stock_transfer_request_id, item_list):
#     try:
#         with transaction.atomic():
#             stock_transfer_request = StockTransferRequest.objects.get(id=stock_transfer_request_id)
#             if stock_transfer_request.status == STOCK_TRANSFER_REQUEST_STATUS[1][0]: # Canceled
#                 print('Stock transfer request is Canceled')
#                 return None

#             if stock_transfer_request.status == STOCK_TRANSFER_REQUEST_STATUS[2][0]: # Complete
#                 print('Stock transfer request is already completed')
#                 return None

#             stock_transfer_request.status = STOCK_TRANSFER_REQUEST_STATUS[2][0] # Complete
#             stock_transfer_request.honoured_date_ts = datetime.datetime.now()
#             stock_transfer_request.save()

#             stock_items_to_transfer = []
#             for item in item_list:
#                 stock_transfer_request_item = StockTransferRequestItem.objects.get(stock_transfer_request=stock_transfer_request, item=item['stock_item_id'])
#                 stock_transfer_request_item.received_quantity = item['received_quantity']
#                 stock_transfer_request_item.save()
#                 stock_items_to_transfer.append({"stock_item_id": item['stock_item_id'], "quantity": item['received_quantity']})
#             # End of for loop

#             res = transfer_stock_between_departments(stock_transfer_request.source_department.id, stock_transfer_request.dest_department.id, stock_items_to_transfer)
#             if not res:
#                 raise Exception('Failed to transfer stock between department')
#             print('Success stock_transfer_request_honoured', stock_transfer_request)
#             return True
#     except Exception as e:
#         print('Error in stock_transfer_request_honoured: ', e)
#         return False


# ----------------------------------------------------------------------------------------------

# def get_total_quantity(department_stock_item_list):
#     total_quantity = 0
#     for department_stock_item in department_stock_item_list:
#         total_quantity = total_quantity + float(department_stock_item['quantity'])

#     return total_quantity


# def get_total_stock_quantity_from_all_department(request):
#     stock_items = StockItem.objects.all()

#     stock_item_list = []

#     for stock_item in stock_items:
#         stock_item_dict = {}
#         stock_item_dict['stock_name'] = stock_item.name
#         department_stocks = DepartmentStock.objects.filter(stock_item=stock_item)
#         department_stock_item_list = []
#         for department_stock in department_stocks:
#             department_stock_item_list.append({'department': department_stock.department.name, 'quantity': department_stock.quantity})

#         stock_item_dict['department_stock_item_list'] = department_stock_item_list

#         total_quantity = get_total_quantity(department_stock_item_list)

#         stock_item_dict['total_quantity'] = total_quantity

#         stock_item_list.append(stock_item_dict)

#     print(stock_item_list)

#     return stock_item_list


def create_system_checkpoint_for_all_stock_items():
    with transaction.atomic():
        system_checkpoint_ts = SystemStockVerificationCheckpoint.objects.create(checkpoint_ts=datetime.datetime.now())

        department_stocks = DepartmentStock.objects.all()

        for department_stock in department_stocks:
            kwargs = {}
            kwargs['system_stock_verification_checkpoint'] = system_checkpoint_ts
            kwargs['dept_stock'] = department_stock
            kwargs['quantity'] = department_stock.quantity
            kwargs['quantity_unit'] = department_stock.quantity_unit

            try:
                system_stock_verification_checkpoint_item = SystemStockVerificationCheckpointItem.objects.create(**kwargs)
                print(system_stock_verification_checkpoint_item)
            except Exception as e:
                print(e)
                return None


def create_manual_checkpoint_for_stock_item(dept_stock, manual_checkpoint_ts):
    kwargs = {}
    kwargs['manual_stock_verification_checkpoint'] = manual_checkpoint_ts
    kwargs['dept_stock'] = dept_stock
    kwargs['quantity'] = dept_stock.quantity
    kwargs['quantity_unit'] = dept_stock.quantity_unit

    try:
        manual_stock_verification_checkpoint_item = SystemStockVerificationCheckpointItem.objects.create(**kwargs)
        print(manual_stock_verification_checkpoint_item)
    except Exception as e:
        print(e)
        return None


def get_sale_item_tax_amount(stock_item):
    if stock_item.tax_rate:
        return (stock_item.sale_price*stock_item.tax_rate.rate)/100
    else:
        return 0


def get_item_total_amount(stock_item, quantity, item_tax_amount):
    return (stock_item.sale_price * quantity) + item_tax_amount


def create_sale_order_draft(item_list, order_code, from_department_id):
    # try:
    with transaction.atomic():
        sale_order = SaleOrder()
        sale_order.placed_date = datetime.datetime.now()
        sale_order.order_code = order_code
        sale_order.order_type = SALE_ORDER_TYPE[0][0] # Parcel
        sale_order.status = SALE_ORDER_STATUS[0][0] # Draft

        sale_order.from_department = Department.objects.get(id=from_department_id)
        sale_order.save()

        for item in item_list:
            if float(item['quantity']) > 0.0:
                sale_order_item = SaleOrderItem()
                sale_order_item.sale_order = sale_order
                sale_order_item.item = StockItem.objects.get(id=item['stock_item_id'])
                sale_order_item.quantity = item['quantity']
                sale_order_item.unit_price = sale_order_item.item.sale_price
                sale_order_item.item_tax_amount = get_sale_item_tax_amount(sale_order_item.item)

                ## This amount is the total amount of that perticular item in this order
                sale_order_item.item_total_amount = get_item_total_amount(sale_order_item.item, item['quantity'], sale_order_item.item_tax_amount)
                sale_order_item.save()
        # End of for loop

        print('Success sale_order_draft', sale_order)
        return True
    # except Exception as e:
    #     print('Error in create_sale_order_draft: ', e)
    #     return False


def sale_order_honoured(sale_order_id, item_list):
    try:
        with transaction.atomic():
            sale_order = SaleOrder.objects.get(id=sale_order_id)
            if sale_order.status == SALE_ORDER_STATUS[1][0]: # Canceled
                print('Sale order is Canceled')
                return None

            if sale_order.status == SALE_ORDER_STATUS[3][0]: # Complete
                print('Sale order is already completed')
                return None

            sale_order.status = SALE_ORDER_STATUS[3][0] # Complete
            sale_order.honoured_date_ts = datetime.datetime.now()
            sale_order.save()

            stock_items_to_consume = []
            for item in item_list:
                sale_order_item = SaleOrderItem.objects.get(sale_order=sale_order, item=item['stock_item_id'])
                sale_order_item.save()
                stock_items_to_consume.append({"stock_item_id": item['stock_item_id'], "quantity": item['quantity']})
            # End of for loop

            res = consume_item_from_department(stock_items_to_consume, sale_order.from_department)

            if not res:
                raise Exception('Failed to add stock in department')
            print('Success sale_order_honoured', sale_order)
            return True
    except Exception as e:
        print('Error in sale_order_honoured: ', e)
        return False

################################################################################################
################################ Validation Functions ##########################################
################################################################################################


# def validate_stock_item(params):
#     kwargs = {}

#     code = params.get("code")
#     name = params.get("name")
#     regional_name = params.get("regional_name")
#     brand = params.get("brand")
#     sale_price = params.get("sale_price")
#     usage_type = params.get("usage_type")
#     nature = params.get("nature")
#     quantity_unit = params.get("quantity_unit")
#     tax_rate = params.get("tax_rate")
#     description = params.get("description")
#     shelf_life = params.get("shelf_life")
#     notes = params.get("notes")
#     is_active = params.get("is_active")

#     if (not code) or (not name) or (not regional_name):
#         return kwargs, "Invalid data", False

#     if StockItem.objects.filter(code=code).exists():
#         return kwargs, "Stock item code is already exists", False

#     kwargs = {
#                 "code": code,
#                 "name": name,
#                 "regional_name": regional_name,
#                 "brand": brand,
#                 "sale_price": sale_price,
#                 "usage_type": usage_type,
#                 "nature": nature,
#                 "quantity_unit": quantity_unit,
#                 "tax_rate": tax_rate,
#                 "description": description,
#                 "shelf_life": shelf_life,
#                 "notes": notes,
#                 "is_active": is_active
#             }

#     return kwargs, "Stock item saved", True


def validate_sell_order(params):
    order_code = params.get("order_code")
    placed_date = params.get("placed_date")
    order_type = params.get("order_type")
    # status = params.get("status")
    # cancellation_reason = params.get("cancellation_reason")

    stock_item_list = params.get("stock_item_list")

    data = {
            "order_code": order_code,
            "placed_date": convert_epoch_to_date(placed_date),
            "order_type": order_type,
           }

    if len(stock_item_list) < 1:
        return "Add items in order", False

    if not placed_date:
        return "Enter order date", False

    placed_date = convert_epoch_to_date(placed_date)

    return data, "Order Placed Successfully", True
