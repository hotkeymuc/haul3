#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.java.haulWriter_java import *

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
		HAULBuilder.__init__(self, lang='java', platform='java')
	
	def build(self, inputFilename, sourcePath, stagingPath, outputPath, resources=None, perform_test_run=False):
		
		put('Starting build...')
		HAULBuilder.build(self, inputFilename, outputPath)
		#self.clean(stagingPath)
		
		name = nameByFilename(inputFilename)
		appNamespace = 'wtf.haul'	#'de.bernhardslawik.haul'
		appId = appNamespace + '.' + name
		
		
		srcPath = os.path.join(stagingPath, 'src')
		javaFilename = name + '.java'
		javaFilenameFull = os.path.join(srcPath, javaFilename)
		
		classPath = os.path.join(stagingPath, 'build')
		classFilename = name + '.class'
		classFilenameFull = os.path.join(classPath, 'wtf', 'haul', classFilename)
		
		jarFilename = name + '.jar'
		jarFilenameFull = os.path.join(stagingPath, jarFilename)
		jarFilenameFinal = os.path.join(outputPath, jarFilename)
		
		
		put('Cleaning staging paths...')
		self.clean(stagingPath)
		self.clean(srcPath)
		self.clean(classPath)
		
		
		if (resources != None):
			#@TODO: Testing: Build a py file with resource data, then translate it to target language
			put('Bundling resources...')
			resPyFilenameFull = os.path.join(stagingPath, 'hresdata.py')
			resFilenameFull = os.path.join(srcPath, 'hresdata.java')
			self.bundle(resources=resources, destFilename=resPyFilenameFull)
			m = self.translate(name='hresdata', sourceFilename=resPyFilenameFull, SourceReaderClass=HAULReader_py, destFilename=resFilenameFull, DestWriterClass=HAULWriter_java)
		
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(sourcePath, inputFilename), SourceReaderClass=HAULReader_py, destFilename=javaFilenameFull, DestWriterClass=HAULWriter_java)
		
		if not os.path.isfile(javaFilenameFull):
			put('Main Java file "%s" was not created! Aborting.' % (javaFilenameFull))
			return False
		
		
		#@TODO: Use module.imports!
		put('Staging source files...')
		libs = ['hio']	#['sys', 'hio']
		
		srcFiles = []
		for l in libs:
			f = os.path.abspath(os.path.join(srcPath, l + '.java'))
			self.copy('haul/langs/java/lib/' + l + '.java', f)
			srcFiles.append(f)
		
		srcFiles.append(javaFilenameFull)
		
		
		put('Compiling Java classes...')
		#cmd = JRE_DIR + '/javac -classpath "%s" -sourcepath "%s" -d "%s" "%s"' % (stagingPath, stagingPath, outputPath, javaFilenameFull)
		cmd = JAVAC_CMD
		cmd += ' -classpath "%s"' % (classPath)
		cmd += ' -sourcepath "%s"' % (srcPath)
		cmd += ' -d "%s"' % (classPath)
		cmd += ' %s' % (' '.join(srcFiles))
		#cmd += ' "%s"' % (javaFilenameFull)
		#cmd += ' "%s"' % (os.path.join(stagingPath, '*.java'))
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
		if perform_test_run:
		
			put('Test: Launching...')
			#self.command(JRE_DIR + '/java -classpath "%s" %s' % (classPath, name))
			cmd = JAVA_CMD
			#cmd += ' -classpath "%s" %s' % (classPath, appId)
			cmd += ' -classpath "%s" %s' % (jarFilenameFull, appId)
			r = self.command(cmd)
			put(r)
		
		
		put('Done.')
		
