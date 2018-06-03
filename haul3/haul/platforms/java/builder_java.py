#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.java.writer_java import *

import json

def put(txt):
	print('HAULBuilder_java:\t' + str(txt))


class HAULBuilder_java(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='java', lang='java')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_java))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		
		app_package = 'wtf.haul'	#'de.bernhardslawik.haul'
		app_id = app_package + '.' + name
		
		src_path = os.path.abspath(os.path.join(self.staging_path, 'src'))
		java_filename = name + '.java'
		java_filename_full = os.path.join(src_path, java_filename)
		
		class_path = os.path.abspath(os.path.join(self.staging_path, 'build'))
		class_filename = name + '.class'
		class_filename_full = os.path.join(class_path, 'wtf', 'haul', class_filename)
		
		jar_filename = name + '.jar'
		jar_filename_full = os.path.abspath(os.path.join(self.staging_path, jar_filename))
		jar_filename_final = os.path.abspath(os.path.join(self.output_path, jar_filename))
		
		data_libs_path = os.path.abspath(os.path.join(self.data_path, 'langs', 'java', 'libs'))
		
		
		#jre_path = os.path.abspath('Z:/Apps/_code/AndroidStudio/jre/bin')
		jre_path = self.get_path('JRE_PATH', os.path.abspath(os.path.join(self.tools_path, 'jre')))
		JAVA_CMD = os.path.abspath(os.path.join(jre_path, 'java'))
		JAVAC_CMD = os.path.abspath(os.path.join(jre_path, 'javac'))
		JAR_CMD = os.path.abspath(os.path.join(jre_path, 'jar'))
		
		
		put('Cleaning staging paths...')
		self.clean(src_path)
		self.clean(class_path)
		
		
		"""
		if (resources != None):
			#@TODO: Testing: Build a py file with resource data, then translate it to target language
			put('Bundling resources...')
			resPyFilenameFull = os.path.join(self.staging_path, 'hresdata.py')
			resFilenameFull = os.path.join(src_path, 'hresdata.java')
			self.bundle(resources=resources, dest_filename=resPyFilenameFull)
			m = self.translate(name='hresdata', source_filename=resPyFilenameFull, SourceReaderClass=HAULReader_py, dest_filename=resFilenameFull, DestWriterClass=HAULWriter_java)
		"""
		
		put('Translating sources to Java...')
		self.translate_project(output_path=src_path)
		
		if not os.path.isfile(java_filename_full):
			put('Main Java file "%s" was not created! Aborting.' % (java_filename_full))
			return False
		
		
		#@TODO: Use module.imports!
		put('Staging source files...')
		
		src_files = []
		for s in self.project.libs:
			f_in = data_libs_path + '/' + s.name + '.java'
			f_out = os.path.abspath(os.path.join(src_path, s.name + '.java'))
			self.copy(f_in, f_out)
			src_files.append(f_out)
		
		src_files.append(java_filename_full)
		
		
		put('Compiling Java classes...')
		#cmd = jre_path + '/javac -classpath "%s" -sourcepath "%s" -d "%s" "%s"' % (self.staging_path, staging_path, output_path, java_filename_full)
		cmd = JAVAC_CMD
		cmd += ' -classpath "%s"' % (class_path)
		cmd += ' -sourcepath "%s"' % (src_path)
		cmd += ' -d "%s"' % (class_path)
		cmd += ' %s' % (' '.join(src_files))
		#cmd += ' "%s"' % (java_filename_full)
		#cmd += ' "%s"' % (os.path.join(self.staging_path, '*.java'))
		r = self.command(cmd)
		
		# Check if successfull
		if not os.path.isfile(class_filename_full):
			put(r)
			put('Class file "%s" was not created! Aborting.' % (class_filename_full))
			return False
		
		
		put('Creating JAR "%s"...' % (jar_filename))
		cmd = JAR_CMD
		cmd += ' cvf'
		cmd += ' "%s"' % (jar_filename_full)
		#cmd += ' "%s"' % (class_path)
		cmd += ' -C "%s" .' % (class_path)
		r = self.command(cmd)
		
		if not os.path.isfile(jar_filename_full):
			put(r)
			put('JAR file "%s" was not created! Aborting.' % (jar_filename_full))
			return False
		
		put('Copying end result to "%s"...' % (jar_filename_final))
		self.copy(jar_filename_full, jar_filename_final)
		
		
		# Test
		if (self.project.run_test == True):
		
			put('Test: Launching...')
			#self.command(jre_path + '/java -classpath "%s" %s' % (class_path, name))
			cmd = JAVA_CMD
			#cmd += ' -classpath "%s" %s' % (class_path, app_id)
			cmd += ' -classpath "%s" %s' % (jar_filename_full, app_id)
			r = self.command(cmd)
			put(r)
		
		
		put('Done.')
		
