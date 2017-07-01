import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db.models import Q
from .models import Department
from helper_functions import get_params

# Create your views here.

def get_all_departments(request):

    department_list = []

    for dept in Department.objects.all():
        department_list.append(dept.get_json())
    return JsonResponse({"data": department_list, "status": True})

