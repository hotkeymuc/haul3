# Python has decorators. Why not use them?

class entryExit(object):
	def __init__(self, f):
		self.f = f
	
	def __call__(self):
		print("Entering: " + self.f.__name__)
		self.f()
		print("Exited: " + self.f.__name__)
	

@entryExit
def func11():
	print("inside func11()")

@entryExit
def func12():
	print("inside func12()")

func11()
func12()



def entryExit2(f):
	def new_f():
		print("Entering " + f.__name__)
		f()
		print("Exited " + f.__name__)
	return new_f

@entryExit2
def func21():
	print("inside func21()")

@entryExit2
def func22():
	print("inside func22()")

func21()
func22()
print(func21.__name__)

