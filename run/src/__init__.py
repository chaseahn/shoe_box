#!/usr/bin/env python3


import os
import time
import sqlite3
import cv2
import tensorflow as tf

from flask import Flask, render_template, request, url_for, redirect,session
from datetime import datetime
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.utils import secure_filename

from .controllers.public  import elekid as public_buzz
from .controllers.private import elekid as private_buzz
from .models.model import User,ShoeView,Sneaker,ShoeRec

from .extentions.loaders import display_rand_shoes,date_to_unix,brander,shoeValues,search_terms,color_list

UPLOAD_FOLDER = '/Users/ahn.ch/Projects/shoe_data/run/src/static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
CATEGORIES = ['Adidas', 'Jordan', 'Nike']

electabuzz = Flask(__name__)

electabuzz.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
electabuzz.secret_key = 'SUPER-DUPER-SECRET'

electabuzz.register_blueprint(public_buzz)
electabuzz.register_blueprint(private_buzz)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def prepare(filepath):
    IMG_SIZE = 80
    img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    return new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

def get_current_date():
    ts = time.time() 
    new_time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    date = new_time.split(' ')[0]
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

        """ 
        --------------------
        RETURN TRENDING LIST
        --------------------
        """

        view = ShoeView()
        trendList = view.trending_list()

        """ 
        ------------------------
        GET SUMS FROM SNEAKER DB
              [for index]
        ------------------------
        """

        sneaker = Sneaker()
        sneakerNum = sneaker.get_total_sneakers()
        sneakerSales = sneaker.get_total_sales()
        sneakerValue = sneaker.get_total_value()
        return render_template('public/index.html',trendList=trendList, num=f"{sneakerNum:,d}", 
                               sale=f"{sneakerSales:,d}", value=f"{sneakerValue:,d}")
    elif request.method == 'POST':
        if request.form['post_button'] == 'Login':
            
            """ 
            --------------------
                    LOGIN
            --------------------
            """

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
        sneaker = Sneaker()
        sneakerNum = sneaker.get_total_sneakers()
        sneakerSales = sneaker.get_total_sales()
        sneakerValue = sneaker.get_total_value()
        return render_template('public/index.html',trendList=trendList, num=f"{sneakerNum:,d}", 
                               sale=f"{sneakerSales:,d}", value=f"{sneakerValue:,d}")
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

    """
    --------------------------------------
    THE FOLLOWING DOCUMENTATION APPLIES TO 
    NIKE/ADIDAS/JORDAN/OTHER
    --------------------------------------
    """

    brand = 'Nike'
    if request.method == 'GET':
        sneaker = Sneaker()

        """ 
        --------------------
        DISPLAY RANDOM SHOES
        --------------------
        """

        shoe_list = display_rand_shoes(brand,24)

        """ 
        --------------------
        FILTER TYPES:
        1. Numbers
        2. Value
        3. Types
        --------------------
        """
        display_nums = disp_nums()
        display_vals = disp_vals()
        type_list = sneaker.get_types(brand)

        return render_template('public/nike.html',display_nums=display_nums,
                                display_vals=display_vals,shoe_list=shoe_list, 
                                type_list=type_list)
    elif request.method == 'POST':
        if request.form['post_button'] == 'Filter':
            sneaker = Sneaker()
        
            display_vals = disp_vals()
            display_nums = disp_nums()
            type_list = sneaker.get_types(brand)

            """ 
            -----------------------------
            RETURN VAL,NUM,TYPE FROM HTML
            -----------------------------
            """

            value = request.form['val']
            num = request.form['num']
            type = request.form['type']

            """ 
            ----------------
            COLOR SELECTIONS
            ----------------
            """

            black  = request.form.get('black')
            white  = request.form.get('white')
            red    = request.form.get('red')
            orange = request.form.get('orange')
            yellow = request.form.get('yellow')
            green  = request.form.get('green')
            blue   = request.form.get('blue')
            purple = request.form.get('purple')

            colorList = [black,white,red,orange,yellow,green,blue,purple]

            """ 
            --------------------------------------
            POP NONETYPE FROM COLOR LIST IF EXISTS
            --------------------------------------
            """

            l = len(colorList)
            for x in range(l-1,-1,-1):
                if colorList[x] is None:
                    colorList.pop(x)
            
            """ 
            --------------
            FILTER CONTENT
            --------------
            """

            shoe_list = sneaker.filter_by(brand, type, value, num, colorlist=colorList)

            return render_template('public/nike.html',display_nums=display_nums,
                                    display_vals=display_vals,shoe_list=shoe_list, 
                                    type_list=type_list)

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
        return render_template('public/adidas.html',display_nums=display_nums,
                                display_vals=display_vals,shoe_list=shoe_list, 
                                type_list=type_list)
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

            return render_template('public/adidas.html',display_nums=display_nums,
                                    display_vals=display_vals,shoe_list=shoe_list, 
                                    type_list=type_list)
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
        return render_template('public/jordan.html',display_nums=display_nums,
                                display_vals=display_vals,shoe_list=shoe_list, 
                                type_list=type_list)
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

            return render_template('public/jordan.html',display_nums=display_nums,
                                    display_vals=display_vals,shoe_list=shoe_list, 
                                    type_list=type_list)
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
        return render_template('public/other.html',display_nums=display_nums,
                                display_vals=display_vals,shoe_list=shoe_list, 
                                type_list=type_list)
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

            return render_template('public/jordan.html',display_nums=display_nums,
                                    display_vals=display_vals,shoe_list=shoe_list, 
                                    type_list=type_list)
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

            """ 
            -----------------------
            REGISTRATION CONDITIONS
            1. Username Exists
            2. Matching Passwords
            3. Unchecked Gender
            -----------------------
            """
            if un.check_un(request.form['username']):
                age_list = ages()
                return render_template('public/register.html', 
                                        age_list=age_list, 
                                        message='Username Exists')
            elif request.form['password'] != request.form['conf_password']:
                age_list = ages()
                return render_template('public/register.html',
                                        age_list=age_list, 
                                        message="Password's Do Not Match")
            elif request.form.get('check') == None:
                age_list = ages()
                return render_template('public/register.html', 
                                        age_list=age_list,  
                                        message="Select Gender")
                """ 
                -------------------
                ONCE MET, REGISTER
                -------------------
                """ 
            else:
                age_list = ages()
                username = request.form['username']
                password = request.form['password']
                age = request.form['age']
                gender = request.form.get('check')
                un.create_user(request.form['username'],request.form['password'],
                               request.form['age'],request.form['check'])
                return redirect('/'+username+'/pref')       
    else:
        pass

