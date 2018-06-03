#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil

import subprocess	# for running commands

from utils import *
from langs.py.haulReader_py import HAULNamespace, HAUL_ROOT_NAMESPACE, HAULReader_py
from translator import *

def put(t):
	print('HAULBuilder:\t' + str(t))


class HAULSource:
	def __init__(self, name, stream, uri=None):
		self.name = name
		self.stream = stream
		self.uri = None
	

class HAULProject:
	def __init__(self):
		self.sources = []
		
		self.libs = []
		self.libs_path = 'libs'
		
	
	def add_source_file(self, filename, name=None):
		if (name == None):
			# Guess name from filename if omitted
			name = name_by_filename(filename)
		
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
	
	def __init__(self, platform, lang=None):
		self.platform = platform
		self.lang = lang
		
		self.source_path = '.'
		self.source_filename = None
		self.name = None
		
		self.libs_path = 'libs'
		self.data_path = 'data'
		self.staging_path = 'staging'
		self.output_path = 'build'
		
		self.libs = []
		self.namespace = HAULNamespace(name='builder', parent=HAUL_ROOT_NAMESPACE)
	
	# File system abstraction
	def exists(self, filename):
		return (os.path.isfile(filename))
	
	def mkdir(self, path):
		if not os.path.exists(path):
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
	
	
	
	
	def stream_from_file(self, filename):
		stream = StringReader(self.type(filename))
		return stream
	
	def set_source(self, filename):
		self.source_filename = filename
		self.name = name_by_filename(self.source_filename)
	
	def add_lib(self, name):
		self.libs.append(name)
	
	def scan_libs(self):
		for l in self.libs:
			name = l
			filename = self.libs_path + '/' + name + '.py'
			
			put('Scanning library "{}" in "{}"...'.format(name, filename))
			stream = self.stream_from_file(filename)
			reader = HAULReader_py(stream=stream, filename=filename)
			m = reader.read_module(name=name, namespace=self.namespace, scan_only=True)
	
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
	
	def build(self, perform_test_run=False):
		"Actually build a file."
		
		put('Starting build...')
		
		put('Cleaning staging path "' + self.staging_path + '"...')
		self.clean(self.staging_path)
		
		put('Scanning libraries...')
		self.scan_libs()
		
		put('Creating output path "' + self.output_path + '"...')
		self.mkdir(self.output_path)
		
		
	
