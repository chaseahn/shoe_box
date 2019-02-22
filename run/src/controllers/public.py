#!/usr/bin/env python3


import os
import json
import codecs
import requests
import time
import random
import cv2
import tensorflow as tf

from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from werkzeug.utils import secure_filename


from flask import Blueprint,render_template,request,session,redirect,url_for

from ..extentions.loaders import tsplit, shoes_like_list
from ..models.model import User,ShoeView,ShoeBox,Sneaker

UPLOAD_FOLDER = '/Users/ahn.ch/Projects/shoe_data/run/src/static'


elekid = Blueprint('public',__name__)

path = '/Users/ahn.ch/Projects/shoe_data/run/src/json/total190120.json'


def get_current_date():
    ts = time.time() 
    new_time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    date = new_time.split(' ')[0]
    return date

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

"""BS4 CHECKS CURRENT INFO"""
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


"""BS4 SCRAPER"""
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

        sneaker.brand	          = sneaker.brand	
        sneaker.type              = sneaker.type
        sneaker.name              = sneaker.name
        sneaker.colorway          = sneaker.colorway 	
        sneaker.image             = sneaker.image  
        sneaker.image_placeholder = sneaker.image_placeholder
        sneaker.release_date      = sneaker.release_date 
        sneaker.retail_price      = sneaker.retail_price
        sneaker.ticker            = sneaker.ticker 
        sneaker.total_sales       = total_sales
        sneaker.url               = sneaker.url 
        sneaker.year_high         = new_yearHigh 
        sneaker.year_low          = new_yearLow 
        sneaker.avg_sale_price    = new_avgSalePrice
        sneaker.premium           = premium
        sneaker.save(name)
    except AttributeError:
        update_shoe(name)

def price_premium(retail,average):
    if retail == '--' or average == '--':
        return None
    else:
        fltRetail = float(retail)
        fltAvg    = float(average)
        difference = fltAvg - fltRetail
        value = difference/fltRetail
        premium = '{:.2f}'.format(value*100)
        return premium

@elekid.route('/id/<shoeName>',methods=['GET','POST'])
def id(shoeName):
    if request.method == 'GET':
        """WORKS WHEN LOGGED IN ONLY"""
        try:
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            shoe = ShoeView(shoename=shoeName)
            
            """ 
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            UPDATE SHOE WITH NEW INFO WHEN OPENED
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            """ 
            
            shoe.save(shoeName)
            update_shoe(shoeName)

            shoeData  = Sneaker(name=shoeName)
            premium   = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            likeShoes = shoes_like_list(shoeName)

            return render_template('public/shoe_id.html',
                                    shoename  = shoeName, 
                                    shoeData  = shoeData, 
                                    message   = user.username,
                                    premium   = premium, 
                                    likeShoes = likeShoes)
        #Will load when user is not logged in
        except KeyError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = Sneaker(name=shoeName)
            premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            likeShoes = shoes_like_list(shoeName)
            return render_template('public/shoe_id.html',
                                    shoename  = shoeName, 
                                    shoeData  = shoeData,
                                    premium   = premium, 
                                    likeShoes = likeShoes)
        except TypeError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = Sneaker(name=shoeName)
            likeShoes = shoes_like_list(shoeName)
            premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            return render_template('public/shoe_id.html',
                                    shoename  = shoeName, 
                                    shoeData  = shoeData,
                                    premium   = premium, 
                                    likeShoes = likeShoes)
        except AttributeError:
            shoe = ShoeView(shoename=shoeName)
            shoe.save(shoeName)
            update_shoe(shoeName)
            shoeData = Sneaker(name=shoeName)
            premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
            likeShoes = shoes_like_list(shoeName)
            return render_template('public/shoe_id.html',shoename=shoeName, 
                    shoeData=shoeData,premium=premium, likeShoes=likeShoes)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Favorite':
            try:
                user = User({'username': session['username'], 
                             'pk': session['pk'], 'age': session['age'], 
                             'gender': session['gender']})
                shoeData = Sneaker(name=shoeName)
                user.favoriteShoe(shoeName,user.pk)
                premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
                likeShoes = shoes_like_list(shoeName)
                return render_template('public/shoe_id.html',
                                        shoename  = shoeName, 
                                        shoeData  = shoeData,
                                        message   = 'This Shoe Has Been Added To Your Account!',
                                        premium   = premium, 
                                        likeShoes = likeShoes)
            except KeyError:
                shoeData = Sneaker(name=shoeName)
                premium = price_premium(shoeData.retail_price,shoeData.avg_sale_price)
                return render_template('public/shoe_id.html',
                                        shoename = shoeName, 
                                        shoeData = shoeData,
                                        message  = 'Log in to favorite a shoe!',
                                        premium  = premium)
        elif request.form['post_button'] == 'Add To Shoebox':
            return redirect('/add-buy/'+shoeName)
    else:
        pass

