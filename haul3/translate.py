#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
	HAUL3
	HotKey's Amphibious Unambiguous Language
	
	This program translates a given HAUL3/Python file into a different language.
	
"""

import os

from haul.utils import *

from haul.langs.py.reader_py import *

from haul.langs.asm.writer_asm import *
from haul.langs.bas.writer_bas import *
from haul.langs.c.writer_c import *
from haul.langs.java.writer_java import *
from haul.langs.js.writer_js import *
from haul.langs.json.writer_json import *
from haul.langs.lua.writer_lua import *
from haul.langs.opl.writer_opl import *
from haul.langs.pas.writer_pas import *
from haul.langs.py.writer_py import *
from haul.langs.vbs.writer_vbs import *


def put(t):
	print(t)


"""
### Manual translation (without using HAULTranslator)
def translate(source_filename, WriterClass, output_path=None, dialect=None, libs=None):
	"Translates the input file using the given language's Writer"
	
	name = name_by_filename(source_filename)
	
	# Prepare input
	put('Preparing input...')
	stream_in = StringReader(readFile(source_filename))
	reader = HAULReader_py(stream=stream_in, filename=source_filename)
	
	
	# Pre-scan libraries, so they are known
	libs_ns = HAUL_ROOT_NAMESPACE
	if (libs != None):
		for lib_filename in libs:
			# By reading the libs in in "scan_only" mode, the namespace gets populated without doing too much extra parsing work
			lib_name = lib_filename[:-3].replace('/', '.')
			lib_stream_in = StringReader(readFile(lib_filename))
			lib_reader = HAULReader_py(stream=lib_stream_in, filename=lib_filename)
			put('Scanning lib "' + lib_filename + '"...')
			lib_m = lib_reader.read_module(name=lib_name, namespace=libs_ns, scan_only=True)
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
	
	put(libs_ns.dump())
	


source_root_path = '.'
package_path = 'haul/langs/py'
source_filename = 'reader_py.py'
libs = ['haul/haul.py', 'haul/utils.py']
output_path = 'build'

WriterClass = HAULWriter_py
try:
	translate(
		source_filename=(source_root_path + '/' + package_path + '/' + source_filename),
		WriterClass=HAULWriter_py,
		output_path=(output_path + '/' + package_path),
		libs=libs
	)
except HAULParseError as e:
	put('HAULParseError: at token ' + str(e.token) + ': ' + str(e.message))
	
"""



from haul.core import HAULTranslator

t = HAULTranslator(HAULReader_py, HAULWriter_js)

try:
	### First: Parse all potential libs (headers), so all the namespaces are known for importing
	#t.process_lib('haul.utils', FileReader('haul/utils.py'))
	t.process_lib('hio', FileReader('libs/hio.py'))
	#t.process_lib('hres', FileReader('libs/hres.py'))
	
	### Then: Actually translate code
	#t.translate('hello', FileReader('examples/hello.py'), FileWriter('build/hello.js'))
	#t.translate('small', FileReader('examples/small.py'), FileWriter('build/small.js'))
	#t.translate('classes', FileReader('examples/classes.py'), FileWriter('build/classes.js'))
	t.translate('core', FileReader('haul/core.py'), FileWriter('build/haul/core.js'))
	
except HAULParseError as e:
	put('HAULParseError: at token ' + str(e.token) + ': ' + str(e.message))

put('translate.py ended.')