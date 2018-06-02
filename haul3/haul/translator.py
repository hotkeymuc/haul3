#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# -*- coding: UTF-8 -*-


#from utils import *
from haul import *


def put(t):
	print('HAULTranslator:\t' + str(t))


class HAULTranslator:
	"Provides the functionality to build a HAUL file for another platform. Like make etc."
	
	def __init__(self, ReaderClass, WriterClass, dialect=None):
		self.ReaderClass = ReaderClass
		self.WriterClass = WriterClass
		self.dialect = dialect
		self.libs = []
		self.namespace = HAULNamespace(name='translator', parent=rootNamespace)
		#self.namespace = HAULNamespace(name='translator', parent=HAUL_ROOT_NAMESPACE)
	
	def process_lib(self, name, stream):
		self.libs.append(name)
		
		lib_reader = self.ReaderClass(stream=stream, name=name)
		lib_m = lib_reader.read_module(name=name, namespace=self.namespace, scan_only=True)
	
	def translate(self, name, stream_in, stream_out):
		put('Translating "' + name + '"...')
		
		reader = self.ReaderClass(stream=stream_in, name=name)
		
		monolithic = True	# Use simple (but good) monolithic version (True) or a memory friendly multi-pass streaming method (False)
		#reader.seek(0)
		
		if (dialect == None):
			writer = self.WriterClass(streamOut)
		else:
			writer = self.WriterClass(streamOut, dialect=dialect)
		
		m = writer.stream(reader=reader, namespace=self.namespace, monolithic=monolithic)	# That's where the magic happens!
		
		return m
		
	
