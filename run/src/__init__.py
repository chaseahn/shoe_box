#!/usr/bin/env python3


import os
import time

from flask import Flask, render_template, request, url_for, redirect,session
from werkzeug.utils import secure_filename

from .controllers.public  import elekid as public_buzz
from .controllers.private import elekid as private_buzz
from .models.model import User,ShoeView

from .extentions.loaders import display_shoes,date_to_unix,brander,get_shoes,shoeValues,search_terms

UPLOAD_FOLDER = '/Users/ahn.ch/Projects/shoe_data/run/src/static'

electabuzz = Flask(__name__)
electabuzz.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
electabuzz.secret_key = 'SUPER-DUPER-SECRET'

electabuzz.register_blueprint(public_buzz)
electabuzz.register_blueprint(private_buzz)

def ages():
    age = []
    for x in range(1,100):
        age.append(x)
    return age

def disp_nums():
    nums = [50,100,200]
    return nums

@electabuzz.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        view = ShoeView()
        trendList = view.trending_list()
        return render_template('public/index.html',trendList=trendList)
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
    brand = 'nike'
    if request.method == 'GET':
        shoe_list = display_shoes(None, brand, '50')
        display_nums = disp_nums()
        return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list)
    elif request.method == 'POST':
        empty = None
        display_nums = disp_nums()
        val = request.form.get('check')
        order = request.form.get('check2')
        if request.form['post_button'] == 'Filter':
            try:
                if order == 'high':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list)
                elif order == 'low':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list)
                else:
                    check = empty
                    num = request.form['num']
                    shoe_list = display_shoes(check,brand,num)
                    return render_template('public/nike.html',display_nums=display_nums,shoe_list=[],message='Invalid Search.')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search1.')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search2.')
        elif request.form['post_button'] == 'Shuffle':
            try:
                num = request.form['num']
                check = empty
                shoe_list = display_shoes(check,brand,num)
                return redirect('/nke',display_nums=display_nums,shoe_list=shoe_list,message='')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list,message='')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return redirect('/nke',display_nums=display_nums,shoe_list=shoe_list,message='')
        elif request.form['post_button'] == 'Search':
            searchTerms = request.form['search_text']
            if searchTerms == "":
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list,message='Enter Something, Then Search...')
            else:
                display_nums = disp_nums()
                searchTerms = request.form['search_text']
                shoe_list = search_terms(searchTerms,brand)
                return render_template('public/nike.html',display_nums=display_nums,shoe_list=shoe_list,results='Results for:'+' '+searchTerms)
    else:
        pass

@electabuzz.route('/ads',methods=['GET','POST'])
def adidas():
    brand = 'adidas'
    if request.method == 'GET':
        shoe_list = display_shoes(None, brand, '50')
        display_nums = disp_nums()
        return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list)
    elif request.method == 'POST':
        empty = None
        display_nums = disp_nums()
        val = request.form.get('check')
        order = request.form.get('check2')
        if request.form['post_button'] == 'Filter':
            try:
                if order == 'high':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list)
                elif order == 'low':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list)
                else:
                    check = empty
                    num = request.form['num']
                    shoe_list = display_shoes(check,brand,num)
                    return render_template('public/adidas.html',display_nums=display_nums,shoe_list=[],message='Invalid Search.')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search1.')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search2.')
        elif request.form['post_button'] == 'Shuffle':
            try:
                num = request.form['num']
                check = empty
                shoe_list = display_shoes(check,brand,num)
                return redirect('/ads',display_nums=display_nums,shoe_list=shoe_list,message='')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list,message='')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return redirect('/ads',display_nums=display_nums,shoe_list=shoe_list,message='')
        elif request.form['post_button'] == 'Search':
            searchTerms = request.form['search_text']
            if searchTerms == "":
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list,message='Enter Something, Then Search...')
            else:
                display_nums = disp_nums()
                searchTerms = request.form['search_text']
                shoe_list = search_terms(searchTerms,brand)
                return render_template('public/adidas.html',display_nums=display_nums,shoe_list=shoe_list,results='Results for:'+' '+searchTerms)
    else:
        pass

