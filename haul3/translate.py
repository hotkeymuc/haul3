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

def translate(source_filename, WriterClass, output_path=None, dialect=None, libs=None):
	"Translates the input file using the given language's Writer"
	
	name = nameByFilename(source_filename)
	
	# Prepare input
	put('Preparing input...')
	stream_in = StringReader(readFile(source_filename))
	reader = HAULReader_py(stream=stream_in, filename=source_filename)
	
	
	# Pre-scan libraries, so they are known
	libs_ns = rootNamespace
	if (libs != None):
		for lib_filename in libs:
			lib_name = lib_filename[:-3].replace('/', '.')
			lib_stream_in = StringReader(readFile(lib_filename))
			lib_reader = HAULReader_py(stream=lib_stream_in, filename=lib_filename)
			put('Scanning lib "' + lib_filename + '"...')
			lib_m = lib_reader.readModule(name=lib_name, namespace=libs_ns, scanOnly=True)
			put('Lib namespace:\n' + libs_ns.dump())
	
	
	# Prepare output
	put('Preparing output...')
	stream_out = StringWriter()
	if dialect is None:
		writer = WriterClass(stream_out)
	else:
		writer = WriterClass(stream_out, dialect=dialect)
	
	if output_path is None:
		output_filename = source_filename + '.' + writer.defaultExtension
	else:
		if not os.path.exists(output_path):
			os.makedirs(output_path)
		output_filename = output_path + '/' + name + '.' + writer.defaultExtension
	
	monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
	
	reader.seek(0)
	
	put('Translating input file "' + source_filename + '"...')
	
	writer.stream(reader, namespace=libs_ns, monolithic=monolithic)	# That's where the magic happens!
	
	put('Writing output file "' + output_filename + '"...')
	writeFile(output_filename, stream_out.r)
	

#source_file = 'examples/hello.py'
#source_file = 'examples/small.py'
#source_file = 'examples/infer.py'
#source_file = 'examples/complex.py'
#source_file = 'examples/classes.py'
#source_file = 'examples/shellmini.py'
#source_file = 'examples/vm.py'
#source_file = 'examples/arrays.py'
#source_file = 'haul/haul.py'
source_file = 'haul/langs/py/haulReader_py.py'

output_path = 'build'

WRITER_CLASSES = [
	HAULWriter_asm,
	HAULWriter_bas,
	HAULWriter_c,
	HAULWriter_java,
	HAULWriter_js,
	HAULWriter_json,
	HAULWriter_lua,
	HAULWriter_opl,
	HAULWriter_pas,
	HAULWriter_py,
	HAULWriter_vbs,
]

WriterClass = HAULWriter_py

libs = ['haul/haul.py', 'haul/utils.py']
#libs = None

try:
	translate(source_file, WriterClass, output_path, libs=libs)
except HAULParseError as e:
	put('Parse error: ' + str(e.message))

put('translate.py ended.')