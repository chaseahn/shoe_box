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

full_file = "/Users/ahn.ch/Projects/shoe_data/run/src/json/missing.json"

def run(dbname="shoebox.db"):
    conn = sqlite3.connect(dbname)
    cur  = conn.cursor()

    PARENT_SQL = """INSERT INTO sneakers (
                brand, 
                name,
                colorway,
                description,
                image,
                release_date,
                retail_price,
                style,
                ticker,
                total_sales,
                url,
                year_high,
                year_low,
                avg_sale_price,
                premium
            ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """


    # importing the raw data json file created through a scrape of TFB html
    dcty = load_dictionary(full_file)

    for key in dcty.keys():

        if key.split('-')[0] == 'nke':
            brand = 'nike'
        elif key.split('-')[0] == 'ads':
            brand = 'adidas'
        elif key.split('-')[0] == 'jrd':
            brand = 'jordan'
        elif key.split('-')[0] == 'otb':
            brand = 'other'
        else:
            pass

        premium = price_premium(dcty[key]['retail_price'],dcty[key]['avg_sale_price'])

        name = dcty[key]['name'].replace('?','')

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
        par_sql_values = (brand, name, dcty[key]['colorway'], 
            dcty[key]['description'], dcty[key]['image'], 
            dcty[key]['release_date'], new_retailPrice, 
            dcty[key]['style'], dcty[key]['ticker'],total_sales, 
            dcty[key]['url'], new_yearHigh, new_yearLow,new_avgSalePrice,premium)
        cur.execute(PARENT_SQL, par_sql_values)


    conn.commit()
    conn.close()

if __name__ == "__main__":
    run()