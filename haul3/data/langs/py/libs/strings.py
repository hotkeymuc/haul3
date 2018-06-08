# HAUL strings

def startsWith(s, prefix):
	return s.startswith(prefix)

def sub(s, startIndex, endIndex):
	return s[startIndex:endIndex]

def rest(s, startIndex):
	return s[startIndex:]

def length(s):
	return len(s)

class _strings:
	def __init__(self, data):
		self.data = data
	def length(self):
		return len(self.data)
	def sub(self, startIndex, endIndex):
		return self.data[startIndex:endIndex]

def new(s):
	return _strings(s)

#print(str(startsWith('lala', 'lo')))
#print(sub('012345', 0, 0))