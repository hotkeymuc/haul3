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

def put(t:str) -> None:
	print(t)
def put_debug(t:str) -> None:
	#print(t)
	pass

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
	
	def read_function(self, pn:mp_parse_node_t, namespace:HAULNamespace) -> HAULFunction:
		#put('@TODO: Function')	#: ' + str(pn))
		#put(self.dump(pn))
		
		f:HAULFunction = HAULFunction()
		f.origin = pn.source_line	#self.loc()
		name = str(pn.nodes[0].id_value)
		f.id = namespace.add_id(name=name, kind=K_FUNCTION, data_type=T_UNKNOWN, origin=f.origin)
		
		ns = namespace.get_or_create_namespace(name)
		f.namespace = ns
		
		# Args
		#put('args=' + str(self.dump(pn.nodes[1])))
		if MP_PARSE_NODE_IS_ID(pn.nodes[1]):
			i = ns.add_id(name=str(pn.nodes[1].id_value), kind=K_VARIABLE, data_type=T_UNKNOWN, origin=f.origin)
			f.add_arg( i )
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_typedargslist_name):
			#put('arglist_name=' + str(self.dump(pn.nodes[1])))
			#name = str(pn.nodes[1].nodes[0].id_value)
			typ = T_UNKNOWN	#@TODO: str(pn.nodes[1].nodes[1].id_value)
			#@TODO: def_value = str(pn.nodes[1].nodes[2])
			i = ns.add_id(name=str(pn.nodes[1].nodes[0].id_value), kind=K_VARIABLE, data_type=typ, origin=f.origin)
			f.add_arg( i )
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_typedargslist):
			# typedargslist_name, typedargslist_name, ...
			#put('arglist=' + str(self.dump(pn.nodes[1])))
			for pnn in pn.nodes[1].nodes:
				#put('arg=' + str(self.dump(pnn)))
				if MP_PARSE_NODE_IS_ID(pnn):
					i = ns.add_id(name=str(pnn.id_value), kind=K_VARIABLE, data_type=T_UNKNOWN, origin=f.origin)
				elif MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_typedargslist_name):
					typ = T_UNKNOWN	#@TODO: pnn.nodes[1].id_value !
					#@TODO: def_value = str(pnn.nodes[2])
					i = ns.add_id(name=str(pnn.nodes[0].id_value), kind=K_VARIABLE, data_type=typ, origin=f.origin)
				else:
					put('UNHANDLED ARG IN ARGLIST: ' + str(self.dump(pnn)))
				f.add_arg( i )
		else:
			put('UNHANDLED argument list: ' + str(self.dump(pn.nodes[1])))
		
		# Return type
		if not MP_PARSE_NODE_IS_NULL(pn.nodes[2]):
			#put('UNHANDLED function return type: ' + str(pn.nodes[2]))
			#@TODO: Set return type: f.returnType = self.parse_type( pn.nodes[2] )
			pass
		
		#if MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[3], RULE_suite_block_stmts):
		f.block = self.read_block(pn.nodes[3], ns)
		#else:
		#	# Single instruction: Wrap in block
		#	f.block = HAULBlock()
		#	f.block.add_instruction(self.read_instruction(pn.nodes[3], ns))
		return f
	
	def read_class(self, pn:mp_parse_node_t, namespace:HAULNamespace) -> HAULClass:
		put('@TODO: Class')	#: ' + str(pn))
		c:HAULClass = HAULClass()
		c.origin = pn.source_line	#self.loc()
		ns = namespace
		
		c.id = ns.add_id(name=str(pn.nodes[0].id_value), kind=K_CLASS, data_type=T_CLASS, origin=c.origin)
		#@TODO: Member variables
		#@TODO: Methods
		return c
	
	def read_instruction(self, pn:mp_parse_node_t, namespace:HAULNamespace) -> HAULInstruction:
		i = HAULInstruction()
		i.origin = pn.source_line	#self.loc()
		ns = namespace
		
		#put_debug('Line %d' % pn.source_line)
		
		if MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_expr_stmt):
			if MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[0], RULE_atom_expr_normal):
				# Call a function
				if MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[0].nodes[1], RULE_trailer_paren):
					i.call = HAULCall()
					i.call.id = ns.find_id(str(pn.nodes[0].nodes[0].id_value), ignore_unknown=True)
					if i.call.id is None:
						put('Adding unknown trailer_paren id "%s"' % str(pn.nodes[0].nodes[0].id_value))
						i.call.id = ns.add_id(str(pn.nodes[0].nodes[0].id_value), kind=K_FUNCTION)
					
					# Add call args
					for pnn in pn.nodes[0].nodes[1].nodes:
						i.call.args.append(self.read_expression(pnn, namespace))
					
				else:
					# e.g. a simple foo = foo2.bar (atomic)
					put('UNKNOWN EXPR_STMT: ' + self.dump(pn))	#.nodes[0]))
			else:
				# Set a variable
				i.call = implicitCall(I_VAR_SET)
				
				e = self.read_expression(pn.nodes[0], namespace=ns, allow_undefined=True)	# We only accept var/identifier, but may infer some stuff
				e_right = self.read_expression(pn.nodes[1], namespace=ns, allow_undefined=INFER_TYPE)	# We only accept var/identifier, but may infer some stuff
				
				# Type inference
				#if (INFER_TYPE) and (e.var != None) and (e.returnType == T_UNKNOWN):
				#	put_debug('Inferring type "' + e_right.returnType + '" for variable "' + str(e.var) + '"')
				#	e.var.kind = K_VARIABLE
				#	e.var.data_type = e_right.returnType
				
				#ns.add_id(name=L_SELF, kind=K_VARIABLE, data_type=t.data, origin=self.loc(), overwrite=True)
				i.call.args = [
					e,	# HAULExpression()
					e_right
				]
			
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_if_stmt):
			# IF instruction
			
			ctrl = implicitControl(C_IF)
			#self.lastIfBlock[-1] = ctrl	# Remember last block for IF/ELIF/ELSE
			#put('IF: ' + str(self.dump(pn)))
			ctrl.add_expression(self.read_expression(pn.nodes[0], ns))
			ctrl.add_block(self.read_block(pn.nodes[1], ns))
			if not MP_PARSE_NODE_IS_NULL(pn.nodes[2]):
				ctrl.add_block(self.read_block(pn.nodes[2], ns))
			i.control = ctrl
			
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_while_stmt):
			# WHILE instruction
			#put('WHILE: ' + str(self.dump(pn)))
			ctrl = implicitControl(C_WHILE)
			ctrl.add_expression(self.read_expression(pn.nodes[0], ns))
			ctrl.add_block(self.read_block(pn.nodes[1], ns))
			#@TODO: Optional else-block at pn.nodes[2]
			i.control = ctrl
			
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_return_stmt):
			ctrl = implicitControl(C_RETURN)
			assert(len(pn.nodes) == 1)	# Assume only one return value
			
			e = self.read_expression(pn.nodes[0], namespace=ns)
			ctrl.add_expression(e)
			
			# Retro-actively infer functio return type:
			#if ((INFER_TYPE) and (e.returnType != T_UNKNOWN) and (i != None) and (i.data_type == T_UNKNOWN)):
			#	put_debug('Inferring return type "' + str(e.returnType) + '" for function "' + str(iret) + '" from return statement')
			#	i.data_type = e.returnType
			#	#self.lastFunction.returnType = e.returnType
			i.control = ctrl
		else:
			put('UNKNOWN INSTRUCTION NODE: ' + self.dump(pn))
		
		return i
	
	def read_expression(self, pn:mp_parse_node_t, namespace:HAULNamespace, allow_undefined=False):
		e = HAULExpression()
		#e.origin = pn.source_line	#self.loc()
		ns = namespace
		
		e.returnType = T_UNKNOWN
		
		#put('@TODO: expression: ' + str(pn))
		if MP_PARSE_NODE_IS_ID(pn):
			if allow_undefined:
				#@TODO: Get type from augmented set!
				e.var = ns.add_id(str(pn.id_value), kind=None)
			else:
				#e.var = ns.find_id(str(pn.id_value), ignore_unknown=False)	# Will stop translation if ID was not found
				e.var = ns.find_id(str(pn.id_value), ignore_unknown=True)	# Just gloss over unknown ids
			
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
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_comparison):
			#put('UNIMPLEMENTED comparison in expression: ' + str(self.dump(pn)))
			
			e.call = HAULCall()
			if MP_PARSE_NODE_IS_TOKEN(pn.nodes[1]):
				# e.g. for "==" = MP_TOKEN_OP_DBL_EQUAL
				e.call.id = ns.find_id(mp_token_kind_names[pn.nodes[1].token_value], ignore_unknown=True)
				if e.call.id is None:
					put('Adding unknown infix: "%s"' % mp_token_kind_names[pn.nodes[1].token_value])
					e.call.id = ns.add_id(mp_token_kind_names[pn.nodes[1].token_value], kind=K_FUNCTION)
			else:
				# e.g. for "type(foo) is bar" = RULE_comp_op_is
				put('UNHANDLED comparison: ' + str(pn.nodes[1]))
				e.call.id = ns.find_id(str(pn.nodes[1]), ignore_unknown=True)
				if e.call.id is None:
					put('Adding unknown comparator: "%s"' % str(pn.nodes[1]))
					e.call.id = ns.add_id(str(pn.nodes[1]), kind=K_FUNCTION)
			
			e.call.args.append(self.read_expression(pn.nodes[0], ns))
			e.call.args.append(self.read_expression(pn.nodes[2], ns))
			
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_atom_expr_normal):
			
			#@TODO: Complete this! Object access! Mixed array/object access! Array slices!
			if MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_trailer_bracket) and MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1].nodes[0], RULE_subscript_3):
				# Simple array access, e.g. "foo[bar]"
				e.call = implicitCall(I_ARRAY_LOOKUP)
				v = ns.find_id(str(pn.nodes[0].id_value))	#, ignore_unknown=True)
				e.call.args = [
					HAULExpression(var=v),
					self.read_expression(pn.nodes[1].nodes[0].nodes[0], ns)	#, allow_undefined=True)
				]
				e.returnType = v.data_type	# This might result in "array", but we need the array base type!
			
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_trailer_paren):
				# Simple function call, e.g. "int(foo)"
				
				e.call = HAULCall()
				e.call.id = ns.find_id(str(pn.nodes[0].id_value), ignore_unknown=True)
				if e.call.id is None:
					put('Adding unknown function id: "%s"' % str(pn.nodes[0].id_value))
					e.call.id = ns.add_id(str(pn.nodes[0].id_value), kind=K_FUNCTION)
				
				# Add args
				for pnn in pn.nodes[1].nodes:
					e.call.args.append(self.read_expression(pnn, ns))
				
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_trailer_period):
				# Simple object lookup, e.g. "foo.bar"
				#put('UNIMPLEMENTED OBJECT LOOK_UP: ' + str(pn.nodes[1]))
				e.call = implicitCall(I_OBJECT_LOOKUP)
				v = ns.find_id(str(pn.nodes[0].id_value), ignore_unknown=True)
				e_var = HAULExpression()
				e_var.var = v
				e.call.args = [
					e_var,
					self.read_expression(pn.nodes[1].nodes[0], ns)
				]
				
			else:
				put('UNHANDLED EXPRESSION ATOM: ' + str(self.dump(pn)))
			
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_term):
			# Handle inline arithmetic, like "1024 * 16"
			#put('UNHANDLED TERM: ' + self.dump(pn))
			#for i,pnn in enumerate(pn.nodes): put('	%d = %s' % (i, self.dump(pnn)))
			e.call = HAULCall()
			#e.call.id = ns.find_id(str(pn.nodes[1].id_value))
			e.call.id = ns.find_id(mp_token_kind_names[pn.nodes[1].token_value], ignore_unknown=True)
			if e.call.id is None:
				put('Adding unknown term id: "%s"' % str(mp_token_kind_names[pn.nodes[1].token_value]))
				e.call.id = ns.add_id(mp_token_kind_names[pn.nodes[1].token_value], kind=K_FUNCTION)
			
			e.call.args.append(self.read_expression(pn.nodes[0], ns))
			e.call.args.append(self.read_expression(pn.nodes[2], ns))
			
		#elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_const_object):
		elif MP_PARSE_NODE_IS_NULL(pn):
			#put('UNHANDLED NULL')
			e.value = HAULValue(T_NOTHING)
			
		elif pn.kind_num_nodes & 0xff == RULE_const_object:
			put('const value!' + self.dump(pn))
			#e.value = HAULValue(T_INTEGER, )
			e.value = HAULValue(T_STRING, data_str=str(pn.nodes[0]))
		else:
			#put('UNKNOWN EXPRESSION: ' + str(self.dump(pn)))
			put('UNKNOWN EXPRESSION (pn.kind_num_nodes=%d): %s' % (pn.kind_num_nodes & 0xff, str(self.dump(pn))))
		return e
	
	def read_block(self, pn:mp_parse_node_t, namespace:HAULNamespace) -> HAULBlock:
		b:HAULBlock = HAULBlock()
		ns = namespace
		
		if MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_suite_block_stmts):
			# Block of code
			for pnn in pn.nodes:	#pnn:mp_parse_node_t
				i:HAULInstruction = self.read_instruction(pnn, ns)
				b.add_instruction(i)
		else:
			# Single instruction
			i:HAULInstruction = self.read_instruction(pn, ns)
			b.add_instruction(i)
		
		return b
	
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
			r += 'STRUCT: pn=%s (%d) {\t// line %d\n' % (
				rule_name_table[kind] if kind < len(rule_name_table) else '0x%02X'%kind,
				kind,
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
			r += 'UNKNOWN NODE: pn=%s\n' % str(pn)
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