@electabuzz.route('/jrd',methods=['GET','POST'])
def jordan():
    brand = 'jordan'
    if request.method == 'GET':
        shoe_list = display_shoes(None, brand, '50')
        display_nums = disp_nums()
        return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list)
    elif request.method == 'POST':
        empty = None
        display_nums = disp_nums()
        val = request.form.get('check')
        order = request.form.get('check2')
        if request.form['post_button'] == 'Filter':
            try:
                if order == 'high':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list)
                elif order == 'low':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list)
                else:
                    check = empty
                    num = request.form['num']
                    shoe_list = display_shoes(check,brand,num)
                    return render_template('public/jordan.html',display_nums=display_nums,shoe_list=[],message='Invalid Search.')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search1.')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search2.')
        elif request.form['post_button'] == 'Shuffle':
            try:
                num = request.form['num']
                check = empty
                shoe_list = display_shoes(check,brand,num)
                return redirect('/jrd',display_nums=display_nums,shoe_list=shoe_list,message='')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list,message='')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return redirect('/jrd',display_nums=display_nums,shoe_list=shoe_list,message='')
        elif request.form['post_button'] == 'Search':
            searchTerms = request.form['search_text']
            if searchTerms == "":
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list,message='Enter Something, Then Search...')
            else:
                display_nums = disp_nums()
                searchTerms = request.form['search_text']
                shoe_list = search_terms(searchTerms,brand)
                return render_template('public/jordan.html',display_nums=display_nums,shoe_list=shoe_list,results='Results for:'+' '+searchTerms)
    else:
        pass

@electabuzz.route('/otb',methods=['GET','POST'])
def other():
    brand = 'other'
    if request.method == 'GET':
        shoe_list = display_shoes(None, brand, '50')
        display_nums = disp_nums()
        return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list)
    elif request.method == 'POST':
        empty = None
        display_nums = disp_nums()
        val = request.form.get('check')
        order = request.form.get('check2')
        if request.form['post_button'] == 'Filter':
            try:
                if order == 'high':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_high'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list)
                elif order == 'low':
                    if val == 'asp':
                        num = request.form['num']
                        check = 'avg_sale_price_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'tts':
                        num = request.form['num']
                        check = 'total_sales_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list)
                    elif val == 'rld':
                        num = request.form['num']
                        check = 'release_date_low'
                        shoe_list = display_shoes(check,brand,num)
                        return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list)
                else:
                    check = empty
                    num = request.form['num']
                    shoe_list = display_shoes(check,brand,num)
                    return render_template('public/other.html',display_nums=display_nums,shoe_list=[],message='Invalid Search.')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search1.')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list,message='Invalid Search2.')
        elif request.form['post_button'] == 'Shuffle':
            try:
                num = request.form['num']
                check = empty
                shoe_list = display_shoes(check,brand,num)
                return redirect('/otb',display_nums=display_nums,shoe_list=shoe_list,message='')
            except TypeError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list,message='')
            except IndexError:
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return redirect('/ads',display_nums=display_nums,shoe_list=shoe_list,message='')
        elif request.form['post_button'] == 'Search':
            searchTerms = request.form['search_text']
            if searchTerms == "":
                check = empty
                num = request.form['num']
                shoe_list = display_shoes(check,brand,num)
                return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list,message='Enter Something, Then Search...')
            else:
                display_nums = disp_nums()
                searchTerms = request.form['search_text']
                shoe_list = search_terms(searchTerms,brand)
                return render_template('public/other.html',display_nums=display_nums,shoe_list=shoe_list,results='Results for:'+' '+searchTerms)
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

# @electabuzz.errorhandler(404)
# def not_found(error):
#     return render_template('public/404.html')

