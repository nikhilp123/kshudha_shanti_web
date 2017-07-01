import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db.models import Q
from .models import StockItem
from department.models import Department
from .my_views import  validate_stock_item
from helper_functions import get_params
from asset.helper_functions import get_usage_type_id

# Create your views here.


'''
    NAME: get_all_stock_items

    expected inputs:
    usage_types = "USAGE_TYPE_1, USAGE_TYPE_2"

    Workflow: This function takes an usage_types input which will be a comma separated string,
    each element considered as usage type of stock item. Function will return all the stock items,
    which are active and usage_types is same as any of input usage_types.
'''
# def get_all_stock_items(request):
#     try:
#         params = get_params(request)
#         usage_types = params.get('usage_types')
#         print("usage_types: ",usage_types)
#         stock_item_list = []
#     except Exception as e:
#         print(e)
#         return JsonResponse({"validation": "Inconsistent data" , "status": True})

#     # usage_types = usage_types.split(',')

#     # usage_types = get_usage_type_id(usage_types)

#     kwargs = {}
#     kwargs["is_active"] = True
#     kwargs["usage_type__in"] = usage_types

#     stock_items = StockItem.objects.filter(**kwargs)

#     for stock_item in stock_items:
#         stock_item_list.append(stock_item.get_json())

#     return JsonResponse({"data": stock_item_list, "status": True})


# def save_stock_item(request):
#     params = get_params(request)

#     data, message, status = validate_stock_item(params)

#     if status:
#         try:
#             stock_item = StockItem.objects.create(**data)
#             return JsonResponse({"validation": message, "status": status})
#         except Exception as e:
#             print(e)
#             return JsonResponse({"validation": "Inconsistent data: "+e , "status": True})
#     else:
#         return JsonResponse({"validation": message, "status": status})


def save_sell_order(request):
    params = get_params(request)

    data, message, status = validate_sell_order(params)

    if not status:
        return JsonResponse({"validation": message, "status": status})

    stock_item_list = params.get("stock_item_list")

    with transaction.atomic():
        try:
            sell_order = SaleOrder.objects.create(**data)
        except Exception as e:
            print(e)
            return JsonResponse({"validation": "Unable to create order" , "status": False})

        order_amount = 0
        order_tax_amount = 0

        for stock_item_dict in stock_item_list:
            try:
                stock_item = StockItem.objects.get(id=stock_item_dict['stock_item_id'])
            except Exception as e:
                print(e)
                return JsonResponse({"validation": "Item not in stock" , "status": False})

            sell_item_tax_amount = get_sell_item_tax_amount(stock_item)

            ## This amount is the total amount of that perticular item in this order
            item_total_amount = (stock_item.sale_price * stock_item_dict['quantity']) + sell_item_tax_amount

            try:
                sale_order_item = SaleOrderItem.objects.create(sale_order=sell_order,
                                                               item=stock_item,
                                                               quantity=stock_item_dict['quantity'],
                                                               unit_price=stock_item.sale_price,
                                                               item_tax_amount=sell_item_tax_amount,
                                                               item_total_amount=item_total_amount,
                                                               )
            except Exception as e:
                print(e)
                return JsonResponse({"validation": "Inconsistent data" , "status": False})

            order_amount = order_amount + item_total_amount
            order_tax_amount = order_tax_amount + sell_item_tax_amount

        sell_order.total_amount = order_amount
        sell_order.total_tax_amount = sell_item_tax_amount
        sell_order.save()

    return JsonResponse({"validation": message , "status": status})

