#!/bin/python3
# -*- coding: UTF-8 -*-

"""
Trying to combine MicroPython's grammar/lexer/parser with HAUL's parse tree.

2024-04-10 Bernhard "HotKey" Slawik
"""

from haul.core import *
from haul.utils import *

#from haul.langs.py.reader_py import *
from haul.langs.py.__test_micropython_lexer import *
from haul.langs.py.__test_micropython_parser import *


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

def put(t:str):
	print(t)

class HAULReader_micropy(HAULReader):
	def __init__(self, stream, filename):
		HAULReader.__init__(self, stream, filename)
		
		self.default_extension = 'py'
		
		self.root_pn = self.prepare_mp_parse_tree()
	
	def prepare_mp_parse_tree(self):
		code = self.stream.data
		put('Setting up reader and lexer...')
		reader = mp_reader_t(code)
		lex = mp_lexer_new(src_name=self.filename, reader=reader)
		
		put('Parsing...')
		t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_FILE_INPUT)
		#t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_SINGLE_INPUT)
		
		#put('Result Tree:')
		#put(self.dump(pn))
		
		pn:mp_parse_node_t = t.root
		
		put('Transforming...')
		#ns:HAULNamespace = HAULNamespace(name='root', parent=None)
		#assert(MP_PARSE_NODE_IS_STRUCT_KIND(pn, file_input_2))
		#m:HAULModule = self.read_module(pn, ns)
		
		#put('HAULNamespace:')
		#put(str(ns.dump()))
		#return m
		return pn
	
	def read_module(self, name:str, namespace:HAULNamespace, pn:mp_parse_node_t=None) -> HAULModule:
		
		if pn is None:
			put('Using root_pn to read module')
			pn = self.root_pn
		assert(MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_file_input_2))
		#for i,pn2 in enumerate(pn.nodes):
		#	put('pn.nodes[%d] = %s' % (i, str(self.dump(pn2))))
		#pn:mp_parse_node_t = pn.nodes[0]
		
		if namespace is None:
			namespace = HAUL_ROOT_NAMESPACE
		
		m:HAULModule = HAULModule()
		m.name = name
		m.origin = pn.source_line	#self.loc()
		m.parent_namespace = namespace
		ns = namespace.get_or_create_namespace(name)	#HAULNamespace()
		m.namespace = ns
		m.block = HAULBlock()
		# if BLOCKS_HAVE_LOCAL_NAMESPACE: ...
		
		for pnn in pn.nodes:	#pnn:mp_parse_node_t
			
			# Childs can be import, classdef, funcdef, other instruction/expression
			if MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_funcdef):
				f:HAULFunction = self.read_function(pnn, ns)
				m.add_func(f)
				
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_classdef):
				c:HAULClass = self.read_class(pnn, ns)
				m.add_class(c)
				
			elif MP_PARSE_NODE_IS_TOKEN_KIND(pnn, MP_TOKEN_NEWLINE):
				# Ignore stray newline
				pass
			else:
				#put('UNHANDLED module node: %s' % self.dump(pnn).strip())
				i:HAULInstruction = self.read_instruction(pnn, ns)
				m.block.add_instruction(i)
			
		return m
	
	def read_function(self, pn:mp_parse_node_t, ns:HAULNamespace) -> HAULFunction:
		put('@TODO: Function')	#: ' + str(pn))
		f:HAULFunction = HAULFunction()
		f.origin = pn.source_line	#self.loc()
		f.id = ns.add_id(name=str(pn.nodes[0].id_value), kind=K_FUNCTION, data_type=T_UNKNOWN, origin=f.origin)
		f.block = HAULBlock()
		return f
	
	def read_class(self, pn:mp_parse_node_t, ns:HAULNamespace) -> HAULClass:
		put('@TODO: Class')	#: ' + str(pn))
		c:HAULClass = HAULClass()
		c.origin = pn.source_line	#self.loc()
		c.id = ns.add_id(name=str(pn.nodes[0].id_value), kind=K_CLASS, data_type=T_CLASS, origin=c.origin)
		return c
	
	def read_instruction(self, pn:mp_parse_node_t, ns:HAULNamespace) -> HAULInstruction:
		i = HAULInstruction()
		i.origin = pn.source_line	#self.loc()
		
		if MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_expr_stmt):
			if MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[0], RULE_atom_expr_normal):
				# Call a function
				if MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[0].nodes[1], RULE_trailer_paren):
					i.call = HAULCall()
					i.call.id = ns.find_id(str(pn.nodes[0].nodes[0].id_value), ignore_unknown=True)
					i.call.args = pn.nodes[0].nodes[1].nodes
					
				else:
					put('UNKNOWN EXPR_STMT: ' + self.dump(pn.nodes[0]))
			else:
				# Set a variable
				i.call = implicitCall(I_VAR_SET)
				
				e = self.read_expression(pn.nodes[0], namespace=ns, allow_undefined=True)	# We only accept var/identifier, but may infer some stuff
				e_right = self.read_expression(pn.nodes[1], namespace=ns, allow_undefined=INFER_TYPE)	# We only accept var/identifier, but may infer some stuff
				
				# Type inference
				if (INFER_TYPE) and (e.var != None) and (e.returnType == T_UNKNOWN):
					put('Inferring type "' + e_right.returnType + '" for variable "' + str(e.var) + '"')
					e.var.kind = K_VARIABLE
					e.var.data_type = e_right.returnType
				
				#ns.add_id(name=L_SELF, kind=K_VARIABLE, data_type=t.data, origin=self.loc(), overwrite=True)
				i.call.args = [
					e,	# HAULExpression()
					e_right
				]
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_if_stmt):
			# IF instruction
			
			ctrl = implicitControl(C_IF)
			#self.lastIfBlock[-1] = ctrl	# Remember last block for IF/ELIF/ELSE
			#ctrl.add_expression(self.read_expression(namespace=ns))
			#ctrl.add_block(self.read_block(namespace=ns, blockName='__ifBlock' + str(self.loc())))
			i.control = ctrl
		else:
			put('UNKNOWN INSTRUCTION NODE: ' + self.dump(pn))
		
		return i
	
	def read_expression(self, pn:mp_parse_node_t, namespace:HAULNamespace, allow_undefined=False):
		e = HAULExpression()
		#e.origin = pn.source_line	#self.loc()
		e.returnType = T_UNKNOWN
		
		#put('@TODO: expression: ' + str(pn))
		if MP_PARSE_NODE_IS_ID(pn):
			#e.id = ns.find_id(str(pn.id_value), ignore_unknown=False)	# Will stop translation if ID was not found
			if allow_undefined:
				#@TODO: Get type from augmented set!
				e.var = ns.add_id(str(pn.id_value), kind=None)
			else:
				e.var = ns.find_id(str(pn.id_value), ignore_unknown=False)
			
		elif MP_PARSE_NODE_IS_SMALL_INT(pn):
			e.value = HAULValue(T_INTEGER, data_int=pn.small_int_value)
			e.returnType = e.value.type
		elif MP_PARSE_NODE_LEAF_KIND(pn) == MP_PARSE_NODE_STRING:
			e.value = HAULValue(T_STRING, data_str=pn.string_value)
			e.returnType = e.value.type
		#elif MP_PARSE_NODE_LEAF_KIND(pn) == MP_PARSE_NODE_FLOAT:
		#	e.value = HAULValue(T_FLOAT, data_float=pn.float_value)
		#	e.returnType = e.value.type
		elif MP_PARSE_NODE_IS_TOKEN(pn):
			if pn.token_value == MP_TOKEN_KW_TRUE:
				e.value = HAULValue(T_BOOLEAN, data_bool=True)
				e.returnType = e.value.type
			elif pn.token_value == MP_TOKEN_KW_FALSE:
				e.value = HAULValue(T_BOOLEAN, data_bool=False)
				e.returnType = e.value.type
			elif pn.token_value == MP_TOKEN_KW_NONE:
				e.value = HAULValue(T_NOTHING)
				e.returnType = T_NOTHING
			else:
				put('UNKNOWN Token in expression: ' + str(pn))
				e.value = HAULValue(T_STRING, data_str=mp_token_kind_names[pn.token_value])	#@FIXME: I am just outputting the MP token as a string
				e.returnType = e.value.type
		else:
			put('UNKNOWN EXPRESSION: ' + str(pn))
		return e
	
	def dump(self, pn:mp_parse_node_t, indent:int=0):
		
		#r = 'pn:\n'
		r = DUMP_INDENT*indent
		
		if pn is None:
			r += 'pn=None\n'
		elif not isinstance(pn, mp_parse_node_t):
			r += 'pn=VALUE: %s (%s)\n' % (str(pn), str(type(pn)))
		elif MP_PARSE_NODE_IS_TOKEN(pn):
			r += 'ignore token: ' + str(pn)
		#elif MP_PARSE_NODE_IS_NULL(pn) and (i == num_nodes-1):
		#	r += 'pn=NULL = END\n' % (DUMP_INDENT * (indent+1))
		#	#continue	# Do not dump trailing NULLs
		elif MP_PARSE_NODE_IS_STRUCT(pn):
			#r += 'root=%s' % pn.dump()
			kind = pn.kind_num_nodes & 0xff
			
			# Parse known rules
			if kind == RULE_import_from:
				#r += 'IMPORT %s.%s\n' % (pn.nodes[0].id_value, str(pn.nodes[1]))
				r += 'IMPORT %s.%s\n' % (str(pn.nodes[0]), str(pn.nodes[1]))
				return r
			elif kind == RULE_term:
				r += '(' + (', '.join([self.dump(pnn).strip() for pnn in pn.nodes])) + ')\n'
				return r
			elif kind == RULE_atom_bracket:
				r += ' [ ' + (', '.join([self.dump(pnn).strip() for pnn in pn.nodes])) + ' ] \n'
				return r
				
			elif kind == RULE_expr_stmt:
				
				if MP_PARSE_NODE_IS_STRUCT(pn.nodes[0]) and (pn.nodes[0].kind_num_nodes & 0xff == RULE_atom_expr_normal):
					# Call!
					r += 'CALL '
					#assert(pn.nodes[0].nodes[1].kind_num_nodes & 0xff == RULE_trailer_paren)
					if (pn.nodes[0].nodes[1].kind_num_nodes & 0xff == RULE_trailer_paren):
						r += pn.nodes[0].nodes[0].id_value
						r += '('
						r += ', '.join([ self.dump(pnn, 0).strip() for pnn in pn.nodes[0].nodes[1].nodes ])
						r += ')\n'
					else:
						r += 'UNKNOWN EXPRESSION:' + self.dump(pn.nodes[0], indent+1)	#indent+1)
					
				else:
					# Set
					r += 'SET '
					r += '<'
					#r += pn.nodes[0].id_value
					r += str(pn.nodes[0])
					#r += dump(pn.nodes[0])
					r += '> := <'
					# node[1] can be "annassign" to include a type
					r += self.dump(pn.nodes[1], 0).strip()	#indent+1)
					r += '>\n'
				
				return r
				
				#pass
			
			## Unhandled: Just dump
			r += 'UNHANDLED STRUCT: pn=%s {\t// line %d\n' % (
				rule_name_table[kind] if kind < len(rule_name_table) else '0x%02X'%kind,
				pn.source_line
			)
			num_nodes = pn.kind_num_nodes >> 8
			#for pnn in pn.nodes:
			for i,pnn in enumerate(pn.nodes[:num_nodes]):
				#r += '%s%s\n' % (DUMP_INDENT * (indent+1), str(pnn))
				r += self.dump(pnn, indent+1)
			r += '%s}\n' % (DUMP_INDENT * indent)
		
		else:
			# Unknown mp_parse_node_t
			r += 'UNHANDLED NODE: pn=%s\n' % str(pn)
		return r


if __name__ == '__main__':
	#source_filename = 'haul/langs/py/reader_py.py'
	source_filename = 'haul/langs/py/__test_micropython_parser.py'
	
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
	reader = HAULReader_micropy(stream_in, name)
	
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