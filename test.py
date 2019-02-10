
import time
from datetime import datetime


ts = time.time() 
time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

print(time.split(' ')[0])