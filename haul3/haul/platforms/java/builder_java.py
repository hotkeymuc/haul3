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


HAULBUILDER_JAVA_DIR = os.path.dirname(__file__)
JRE_DIR = os.path.abspath('Z:/Apps/_code/AndroidStudio/jre/bin')
JAVA_CMD = os.path.abspath(os.path.join(JRE_DIR, 'java'))
JAVAC_CMD = os.path.abspath(os.path.join(JRE_DIR, 'javac'))
JAR_CMD = os.path.abspath(os.path.join(JRE_DIR, 'jar'))

class HAULBuilder_java(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='java', lang='java')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_java))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		appNamespace = 'wtf.haul'	#'de.bernhardslawik.haul'
		appId = appNamespace + '.' + name
		
		libsPath = os.path.join(self.data_path, 'langs/java/libs')
		
		srcPath = os.path.join(self.staging_path, 'src')
		javaFilename = name + '.java'
		javaFilenameFull = os.path.join(srcPath, javaFilename)
		
		classPath = os.path.join(self.staging_path, 'build')
		classFilename = name + '.class'
		classFilenameFull = os.path.join(classPath, 'wtf', 'haul', classFilename)
		
		jarFilename = name + '.jar'
		jarFilenameFull = os.path.join(self.staging_path, jarFilename)
		jarFilenameFinal = os.path.join(self.output_path, jarFilename)
		
		
		put('Cleaning staging paths...')
		self.clean(srcPath)
		self.clean(classPath)
		
		
		"""
		if (resources != None):
			#@TODO: Testing: Build a py file with resource data, then translate it to target language
			put('Bundling resources...')
			resPyFilenameFull = os.path.join(self.staging_path, 'hresdata.py')
			resFilenameFull = os.path.join(srcPath, 'hresdata.java')
			self.bundle(resources=resources, dest_filename=resPyFilenameFull)
			m = self.translate(name='hresdata', source_filename=resPyFilenameFull, SourceReaderClass=HAULReader_py, dest_filename=resFilenameFull, DestWriterClass=HAULWriter_java)
		"""
		
		put('Translating sources to Java...')
		self.translate_project(output_path=srcPath)
		
		if not os.path.isfile(javaFilenameFull):
			put('Main Java file "%s" was not created! Aborting.' % (javaFilenameFull))
			return False
		
		
		#@TODO: Use module.imports!
		put('Staging source files...')
		
		srcFiles = []
		for s in self.project.libs:
			f_in = libsPath + '/' + s.name + '.java'
			f_out = os.path.abspath(os.path.join(srcPath, s.name + '.java'))
			self.copy(f_in, f_out)
			srcFiles.append(f_out)
		
		srcFiles.append(javaFilenameFull)
		
		
		put('Compiling Java classes...')
		#cmd = JRE_DIR + '/javac -classpath "%s" -sourcepath "%s" -d "%s" "%s"' % (self.staging_path, staging_path, output_path, javaFilenameFull)
		cmd = JAVAC_CMD
		cmd += ' -classpath "%s"' % (classPath)
		cmd += ' -sourcepath "%s"' % (srcPath)
		cmd += ' -d "%s"' % (classPath)
		cmd += ' %s' % (' '.join(srcFiles))
		#cmd += ' "%s"' % (javaFilenameFull)
		#cmd += ' "%s"' % (os.path.join(self.staging_path, '*.java'))
		r = self.command(cmd)
		
		# Check if successfull
		if not os.path.isfile(classFilenameFull):
			put(r)
			put('Class file "%s" was not created! Aborting.' % (classFilenameFull))
			return False
		
		
		put('Creating JAR "%s"...' % (jarFilename))
		cmd = JAR_CMD
		cmd += ' cvf'
		cmd += ' "%s"' % (jarFilenameFull)
		#cmd += ' "%s"' % (classPath)
		cmd += ' -C "%s" .' % (classPath)
		r = self.command(cmd)
		
		if not os.path.isfile(jarFilenameFull):
			put(r)
			put('JAR file "%s" was not created! Aborting.' % (jarFilenameFull))
			return False
		
		put('Copying end result to "%s"...' % (jarFilenameFinal))
		self.copy(jarFilenameFull, jarFilenameFinal)
		
		
		# Test
		if (self.project.run_test == True):
		
			put('Test: Launching...')
			#self.command(JRE_DIR + '/java -classpath "%s" %s' % (classPath, name))
			cmd = JAVA_CMD
			#cmd += ' -classpath "%s" %s' % (classPath, appId)
			cmd += ' -classpath "%s" %s' % (jarFilenameFull, appId)
			r = self.command(cmd)
			put(r)
		
		
		put('Done.')
		
