#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
	HAUL3
	HotKey's Amphibious Unambiguous Language
	
	This program translates a given HAUL3/Python file into a different language.
	
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
	"Translates the input file using the given language's Writer"
	
	name = nameByFilename(inputFilename)
	
	streamIn = StringReader(readFile(inputFilename))
	reader = HAULReader_py(stream=streamIn, filename=inputFilename)
	
	streamOut = StringWriter()
	if dialect is None:
		writer = WriterClass(streamOut)
	else:
		writer = WriterClass(streamOut, dialect=dialect)
	
	if outputPath is None:
		outputFilename = inputFilename + '.' + writer.defaultExtension
	else:
		if not os.path.exists(dest_path):
			os.makedirs(dest_path)
		outputFilename = outputPath + '/' + name + '.' + writer.defaultExtension
	
	monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
	
	reader.seek(0)
	
	put('Translating input file "' + inputFilename + '"...')
	
	try:
		writer.stream(reader, monolithic=monolithic)	# That's where the magic happens!
	except HAULParseError as e:
		put('Parse error: ' + str(e.message))
		#raise
	
	put('Writing output file "' + outputFilename + '"...')
	writeFile(outputFilename, streamOut.r)
	

source_file = 'examples/hello.py'
#source_file = 'examples/small.py'
#source_file = 'examples/infer.py'
#source_file = 'examples/complex.py'
#source_file = 'examples/classes.py'
#source_file = 'examples/shellmini.py'
#source_file = 'examples/vm.py'

dest_path = 'build'

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

translate(source_file, WriterClass, dest_path)


put('translate.py ended.')