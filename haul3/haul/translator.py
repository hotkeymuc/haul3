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
		self.namespace = HAULNamespace(name='translator', parent=HAUL_ROOT_NAMESPACE)
		
	
	def process_lib(self, name, stream):
		self.libs.append(name)
		
		put('Scanning "{}"...'.format(name))
		lib_reader = self.ReaderClass(stream=stream, filename=name)
		lib_m = lib_reader.read_module(name=name, namespace=self.namespace, scan_only=True)
	
	def translate(self, name, stream_in, stream_out, close_stream=True):
		put('Translating "{}"...'.format(name))
		
		reader = self.ReaderClass(stream=stream_in, filename=name)
		
		monolithic = True	# Use simple (but good) monolithic version (True) or a memory friendly multi-pass streaming method (False)
		reader.seek(0)
		
		if (self.dialect == None):
			writer = self.WriterClass(stream_out)
		else:
			writer = self.WriterClass(stream_out, dialect=self.dialect)
		
		m = writer.stream(reader=reader, namespace=self.namespace, monolithic=monolithic)	# That's where the magic happens!
		
		if (close_stream): stream_out.close()
		return m
		
	
