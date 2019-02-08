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

print(price_premium('$130','$188'))