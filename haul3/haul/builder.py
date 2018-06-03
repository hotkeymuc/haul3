#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil

import subprocess	# for running commands

from utils import *
from langs.py.haulReader_py import HAULNamespace, HAUL_ROOT_NAMESPACE, HAULReader_py

def put(t):
	print('HAULBuilder:\t' + str(t))


class HAULSource:
	def __init__(self, name, stream, uri=None):
		self.name = name
		self.stream = stream
		self.uri = None
		self.dest_filename = None
	

class HAULProject:
	def __init__(self, name):
		self.name = name
		
		self.sources_path = '.'
		self.sources = []
		
		self.libs_path = 'libs'
		self.libs = []
		
		self.run_test = False
	
	def add_source(self, name=None, filename=None):
		if ((name == None) and (filename == None)):
			raise Exception('A name or filename has to be specified as source')
		
		if (name == None):
			# Guess name from filename if omitted
			name = name_by_filename(filename)
		if (filename == None):
			# Guess filename from name if omitted
			filename = self.sources_path + '/' + name + '.py'
		
		source = HAULSource(name=name, stream=FileReader(filename), uri=filename)
		self.sources.append(source)
		
	
	def add_lib(self, name, filename=None):
		if (filename == None):
			# Guess default lib filename if omitted
			filename = self.libs_path + '/' + name + '.py'
		
		source = HAULSource(name=name, stream=FileReader(filename), uri=filename)
		self.libs.append(source)
		
	

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
	
	
	
	
	
	
	### User interface
	def set_project(self, project):
		self.project = project
	
	def set_translator(self, t):
		self.translator = t
	
	def process_libs(self):
		put('Processing libs...')
		for s in self.project.libs:
			self.translator.process_lib(name=s.name, stream=s.stream, filename=s.uri)
		
	
	def translate_project(self, output_path=None, dest_extension=None, stream_out_single=None):
		"Translate the loaded project using the given translator. If stream_out_single is given, all files are written to that stream instead of individual files."
		m = None
		
		self.process_libs()
		
		if (output_path == None):
			output_path = self.staging_path
		
		if (dest_extension == None):
			dest_extension = self.lang
		
		put('Translating source(s)...')
		for s in self.project.sources:
			if (stream_out_single == None):
				# Each file to own output file
				if (s.dest_filename == None):
					# Assume default names
					s.dest_filename = output_path + '/' + s.name + '.' + dest_extension
					put('Assigned output filename "{}"'.format(s.dest_filename))
				
				stream_out = FileWriter(s.dest_filename)
				m = self.translator.translate(s.name, s.stream, stream_out, close_stream=True)
			else:
				# All files into one stream
				m = self.translator.translate(s.name, s.stream, stream_out_single, close_stream=False)
				
			
		# Return last translated module, which is most likely the main module
		return m
	
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
		m = writer.stream(reader, namespace=self.namespace, monolithic=monolithic)	# That's where the magic happens!
		
		put('Writing to "%s"...' % (dest_filename))
		self.touch(dest_filename, stream_out.r)
		return m
	
	def bundle(self, resources, dest_filename):
		r = '# HRES data\n'
		r += '#@var _data str[]\n'
		r += '_data = []\n'
		i = 0
		for res in resources:
			r += '# "' + str(res) + '"\n'
			t = self.type(res)
			t = t.replace('\\', '\\\\')
			t = t.replace('\'', '\\\'')
			t = t.replace('\n', '\\n')
			t = t.replace('\r', '\\r')
			r += '_data[' + str(i) + '] = \'' + t + '\'\n'
			i += 1
		self.touch(dest_filename, r)
	
	def build(self, project):
		"Actually build a file."
		
		put('Starting build...')
		self.set_project(project)
		
		if (self.exists_dir(self.output_path) == False):
			put('Creating output path "' + self.output_path + '"...')
			self.mkdir(self.output_path)
		
		if (self.exists_dir(self.staging_path) == False):
			put('Creating staging path "' + self.staging_path + '"...')
			self.mkdir(self.staging_path)
		
		put('Cleaning staging path "' + self.staging_path + '"...')
		self.clean(self.staging_path)
		
		
	
