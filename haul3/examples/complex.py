# I am currently testing annotations


### Let's start with some HAL code...
"""
2013-01-04
This was made way after SR1 and SR2
Idea: Self-parsing AST
Currently it is just a lexer, parser and generator

"""
#import os
#import copy
#import datetime

#@const mypi float 3.2

#@fun put
#@arg t String
def put(t):
	print(t)

class MyClassOne:
	"A unique identifier (e.g. function name, variable name, ...)"
	
	#@var name String
	
	#@fun __init__
	#@arg newName String
	def __init__(self, newName):
		self.name = newName
		#@var someOtherName String
		someOtherName = name
	
	#@fun test
	#@arg a int
	#@arg b int
	#@arg c int
	def test(self, a, b, c):
		print((str(a) + str(b)) + str(c))
	
	def test2(self):
		self.test(7,8,9)
	
	#@fun __repr__ String
	def __repr__(self):
		return str(self.name)
	

class TheSecond:
	"Simple value (e.g. of a variable or constant expression)"
	
	#@var data String
	
	def __init__(self):
		self.data = None	# binary
	
	#@fun __repr__ String
	def __repr__(self):
		return str(self.data)


class ThirdClass:
	"Some class"
	#@var ident MyClassOne
	#@var vals TheSecond []
	
	#@var name String
	def __init__(self, name):
		#@TODO: Static values?
		#@TODO: Inheritance?
		self.ident = MyClassOne(name)	#MyClassOne	name of module
		self.vals = []	#TheSecond[]	Global variables
		#idents = []	#MyClassOne[]	Global identifier database?
		#self.block = None	#SRBlock (or SRFunction, or self.funcs[0])


class TestClass:
	#@fun someMethod
	#@arg a int
	#@arg b int
	#@arg c int
	def someMethod(self, a,b,c):
		print("someMethod")

#@fun testFunc int
#@arg a1 int
#@arg a2 int
def testFunc(a1, a2):
	#@var m int
	m = a1 * a2
	print(str(a1))
	print(str(a1*6))
	print(str(a1*a2*3))
	return (a1 + a2)


### And now for some direct tests
put('Testing variable assignments...')

# "a" is a variable
#@var a int
a = 1

#@var b int
b = 5

# infer that
test = 0

#@var s str
s = "Hello"
if s == "Hello":
	print("String is what it should be!")
	# var test int
	test = 3

#@var c float
c = 3+4
#@var d int
d = (a + b) * 2
#@var x int
if (d > 6) and (b <= 10):
	x = 1
else:
	x = 2

if (d < 13) or (b > 13):
	x = 3

if d > 25:
	x = 3
elif d > 15:
	x = 2
elif d > 5:
	x = 1
else:
	x = 0

put('Testing "for"...')
#@var i int
for i in range(10):
	print(str(i))


put('Testing function calls...')



put('Testing class instantiation...')
#@var v TheSecond
v = TheSecond()
#v.data = "Test"	# @FIXME: Accessing remote namespaces from outside is problematic at streaming translation...

#unknownFunctionCall()	# Should raise a HALNamespaceError


testFunc(123, 456)

#@var e int
e = 6

put('Testing arrays...')
#@var ar int []
ar = [1,2,3]
ar[0] = 2



