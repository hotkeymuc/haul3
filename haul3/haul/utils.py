#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Commonly used functions
"""

#@fun put 
#@arg t str
def put(t):
	print(t)

#@fun readFile str
#@arg filename str
def readFile(filename):
	#with open(filename, 'rb') as h: return h.read()
	h = open(filename, 'rb')
	data = h.read()
	h.close()
	return data

#@fun writeFile
#@arg filename str
#@arg data str
def writeFile(filename, data):
	#with open(filename, 'wb') as h: h.write(data)
	h = open(filename, 'wb')
	h.write(data)
	h.close()
	


#@fun nameByFilename str
#@arg inputFilename str
def nameByFilename(inputFilename):
	# Create human readable name from filename
	
	#@var inputName str
	inputName = inputFilename
	p = inputName.rfind('/')
	if p > -1:
		inputName = inputName[p+1:]
	p = inputName.rfind('.')
	if p > -1:
		inputName = inputName[:p]
	return inputName



class StringReader:
	"Just a naive Stream implementation for quick and dirty testing."
	#@var data str
	#@var ofs int
	#@var len int
	
	#@fun __init__
	#@arg data str
	def __init__(self, data):
		self.data = data
		self.ofs = 0
		self.len = len(data)
	
	#@fun eof bool
	def eof(self):
		return (self.ofs >= self.len)
	
	#@fun seek
	#@arg ofs int
	def seek(self, ofs):
		#put('StringReader seeking to ' + str(ofs) + '...')
		self.ofs = ofs
	
	#@fun get str
	def get(self):
		if (self.eof()): return None
		r = self.data[self.ofs]
		self.ofs = self.ofs + 1
		return r
	
	#@fun peek str
	def peek(self):
		if (self.eof()): return None
		return self.data[self.ofs]
	
class StringWriter:
	#@var r str
	#@var size int
	def __init__(self):
		self.r = ''
		self.size = 0
	
	#@fun put
	#@arg data str
	def put(self, data):
		self.r = self.r + data
		self.size = self.size + len(data)

