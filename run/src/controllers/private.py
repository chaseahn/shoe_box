#!/usr/bin/env python3


import os
import urllib.request
import requests
import pygal

from bs4 import BeautifulSoup
from collections import Counter
from pygal.style import Style

from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from time import gmtime, strftime

from ..models.model import User, ShoeBox, Sneaker

elekid = Blueprint('private',__name__,url_prefix='/2492')

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

def add_dict_total(dict, val):
    """VAL is a parameter to search for price_bought,
       value and profit which are values in shoebox dict"""
    sum_list = []
    for key in dict.keys():
        if val == 'value':
            if dict[key]['type'] != 'SELL':
                sum_list.append(dict[key][val])
        else:
            sum_list.append(dict[key][val])
    return sum(sum_list)

def scrape_new_shoe(url):
    try:
        """CONTAINERS"""
        shoe_html = requests.get(url).content
        shoe_soup = BeautifulSoup(shoe_html, 'html.parser')
        shoe_container = shoe_soup.find("div", {"class": "product-view"})
        header_stat = shoe_container.find_all('div', {'class': 'header-stat'})
        """HEADER INFO"""
        name = shoe_container.find('h1').get_text().replace('/','-').strip()
        new_name = name.replace('?','')
        image = shoe_container.find('div', {'class': 'product-media'}).img['src']
        ticker = header_stat[1].get_text().strip().split(' ')[1]
        """PRODUCT INFO"""
        product_info = shoe_container.find('div', {'class': 'product-info'}).get_text().strip()
        product_data = tsplit(product_info,('Style ',' Colorway ',' Retail Price ', ' Release Date '))
        colorway = product_data[2]
        retail_price = product_data[3]
        release_date = product_data[4][:10]
        """MARKET INFO"""
        market_summary = shoe_container.find('div', {'class': 'product-market-summary'}).get_text().strip()
        market_data = tsplit(market_summary,('52 Week High ',' | Low ','Trade Range (12 Mos.)','Volatility'))
        year_high = market_data[1]
        year_low = market_data[2]
        trade_range = market_data[3]
        """HISTORICAL"""
        twelve_month_historical = shoe_container.find('div', {'class': 'gauges'}).get_text().strip()
        twelve_data = tsplit(twelve_month_historical,('# of Sales','Price Premium(Over Original Retail Price)','Average Sale Price'))
        total_sales = twelve_data[1]
        avg_sale_price = twelve_data[3]
        """BRAND INFO"""
        trail = shoe_container.find('div', {'class': 'grails-crumbs'}).get_text()
        identifier = trail[12:13]

        if identifier == 'O':
            brand = 'Other'
        elif identifier == 'a':
            brand = 'Adidas'
        elif identifier == 'N':
            brand = 'Nike'
        elif identifier == 'J':
            brand = 'Jordan'
        else:
            brand = 'Other'

        new_totalSales = total_sales.replace(',','')
        
        retailPrice = retail_price.strip('$')
        new_retailPrice = retailPrice.replace(',','')

        avgSalePrice = avg_sale_price.strip('$')
        new_avgSalePrice = avgSalePrice.replace(',','')

        yearHigh = year_high.strip('$')
        new_yearHigh = yearHigh.replace(',','')

        yearLow = year_low.strip('$')
        new_yearLow = yearLow.replace(',','')

        if 'Harden' in name.split(' ') and brand != 'Nike':
            type = 'Harden'
        elif 'Curry' in name.split(' ') and brand != 'Nike':
            type = 'Curry'
        elif 'PG' in name.split(' '):
            type = 'PG'
        elif 'Westbrook' in name.split(' '):
            type = 'Westbrook'
        elif 'Kyrie' in name.split(' '):
            type = 'Kyrie'
        elif 'Dame' in name.split(' '):
            type = 'Dame'
        elif 'React' in name.split(' '):
            type = 'React'
        elif 'Foamposite' in name.split(' '):
            type = 'Foamposite'
        elif 'NMD' in name.split(' '):
            type = 'NMD'
        elif 'Ultra Boost' in name.split(' ') or 'UltraBoost' in name.split(' '):
            type = 'Ultraboost'
        elif 'Air Force' in name.split(' '):
            type = 'Air Force'
        elif 'Air Max' in name.split(' '):
            type = 'Air Max'
        elif 'SB' in name.split(' '):
            type = 'SB'
        elif 'React' in name.split(' '):
            type = 'React'
        elif 'Foamposite' in name.split(' '):
            type = 'Foamposite'
        elif 'KD' in name.split(' '):
            type = 'KD'
        elif 'Lebron' in name.split(' ') or 'UltraBoost' in name.split(' '):
            type = 'Lebron'
        elif 'Kobe' in name.split(' '):
            type = 'Kobe'
        elif 'Yeezy' in name.split(' '):
            type = 'Yeezy'
        elif 'Jordan' in name.split(' ') and '1' in name.split(' '):
            type = '1'
        elif 'Jordan' in name.split(' ') and '2' in name.split(' '):
            type = '2'
        elif 'Jordan' in name.split(' ') and '3' in name.split(' '):
            type = '3'
        elif 'Jordan' in name.split(' ') and '4' in name.split(' '):
            type = '4'
        elif 'Jordan' in name.split(' ') and '5' in name.split(' '):
            type = '5'
        elif 'Jordan' in name.split(' ') and '6' in name.split(' '):
            type = '6'
        else:
            type = 'Other'

        if new_avgSalePrice == '--' or new_retailPrice =='--':
            premium = None
        else:
            value = (float(new_avgSalePrice)-float(new_retailPrice))/float(new_retailPrice)
            premium = '{:.2f}'.format(value*100)

        data = { 
                "name" : new_name,
                "url" : url,
                "brand": brand,
                "type": type,
                "image" : image,
                "image_placeholder" : '--',
                "ticker" : ticker,
                "colorway" : colorway,
                "retail_price" : new_retailPrice,
                "release_date" : release_date,
                "year_high" : new_yearHigh,
                "year_low" : new_yearLow,
                "trade_range" : trade_range,
                "total_sales" : new_totalSales,
                "avg_sale_price" : new_avgSalePrice,
                "premium" : premium
            }

    except AttributeError:
        print('attribute error trying again')
        scrape_new_shoe(url)

    except IndexError:
        print('index error, try a valid url')
        data = {}
    
    return data

