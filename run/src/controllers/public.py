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
from ..models.model import User,ShoeView,ShoeBox,Sneaker

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
    """CONTAINERS"""
    shoe_html = requests.get(url).content
    shoe_soup = BeautifulSoup(shoe_html, 'html.parser')
    shoe_container = shoe_soup.find("div", {"class": "product-view"})
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

    newData = { 
                "year_high" : year_high,
                "year_low" : year_low,
                "trade_range" : trade_range,
                "volatility" : volatility,
                "total_sales" : total_sales,
                "price_premium" : price_premium,
                "avg_sale_price" : avg_sale_price
        }

    return newData

def update_shoe(name):
    try:
        sneaker = Sneaker(name=name)
        updatedData = shoeInfo(sneaker.url)
        total_sales = updatedData['total_sales'].replace(',','')

        avgSalePrice = updatedData['avg_sale_price'].strip('$')
        new_avgSalePrice = avgSalePrice.replace(',','')

        yearHigh = updatedData['year_high'].strip('$')
        new_yearHigh = yearHigh.replace(',','')

        yearLow = updatedData['year_low'].strip('$')
        new_yearLow = yearLow.replace(',','')

        premium = price_premium(sneaker.retail_price,new_avgSalePrice)

        sneaker.brand	       = sneaker.brand	
        sneaker.name           = sneaker.name
        sneaker.colorway       = sneaker.colorway 	
        sneaker.description    = sneaker.description 
        sneaker.image          = sneaker.image  
        sneaker.release_date   = sneaker.release_date 
        sneaker.retail_price   = sneaker.retail_price
        sneaker.style          = sneaker.style 
        sneaker.ticker         = sneaker.ticker 
        sneaker.total_sales    = total_sales
        sneaker.url            = sneaker.url 
        sneaker.year_high      = new_yearHigh 
        sneaker.year_low       = new_yearLow 
        sneaker.avg_sale_price = new_avgSalePrice
        sneaker.premium        = premium
        sneaker.save(name)
    except AttributeError:
        update_shoe(name)

def price_premium(retail,average):
    if retail == '--' or average == '--':
        return None
    else:
        premium = round((((int(average)/int(retail))-1)*100),2)
        return premium

@elekid.route('/id/<shoeName>',methods=['GET','POST'])
def id(shoeName):
    if request.method == 'GET':
        #Works if user is logged in
        try:
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = Sneaker(name=shoeName)
            print(shoeData)
            premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            return render_template('public/shoe_id.html',shoename=shoeName, 
                shoeData=shoeData, message=user.username,premium=premium)
        #Will load when user is not logged in
        except KeyError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = Sneaker(name=shoeName)
            premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            return render_template('public/shoe_id.html',shoename=shoeName, 
                    shoeData=shoeData,premium=premium)
        except TypeError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = Sneaker(name=shoeName)
            print(shoeData)
            premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            return render_template('public/shoe_id.html',shoename=shoeName, 
                    shoeData=shoeData,premium=premium)
        except AttributeError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = Sneaker(name=shoeName)
            premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            return render_template('public/shoe_id.html',shoename=shoeName, 
                    shoeData=shoeData,premium=premium)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Favorite':
            try:
                user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
                shoeData = Sneaker(name=shoeName)
                user.favoriteShoe(shoeName,user.pk)
                premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
                return render_template('public/shoe_id.html',shoename=shoeName, 
                        shoeData=shoeData,message='shoe saved',premium=premium)
            except KeyError:
                shoeData = Sneaker(name=shoeName)
                premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
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
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            type = 'Buy'
            price_bought = request.form['price'].strip('$')
            new_price_bought = float(price_bought.replace(',',''))
            date = request.form['input']
            user.add_to_box(type,shoeName,date,new_price_bought,user.pk)
            return redirect('/add/success')
        except ValueError:
            return render_template('public/add_buy.html',shoeName=shoeName, message="Enter a number.")
    else:
        pass

@elekid.route('/add-sell/<shoeName>',methods=['GET','POST'])
def add_sell(shoeName):
    shoeName=shoeName
    if request.method == 'GET':
        user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
        return render_template('public/add_sell.html',shoeName=shoeName)
    elif request.method == 'POST':
        try:
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            type = 'Sell'
            price_bought = request.form['price_bought'].strip('$')
            new_price_bought = float(price_bought.replace(',',''))
            price_sold = request.form['price_sold'].strip('$')
            new_price_sold = float(price_sold.replace(',',''))
            date = request.form['input']
            user.add_to_box(type,shoeName,date,new_price_bought,user.pk,new_price_sold)
            return redirect('/add/success')
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