#!/usr/bin/env python3


import os

from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from time import gmtime, strftime

from ..models.model import User

elekid = Blueprint('private',__name__,url_prefix='/2492')

@elekid.route('/account',methods=['GET','POST'])
def account():
    if request.method == 'GET':
        try:
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            favList = user.display_favorites()
            shoebox = user.display_shoebox()
            return render_template('private/account.html',message='Welcome '+session['username'],favList=favList,shoebox=shoebox)
        except KeyError:
            return redirect('/register')
    elif request.method == 'POST':
        print(request.form['post_button'])
    else:
        pass