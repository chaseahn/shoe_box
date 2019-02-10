#!/usr/bin/env python3

import sqlite3
import time

from datetime import datetime
from flask import session
from random import randint
from time import gmtime, strftime, sleep

from ..mappers.opencursor import OpenCursor

def tsplit(string, delimiters):
    """Behaves str.split but supports multiple delimiters."""
    
    delimiters = tuple(delimiters)
    stack = [string,]
    
    for delimiter in delimiters:
        for i, substring in enumerate(stack):
            substack = substring.split(delimiter)
            stack.pop(i)
            for j, _substring in enumerate(substack):
                stack.insert(i+j, _substring)
    return stack

def get_current_date():
    ts = time.time() 
    time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    date = time.split(' ')[0]
    return date

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
    
    def favoriteShoe(self,shoename,pk):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM user_favorites WHERE  
                user_pk = ? and shoename= ?; """
            val = (pk,shoename)
            cur.execute(SQL,val)
            data = cur.fetchone()
        if data:
            print("Already Saved")
            return False
        else:
            userFav          = UserFavorites()
            userFav.shoename = shoename
            userFav.user_pk  = pk
            userFav.save()
    
    def display_favorites(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM user_favorites WHERE
                  user_pk=?; """
            val = (self.pk,)
            cur.execute(SQL,val)
            row = cur.fetchall()
        if row:
            favorite_list=[]
            for rows in row:
                shoe = rows['shoename']
                favorite_list.append(shoe)
            return favorite_list
        else:
            favorite_list=[]
            return favorite_list
    
    def display_shoebox(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM shoebox WHERE
                  user_pk=?; """
            val = (self.pk,)
            cur.execute(SQL,val)
            row = cur.fetchall()
        if row:
            shoebox = {}
            key=0
            for rows in row:

                sneaker = Sneaker(name=rows['shoename'])
                value = float(sneaker.avg_sale_price)

                if sneaker.retail_price == '--':
                    sneaker.retail_price = sneaker.avg_sale_price

                shoebox[key] = {
                    'shoename': rows['shoename'],
                    'ticker': rows['ticker'],
                    'type': rows['type'],
                    'date': rows['date'],
                    'price_bought': rows['price_bought'],
                    'gain-loss-retail-dollar': sneaker.retail_price-float(rows['price_bought']),
                    'gain-loss-retail-percentage': '{:.2f}'.format(float(((sneaker.retail_price-float(rows['price_bought']))/float(rows['price_bought'])*100))),
                    'retail_price': sneaker.retail_price,
                    'price_sold': rows['price_sold'],
                    'gain-loss-profit': round(float(rows['profit'])/float(rows['price_bought']),2)*100,
                    'profit': rows['profit'],
                    'pk': rows['pk']
                }
                
                key+=1
            return shoebox
        else:
            shoebox={}
            return shoebox

    def get_pk(self,username):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM user WHERE
                  username=?; """
            val = (username,)
            cur.execute(SQL,val)
            row = cur.fetchone()
        if row:
            return row['pk']
        else:
            return False

    def insert_preferences(self,brands,colors,pk):
        userPref = UserPreferences()
        userPref.brand   = brands
        userPref.color   = colors
        userPref.user_pk = pk
        userPref.save()
    
    def add_to_box(self,type,shoename,date,price_bought, profit, pk, price_sold=''):

        sneaker = Sneaker(name=shoename)

        if type == 'Buy':
            box = ShoeBox()
            box.shoename = shoename
            box.ticker = sneaker.ticker
            box.type = 'BUY'
            box.date = date
            box.price_bought = price_bought
            box.price_sold = 0
            box.profit = 0
            box.user_pk = pk
            box.save()
        else:
            box = ShoeBox()
            box.shoename = shoename
            box.ticker = sneaker.ticker
            box.type = 'SELL'
            box.date = date
            box.price_bought = price_bought
            box.price_sold = price_sold
            box.profit = profit
            box.user_pk = pk
            box.save()
    
    def get_preferences(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM user_preferences WHERE
                  user_pk=?; """
            val = (self.pk,)
            cur.execute(SQL,val)
            row = cur.fetchone()
        if row:
            brands = row['brand'].split('-')
            colors = row['color'].split('-')
            return [brands,colors]
        else:
            return False

    # def get_like_accounts(self):
    #     with OpenCursor() as cur:
    #         SQL = """ SELECT * FROM user_preferences WHERE
    #               user_pk=?; """
    #         val = (self.pk,)
    #         cur.execute(SQL,val)
    #         row = cur.fetchone()
    #     if row:
    #         brands = row['brand'].split('-')
    #         colors = row['color'].split('-')
    #         return [brands,colors]
    #     else:
    #         return False


class ShoeView:

    def __init__(self,row={},shoename=''):
        if shoename:
            self.check_shoe(shoename)
        else:
            self.row_set(row)

    def row_set(self,row={}):
        row              = dict(row)
        self.pk          = row.get('pk')
        self.shoename    = row.get('shoename')
        self.click_count = row.get('click_count')
    
    def check_shoe(self,shoename):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM shoes_viewed WHERE
                  shoename=?; """
            val = (shoename,)
            cur.execute(SQL,val)
            row = cur.fetchone()
        if row:
            self.row_set(row)
        else:
            self.row_set({})
    
    def trending_list(self):
        with OpenCursor() as cur:
            SQL = """ SELECT shoename FROM shoes_viewed 
            ORDER BY click_count DESC limit 40; """
            cur.execute(SQL)
            data = cur.fetchall()
            trending_list=[]
            for row in data:
                shoename = row['shoename']
                trending_list.append(shoename)
            return trending_list

    def __bool__(self):
        return bool(self.pk)
    
    def save(self,shoeName):
        if self:
            with OpenCursor() as cur:
                SQL = """ UPDATE shoes_viewed SET 
                    shoename = ?, click_count = ?
                    WHERE shoename=?; """
                val = (self.shoename, (self.click_count+1), self.shoename)
                cur.execute(SQL, val)
        else:
            with OpenCursor() as cur:
                SQL = """ INSERT INTO shoes_viewed (
                    shoename, click_count)
                    VALUES (?, ?); """
                val = (shoeName, 1)
                cur.execute(SQL, val)
                self.pk = cur.lastrowid

class UserFavorites:

    def __init__(self, row={}):
        row           = dict(row)
        self.pk       = row.get('pk')
        self.shoename = row.get('shoename')
        self.user_pk  = row.get('user_pk')

    def __bool__(self):
        return bool(self.pk)
    
    def save(self):
        with OpenCursor() as cur:
            SQL = """ INSERT INTO user_favorites(
                shoename,user_pk
                ) VALUES (?,?); """
            val = (self.shoename,self.user_pk)
            cur.execute(SQL,val)
    
    def remove(self,shoename):
        with OpenCursor() as cur:
            SQL = """ REMOVE FROM user_favorites WHERE 
                shoename=? and user_pk=?; """
            val = (shoename,self.pk)
            cur.execute(SQL,val)

    def __repr__(self):
        output = 'Account: {}, Shoe: {}'
        return output.format(self.account_pk,self.shoename)

class UserPreferences:

    def __init__(self, row={}):
        row           = dict(row)
        self.pk       = row.get('pk')
        self.brand    = row.get('brand')
        self.color    = row.get('color')
        self.user_pk  = row.get('user_pk')

    def __bool__(self):
        return bool(self.pk)
    
    def check_against_all(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM user_preferences; """
            cur.execute(SQL,)
            data = cur.fetchall()
            check_list = []
            for row in data:
                brands = row['brand'].split('-')
                colors = row['color'].split('-')
                user_pk = row['user_pk']
                check_list,append([brands,colors,user_pk])
            return check_list

    def save(self):
        with OpenCursor() as cur:
            SQL = """ INSERT INTO user_preferences(
                brand,color,user_pk
                ) VALUES (?,?,?); """
            val = (self.brand,self.color,self.user_pk)
            cur.execute(SQL,val)

    def __repr__(self):
        output = 'Account: {}, Brand: {}, Color: {}'
        return output.format(self.user_pk,self.brand,self.color)

class ShoeBox:

    def __init__(self, row={}):
        row               = dict(row)
        self.pk           = row.get('pk')
        self.shoename     = row.get('shoename')
        self.ticker       = row.get('ticker')
        self.type         = row.get('type')
        self.date         = row.get('date')
        self.price_bought = row.get('price_bought')
        self.price_sold   = row.get('price_sold')
        self.profit       = row.get('profit')
        self.user_pk      = row.get('user_pk')

    def __bool__(self):
        return bool(self.pk)
    
    def save(self):
        if self:
            date = get_current_date()
            with OpenCursor() as cur:
                SQL = """ UPDATE shoebox SET 
                    shoename=?, ticker=?, type=?, date=?, price_bought=?, price_sold=?, profit=?, user_pk=?
                    WHERE shoename=?; """
                val = (self.shoename, self.ticker, self.type, date, self.price_bought, self.price_sold, self.profit, self.user_pk)
                cur.execute(SQL, val)
        else:
            with OpenCursor() as cur:
                SQL = """ INSERT INTO shoebox (
                    shoename, ticker, type, date, price_bought, price_sold, profit, user_pk)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?); """
                val = (self.shoename, self.ticker, self.type, self.date, self.price_bought, self.price_sold, self.profit, self.user_pk)
                cur.execute(SQL, val)
                self.pk = cur.lastrowid

    # def __repr__(self):
    #     output = 'Account: {}, Brand: {}, Color: {}'
    #     return output.format(self.user_pk,self.brand,self.color)

class Sneaker:

    def __init__(self, row={}, name=''):
        if name:
            self.check_shoe(name)
        else:
            self.row_set(row)
    
    def __bool__(self):
        return bool(self.pk)

    def __enter__(self):
        return self

    def __exit__(self,exception_type,exception_value,exception_traceback):
        sleep(randint(10,10000)/10000)

    def row_set(self,row={}):
        row                    = dict(row)
        self.pk                = row.get('pk')
        self.brand	           = row.get('brand')
        self.type              = row.get('type')
        self.name              = row.get('name')
        self.colorway          = row.get('colorway')
        self.image             = row.get('image')
        self.image_placeholder = row.get('image_placeholder')
        self.release_date      = row.get('release_date')
        self.retail_price      = row.get('retail_price')
        self.ticker            = row.get('ticker')
        self.total_sales       = row.get('total_sales')
        self.url               = row.get('url')
        self.year_high         = row.get('year_high')
        self.year_low          = row.get('year_low')
        self.avg_sale_price    = row.get('avg_sale_price')
        self.premium           = row.get('premium')

    def check_shoe(self,name):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM sneakers WHERE
                  name=?; """
            val = (name,)
            cur.execute(SQL,val)
            row = cur.fetchone()
        if row:
            self.row_set(row)
        else:
            self.row_set({})
    
    def get_shoes(self,brand):
        brand = brand.capitalize()
        if brand == 'All':
            with OpenCursor() as cur:
                SQL = """ SELECT * FROM sneakers; """
                cur.execute(SQL,)
                data = cur.fetchall()
                if data:
                    shoes = []
                    for row in data:
                        shoes.append(row['name'])
                    return shoes
                else:
                    shoes = []
                    return []
        else:
            with OpenCursor() as cur:
                SQL = """ SELECT * FROM sneakers WHERE brand = ?; """
                val = (brand,)
                cur.execute(SQL,val)
                data = cur.fetchall()
                if data:
                    shoes = []
                    for row in data:
                        shoes.append(row['name'])
                    return shoes
                else:
                    shoes = []
                    return []

    #FIXME ADD TYPE FILTER
    def filter_by(self, brand, type, value, num, colorlist = []):
        if value == 'Valuable ↑':
            with OpenCursor() as cur:
                if type == 'None':
                    SQL = """ SELECT * FROM sneakers WHERE brand=? ORDER BY premium DESC; """
                    val = (brand,)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                else:
                    SQL = """ SELECT * FROM sneakers WHERE brand=? and type=? ORDER BY premium DESC; """
                    val = (brand,type)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                if data:
                    shoes = []
                    if colorlist == []:
                        for row in data:
                            if row['avg_sale_price'] == '--':
                                pass
                            else:
                                shoes.append(row['name'])
                    else:
                        for row in data:
                            colorway = tsplit(row['colorway'], ('/', '-', ' '))
                            for color in colorlist:
                                if color.capitalize() in colorway and row['avg_sale_price'] != '--':
                                    shoes.append(row['name'])
                    
                    if num == 'All':
                        num = len(shoes)
                    
                    return shoes[:int(num)]

        elif value == 'Valuable ↓':
            with OpenCursor() as cur:
                if type == 'None':
                    SQL = """ SELECT * FROM sneakers WHERE brand=? ORDER BY premium ASC; """
                    val = (brand,)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                else:
                    SQL = """ SELECT * FROM sneakers WHERE brand=? and type=? ORDER BY premium ASC; """
                    val = (brand,type)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                if data:
                    shoes = []
                    if colorlist == []:
                        for row in data:
                            if row['premium'] is None:
                                pass
                            else:
                                shoes.append(row['name'])
                    else:
                        for row in data:
                            colorway = tsplit(row['colorway'], ('/', '-', ' '))
                            for color in colorlist:
                                if color.capitalize() in colorway:
                                    shoes.append(row['name'])
                    
                    if num == 'All':
                        num = len(shoes)

                    return shoes[:int(num)]

        elif value == 'Price ↑':
            with OpenCursor() as cur:
                if type == 'None':
                    SQL = """ SELECT * FROM sneakers WHERE brand=? ORDER BY avg_sale_price DESC; """
                    val = (brand,)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                else:
                    SQL = """ SELECT * FROM sneakers WHERE brand=? and type=? ORDER BY avg_sale_price DESC; """
                    val = (brand,type)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                if data:

                    shoes = []

                    if colorlist == []:
                        for row in data:
                            if row['avg_sale_price'] == '--':
                                pass
                            else:
                                shoes.append(row['name'])
                    else:
                        for row in data:
                            colorway = tsplit(row['colorway'], ('/', '-', ' '))
                            for color in colorlist:
                                if color.capitalize() in colorway and row['avg_sale_price'] != '--':
                                    shoes.append(row['name'])

                    if num == 'All':
                        num = len(shoes)

                    return shoes[:int(num)]

        elif value == 'Price ↓':
            with OpenCursor() as cur:
                SQL = """ SELECT * FROM sneakers WHERE brand = ? ORDER BY avg_sale_price ASC; """
                val = (brand,)
                cur.execute(SQL,val)
                data = cur.fetchall()
                if data:

                    shoes = []

                    if colorlist == []:
                        for row in data:
                            shoes.append(row['name'])
    
                    else:
                        for row in data:
                            colorway = tsplit(row['colorway'], ('/', '-', ' '))
                            for color in colorlist:
                                if color.capitalize() in colorway:
                                    shoes.append(row['name'])
                    if num == 'All':
                        num = len(shoes)

                    return shoes[:int(num)]

        elif value == 'Sales ↑':
            with OpenCursor() as cur:
                if type == 'None':
                    SQL = """ SELECT * FROM sneakers WHERE brand=? ORDER BY total_sales DESC; """
                    val = (brand,)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                else:
                    SQL = """ SELECT * FROM sneakers WHERE brand=? and type=? ORDER BY total_sales DESC; """
                    val = (brand,type)
                    cur.execute(SQL,val)
                    data = cur.fetchall()
                if data:
                    shoes = []
                    if colorlist == []:
                        for row in data:
                            if row['avg_sale_price'] == '--':
                                pass
                            else:
                                shoes.append(row['name'])
                    else:
                        for row in data:
                            colorway = tsplit(row['colorway'], ('/', '-', ' '))
                            for color in colorlist:
                                if color.capitalize() in colorway and row['avg_sale_price'] != '--':
                                    shoes.append(row['name'])
                    if num == 'All':
                        num = len(shoes)

                    return shoes[:int(num)]

        elif value == 'Sales ↓':
            with OpenCursor() as cur:
                SQL = """ SELECT * FROM sneakers WHERE brand = ? ORDER BY total_sales ASC; """.format(num)
                val = (brand,)
                cur.execute(SQL,val)
                data = cur.fetchall()
                if data:
                    shoes = []
                    if colorlist == []:
                        for row in data:
                            shoes.append(row['name'])
    
                    else:
                        for row in data:
                            colorway = tsplit(row['colorway'], ('/', '-', ' '))
                            for color in colorlist:
                                if color.capitalize() in colorway:
                                    shoes.append(row['name'])
                    if num == 'All':
                        num = len(shoes)
                        
                    return shoes[:int(num)]
        else:
            with OpenCursor() as cur:
                SQL = """ SELECT * FROM sneakers WHERE brand = ?; """
                val = (brand,)
                cur.execute(SQL,val)
                data = cur.fetchall()
                if data:
                    shoes = []
                    if colorlist == []:
                        x = 0
                        while x < num:
                            for row in data:
                                shoes.append(row['name'])
                                x+=1
                            return shoes
                    else:
                        colored_shoes = []
                        for row in data:
                            colorway = tsplit(row['colorway'], ('/', '-', ' '))
                            for color in colorlist:
                                if color.capitalize() in colorway:
                                    colored_shoes.append(row['name'])
                        return colored_shoes
                else:
                    pass

    def get_color_list(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM sneakers; """
            cur.execute(SQL,)
            data = cur.fetchall()
            if data:
                color_list = []
                for row in data:
                    colorway = str(row['colorway'])
                    colors = tsplit(colorway, ('/', '-', ' '))
                    x = 0 
                    for color in colors:
                        color_list.append(color)
                counter = [[x,color_list.count(x)] for x in set(color_list)]
                sorted_counter = sorted(counter, key = lambda x: int(x[1]), reverse=True)
                i = 0
                finalcol = []
                while i < 50:
                    for colors in sorted_counter:
                        finalcol.append(colors[0])
                        i+=1
                return finalcol
            else:
                pass

    def get_types(self, brand):
        with OpenCursor() as cur:
            SQL = """ SELECT type FROM sneakers WHERE brand='{}'; """.format(brand)
            cur.execute(SQL,)
            data = cur.fetchall()
            if data:
                types = ['None']
                for row in data:
                    types.append(row['type'])
                typeList = set(types)
                return typeList

    def get_total_sneakers(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM sneakers; """
            cur.execute(SQL,)
            data = cur.fetchall()
            num = len(data)
            return num
    
    def get_total_sales(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM sneakers; """
            cur.execute(SQL,)
            data = cur.fetchall()
            if data:
                sales = []
                for row in data:
                    if row['total_sales'] != '--':
                        sales.append(row['total_sales'])
                total = sum(sales)
                return total
    
    def get_total_sales_by_brand(self, brand):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM sneakers WHERE brand='{}'; """.format(brand)
            cur.execute(SQL,)
            data = cur.fetchall()
            if data:
                sales = []
                for row in data:
                    if row['total_sales'] != '--':
                        sales.append(row['total_sales'])
                total = sum(sales)
                return total
    
    def get_total_value(self):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM sneakers; """
            cur.execute(SQL,)
            data = cur.fetchall()
            if data:
                sales = []
                for row in data:
                    if row['total_sales'] != '--' and row['avg_sale_price'] != '--':
                        sales.append(row['total_sales']*row['avg_sale_price'])
                total = sum(sales)
                return total
    
    def get_total_value_by_brand(self, brand):
        with OpenCursor() as cur:
            SQL = """ SELECT * FROM sneakers WHERE brand='{}'; """.format(brand)
            cur.execute(SQL,)
            data = cur.fetchall()
            if data:
                sales = []
                for row in data:
                    if row['total_sales'] != '--' and row['avg_sale_price'] != '--':
                        sales.append(row['total_sales']*row['avg_sale_price'])
                total = sum(sales)
                return total

    def save(self,name):
        if self:
            with OpenCursor() as cur:
                SQL = """ UPDATE sneakers SET 
                    brand=?, type=?, name=?, colorway=?, image=?, image_placeholder=?, release_date=?,
                    retail_price=?, ticker=?, total_sales=?, url=?, year_high=?,
                    year_low=?, avg_sale_price=?, premium=? WHERE name=?; """
                val = (self.brand, self.type, self.name, self.colorway, self.image, self.image_placeholder, self.release_date, self.retail_price, self.ticker, self.total_sales, self.url, self.year_high, self.year_low, self.avg_sale_price, self.premium, name)
                cur.execute(SQL, val)
        else:
            with OpenCursor() as cur:
                SQL = """ INSERT INTO sneakers (
                    brand, type, name, colorway, image, image_placeholder, release_date, retail_price, ticker, total_sales, url, year_high, year_low, avg_sale_price, premium)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """
                val = (self.brand, self.name, self.colorway, self.image, self.image_placeholder, self.release_date, self.retail_price, self.style, self.ticker, self.total_sales, self.url, self.year_high, self.year_low, self.avg_sale_price, self.premium)
                cur.execute(SQL, val)
                self.pk = cur.lastrowid