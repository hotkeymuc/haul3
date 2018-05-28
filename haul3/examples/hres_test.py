# Testing HRES resources

from hio import *
from hres import *
#import sys
#from sys import *

shout('hres_test.py...')

put('Using resources...')
#@var i1 int
i1 = hres.use('hres_data1.txt')
#@var i2 int
i2 = hres.use('hres_data2.txt')


put('Getting data from resources...')
#@var data str
data = hres.get(i1)
put('---------- DATA1 ----------')
put(data)
put('--------------------------')

data = hres.get(i2)
put('---------- DATA2 ----------')
put(data)
put('--------------------------')


shout('hres_test.py end.')
#return 0
