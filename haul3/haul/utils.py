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
def read_file(filename):
	#with open(filename, 'rb') as h: return h.read()
	h = open(filename, 'rb')
	data = h.read()
	h.close()
	return data

#@fun writeFile
#@arg filename str
#@arg data str
def write_file(filename, data):
	#with open(filename, 'wb') as h: h.write(data)
	h = open(filename, 'wb')
	h.write(data)
	h.close()
	


#@fun name_by_filename str
#@arg inputFilename str
def name_by_filename(inputFilename):
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

class FileReader:
	#@var has_peek bool
	#@var peeked str
	#@var ofs int
	#@var is_eof bool
	#@var h #hnd
	
	#@fun __init__
	#@arg filename str
	def __init__(self, filename):
		self.has_peek = False
		self.peeked = None
		self.is_eof = False
		self.ofs = 0
		self.h = open(filename, 'rb')
	
	def __del__(self):
		self.h.close()
	
	#@fun eof bool
	def eof(self):
		return self.is_eof
	
	#@fun seek
	#@arg ofs int
	def seek(self, ofs):
		self.h.seek(ofs)
		self.has_peek = False
	
	#@fun get str
	def get(self):
		#@var r str
		
		if (self.eof()): return ''
		if (self.has_peek == True):
			self.has_peek = False
			return self.peeked
		
		self.has_peek = False
		
		r = self.h.read(1)
		self.ofs = self.ofs + 1
		if (r == ''):
			self.is_eof = True
		return r
	
	#@fun peek str
	def peek(self):
		#@var r str
		
		if (self.eof()): return ''
		if (self.has_peek):
			return self.peeked
		
		r = self.h.read(1)
		self.ofs = self.ofs + 1
		if (r == ''): self.is_eof = True
		
		self.peeked = r
		self.has_peek = True
		return r
	

class FileWriter:
	#@var h #hnd
	#@var size int
	
	def __init__(self, filename):
		self.size = 0
		self.h = open(filename, 'wb+')
	
	def close(self):
		self.h.close()
	
	def __del__(self):
		self.h.close()
	
	#@fun put
	#@arg data str
	def put(self, data):
		self.h.write(data)
		self.size = self.size + len(data)
	