@electabuzz.route('/<username>/pref',methods=['GET','POST'])
def user_preferences(username):
    user = User({'username': username})
    if request.method == 'GET':
        return render_template('public/preferences.html', username=user.username)
    elif request.method == 'POST':

        """ 
        -------------------
        RETURN BRAND VALUES
        -------------------
        """

        nike   = request.form.get('nike')
        adidas = request.form.get('adidas')
        jordan = request.form.get('jordan')
        other  = request.form.get('other')
        userBrandList = [nike,adidas,jordan,other]

        """ 
        ----------------------------
        POP NONETYPE FROM BRAND LIST
        ----------------------------
        """

        l = len(userBrandList)
        for x in range(l-1,-1,-1):
            if userBrandList[x] is None:
                userBrandList.pop(x)

        """ 
        -------------------
        RETURN COLOR VALUES
        -------------------
        """

        black  = request.form.get('black')
        white  = request.form.get('white')
        red    = request.form.get('red')
        orange = request.form.get('orange')
        yellow = request.form.get('yellow')
        green  = request.form.get('green')
        blue   = request.form.get('blue')
        purple = request.form.get('purple')
        userColorList = [black,white,red,orange,yellow,green,blue,purple]

        """ 
        ----------------------------
        POP NONETYPE FROM COLOR LIST
        ----------------------------
        """

        l = len(userColorList)
        for x in range(l-1,-1,-1):
            if userColorList[x] is None:
                userColorList.pop(x)

        userBrands = '-'.join(userBrandList)
        userColors = '-'.join(userColorList)
        userPK     = user.get_pk(user.username)

        """ 
        -----------------------------
        INSERT TO USER_PREFERENCES DB
                     ex.
             'nke-ads-jrd-otb'
         'red-blue-green-white-black'
        -----------------------------
        """

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
        """ 
        ----------------------------
        SEARCH FOR KEYWORD STRENGTH
        INCLUDES ALL BRAND PARAMETER
        ----------------------------
        """
        shoe_list = search_terms(searchterms,'all')
        return render_template('public/search_results.html',shoe_list=shoe_list)
    elif request.method == "POST":
        pass
    else:
        pass


