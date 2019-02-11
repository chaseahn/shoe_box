#!/usr/bin/env python3


import os
import time
import sqlite3

from flask import Flask, render_template, request, url_for, redirect,session
from datetime import datetime
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.utils import secure_filename

from .controllers.public  import elekid as public_buzz
from .controllers.private import elekid as private_buzz
from .models.model import User,ShoeView,Sneaker

from .extentions.loaders import display_rand_shoes,date_to_unix,brander,shoeValues,search_terms,color_list

UPLOAD_FOLDER = '/Users/ahn.ch/Projects/shoe_data/run/src/static'

electabuzz = Flask(__name__)

electabuzz.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
electabuzz.secret_key = 'SUPER-DUPER-SECRET'

electabuzz.register_blueprint(public_buzz)
electabuzz.register_blueprint(private_buzz)

def get_current_date():
    ts = time.time() 
    time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    date = time.split(' ')[0]
    return date

def ages():
    age = []
    for x in range(18,80):
        age.append(x)
    return age

def disp_nums():
    nums = ['All',24,48,96,192,384]
    return nums

def disp_vals():
    vals = ['None', 'Valuable ↑','Valuable ↓', 'Price ↑', 'Price ↓', 'Sales ↑','Sales ↓']
    return vals

@electabuzz.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        view = ShoeView()
        trendList = view.trending_list()
        sneaker = Sneaker()
        sneakerNum = sneaker.get_total_sneakers()
        sneakerSales = sneaker.get_total_sales()
        sneakerValue = sneaker.get_total_value()
        return render_template('public/index.html',trendList=trendList, num=sneakerNum, sale=sneakerSales, value=sneakerValue)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Login':
            try:
                with User(username=request.form['username'],password=request.form['password']) as un:
                    if un.login(request.form['password']):
                        session['username'] = un.username
                        session['pk']       = un.pk
                        session['age']      = un.age
                        session['gender']   = un.gender
                        return redirect('2492/account')
                    else:
                        return redirect('/',message='Bad Credentials')
            except TypeError:
                return render_template('public/index.html',message='Bad Credentials')
        else:
            search_terms = request.form['post_button']
            return redirect('/search/'+search_terms)
    else:
        pass

@electabuzz.route('/logout',methods=['GET','POST'])
def logout():
    if request.method == 'GET':
        session.clear()
        view = ShoeView()
        trendList = view.trending_list()
        return render_template('public/index.html',trendList=trendList,message='Logged out.')
    elif request.method == 'POST':
        if request.form['post_button'] == 'Register':
            return redirect('/register')
        elif request.form['post_button'] == 'Login':
            try:
                with User(username=request.form['username'],password=request.form['password']) as un:
                    if un.login(request.form['password']):
                        session['username'] = un.username
                        session['pk']       = un.pk
                        session['age']      = un.age
                        session['gender']   = un.gender
                        return redirect('2492/account')
                    else:
                        return redirect('/',message='Bad Credentials')
            except TypeError:
                return render_template('public/index.html',message='Bad Credentials')
    else:
        pass