@elekid.route('/add-buy/<shoeName>',methods=['GET','POST'])
def add_buy(shoeName):
    if request.method == 'GET':
        user = User({'username': session['username'], 'pk': session['pk'], 
                     'age': session['age'], 'gender': session['gender']})
        print(user.pk)
        return render_template('public/add_buy.html',shoeName=shoeName)
    elif request.method == 'POST':
        try:
            user = User({'username': session['username'], 'pk': session['pk'], 
                         'age': session['age'], 'gender': session['gender']})
            type = 'Buy'
            price_bought = request.form['price'].strip('$')
            new_price = float(price_bought.replace(',',''))
            date = get_current_date()
            profit = 0
            user.add_to_box(type,shoeName,date,new_price,profit,user.pk)
            return redirect('/add/success')
        except ValueError:
            return render_template('public/add_buy.html',shoeName=shoeName, 
                                   message="Enter a number.")
    else:
        pass

@elekid.route('/add-sell/<shoeName>',methods=['GET','POST'])
def add_sell(shoeName):
    shoeName=shoeName
    if request.method == 'GET':
        user = User({'username': session['username'], 'pk': session['pk'], 
                     'age': session['age'], 'gender': session['gender']})
        return render_template('public/add_sell.html',shoeName=shoeName)
    elif request.method == 'POST':
        try:
            sneaker = Sneaker(name=shoeName)
            user = User({'username': session['username'], 'pk': session['pk'], 
                         'age': session['age'], 'gender': session['gender']})

            type = 'Sell'

            """ vv CLEAN USER INPUT vv """

            price_bought = request.form['price_bought'].strip('$')
            new_price_bought = price_bought.replace(',','')
            new_price_bought = float(new_price_bought)

            price_sold = request.form['price_sold'].strip('$')
            new_price_sold = float(price_sold.replace(',',''))

            profit = new_price_sold - new_price_bought
            print(sneaker.retail_price)

            date = get_current_date()
            user.add_to_box(type,shoeName,date,new_price_bought,profit,user.pk, new_price_sold)
            return redirect('/add/success')
        except ValueError:
            return render_template('public/add_sell.html',shoeName=shoeName, message="Enter a number.")
    else:
        pass

@elekid.route('/update-box/<box_pk>/<shoeName>',methods=['GET','POST'])
def update_box(shoeName,box_pk):
    shoeName=shoeName
    if request.method == 'GET':
        user = User({'username': session['username'], 'pk': session['pk'], 
                     'age': session['age'], 'gender': session['gender']})
        return render_template('public/update-box.html',shoeName=shoeName, box_pk=box_pk)
    elif request.method == 'POST':
        try:
            box = ShoeBox(pk=box_pk)
            user = User({'username': session['username'], 'pk': session['pk'], 
                         'age': session['age'], 'gender': session['gender']})

            price_bought = request.form['price_bought'].strip('$')
            new_price_bought = price_bought.replace(',','')
            new_price_bought = float(new_price_bought)

            price_sold = request.form['price_sold'].strip('$')
            new_price_sold = float(price_sold.replace(',',''))
            type = box.type
            profit = new_price_sold - new_price_bought
            user.update_shoebox(box_pk, type, price_bought, price_sold, profit, user.pk)
            return redirect('/add/success')
        except ValueError:
            return render_template('public/add_sell.html',shoeName=shoeName, 
                                    box_pk=box_pk, message="Enter a number.")
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

