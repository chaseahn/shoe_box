#!/usr/bin/env python3

import json
import random 
import time
import datetime
import codecs
import requests
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from random import randint

from ..mappers.opencursor import OpenCursor

path = 'run/src/json/total190120.json'

def tsplit(string, delimiters):
    """Behaves str.split but supports multiple delimiters."""
    
    delimiters = tuple(delimiters)
    stack = [string,]
    
    for delimiter in delimiters:
        for i, substring in enumerate(stack):
            substack = substring.split(delimiter)
            stack.pop(i)
            for j, _substring in enumerate(substack):
                stack.insert(i+j, _substring)
            
    return stack

def color_list():
    with open(path) as file:
        data = json.load(file)
        color_list = []
        for key,value in data.items():
            colorway = data[key]['colorway']
            colors = colorway.split('/')
            for color in colors:
                if color not in color_list:
                    color_list.append(color)
                else:
                    pass
        print(color_list)
        return color_list

def search_terms(string,brand):
    relevanceList = []
    shoes = get_shoes(brand)
    for shoe in shoes:
        ignoreList = [ 'of', 'a', 'the' ]
        searchTerms = string.lower().split(' ')
        searchFor = shoe.lower().split(' ')
        x = 0
        for terms in searchTerms:
            if terms in ignoreList:
                pass
            elif terms in searchFor:
                    x += 1
            else:
                pass
        if x == 0:
            pass
        else:
            relevanceList.append((shoe,x))

    relevanceList = sorted(relevanceList, key=lambda x:x[1])[::-1]
    relevanceList = [relevant[0] for relevant in relevanceList]
        
    return relevanceList

def date_to_unix(date):
    split = date.split("-")
    year,month,day = split[0],split[1],split[2]
    s = day+'/'+month+'/'+year
    time = datetime.datetime.strptime(s, "%d/%m/%Y").timestamp()
    return time
    
def brander(brand):
    if brand.upper() == 'nike'.upper():
        return 'nke'
    elif brand.upper() == 'adidas'.upper():
        return 'ads'
    elif brand.upper() == 'jordan'.upper():
        return 'jrd'
    elif brand.upper() == 'other'.upper():
        return 'otb'
    elif brand.upper() == 'all'.upper():
        return 'all'
    else:
        print('Brand not recognized. Try searching "Others"?')
        return False

#TODO WORKS BUT ADD ALL FUNCTION
def get_shoes(brand):
    """ create list of specific brand """
    brand_name = brander(brand)
    if brand_name == 'all':
        with open(path) as file:
            data = json.load(file)
            shoes = []
            for key,value in data.items():
                shoes.append((data[key]['name']))
            return shoes
    else:
        with open(path) as file:
            data = json.load(file)
            shoes = []
            for key,value in data.items():
                if key.split('-')[0] == brand_name:
                    shoes.append((data[key]['name']))
                else:
                    pass
            return shoes

