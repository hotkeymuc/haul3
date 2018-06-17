#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from utils import *

def put(t):
	print('HAULProject:\t' + str(t))

class HAULSource:
	def __init__(self, name, stream, uri=None):
		self.name = name
		self.stream = stream
		self.uri = uri
		
		self.dest_filename = None
	

class HAULProject:
	def __init__(self, name, package='wtf.haul'):
		self.name = name
		
		self.package = package
		self.version = '0.0.0'
		
		self.sources_path = '.'
		self.sources = []
		
		self.libs_path = 'libs'
		self.libs = []
		
		self.ress_path = 'data'
		self.ress = []
		
		self.dest_path = 'build'
		self.run_test = False
		self.merge = False
	
	def add_source(self, name=None, filename=None):
		if ((name == None) and (filename == None)):
			raise Exception('A name or filename has to be specified as source')
		
		if (name == None):
			# Guess name from filename if omitted
			name = name_by_filename(filename)
		
		if (filename == None):
			# Guess filename from name if omitted
			filename = self.sources_path + '/' + name.replace('.', '/') + '.py'
		
		source = HAULSource(name=name, stream=FileReader(filename), uri=filename)
		self.sources.append(source)
		
	
	def add_lib(self, name, filename=None):
		if (filename == None):
			# Guess default lib filename if omitted
			filename = os.path.join(self.libs_path, name + '.py')
		
		source = HAULSource(name=name, stream=FileReader(filename), uri=filename)
		self.libs.append(source)
		
	
	def add_res(self, name=None, filename=None):
		if ((name == None) and (filename == None)):
			raise Exception('A name or filename has to be specified as resource')
		
		if (name == None):
			# Guess name from filename if omitted
			name = name_by_filename(filename)
		if (filename == None):
			# Guess filename from name if omitted
			filename = os.path.join(self.sources_path, name)
		
		source = HAULSource(name=name, stream=FileReader(filename), uri=filename)
		self.ress.append(source)
		
	


