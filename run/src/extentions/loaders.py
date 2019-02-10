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
from random import shuffle

from ..models.model import Sneaker

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
    sneaker = Sneaker()
    colorlist = sneaker.get_color_list()

def shoes_like_list(shoename):
    sneaker = Sneaker()
    shoe_list = sneaker.get_shoes('all')
    like_list_major, like_list_minor = [], []
    for shoe in shoe_list: 
        ignoreList = [ 'of', 'a', 'the', 'air', 'nike', 'adidas', 'jordan', 'red', 'white', 'black', 'green', 'blue', 'pink', 'gum', 'yellow' ]
        searchShoe = shoename.lower().split(' ')
        likeShoe = shoe.lower().split(' ')
        x = 0
        lessSpecific = True
        for terms in searchShoe:
            if terms in ignoreList:
                pass
            elif terms in likeShoe:
                x += 1
            else:
                pass
        if x >= 4:
            lessSpecific = False
            like_list_major.append(shoe)
        if 1 < x < 4:
            like_list_minor.append(shoe)

    if lessSpecific: 
        shuffle(like_list_minor)
        return like_list_minor[:4]
    else: 
        shuffle(like_list_major)
        return like_list_major[:4]


def search_terms(string,brand):
    relevanceListofOne, relevanceListofMany = [], []
    sneaker = Sneaker() 
    shoes = sneaker.get_shoes(brand)
    single = True
    for shoe in shoes:
        ignoreList = [ 'of', 'a', 'the', 'adidas', 'nike', 'jordan' ]
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
        elif x > 1:
            single = False
            relevanceListofMany.append((shoe,x))
        else:
            relevanceListofOne.append((shoe,x))
    
    if single:
        relevanceListofOne = [relevant[0] for relevant in relevanceListofOne]
        return relevanceListofOne
    else:
        relevanceListofMany = sorted(relevanceListofMany, key=lambda x:x[1])[::-1]
        relevanceListofMany = [relevant[0] for relevant in relevanceListofMany]
        return relevanceListofMany

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

def display_rand_shoes(brand,num):

    sneaker = Sneaker() 
    shoe_list = sneaker.get_shoes(brand)
    shuffle(shoe_list)
    return shoe_list[:int(num)]
    

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

