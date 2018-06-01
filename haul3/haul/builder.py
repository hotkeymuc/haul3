#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil

import subprocess	# for running commands

from utils import *

def put(t):
	print('HAULBuilder:\t' + str(t))


class HAULBuilder:
	"Provides the functionality to build a HAUL file for another platform. Like make etc."
	
	def __init__(self, lang, platform):
		self.lang = lang
		self.platform = platform
		
		self.source_filename = ''
		self.staging_path = ''
		self.output_path = ''
	
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
	
	
	
	def translate(self, name, source_filename, SourceReaderClass, dest_filename, DestWriterClass, dialect=None):
		put('Translating file "' + source_filename + '" to "' + dest_filename + '"...')
		streamIn = StringReader(readFile(source_filename))
		reader = SourceReaderClass(streamIn, name)
		monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
		reader.seek(0)
		streamOut = StringWriter()
		
		if (dialect == None):
			writer = DestWriterClass(streamOut)
		else:
			writer = DestWriterClass(streamOut, dialect=dialect)
		m = writer.stream(reader, monolithic=monolithic)	# That's where the magic happens!
		
		put('Writing to "%s"...' % (dest_filename))
		writeFile(dest_filename, streamOut.r)
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
		writeFile(dest_filename, r)
	
	def build(self, source_path, source_filename, output_path, staging_path, data_path=None, resources=None, perform_test_run=False):
		"Actually build a file."
		
		put('Starting build...')
		self.source_filename = source_filename
		self.output_path = output_path
		
		put('Creating output path "' + output_path + '"...')
		self.mkdir(output_path)
		
		put('Cleaning staging path "' + staging_path + '"...')
		self.clean(staging_path)
		
		
	
