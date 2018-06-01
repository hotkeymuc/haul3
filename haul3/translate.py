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
			# By reading the libs in in "scanOnly" mode, the namespace gets populated without doing too much extra parsing work
			lib_name = lib_filename[:-3].replace('/', '.')
			lib_stream_in = StringReader(readFile(lib_filename))
			lib_reader = HAULReader_py(stream=lib_stream_in, filename=lib_filename)
			put('Scanning lib "' + lib_filename + '"...')
			lib_m = lib_reader.read_module(name=lib_name, namespace=libs_ns, scanOnly=True)
			#put('Lib namespace:\n' + libs_ns.dump())
	
	
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
	
	put('Translating input file "' + source_filename + '"...')
	reader.seek(0)
	monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
	writer.stream(reader, namespace=libs_ns, monolithic=monolithic)	# That's where the magic happens!
	
	put('Writing output file "' + output_filename + '"...')
	writeFile(output_filename, stream_out.r)
	

#source_filename = 'examples/hello.py'
#source_filename = 'examples/small.py'
#source_filename = 'examples/infer.py'
#source_filename = 'examples/complex.py'
#source_filename = 'examples/classes.py'
#source_filename = 'examples/shellmini.py'
#source_filename = 'examples/vm.py'
#source_filename = 'examples/arrays.py'
#output_path = 'build'
#libs = None
#libs = ['haul/utils.py']


#source_filename = 'haul/utils.py'
#output_path = 'build/haul'
#libs = None


#source_filename = 'haul/haul.py'
#output_path = 'build/haul'
#libs = None

source_root_path = '.'
package_path = 'haul/langs/py'
source_filename = 'haulReader_py.py'
libs = ['haul/haul.py', 'haul/utils.py']
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
try:
	#translate(source_filename, WriterClass, output_path, libs=libs)
	translate(
		source_filename=(source_root_path + '/' + package_path + '/' + source_filename),
		WriterClass=HAULWriter_py,
		output_path=(output_path + '/' + package_path),
		libs=libs)
except HAULParseError as e:
	put('HAULParseError: at token ' + str(e.token) + ': ' + str(e.message))
	

put('translate.py ended.')