#TODO INSERT TENSORFLOW/KERAS HERE 
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
        """ 
        -------------------------------
        DATA VISUALIZATIONS FROM PLOTLY
        -------------------------------
        """
        return render_template('public/chart.html')
    elif request.method == "POST":
        pass
    else:
        pass

# @electabuzz.errorhandler(404)
# def not_found(error):
#     return render_template('public/404.html')

@electabuzz.route('/finder',methods=['GET','POST'])
def finder():
    user = User({'username': session['username']})
    if request.method == 'GET':

        return render_template('public/finder.html')
    elif request.method == "POST":

        if request.form['post_button'] == 'Submit':

            file = request.files['file']
            print(file)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(electabuzz.config['UPLOAD_FOLDER']+'/user_uploads', filename))

                model = tf.keras.models.load_model("/Users/ahn.ch/Projects/shoe_data/run/src/32x3-CNN.model")
                prediction = model.predict([prepare('/Users/ahn.ch/Projects/shoe_data/run/src/static/user_uploads/{}'.format(filename))])
                brand = CATEGORIES[int(prediction[0][0])]
                print(brand)

            price_min = request.form['min'].strip('$')
            price_max = request.form['max'].strip('$')

            int_min = int(price_min)
            int_max = int(price_max)
            session['price_min'] = int_min
            session['price_max'] = int_max

            premium  = request.form.get('premium')
            value = request.form.get('value')

            black  = request.form.get('black')
            white  = request.form.get('white')
            red    = request.form.get('red')
            orange = request.form.get('orange')
            yellow = request.form.get('yellow')
            green  = request.form.get('green')
            blue   = request.form.get('blue')
            purple = request.form.get('purple')

            colorList = [black,white,red,orange,yellow,green,blue,purple]
            valueList = [premium,value]

            l = len(colorList)
            for x in range(l-1,-1,-1):
                if colorList[x] is None:
                    colorList.pop(x)
            
            l = len(valueList)
            for x in range(l-1,-1,-1):
                if valueList[x] is None:
                    valueList.pop(x)

            session['colorList'] = colorList
            session['valueList'] = valueList
            print(colorList)
            print(valueList)

            brand = 'Nike'

            sneaker = Sneaker()

            shoeList = sneaker.finder(int_min, int_max, brand, valueList, colorList)

            shoeData = {}
            for shoe in shoeList:
                s = Sneaker(name=shoe)
                shoeData[shoe] = {
                    'value': s.avg_sale_price,
                    'premium': s.premium
                }
            
            print(shoeData)

            return render_template('public/found_shoes.html', shoeList=shoeList, shoeData=shoeData)
        else:
            image_button = request.form['post_button']
            print(image_button)

            pk = user.get_pk(user.username)

            rec = ShoeRec()
            rec.shoename = image_button
            rec.result = 'NO'
            rec.user_pk = pk
            rec.save()
            
            no_list = user.get_dislikes(pk)
            print('')
            print(no_list)
            print('')

            int_min = session.get('price_min', None)
            int_max = session.get('price_max', None)

            colorList = session.get('colorList', None)
            valueList = session.get('valueList', None)
            
            print(colorList)
            brand = 'Nike'

            sneaker = Sneaker()

            shoeList = sneaker.finder(int_min, int_max, brand, valueList, colorList, no_list)
            print('')
            print(shoeList)
            print('')   

            shoeData = {}
            for shoe in shoeList:
                s = Sneaker(name=shoe)
                shoeData[shoe] = {
                    'value': s.avg_sale_price,
                    'premium': s.premium
                }
            print(shoeData)

            return render_template('public/found_shoes.html', shoeList=shoeList, shoeData=shoeData)
    else:
        pass