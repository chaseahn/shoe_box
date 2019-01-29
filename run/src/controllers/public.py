#!/usr/bin/env python3


import os
import json
import codecs
import requests
import time
import random

from bs4 import BeautifulSoup
from selenium import webdriver

from flask import Blueprint,render_template,request,session,redirect,url_for

from ..extentions.loaders import tsplit
from ..models.model import User,ShoeView,ShoeBox

UPLOAD_FOLDER = '/Users/ahn.ch/Projects/shoe_data/run/src/static'

elekid = Blueprint('public',__name__)

path = '/Users/ahn.ch/Projects/shoe_data/run/src/json/total190120.json'

def open_shoe_data(shoe):
    with open(path) as file:
        data = json.load(file)
        for k,v in data.items():
            if data[k]['name'] == shoe:
                shoeData = data[k]
                return shoeData

def get_shoeKey(name):
    with open(path) as file:
        data = json.load(file)
        for key,value in data.items():
            if data[key]['name'] == name:
                return key

def shoeInfo(url):

    try:
        """CONTAINERS"""
        shoe_html = requests.get(url).content
        shoe_soup = BeautifulSoup(shoe_html, 'html.parser')
        shoe_container = shoe_soup.find("div", {"class": "product-view"})
        header_stat = shoe_container.find_all('div', {'class': 'header-stat'})
        """HEADER INFO"""
        name = shoe_container.find('h1').get_text().replace('/','-').strip()
        image = shoe_container.find('div', {'class': 'product-media'}).img['src']
        ticker = header_stat[1].get_text().strip().split(' ')[1]
        """PRODUCT INFO"""
        product_info = shoe_container.find('div', {'class': 'product-info'}).get_text().strip()
        product_data = tsplit(product_info,('Style ',' Colorway ',' Retail Price ',' Release Date '))
        style = product_data[1]
        colorway = product_data[2]
        retail_price = product_data[3]
        release_date = product_data[4][:10]
        description = product_data[4][11:]
        """MARKET INFO"""
        market_summary = shoe_container.find('div', {'class': 'product-market-summary'}).get_text().strip()
        market_data = tsplit(market_summary,('52 Week High ',' | Low ','Trade Range (12 Mos.)','Volatility'))
        year_high = market_data[1]
        year_low = market_data[2]
        trade_range = market_data[3]
        volatility = market_data[4]
        """HISTORICAL"""
        twelve_month_historical = shoe_container.find('div', {'class': 'gauges'}).get_text().strip()
        twelve_data = tsplit(twelve_month_historical,('# of Sales','Price Premium(Over Original Retail Price)','Average Sale Price'))
        total_sales = twelve_data[1]
        price_premium = twelve_data[2]
        avg_sale_price = twelve_data[3]

        newData = { "name" : name.replace('?',''),
                    "url" : url,
                    "image" : image,
                    "ticker" : ticker,
                    "style" : style,
                    "colorway" : colorway,
                    "retail_price" : retail_price,
                    "release_date" : release_date,
                    "year_high" : year_high,
                    "year_low" : year_low,
                    "trade_range" : trade_range,
                    "volatility" : volatility,
                    "total_sales" : total_sales,
                    "price_premium" : price_premium,
                    "avg_sale_price" : avg_sale_price,
                    "description" : description
            }

        return newData

    except AttributeError:
        shoeInfo(url)

def update_shoe(name):
    try:
        with open(path,'r') as f:
            data = json.load(f)
            shoeKey = get_shoeKey(name)
            shoeUrl = data[shoeKey]['url']
            updatedData = shoeInfo(shoeUrl)

            data[shoeKey] = { "name" : updatedData['name'],
                            "url" : updatedData['url'],
                            "image" : updatedData['image'],
                            "ticker" : updatedData['ticker'],
                            "style" : updatedData['style'],
                            "colorway" : updatedData['colorway'],
                            "retail_price" : updatedData['retail_price'],
                            "release_date" : updatedData['release_date'],
                            "year_high" : updatedData['year_high'],
                            "year_low" : updatedData['year_low'],
                            "trade_range" : updatedData['trade_range'],
                            "volatility" : updatedData['volatility'],
                            "total_sales" : updatedData['total_sales'],
                            "price_premium" : updatedData['price_premium'],
                            "avg_sale_price" : updatedData['avg_sale_price'],
                            "description" : updatedData['description']
                    }

        with open(path,'w') as output:
            json.dump(data,output,indent=4,sort_keys=True)

    except TypeError:
        update_shoe(name)