def insert_shoe_to_db(data):
    sneaker = Sneaker()
    sneaker.brand	          = data['brand']
    sneaker.type              = data['type']
    sneaker.name              = data['name']
    sneaker.colorway          = data['colorway']	
    sneaker.image             = data['image'] 
    sneaker.image_placeholder = data['image_placeholder'] 
    sneaker.release_date      = data['release_date'] 
    sneaker.retail_price      = data['retail_price']
    sneaker.ticker            = data['ticker']
    sneaker.total_sales       = data['total_sales']
    sneaker.url               = data['url'] 
    sneaker.year_high         = data['year_high']
    sneaker.year_low          = data['year_low']
    sneaker.avg_sale_price    = data['avg_sale_price']
    sneaker.premium           = data['premium']
    sneaker.save(data['name'])

def download_sneaker_img(data):
    img_link = data['image']
    print(img_link)
    name = data['name']
            
    if 'Placeholder' in img_link.split('-'):

        placeholder = open('/Users/ahn.ch/Desktop/sb_placeholder.jpg')
        f = open('run/src/static/{}.jpg'.format(name),'wb')
        f.write(placeholder.read())
        f.close()

        print('Placeholder Added')

    else:
        picture_request = requests.get(img_link)
        if picture_request.status_code == 200:
            with open("run/src/static/{}.jpg".format(name), 'wb') as f:
                f.write(picture_request.content)

def account_pairing_scores(pk):

    user = User()
    account_preferences = user.get_account_preferences(pk)
    other_preferences = user.get_other_account_preferences(pk)

    print(account_preferences)
    print(other_preferences)

    pairing_scores = []
    for key,value in account_preferences.items():

        user_brand = account_preferences[key]['brand']
        user_color = account_preferences[key]['color']
        
        for key, value in other_preferences.items():

            brand_score, color_score = 0, 0

            for brand in other_preferences[key]['brand']:
                if brand in user_brand:
                    brand_score += 18
            for color in other_preferences[key]['color']:
                if color in user_color:
                    color_score += 12
            
            pairing_scores.append((key,(brand_score+color_score)))

    sorted_pairing_scores = sorted(pairing_scores, key=lambda x:x[1])[::-1]
    pk1 = sorted_pairing_scores[0][0]
    pk2 = sorted_pairing_scores[1][0]
    return [pk1,pk2]

def shoebox_graph_labels(box, val):
    date_labels = []
    num_labels = []
    values = []
  
    for key in box.keys():
        if box[key]['date'] not in date_labels:
            date_labels.append(box[key]['date'])
    if val == 'value':
        for key in box.keys():
            for i in range(len(date_labels)):
                if box[key]['date'] == date_labels[i]:
                    if box[key]['type'] != 'SELL':
                        num_labels.append({box[key]['date']: box[key]['{}'.format(val)]})
                    else:
                        num_labels.append({box[key]['date']: 0 })
                else:
                    pass
    elif val == 'profit':
        for key in box.keys():
            for i in range(len(date_labels)):
                if box[key]['date'] == date_labels[i]:
                    num_labels.append({box[key]['date']: box[key]['{}'.format(val)]})
                else:
                    pass

    print(date_labels)
    print(num_labels)
    print(values)
    c = Counter()
    for d in num_labels:
        c.update(d)

    result = [{key: value} for key, value in c.items()]
    
    for vals in result:
        for key in vals.keys():
            values.append(vals[key])
    
    final = [sum(values[:i+1]) for i in range(len(values))]
    print(final)


    return [date_labels,final]


