#!/usr/bin/env python3


import os

from flask import Flask, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

from .controllers.public  import elekid as public_buzz
from .controllers.private import elekid as private_buzz
from .models.model import User

ICON_FOLDER = '/Users/ahn.ch/Projects/shoe_data/run/src/static/icons/'

electabuzz = Flask(__name__)
electabuzz.config['UPLOAD_FOLDER'] = ICON_FOLDER
Bootstrap(electabuzz)

electabuzz.register_blueprint(public_buzz)

def ages():
    age = []
    for x in range(1,100):
        age.append(x)
    return age

@electabuzz.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        filename = os.path.join(electabuzz.config['UPLOAD_FOLDER'],'adidas_logo.png')
        return render_template('public/index.html', filename=filename)
    elif request.method == 'POST':
        if request.form['post_image'] == 'nike':
            return redirect('/nke')
        elif request.form['post_image'] == 'adidas':
            return redirect('/ads')
        elif request.form['post_image'] == 'jordan':
            return redirect('/jrd')
        else:
            pass
    else:
        pass

@electabuzz.route('/register',methods=['GET','POST'])
def register():
    age_list = ages()
    if request.method == 'GET':
        return render_template('public/register.html',age_list=age_list)
    elif request.method == 'POST':
        with User(username=request.form['username'],password=request.form['password']) as un:
            if un.check_un(request.form['username']):
                return render_template('public/register.html', message='Username Exists')
            elif request.form['password'] != request.form['conf_password']:
                return render_template('public/register.html', message="Passwords Don't Match")
            else:
                print('hi')
                print(request.form['age'])
                print(request.form.get('check'))
                return render_template('public/register.html', message="hi")
                # un.create_user(request.form['username'],request.form['password'],request.form['age'],request.form['check'])
    else:
        pass

@electabuzz.route('/nke',methods=['GET','POST'])
def nike():
    if request.method == 'GET':
        return render_template('public/nike.html')
    elif request.method == 'POST':
        pass
    else:
        pass

@electabuzz.route('/ads',methods=['GET','POST'])
def adidas():
    if request.method == 'GET':
        return render_template('public/adidas.html')
    elif request.method == 'POST':
        pass
    else:
        pass

@electabuzz.route('/jrd',methods=['GET','POST'])
def jordan():
    if request.method == 'GET':
        return render_template('public/jordan.html')
    elif request.method == 'POST':
        pass
    else:
        pass

@electabuzz.route('/otb',methods=['GET','POST'])
def other():
    if request.method == 'GET':
        return render_template('public/other_brands.html')
    elif request.method == 'POST':
        pass
    else:
        pass

# @electabuzz.errorhandler(404)
# def not_found(error):
#     return render_template('public/404.html')

