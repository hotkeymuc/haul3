# Small test file

class MyClass:
	#@var name str
	
	#@fun setName
	#@arg n str
	def setName(self, n):
		self.name = n
		#@var someLocal str
		someLocal = (self.name)

class SecondClass(MyClass):
	#@var name2 str
	
	def otherMethod(self):
		return 5
		

# Main:
print('Begin...')

#@var c MyClass
c = MyClass()
c.name = "some name"
c.setName("set via method")

print("Name: \"" + c.name + "\"")