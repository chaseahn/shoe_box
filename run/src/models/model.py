#!/usr/bin/env python3

import sqlite3

from flask import session
from random import randint
from time import gmtime, strftime, sleep

from ..mappers.opencursor import OpenCursor

class User:
    def __init__(self, row={}, username='', password=''):
        if username:
            self.check_cred(username,password)
        else:
            self.row_set(row)
    def __enter__(self):
        return self

    def __exit__(self,exception_type,exception_value,exception_traceback):
        sleep(randint(10,10000)/10000)

    def row_set(self,row={}):
        row           = dict(row)
        self.pk       = row.get('pk')
        self.username = row.get('username')
        self.password = row.get('password')
        self.age      = row.get('age')
        self.gender   = row.get('gender')

    def check_cred(self,username,password):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM user WHERE
                  username=? and password=?; """
            val = (username,password)
            cur.execute(SQL,val)
            row = cur.fetchone()
        if row:
            self.row_set(row)
        else:
            self.row_set({})

    def check_un(self,username):
        with OpenCursor() as cur:
            SQL = """ SELECT username FROM user WHERE
                  username=?; """
            val = (username,)
            cur.execute(SQL,val)
            row = cur.fetchone()
        if row:
            return True
        else:
            return False

    def login(self,password):
        with OpenCursor() as cur:
            cur.execute('SELECT password FROM user WHERE username=?;',(self.username,))
            if password == cur.fetchone()['password']:
                return True
            else:
                return False

    def create_user(self,username,password,age,gender):
        self.username = username
        self.password = password
        self.age      = age
        self.gender   = gender
        with OpenCursor() as cur:
            SQL = """ INSERT INTO user(
                username,password,age,gender) VALUES (
                ?,?,?,?); """
            val = (self.username,self.password,self.age,self.gender)
            cur.execute(SQL,val)

class ShoeReq:

    def __init__(self, row={}):
        # print(row)
        # dict(row)
        if row:
            self.pk       = row[0]
            self.content  = row[1]
            self.time     = row[2]
            self.username = row[3]
            self.users_pk = row[4]
            self.filename = row[5]
        else:
            self.pk = None
            self.content = None
            self.time = None
            self.user_pk = None
            self.username = None
            self.filename = None

    def __bool__(self):
        return bool(self.pk)
    
    def save(self):
        with OpenCursor() as cur:
            SQL = """ INSERT INTO posts(
                content,time,username,user_pk,filename
                ) VALUES (?,?,?,?,?); """
            val = (self.content,self.time,self.username,self.users_pk,self.filename)
            cur.execute(SQL,val)

    def __repr__(self):
        output = '{}@{}: {}'
        return output.format(self.username,self.time,self.content)