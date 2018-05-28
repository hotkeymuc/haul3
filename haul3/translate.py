#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
	HAUL
	HotKey's Amphibious Unambiguous Language
	HotKey's Average Universal Language
	
	XXX HAUL3 - HotKey's Averaging Language

"""
import os

from haul.utils import *

from haul.langs.py.haulReader_py import *

from haul.langs.asm.haulWriter_asm import *
from haul.langs.bas.haulWriter_bas import *
from haul.langs.c.haulWriter_c import *
from haul.langs.java.haulWriter_java import *
from haul.langs.js.haulWriter_js import *
from haul.langs.json.haulWriter_json import *
from haul.langs.lua.haulWriter_lua import *
from haul.langs.opl.haulWriter_opl import *
from haul.langs.pas.haulWriter_pas import *
from haul.langs.py.haulWriter_py import *
from haul.langs.vbs.haulWriter_vbs import *


def put(t):
	print(t)


############################################################

def translate(inputFilename, WriterClass, outputPath=None, dialect=None):
	name = nameByFilename(inputFilename)
	
	streamIn = StringReader(readFile(inputFilename))
	reader = HAULReader_py(stream=streamIn, filename=inputFilename)
	
	streamOut = StringWriter()
	if dialect is None:
		writer = WriterClass(streamOut)
	else:
		writer = WriterClass(streamOut, dialect=dialect)
	
	if outputPath == None:
		outputFilename = inputFilename + '.' + writer.defaultExtension
	else:
		outputFilename = outputPath + '/' + name + '.' + writer.defaultExtension
	
	monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
	
	reader.seek(0)
	
	try:
		writer.stream(reader, monolithic=monolithic)	# That's where the magic happens!
	except HAULParseError as e:
		put('Parse error: ' + str(e.message))
		#raise
	
	writeFile(outputFilename, streamOut.r)
	
	"""
	# Dump to pickle
	import pickle
	h = open(outputFilename + '.pickle', 'wb')
	pickle.dump(reader.readModule(), h)
	h.close()
	"""


#WriterClass = HAULWriter_asm
#WriterClass = HAULWriter_bas
#WriterClass = HAULWriter_c
#WriterClass = HAULWriter_java
#WriterClass = HAULWriter_js
#WriterClass = HAULWriter_json
#WriterClass = HAULWriter_lua
#WriterClass = HAULWriter_opl
#WriterClass = HAULWriter_pas
WriterClass = HAULWriter_py
#WriterClass = HAULWriter_vbs

# Translate test file

# Test limited OPL capabilities
#translate('examples/hello.py', HAULWriter_opl, 'build')
#translate('examples/small.py', HAULWriter_opl, 'build')
#translate('examples/infer.py', HAULWriter_opl, 'build')

# Test type inference
#translate('examples/infer.py', WriterClass, 'build')
#translate('examples/hio_test.py', WriterClass, 'build')
translate('examples/small.py', WriterClass, 'build')
#translate('examples/complex.py', WriterClass, 'build')
#translate('examples/classes.py', WriterClass, 'build')
#translate('Z:/Data/_code/_pythonWorkspace/oos/oos.py', WriterClass, 'build')
#translate('examples/shellmini.py', WriterClass)	#, 'build')
#translate('examples/vm.py', WriterClass)


put('Translation ended.')