import sqlite3
import json
from pprint import pprint


def load_dictionary(filename):
    """imports json file as a dictionary"""
    with open(filename, 'r') as json_file:
        return json.load(json_file)

def price_premium(retail,average):
    if retail == '--' or average == '--':
        return None
    else:
        intRetail = retail.strip('$')
        new_intRetail = intRetail.replace(',','')
        final_intRetail = int(new_intRetail)
        intAverage = average.strip('$')
        new_intAverage = intAverage.replace(',','')
        final_intAverage = int(new_intAverage)
        premium = round((((final_intAverage/final_intRetail)-1)*100),2)
        return premium

full_file = "/Users/ahn.ch/Projects/shoe_data/run/src/json/total190130.json"

def run(dbname="shoebox.db"):
    conn = sqlite3.connect(dbname)
    cur  = conn.cursor()

    PARENT_SQL = """INSERT INTO sneakers (
                brand,
                type,
                name,
                colorway,
                image,
                release_date,
                retail_price,
                ticker,
                total_sales,
                url,
                year_high,
                year_low,clea
                avg_sale_price,
                premium
            ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """


    # importing the raw data json file created through a scrape of TFB html
    dcty = load_dictionary(full_file)

    for key in dcty.keys():

        premium = price_premium(dcty[key]['retail_price'],dcty[key]['avg_sale_price'])

        name = key

        brand = dcty[key]['brand']

        if 'Harden' in name.split(' '):
            type = 'Harden'
        elif 'Curry' in name.split(' '):
            type = 'Curry'
        elif 'PG' in name.split(' '):
            type = 'PG'
        elif 'Westbrook' in name.split(' '):
            type = 'Westbrook'
        elif 'Kyrie' in name.split(' '):
            type = 'Kyrie'
        elif 'Dame' in name.split(' '):
            type = 'Dame'
        else:
            type = dcty[key]['type']

        total_sales = dcty[key]['total_sales'].replace(',','')
        
        retailPrice = dcty[key]['retail_price'].strip('$')
        new_retailPrice = retailPrice.replace(',','')

        avgSalePrice = dcty[key]['avg_sale_price'].strip('$')
        new_avgSalePrice = avgSalePrice.replace(',','')

        yearHigh = dcty[key]['year_high'].strip('$')
        new_yearHigh = yearHigh.replace(',','')

        yearLow = dcty[key]['year_low'].strip('$')
        new_yearLow = yearLow.replace(',','')

        # populate all values in parent_ingredients table
        par_sql_values = (brand, dcty[key]['type'], name, dcty[key]['colorway'], dcty[key]['image'], 
            dcty[key]['release_date'], new_retailPrice, dcty[key]['ticker'],total_sales, 
            dcty[key]['url'], new_yearHigh, new_yearLow,new_avgSalePrice,premium)
        cur.execute(PARENT_SQL, par_sql_values)


    conn.commit()
    conn.close()

if __name__ == "__main__":
    run()