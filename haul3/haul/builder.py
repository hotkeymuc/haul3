#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil

import subprocess	# for running commands

from utils import *
from core import HAULParseError, HAULNamespace, HAUL_ROOT_NAMESPACE

def put(t):
	print('HAULBuilder:\t' + str(t))


class HAULBuildError(Exception):
	pass



class HAULTranslator:
	"Provides the functionality to compile a HAUL file to another platform. Like make etc."
	
	#@var ReaderClass HAULReader
	#@var WriterClass HAULWriter
	#@var libs arr str
	#@var dialect str
	#@var namespace HAULNamespace
	
	def __init__(self, ReaderClass, WriterClass, dialect=None):
		self.ReaderClass = ReaderClass
		self.WriterClass = WriterClass
		self.dialect = dialect
		self.libs = []
		
		# For the sake of compilation we could also clone the HAUL_ROOT_NAMESPACE and write directly to it
		#self.namespace = HAUL_ROOT_NAMESPACE.clone()
		self.namespace = HAULNamespace(name='translator', parent=HAUL_ROOT_NAMESPACE)
		
	
	#@fun process_lib HAULModule
	#@arg name str
	#@arg stream_out #hnd
	#@arg filename str
	def process_lib(self, name, stream_in, filename=None):
		"Read and parse the given file"
		self.libs.append(name)
		
		if (filename == None):
			filename = name + '.py'	#self.ReaderClass.default_extension
		
		#put('Scanning "{}"...'.format(name))
		lib_reader = self.ReaderClass(stream=stream_in, filename=name)
		lib_m = lib_reader.read_module(name=name, namespace=self.namespace, scan_only=True)
		return lib_m
	
	#@fun translate_source HAULModule
	#@arg name str
	#@arg stream_in #hnd
	#@arg stream_out #hnd
	#@arg close_stream bool True
	def translate_source(self, source, stream_out, close_stream=True):
		#put('Translating "{}" from "{}" to "{}"...'.format(name, stream_in.filename, stream_out.filename))
		
		reader = self.ReaderClass(stream=source.stream, filename=source.uri)
		
		monolithic = True	# Use simple (but good) monolithic version (True) or a memory friendly multi-pass streaming method (False)
		reader.seek(0)
		
		#@var writer HAULWriter
		if (self.dialect == None):
			writer = self.WriterClass(stream_out)
		else:
			writer = self.WriterClass(stream_out, dialect=self.dialect)
		
		m = writer.stream(reader=reader, name=source.name, namespace=self.namespace, monolithic=monolithic)	# That's where the magic happens!
		
		if (close_stream): stream_out.close()
		return m
		
	
	#@fun translate_project
	#@arg project HAULProject
	def translate_project(self, project, output_path=None, dest_extension=None, stream_out_single=None):
		
		if (stream_out_single == None):
			put('Checking source filenames...')
			for s in project.sources:
				# Each file to own output file
				if (s.dest_filename == None):
					# Assume default names
					s.dest_filename = os.path.abspath(os.path.join(output_path, s.name.replace('.', '/') + '.' + dest_extension))
					put('Assigned automatic filename "{}"'.format(s.dest_filename))
					
				
			
		
		put('Processing libs...')
		for s in project.libs:
			self.process_lib(name=s.name, stream_in=s.stream, filename=s.uri)
		
		#@var m HAULModule
		m = None
		
		put('Translating source(s)...')
		for s in project.sources:
			#try:
				if (stream_out_single == None):
					
					path = os.path.dirname(s.dest_filename)
					if (os.path.exists(path) == False):
						os.makedirs(path)
					
					stream_out = FileWriter(s.dest_filename)
					
					m = self.translate_source(s, stream_out, close_stream=True)
				else:
					# All files into one stream
					m = self.translate_source(s, stream_out_single, close_stream=False)
					
			#except HAULParseError as e:
			#	raise Exception('Cannot translate "{}": {} in {}'.format(s.uri, e.message, str(e.token)))
			#	return None
		
		# Return last translated module, which is most likely the main module
		return m
	