@elekid.route('/account',methods=['GET','POST'])
def account():
    if request.method == 'GET':
        try:
            """
            ~~~~~~~~~
            USER INFO
            ~~~~~~~~~
            """
            user    = User({'username': session['username'], 
                            'pk': session['pk'], 'age': session['age'], 
                            'gender': session['gender']})
            favList = user.display_favorites()
            shoebox = user.display_shoebox()
            spent   = add_dict_total(shoebox, 'price_bought')
            worth   = add_dict_total(shoebox, 'value')
            profit  = add_dict_total(shoebox, 'profit')

            """
            ~~~~~~~~~~~
            PyGAL CHART
            ~~~~~~~~~~~
            """
            label_list = shoebox_graph_labels(shoebox, 'value')
            profit_list = shoebox_graph_labels(shoebox, 'profit')

            date_label = label_list[0]
            value_label = label_list[1]
            profit_label = profit_list[1]

            print(value_label)
            print(profit_label)

            custom_style = Style(
                colors = ('purple')
            )

            line_chart = pygal.Line(fill=True,explicit_size=True, height=500,width=500,style=custom_style)
            line_chart.x_labels = date_label
            line_chart.add('Box Value', value_label)
            line_chart.render()

            line_chart_profit = pygal.Line(fill=True, explicit_size=True, height=500,width=500)
            line_chart_profit.x_labels = date_label
            line_chart_profit.add('Profit', profit_label)
            line_chart_profit.render()
            
            return render_template('private/account.html',
                                    favList = favList,
                                    shoebox=shoebox, 
                                    profit  = profit, 
                                    spent   = spent, 
                                    worth   = worth,
                                    chart   = line_chart,
                                    chart2  = line_chart_profit )
        except KeyError:
            return redirect('/register')
    elif request.method == 'POST':
        if request.form['post_button'].split('-')[0] == 'Update':
            box_pk   = request.form['post_button'].split('-')[1]
            box      = ShoeBox(pk=box_pk)
            shoeName = box.shoename
            return redirect('/update-box/'+box_pk+'/'+shoeName)
        elif request.form['post_button'].split('-')[0] == 'Remove':
            box_pk = request.form['post_button'].split('-')[1]
            box = ShoeBox(pk=box_pk)
            box.remove(box_pk)
            user = User({'username': session['username'], 
                         'pk': session['pk'], 'age': session['age'], 
                         'gender': session['gender']})
            favList = user.display_favorites()
            shoebox = user.display_shoebox()
            spent   = add_dict_total(shoebox, 'price_bought')
            worth   = add_dict_total(shoebox, 'value')
            profit  = add_dict_total(shoebox, 'profit')
            label_list = shoebox_graph_labels(shoebox, 'value')
            profit_list = shoebox_graph_labels(shoebox, 'profit')

            date_label = label_list[0]
            value_label = label_list[1]
            profit_label = profit_list[1]

            print(value_label)
            print(profit_label)

            line_chart = pygal.Line(fill=True,explicit_size=True, height=500,width=500)
            line_chart.x_labels = date_label
            line_chart.add('Box Value', value_label)
            line_chart.render()

            line_chart_profit = pygal.Line(fill=True,explicit_size=True, height=500,width=500)
            line_chart_profit.x_labels = date_label
            line_chart_profit.add('Profit', profit_label)
            line_chart_profit.render()
            return render_template('private/account.html',
                                    favList = favList,shoebox=shoebox, 
                                    profit  = profit, 
                                    spent   = spent, 
                                    worth   = worth,
                                    chart   = line_chart,
                                    chart2  = line_chart_profit )
    else:
        pass

@elekid.route('/favorites',methods=['GET','POST'])
def favorites():
    if request.method == 'GET':
        try:
            """
            ~~~~~~~~~
            USER INFO
            ~~~~~~~~~
            """
            user    = User({'username': session['username'], 
                            'pk': session['pk'], 'age': session['age'], 
                            'gender': session['gender']})
            favList = user.display_favorites()

            like_account = account_pairing_scores(user.pk)
            pk1 = like_account[0]
            pk2 = like_account[1]
            print(pk1)

            u = User()
            recList = u.display_reccomendations(pk1,pk2)

            print(recList)

            return render_template('private/favorites.html',
                                    favList = favList,
                                    recList = recList )
        except KeyError:
            return redirect('/register')
    elif request.method == 'POST':
        pass
    else:
        pass


@elekid.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        return render_template('/private/upload.html')
    elif request.method == 'POST':
        name = request.form['url']
        print(name)
        lower_name = name.lower().split(' ')
        print(lower_name)
        join_name = '-'.join(lower_name)
        print(join_name)
        url = 'https://stockx.com/'+str(join_name)
        print(url)
        sneaker = Sneaker()
        shoeData = scrape_new_shoe(url)
        if not sneaker.existing(shoeData['name']):
            download_sneaker_img(shoeData)
            print('.')
            print('.')
            print('.')
            print('DOWNLOADED IMAGE: {}'.format(shoeData['image']))
            print('.')
            print('.')
            print('.')
            print('.')
            print('.')
            print('.')
            insert_shoe_to_db(shoeData)
            print('ADDED SHOE TO DATABASE - CONGRATS DUDE')
            print('.')
            print('.')
            print('.')
            print('.')
            print('.')
            print('.')
            return redirect('/add/success')
        else:
            return render_template('/private/upload.html', 
                                message='Shoe Exists Homie!')
    else:
        pass
    