# Testing HRES resources

#from hio import *
#from hres import *
import hres

print('hres_test.py...')

print('Using resources...')
#@var i1 int
i1 = hres.use('hres_data1.txt')
#@var i2 int
i2 = hres.use('hres_data2.txt')


print('Getting data from resources...')
#@var data str
data = hres.get(i1)
print('---------- DATA1 ----------')
print(data)
print('--------------------------')

data = hres.get(i2)
print('---------- DATA2 ----------')
print(data)
print('--------------------------')


print('hres_test.py end.')
#return 0