class HAULBuilder:
	"Provides the functionality to build a HAUL file for another platform. Like make etc."
	
	def __init__(self, platform, lang):
		self.platform = platform
		self.lang = lang
		
		self.project = None
		self.translator = None
		
		self.data_path = 'data'
		self.staging_path = 'staging'
		self.output_path = 'build'
		self.tools_path = 'tools'
		
	
	### File system abstraction
	def exists(self, filename):
		return (os.path.isfile(filename))
	
	def exists_dir(self, path):
		return os.path.exists(path)
	
	def mkdir(self, path):
		if (self.exists_dir(path) == False):
			os.makedirs(path)
	
	def chdir(self, path):
		os.chdir(path)
	
	def copy(self, source_filename, dest_filename):
		shutil.copy(source_filename, dest_filename)
	
	def clean(self, path):
		"Make sure the path exists and is empty. Delete all files and folders within."
		
		if not os.path.isdir(path):
			self.mkdir(path)
		
		for root, dirs, files in os.walk(path):
			for f in files:
				os.unlink(os.path.join(root, f))
			for d in dirs:
				p = os.path.join(root, d)
				self.clean(p)	# Recurse
				shutil.rmtree(p)
		
	def rm(self, filename):
		"delete given filename"
		os.unlink(filename)
	def rm_if_exists(self, filename):
		"delete if exists"
		if os.path.isfile(filename):
			self.rm(filename)
	
	def touch(self, filename, data=''):
		"put data into file / create empty file"
		with open(filename, 'wb+') as h:
			if (len(data) > 0): h.write(data)
	
	def type(self, filename):
		"read file"
		with open(filename, 'rb') as h:
			return h.read()
	
	def command(self, cmd, faf=False, env=None):	# faf = fire and forget (i.e. run in background)
		"Execute command"
		put('Running "' + str(cmd) + '"...')
		if faf:
			subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, env=env)
			return None
		else:
			return subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, env=env).stdout.read()
	
	def get_path(self, name, default):
		r = None
		
		if (name in os.environ):
			r = os.environ[name]
		
		if ((r == None) or (self.exists_dir(r) == False)):
			raise HAULBuildError('Set {} to a valid path. Tried "{}", but did not exist.'.format(name, default))
			return None
		
		return r
	
	def name_to_8(self, n):
		if ('.' in n):
			p = n.rfind('.')
			n = n[p+1:]
		
		return n[0:8]
	
	
	### User interface
	
	def set_translator(self, t):
		self.translator = t
	
	def translate_project(self, output_path=None, dest_extension=None, stream_out_single=None):
		"Translate the loaded project using the given translator. If stream_out_single is given, all files are written to that stream instead of individual files."
		m = None
		
		if (output_path == None):
			output_path = self.staging_path
		
		if (dest_extension == None):
			dest_extension = self.lang
		
		m = self.translator.translate_project(self.project, output_path=output_path, dest_extension=dest_extension, stream_out_single=stream_out_single)
		
		# Return last translated module, which is most likely the main module
		return m
	
	"""
	def translate(self, name, source_filename, dest_filename, DestWriterClass, dialect=None):
		
		put('Translating file "' + source_filename + '" to "' + dest_filename + '"...')
		stream_in = self.stream_from_file(source_filename)
		
		reader = HAULReader_py(stream_in, name)
		monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
		reader.seek(0)
		stream_out = StringWriter()
		
		if (dialect == None):
			writer = DestWriterClass(stream_out)
		else:
			writer = DestWriterClass(stream_out, dialect=dialect)
		
		try:
			m = writer.stream(reader, name, namespace=self.namespace, monolithic=monolithic)	# That's where the magic happens!
		except HAULParseError as e:
			raise
		
		put('Writing to "%s"...' % (dest_filename))
		self.touch(dest_filename, stream_out.r)
		return m
	"""
	
	def resources_to_string(self):
		"Convert the resources into a string"
		
		r = '# HRES data\n'
		r += '#@var _data arr\n'
		r += '_data = []\n'
		i = 0
		for res in self.project.ress:
			r += '# "' + str(res.name) + '"\n'
			t = self.type(res.uri)
			t = t.replace('\\', '\\\\')
			t = t.replace('\'', '\\\'')
			t = t.replace('\n', '\\n')
			t = t.replace('\r', '\\r')
			r += '_data[' + str(i) + '] = \'' + t + '\'\n'
			i += 1
		#self.touch(dest_filename, r)
		return r
	
	
	def build(self, project):
		"Actually build stuff"
		
		# These are the basic steps needed for any kind of builder
		put('Starting build...')
		self.project = project
		
		if (self.exists_dir(self.output_path) == False):
			put('Creating output path "' + self.output_path + '"...')
			self.mkdir(self.output_path)
		
		if (self.exists_dir(self.staging_path) == False):
			put('Creating staging path "' + self.staging_path + '"...')
			self.mkdir(self.staging_path)
		
		put('Cleaning staging path "' + self.staging_path + '"...')
		self.clean(self.staging_path)
		
		# Everything after that is implemented by the Builders themselves
		
	
