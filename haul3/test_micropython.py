#!/bin/python3
# -*- coding: UTF-8 -*-

"""
Trying to combine MicroPython's grammar/lexer/parser with HAUL's parse tree.

2024-04-10 Bernhard "HotKey" Slawik
"""

from haul.core import *
from haul.utils import *

#from haul.langs.py.reader_py import *
from haul.langs.py.reader_py_micropython import *

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

def put(t:str) -> None:
	print(t)
def put_debug(t:str) -> None:
	print(t)
	#pass


if __name__ == '__main__':
	#source_filename = 'haul/langs/py/reader_py.py'
	#source_filename = 'haul/langs/py/__test_micropython_parser.py'
	#source_filename = 'examples/hello.py'
	source_filename = 'examples/complex.py'
	
	stream_in = StringReader(read_file(source_filename))
	"""
	while True:
		r = stream_in.get()
		if r == None: break
		put(r)
	"""
	"""
	with open(source_filename, 'r') as h: code = h.read()
	
	put('Setting up reader and lexer...')
	reader = mp_reader_t(code)
	lex = mp_lexer_new(src_name=source_filename, reader=reader)
	
	put('Parsing...')
	t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_FILE_INPUT)
	#t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_SINGLE_INPUT)
	put('Result Tree:')
	#put(str(t.root))
	"""
	put('Preparing reader...')
	name = name_by_filename(source_filename)
	reader = HAULReader_micropython(stream_in, name)
	
	libs_ns = HAUL_ROOT_NAMESPACE
	ns = libs_ns
	#m:HAULModule = reader.read_module(name=source_filename, namespace=ns)
	#put('HAULModule:')
	#put(str(m))
	
	
	#WriterClass = HAULWriter_java
	WriterClass = HAULWriter_js
	
	put('Preparing output...')
	stream_out = StringWriter()
	dialect = None
	if dialect is None:
		writer = WriterClass(stream_out)
	else:
		writer = WriterClass(stream_out, dialect=dialect)
	
	monolithic = True	# Use simple (but good) monolithic version (True) or a smart multi-pass streaming method (False)
	writer.stream(name, reader, namespace=ns, monolithic=monolithic)	# That's where the magic happens!
	put('-' * 40)
	put(stream_out.r)
	put('-' * 40)
	
