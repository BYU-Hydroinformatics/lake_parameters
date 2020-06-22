from django.shortcuts import render
from django.shortcuts import reverse
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import MapView, Button
from tethys_sdk.gizmos import TimeSeries
from django.http import HttpResponse, JsonResponse
import datetime

from csv import writer as csv_writer
import plotly.graph_objs as go
import requests
import numpy as np
import pandas as pd
import io
import os
import math
from .app import Lake as app
from pandas import DataFrame


@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    app_workspace = app.get_app_workspace()
    file_path = os.path.join(app_workspace.path,"awqms_lake.csv")
    dataLake = pd.read_csv(file_path)
    dataJson = dataLake.to_dict()

    lake_map = MapView(
        height='100%',
        width='100%',
        layers=[],
        basemap='OpenStreetMap',
    )

    context = {
        'lake_map': lake_map,
        'jsonLake':dataJson
    }

    return render(request, 'lake/home.html', context)

@login_required()
def add_data(request):
    """
    Controller for the Search Data page.
    """
    lake_map = MapView(
        height='100%',
        width='100%',
        layers=[],
        basemap='OpenStreetMap',
    )

    context = {
        'lake_map': lake_map,
    }
    return render(request, 'lake/add_data.html', context)

@login_required()
def instructions(request):
    """
    Controller for the Instructions page.
    """

    context = {
    }

    return render(request, 'lake/instructions.html', context)


def getData(characteristic):
    app_workspace = app.get_app_workspace()
    file_path = os.path.join(app_workspace.path, "awqms_lake.csv")
    dataLake = pd.read_csv(file_path)
    param = dataLake['Characteristic Name'] == characteristic
    row = dataLake[param]
    locations = dataLake['Monitoring Location ID'].unique()
    locations.sort()
    context = {}
    context['characteristic'] = characteristic
    context['csvLake'] = dataLake
    lake_map = MapView(
        height='100%',
        width='100%',
        layers=[],
        basemap='OpenStreetMap',
    )
    context['lake_map'] = lake_map
    context['all_data'] = {}
    for location in locations:
        df = dataLake[dataLake['Monitoring Location ID'] == location]
        if len(df) > 0:
            lat = df['Monitoring Location Latitude'].tolist()[0]
            lon = df['Monitoring Location Longitude'].tolist()[0]
            unit = df['Result Unit'].tolist()[0]
            dataname = str(location)
            charac_id = row['Monitoring Location ID'] == location
            charac = row[charac_id]
            value = charac['Result Value']
            date = charac['Activity Start Date']
            valuesNumpy = value.to_numpy()
            valuesNoNan = np.nan_to_num(valuesNumpy)
            valuesFin = valuesNoNan.tolist()
            # sacar el 1
            responseObject = {}
            responseObject['values'] = valuesFin
            responseObject['dates'] = date.to_numpy().tolist()


            context['all_data'][dataname] = {'coords': [lat, lon], 'unit': unit, 'data': responseObject}
    return context



def chl_a(request):
    context = getData('Chlorophyll a, uncorrected for pheophytin')
    #print(context)
    return render(request, 'lake/show_data.html', context)

def do(request):
    context = getData('Dissolved oxygen (DO)')
    return render(request, 'lake/show_data.html', context)

def nit(request):
    context = getData('Nitrogen')
    return render(request, 'lake/show_data.html', context)

def ph(request):
    context = getData('pH')
    return render(request, 'lake/show_data.html', context)

def phosp(request):
    context = getData('Phosphate-phosphorus')
    return render(request, 'lake/show_data.html', context)

def water_temp(request):
    context = getData('Temperature, water')
    return render(request, 'lake/show_data.html', context)

def tds(request):
    context = getData('Total dissolved solids')
    return render(request, 'lake/show_data.html', context)

def turb(request):
    context = getData('Turbidity')
    return render(request, 'lake/show_data.html', context)

def secchi(request):
    context = getData('Depth, Secchi disk depth')
    return render(request, 'lake/show_data.html', context)