def price_premium(retail,average):
    if retail == '--':
        return None
    else:
        intRetail = retail.strip('$')
        new_intRetail = intRetail.replace(',','')
        final_intRetail = int(new_intRetail)
        intAverage = average.strip('$')
        new_intAverage = intAverage.replace(',','')
        final_intAverage = int(new_intAverage)
        percentage = round((((final_intAverage/final_intRetail)-1)*100),2)
        premium = str(percentage)+str('%')
        return premium

@elekid.route('/id/<shoeName>',methods=['GET','POST'])
def id(shoeName):
    if request.method == 'GET':
        try:
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = open_shoe_data(shoeName)
            premium = price_premium(shoeData['retail_price'],shoeData['avg_sale_price'])
            return render_template('public/shoe_id.html',shoename=shoeName, 
                shoeData=shoeData, message=user.username,premium=premium)
        except KeyError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = open_shoe_data(shoeName)
            premium = price_premium(shoeData['retail_price'],shoeData['avg_sale_price'])
            return render_template('public/shoe_id.html',shoename=shoeName, 
                    shoeData=shoeData,premium=premium)
        except TypeError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = open_shoe_data(shoeName)
            premium = price_premium(shoeData['retail_price'],shoeData['avg_sale_price'])
            return render_template('public/shoe_id.html',shoename=shoeName, 
                    shoeData=shoeData,premium=premium)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Favorite':
            try:
                user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
                shoeData = open_shoe_data(shoeName)
                user.favoriteShoe(shoeName,user.pk)
                premium = price_premium(shoeData['retail_price'],shoeData['avg_sale_price'])
                return render_template('public/shoe_id.html',shoename=shoeName, 
                        shoeData=shoeData,message='shoe saved',premium=premium)
            except KeyError:
                shoeData = open_shoe_data(shoeName)
                premium = price_premium(shoeData['retail_price'],shoeData['avg_sale_price'])
                return render_template('public/shoe_id.html',shoename=shoeName, 
                        shoeData=shoeData,message='Log in to favorite a shoe!',premium=premium)
        elif request.form['post_button'] == 'Add To Shoebox':
            return redirect('/add-buy/'+shoeName)
    else:
        pass

@elekid.route('/add-buy/<shoeName>',methods=['GET','POST'])
def add_buy(shoeName):
    if request.method == 'GET':
        user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
        print(user.pk)
        return render_template('public/add_buy.html',shoeName=shoeName)
    elif request.method == 'POST':
        try:
            shoeName=shoeName
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            type = 'Buy'
            price_bought = request.form['price'].strip('$')
            new_price_bought = float(price_bought.replace(',',''))
            date = request.form['input']
            user.add_to_box(type,shoeName,date,new_price_bought,user.pk)
            return redirect('/add/success')
        except ValueError:
            print('hi')
            return render_template('public/add_buy.html',shoeName=shoeName, message="Enter a number.")
    else:
        pass

@elekid.route('/add-sell/<shoeName>',methods=['GET','POST'])
def add_sell(shoeName):
    shoeName=shoeName
    if request.method == 'GET':
        return render_template('public/add_sell.html',shoeName=shoeName)
    elif request.method == 'POST':
        try:
            type = 'Sell'
            price = int(request.form['price'].strip('$'))
            date = request.form['input']
            

            return render_template('public/add_sell.html',shoeName=shoeName)
        except ValueError:
            return render_template('public/add_sell.html',shoeName=shoeName, message="Enter a number.")
    else:
        pass

@elekid.route('/add/success',methods=['GET','POST'])
def add_success():
    if request.method == 'GET':
        return render_template('public/success_add.html')
    elif request.method == "POST":
        pass
    else:
        pass