

from bs4 import BeautifulSoup
from selenium import webdriver

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

url='https://www.stockx.com/adidas-nmd-pharrell-hu-human-race-yellow'
url2 = 'https://stockx.com/air-max-1-animal-pack'


# chrome_options = Options()  
# chrome_options.add_argument("--headless")  
# chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
# chrome_options.binary_location = CHROME_PATH

driver = webdriver.Chrome('/Users/ahn.ch/Downloads/chromedriver')
driver.get(url)


driver_html = driver.page_source
table_soup = BeautifulSoup(driver_html,features="html.parser")
latest_sales = table_soup.find('table', {'id': 'latest-sales-table'}).get_text()
d = tsplit(latest_sales,('SizeSale PriceDateTime',' EST','Monday', 'Sunday', 'Tuesday', 'Wednesday', 'Friday', 'Thursday', 'Saturday', '$', ',  ', ', 2019', ', 2018', ', 2017'))
sales_data = [[d[1],d[2]],[d[5],d[6]],[d[9],d[10]],[d[13],d[14]],[d[17],d[18]],[d[21],d[22]],[d[25],d[26]],[d[29],d[30]],[d[33],d[34]],[d[37],d[38]]]

print(sales_data)


