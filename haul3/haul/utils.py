#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Commonly used functions
"""

def put(t):
	print(str(t))


def readFile(filename):
	with open(filename, 'rb') as h:
		data = h.read()
		h.close()
	return data

def writeFile(filename, data):
	with open(filename, 'wb') as h:
		h.write(data)
		h.close()


def str_pos(haystack, needle):
	if needle in haystack:
		return haystack.index(needle)
	return -1

def nameByFilename(inputFilename):
	# Create human readable name from filename
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
	def __init__(self, data):
		self.data = data
		self.ofs = 0
		self.len = len(data)
	
	def eof(self):
		return (self.ofs >= self.len)
	
	def seek(self, ofs):
		#put('StringReader seeking to ' + str(ofs) + '...')
		self.ofs = ofs
	
	def get(self):
		if (self.eof()): return None
		r = self.data[self.ofs]
		self.ofs += 1
		return r
	
	def peek(self):
		if (self.eof()): return None
		return self.data[self.ofs]
	
class StringWriter:
	def __init__(self):
		self.r = ''
		self.size = 0
	
	def put(self, data):
		self.r += data
		self.size += len(data)