# @elekid.route('/finder',methods=['GET','POST'])
# def finder():
#     if request.method == 'GET':

#         return render_template('public/finder.html')
#     elif request.method == "POST":

#         if request.form['post_button'] == 'Submit':

#             file = request.files['file']
#             print(file)
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(electabuzz.config['UPLOAD_FOLDER'+'/user_inputs'], filename))

#                 model = tf.keras.models.load_model("/Users/ahn.ch/Projects/shoe_data/run/src/32x3-CNN.model")
#                 prediction = model.predict([prepare('/Users/ahn.ch/Projects/shoe_data/run/src/static/{}'.format(filename))])
#                 brand = CATEGORIES[int(prediction[0][0])]
#                 print(brand)

#             price_min = request.form['min'].strip('$')
#             price_max = request.form['max'].strip('$')

#             int_min = int(price_min)
#             int_max = int(price_max)

#             premium  = request.form.get('premium')
#             value = request.form.get('value')

#             black  = request.form.get('black')
#             white  = request.form.get('white')
#             red    = request.form.get('red')
#             orange = request.form.get('orange')
#             yellow = request.form.get('yellow')
#             green  = request.form.get('green')
#             blue   = request.form.get('blue')
#             purple = request.form.get('purple')

#             colorList = [black,white,red,orange,yellow,green,blue,purple]
#             valueList = [premium,value]

#             l = len(colorList)
#             for x in range(l-1,-1,-1):
#                 if colorList[x] is None:
#                     colorList.pop(x)
            
#             l = len(valueList)
#             for x in range(l-1,-1,-1):
#                 if valueList[x] is None:
#                     valueList.pop(x)

#             print(colorList)
#             print(valueList)

#             brand = 'Nike'

#             sneaker = Sneaker()

#             shoeList = sneaker.finder(int_min, int_max, brand, valueList, colorList)

#             shoeData = {}
#             for shoe in shoeList:
#                 s = Sneaker(name=shoe)
#                 shoeData[shoe] = {
#                     'value': s.avg_sale_price,
#                     'premium': s.premium
#                 }
                
#             print(shoeData)

#             return render_template('public/found_shoes.html', shoeList=shoeList, shoeData=shoeData)
#         else:
#             image_button = request.form['post_button']
#             print(image_button)

#             price_min = request.form['min'].strip('$')
#             price_max = request.form['max'].strip('$')

#             int_min = int(price_min)
#             int_max = int(price_max)

#             premium  = request.form.get('premium')
#             value = request.form.get('value')

#             black  = request.form.get('black')
#             white  = request.form.get('white')
#             red    = request.form.get('red')
#             orange = request.form.get('orange')
#             yellow = request.form.get('yellow')
#             green  = request.form.get('green')
#             blue   = request.form.get('blue')
#             purple = request.form.get('purple')

#             colorList = [black,white,red,orange,yellow,green,blue,purple]
#             valueList = [premium,value]

#             l = len(colorList)
#             for x in range(l-1,-1,-1):
#                 if colorList[x] is None:
#                     colorList.pop(x)
            
#             l = len(valueList)
#             for x in range(l-1,-1,-1):
#                 if valueList[x] is None:
#                     valueList.pop(x)

#             print(colorList)
#             print(valueList)

#             brand = 'Nike'

#             sneaker = Sneaker()

#             shoeList = sneaker.finder(int_min, int_max, brand, valueList, colorList)

#             shoeData = {}
#             for shoe in shoeList:
#                 s = Sneaker(name=shoe)
#                 shoeData[shoe] = {
#                     'value': s.avg_sale_price,
#                     'premium': s.premium
#                 }
#             print(shoeData)

#             return render_template('public/found_shoes.html', shoeList=shoeList, shoeData=shoeData)
#     else:
#         pass