# Small test file

from hio import *

###import sys
###from sys import *

#@fun foo int
#@arg a int
#@arg b int
def foo(a, b=3):
	#@var m int
	# Start easy: set m to a1
	m = a
	#m=o # error forced
	# Output m.
	#put(str(m))
	#put(float_str(m))
	put(int_str(m))
	
	# Now using two arguments
	m = a * b
	put(int_str(m))
	return (a + b + m)

#@fun bar int
#@arg f1 int
def bar(f1):
	put("Hello bar!")
	return 4

"""
class MyClass:
	#@var name str
	
	#@fun setName
	#@arg n str
	def setName(self, n):
		self.name = n
"""

### Main:
pass	# The main block must start with an instruction, or else the first annotation could be skipped or interpreted in "module" scope (instead of "block" scope)
put('Hello world.')
shout('Shout')

put(int_str(1))
put(int_str(2))
put(int_str(3))

"""
# @ var cl MyClass
cl = MyClass()
cl.name = "some name"
"""

#@var a int
a = 1

#@var b int
b = 5

# @ v ar c float
# c = (a + b) / 2
#@var c int
c = (a + b)

#@var x int
#if (c > 6.0) and (c <= 10.0): x = 1
if (c > 6) and (c <= 10): x = 1

a = 1
put_('a:=1=')
put(int_str(a))

a = -1
put_('a:=-1=')
put(int_str(a))


a = 127
put_('a:=127=')
put(int_str(a))

a = 128
put_('a:=128=')
put(int_str(a))


a = 255
put_('a:=255=')
put(int_str(a))

a = 256
put_('a:=256=')
put(int_str(a))

a = 32767
put_('a:=32767=')
put(int_str(a))

## This is "out of range" for TurboPascal (DOS)
#a = 32768
#put_('a:=32768=')
#put(int_str(a))


foo(123, 3)

bar(1234)


#@var s str
put_('Enter something!')
s = fetch()
shout(s)

shout('small.py end.')
#return 0
