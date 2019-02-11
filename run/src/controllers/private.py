#!/usr/bin/env python3


import os

from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from time import gmtime, strftime

from ..models.model import User, ShoeBox

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
        if request.form['post_button'].split('-')[0] == 'Update':
            box_pk = request.form['post_button'].split('-')[1]
            box = ShoeBox(pk=box_pk)
            shoeName = box.shoename
            return redirect('/update-box/'+box_pk+'/'+shoeName)
        elif request.form['post_button'].split('-')[0] == 'Remove':
            box_pk = request.form['post_button'].split('-')[1]
            print('remove' + box_pk)
            user = User({'username': session['username'], 'pk': session['pk'], 'age': session['age'], 'gender': session['gender']})
            favList = user.display_favorites()
            shoebox = user.display_shoebox()
            return render_template('private/account.html',message='Welcome '+session['username'],favList=favList,shoebox=shoebox)
    else:
        pass