@electabuzz.route('/nke',methods=['GET','POST'])
def nike():
    brand = 'Nike'
    if request.method == 'GET':
        sneaker = Sneaker()
        shoe_list = display_rand_shoes(brand,24)
        display_nums = disp_nums()
        display_vals = disp_vals()
        type_list = sneaker.get_types(brand)
        return render_template('public/nike.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Filter':
            sneaker = Sneaker()

            display_vals = disp_vals()
            display_nums = disp_nums()
            type_list = sneaker.get_types(brand)

            value = request.form['val']
            num = request.form['num']
            type = request.form['type']

            black  = request.form.get('black')
            white  = request.form.get('white')
            red    = request.form.get('red')
            orange = request.form.get('orange')
            yellow = request.form.get('yellow')
            green  = request.form.get('green')
            blue   = request.form.get('blue')
            purple = request.form.get('purple')

            colorList = [black,white,red,orange,yellow,green,blue,purple]

            l = len(colorList)
            for x in range(l-1,-1,-1):
                if colorList[x] is None:
                    colorList.pop(x)
                    
            shoe_list = sneaker.filter_by(brand, type, value, num, colorlist=colorList)

            return render_template('public/nike.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)

        elif request.form['post_button'] == 'Shuffle':
            return redirect('/nke')
        else:
            pass 
    else:
        pass

@electabuzz.route('/ads',methods=['GET','POST'])
def adidas():
    brand = 'Adidas'
    if request.method == 'GET':
        sneaker = Sneaker()
        shoe_list = display_rand_shoes(brand,24)
        display_nums = disp_nums()
        display_vals = disp_vals()
        type_list = sneaker.get_types(brand)
        return render_template('public/adidas.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Filter':
            sneaker = Sneaker()
            display_vals = disp_vals()
            display_nums = disp_nums()
            type_list = sneaker.get_types(brand)

            value = request.form['val']
            num = request.form['num']
            type = request.form['type']

            black  = request.form.get('black')
            white  = request.form.get('white')
            red    = request.form.get('red')
            orange = request.form.get('orange')
            yellow = request.form.get('yellow')
            green  = request.form.get('green')
            blue   = request.form.get('blue')
            purple = request.form.get('purple')

            colorList = [black,white,red,orange,yellow,green,blue,purple]

            l = len(colorList)
            for x in range(l-1,-1,-1):
                if colorList[x] is None:
                    colorList.pop(x)

            sneaker = Sneaker()
            shoe_list = sneaker.filter_by(brand, type, value, num, colorlist=colorList)
            print(shoe_list)

            return render_template('public/adidas.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)
        elif request.form['post_button'] == 'Shuffle':
            return redirect('/ads')
        else:
            pass
    else:
        pass

@electabuzz.route('/jrd',methods=['GET','POST'])
def jordan():
    brand = 'Jordan'
    if request.method == 'GET':
        sneaker = Sneaker()
        shoe_list = display_rand_shoes(brand,24)
        display_nums = disp_nums()
        display_vals = disp_vals()
        type_list = sneaker.get_types(brand)
        return render_template('public/jordan.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Filter':
            sneaker = Sneaker()
            display_vals = disp_vals()
            display_nums = disp_nums()
            type_list = sneaker.get_types(brand)
            value = request.form['val']
            num = request.form['num']
            type = request.form['type']
            black  = request.form.get('black')
            white  = request.form.get('white')
            red    = request.form.get('red')
            orange = request.form.get('orange')
            yellow = request.form.get('yellow')
            green  = request.form.get('green')
            blue   = request.form.get('blue')
            purple = request.form.get('purple')

            colorList = [black,white,red,orange,yellow,green,blue,purple]

            l = len(colorList)
            for x in range(l-1,-1,-1):
                if colorList[x] is None:
                    colorList.pop(x)

            sneaker = Sneaker()
            shoe_list = sneaker.filter_by(brand, type, value, num, colorlist=colorList)

            return render_template('public/jordan.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)
        elif request.form['post_button'] == 'Shuffle':
            return redirect('/jrd')
        else:
            pass
    else:
        pass

@electabuzz.route('/otb',methods=['GET','POST'])
def other():
    brand = 'Other'
    if request.method == 'GET':
        sneaker = Sneaker()
        shoe_list = display_rand_shoes(brand,24)
        display_nums = disp_nums()
        display_vals = disp_vals()
        type_list = sneaker.get_types(brand)
        return render_template('public/other.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Filter':
            sneaker = Sneaker()
            display_vals = disp_vals()
            display_nums = disp_nums()
            type_list = sneaker.get_types(brand)
            value = request.form['val']
            num = request.form['num']
            type = request.form['type']
            black  = request.form.get('black')
            white  = request.form.get('white')
            red    = request.form.get('red')
            orange = request.form.get('orange')
            yellow = request.form.get('yellow')
            green  = request.form.get('green')
            blue   = request.form.get('blue')
            purple = request.form.get('purple')

            colorList = [black,white,red,orange,yellow,green,blue,purple]

            l = len(colorList)
            for x in range(l-1,-1,-1):
                if colorList[x] is None:
                    colorList.pop(x)

            sneaker = Sneaker()
            shoe_list = sneaker.filter_by(brand, type, value, num, colorlist=colorList)

            return render_template('public/jordan.html',display_nums=display_nums,display_vals=display_vals,shoe_list=shoe_list, type_list=type_list)
        elif request.form['post_button'] == 'Shuffle':
            return redirect('/otb')
        else:
            pass
    else:
        pass

@electabuzz.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        age_list = ages()
        return render_template('public/register.html',age_list=age_list)
    elif request.method == 'POST':
        with User(username=request.form['username'],password=request.form['password']) as un:
            if un.check_un(request.form['username']):
                age_list = ages()
                return render_template('public/register.html', age_list=age_list, message='Username Exists')
            elif request.form['password'] != request.form['conf_password']:
                age_list = ages()
                return render_template('public/register.html',age_list=age_list, message="Password's Do Not Match")
            elif request.form.get('check') == None:
                age_list = ages()
                return render_template('public/register.html',age_list=age_list, message="Select Gender")
            else:
                age_list = ages()
                username = request.form['username']
                password = request.form['password']
                age = request.form['age']
                gender = request.form.get('check')
                un.create_user(request.form['username'],request.form['password'],request.form['age'],request.form['check'])
                return redirect('/'+username+'/pref')       
    else:
        pass

@electabuzz.route('/<username>/pref',methods=['GET','POST'])
def user_preferences(username):
    user = User({'username': username})
    if request.method == 'GET':
        return render_template('public/preferences.html', username=user.username)
    elif request.method == 'POST':

        """BRANDS"""
        nike   = request.form.get('nike')
        adidas = request.form.get('adidas')
        jordan = request.form.get('jordan')
        other  = request.form.get('other')
        userBrandList = [nike,adidas,jordan,other]
        l = len(userBrandList)
        for x in range(l-1,-1,-1):
            if userBrandList[x] is None:
                userBrandList.pop(x)

        """COLORS"""
        black  = request.form.get('black')
        white  = request.form.get('white')
        red    = request.form.get('red')
        orange = request.form.get('orange')
        yellow = request.form.get('yellow')
        green  = request.form.get('green')
        blue   = request.form.get('blue')
        purple = request.form.get('purple')
        userColorList = [black,white,red,orange,yellow,green,blue,purple]
        l = len(userColorList)
        for x in range(l-1,-1,-1):
            if userColorList[x] is None:
                userColorList.pop(x)

        userBrands = '-'.join(userBrandList)
        userColors = '-'.join(userColorList)
        userPK     = user.get_pk(user.username)
        #FIXME IF THEY INSERT NONE
        user.insert_preferences(userBrands,userColors,userPK)
        
        return redirect('/'+user.username+'/success') 
    else:
        pass

@electabuzz.route('/<username>/success',methods=['GET','POST'])
def user_success(username):
    if request.method == 'GET':
        return render_template('public/success.html')
    elif request.method == "POST":
        pass
    else:
        pass

@electabuzz.route('/search/<searchterms>',methods=['GET','POST'])
def search_results(searchterms):
    if request.method == 'GET':
        shoe_list = search_terms(searchterms,'all')
        return render_template('public/search_results.html',shoe_list=shoe_list)
    elif request.method == "POST":
        pass
    else:
        pass

@electabuzz.route('/reccomend',methods=['GET','POST'])
def reccomend():
    if request.method == 'GET':

        budget = request.form['budget']

        nike   = request.form.get('nike')
        adidas = request.form.get('adidas')
        jordan = request.form.get('jordan')
        other  = request.form.get('other')

        brandList = [nike,adidas,jordan,other]

        l = len(brandList)
        for x in range(l-1,-1,-1):
            if userBrandList[x] is None:
                userBrandList.pop(x)

        black  = request.form.get('black')
        white  = request.form.get('white')
        red    = request.form.get('red')
        orange = request.form.get('orange')
        yellow = request.form.get('yellow')
        green  = request.form.get('green')
        blue   = request.form.get('blue')
        purple = request.form.get('purple')

        colorList = [black,white,red,orange,yellow,green,blue,purple]

        l = len(userColorList)
        for x in range(l-1,-1,-1):
            if colorList[x] is None:
                colorList.pop(x)

        return render_template('public/reccomend.html')
    elif request.method == "POST":
        pass
    else:
        pass

@electabuzz.route('/chartzard',methods=['GET','POST'])
def data_visualization():
    if request.method == 'GET':
        return render_template('public/chart.html')
    elif request.method == "POST":
        pass
    else:
        pass

# @electabuzz.errorhandler(404)
# def not_found(error):
#     return render_template('public/404.html')