def display_shoes(val,brand,disp_num):
    """ 
    disp_num = 50,100,200
    vals are sorting options
    1) Default-Random 2) Most sales 3) avgsale (inv) 4) release date high & low
    """
    #GENERATE BRAND LIST OF ALL SHOES
    shoe_list = get_shoes(brand)
    
    if val == None:
        rand_shoe_list = []
        x = 0
        while x < int(disp_num):
            i = random.randint(1,len(shoe_list))
            try:
                if shoe_list[i] not in rand_shoe_list:
                    rand_shoe_list.append(shoe_list[i])
                    x += 1
                else:
                    pass
            except IndexError:
                pass
        """ GENERATE RANDOM LIST OF SHOE NAMES """
        return rand_shoe_list
    elif val == 'total_sales_high':
        brand_name = brander(brand)
        with open(path) as file:
            data = json.load(file)
            sales_list = []
            for key,value in data.items():
                if key.split('-')[0] == brand_name:
                    if data[key]['total_sales'] == '--':
                        sales_list.append((key,int('0')))
                    else:
                        sales_list.append((key,int(data[key]['total_sales'])))
            ordered_list = sorted(sales_list, key=lambda x:x[1])
            osl_r = ordered_list[::-1]
            x = 0
            display_list = []
            while x < int(disp_num):
                key = osl_r[x][0]
                display_list.append(data[key]['name'])
                x+=1
            return display_list
    elif val == 'total_sales_low':
        brand_name = brander(brand)
        with open(path) as file:
            data = json.load(file)
            sales_list = []
            for key,value in data.items():
                if key.split('-')[0] == brand_name:
                    if data[key]['total_sales'] == '--':
                        pass
                    else:
                        sales_list.append((key,int(data[key]['total_sales'])))
            ordered_list = sorted(sales_list, key=lambda x:x[1])
            x = 0
            display_list = []
            while x < int(disp_num):
                key = ordered_list[x][0]
                display_list.append(data[key]['name'])
                x+=1
            return display_list
    elif val == 'avg_sale_price_high':
        brand_name = brander(brand)
        with open(path) as file:
            data = json.load(file)
            sales_list = []
            for key,value in data.items():
                if key.split('-')[0] == brand_name:
                    if data[key]['avg_sale_price'] == '--':
                        sales_list.append((key,int('0')))
                    else:
                        price = data[key]['avg_sale_price'].replace(',','').split('$')[1]
                        sales_list.append((key,int(price)))
            ordered_list = sorted(sales_list, key=lambda x:x[1])
            osl_r = ordered_list[::-1]
            x = 0
            display_list = []
            while x < int(disp_num):
                key = osl_r[x][0]
                display_list.append(data[key]['name'])
                x+=1
            return display_list
    elif val == 'release_date_high':
        brand_name = brander(brand)
        with open(path) as file:
            data = json.load(file)
            sales_list = []
            for key,value in data.items():
                if key.split('-')[0] == brand_name:
                    if data[key]['release_date'] == '--':
                        sales_list.append((key,'NO DATE'))
                    else:
                        time = date_to_unix(data[key]['release_date'].strip())
                        sales_list.append((key,time))
            ordered_list = sorted(sales_list, key=lambda x:x[1])
            osl_r = ordered_list[::-1]
            x = 0
            display_list = []
            while x < int(disp_num):
                key = osl_r[x][0]
                display_list.append(data[key]['name'])
                x+=1
            return display_list
    elif val == 'avg_sale_price_low':
        brand_name = brander(brand)
        with open(path) as file:
            data = json.load(file)
            sales_list = []
            for key,value in data.items():
                if key.split('-')[0] == brand_name:
                    if data[key]['avg_sale_price'] == '--':
                        pass
                    else:
                        price = data[key]['avg_sale_price'].replace(',','').split('$')[1]
                        sales_list.append((key,int(price)))
            ordered_list = sorted(sales_list, key=lambda x:x[1])
            x = 0
            display_list = []
            while x < int(disp_num):
                key = ordered_list[x][0]
                display_list.append(data[key]['name'])
                x+=1
            return display_list
    elif val == 'release_date_low':
        brand_name = brander(brand)
        with open(path) as file:
            data = json.load(file)
            sales_list = []    
            for key,value in data.items():
                if key.split('-')[0] == brand_name:
                    if data[key]['release_date'] == '--':
                        sales_list.append((key,'NO DATE'))
                    else:
                        time = date_to_unix(data[key]['release_date'].strip())
                        sales_list.append((key,time))
            ordered_list = sorted(sales_list, key=lambda x:x[1])

            x = 0
            display_list = []
            while x < int(disp_num):
                key = ordered_list[x][0]
                display_list.append(data[key]['name'])
                x+=1
            return display_list
    else:
        pass

def shoeValues(list,val,par):
    
    with open(path) as file:
        data = json.load(file)
        val_list = []

        if val == 'avg_sale_price':

            for key,value in data.items():
                for name in list:
                    if data[key]['name'] == name:
                        price = data[key]['avg_sale_price'].replace(',','').split('$')[1]
                        val_list.append(int(price))
        sortedValues = sorted(val_list)
        if par == 'h':
            val_list = sortedValues[::-1]
            return val_list
        else:
            return val_list

