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
	print(t)
	#pass

#mp_token_to_id = mp_token_kind_names, see micropython_lexer.py
mp_token_to_id = [
	'MP_TOKEN_END',	#0
	'MP_TOKEN_INVALID',	#1
	'MP_TOKEN_DEDENT_MISMATCH',	#2
	'MP_TOKEN_LONELY_STRING_OPEN',	#3
	#if MICROPY_PY_FSTRINGS
	'MP_TOKEN_MALFORMED_FSTRING',	#4
	'MP_TOKEN_FSTRING_RAW',	#5
	#endif
	'MP_TOKEN_NEWLINE',	#6
	'MP_TOKEN_INDENT',	#7
	'MP_TOKEN_DEDENT',	#8
	'MP_TOKEN_NAME',	#9
	'MP_TOKEN_INTEGER',	#10
	'MP_TOKEN_FLOAT_OR_IMAG',	#11
	'MP_TOKEN_STRING',	#12
	'MP_TOKEN_BYTES',	#13
	'MP_TOKEN_ELLIPSIS',	#14
	'False',	#' = MP_TOKEN_KW_FALSE',	#15
	'MP_TOKEN_KW_NONE',	#16
	'True',	#' = MP_TOKEN_KW_TRUE',	#17
	'MP_TOKEN_KW___DEBUG__',	#18
	'and',	#' = MP_TOKEN_KW_AND',	#19
	'MP_TOKEN_KW_AS',	#20
	'MP_TOKEN_KW_ASSERT',	#21
	#if MICROPY_PY_ASYNC_AWAIT
	'MP_TOKEN_KW_ASYNC',	#22
	'MP_TOKEN_KW_AWAIT',	#23
	#endif
	'MP_TOKEN_KW_BREAK',	#24
	'MP_TOKEN_KW_CLASS',	#25
	'MP_TOKEN_KW_CONTINUE',	#26
	'MP_TOKEN_KW_DEF',	#27
	'MP_TOKEN_KW_DEL',	#28
	'MP_TOKEN_KW_ELIF',	#29
	'MP_TOKEN_KW_ELSE',	#30
	'MP_TOKEN_KW_EXCEPT',	#31
	'MP_TOKEN_KW_FINALLY',	#32
	'MP_TOKEN_KW_FOR',	#33
	'MP_TOKEN_KW_FROM',	#34
	'MP_TOKEN_KW_GLOBAL',	#35
	'MP_TOKEN_KW_IF',	#36
	'MP_TOKEN_KW_IMPORT',	#37
	'MP_TOKEN_KW_IN',	#38
	'MP_TOKEN_KW_IS',	#39
	'MP_TOKEN_KW_LAMBDA',	#40
	'MP_TOKEN_KW_NONLOCAL',	#41
	'not',	#'MP_TOKEN_KW_NOT',	#42
	'or',	#'MP_TOKEN_KW_OR',	#43
	'MP_TOKEN_KW_PASS',	#44
	'MP_TOKEN_KW_RAISE',	#45
	'MP_TOKEN_KW_RETURN',	#46
	'MP_TOKEN_KW_TRY',	#47
	'MP_TOKEN_KW_WHILE',	#48
	'MP_TOKEN_KW_WITH',	#49
	'MP_TOKEN_KW_YIELD',	#50
	'MP_TOKEN_OP_ASSIGN',	#51
	'MP_TOKEN_OP_TILDE',	#52
	# Order of these 6 matches corresponding 'MP_binary_op_t operator
	'<',	#' = MP_TOKEN_OP_LESS',	#53
	'>',	#' = MP_TOKEN_OP_MORE',	#54
	'==',	#' = MP_TOKEN_OP_DBL_EQUAL',	#55
	'<=',	#' = MP_TOKEN_OP_LESS_EQUAL',	#56
	'>=',	#' = MP_TOKEN_OP_MORE_EQUAL',	#57
	'!=',	#' = MP_TOKEN_OP_NOT_EQUAL',	#58
	# Order of these 13 matches corresponding 'MP_binary_op_t operator
	'|',	#' = MP_TOKEN_OP_PIPE',	#59
	'^',	#' = MP_TOKEN_OP_CARET',	#60
	'&',	#' = MP_TOKEN_OP_AMPERSAND',	#61
	'<<',	#' = MP_TOKEN_OP_DBL_LESS',	#62
	'>>',	#' = MP_TOKEN_OP_DBL_MORE',	#63
	'+',	#' = MP_TOKEN_OP_PLUS',	#64
	'-',	#' = MP_TOKEN_OP_MINUS',	#65
	'*',	#' = MP_TOKEN_OP_STAR',	#66
	'@',	#' = MP_TOKEN_OP_AT',	#67
	'//',	#' = MP_TOKEN_OP_DBL_SLASH',	#68
	'/',	#' = MP_TOKEN_OP_SLASH',	#69
	'%',	#' = MP_TOKEN_OP_PERCENT',	#70
	'**',	#' = MP_TOKEN_OP_DBL_STAR',	#71
	# Order of these 13 matches corresponding 'MP_binary_op_t operator
	'|=',	#' = MP_TOKEN_DEL_PIPE_EQUAL',	#72
	'^=',	#' = MP_TOKEN_DEL_CARET_EQUAL',	#73
	'&=',	#' = MP_TOKEN_DEL_AMPERSAND_EQUAL',	#74
	'<<=',	#' = MP_TOKEN_DEL_DBL_LESS_EQUAL',	#75
	'>>=',	#' = MP_TOKEN_DEL_DBL_MORE_EQUAL',	#76
	'+=',	#' = MP_TOKEN_DEL_PLUS_EQUAL',	#77
	'-=',	#' = MP_TOKEN_DEL_MINUS_EQUAL',	#78
	'*=',	#' = MP_TOKEN_DEL_STAR_EQUAL',	#79
	'@=',	#' = MP_TOKEN_DEL_AT_EQUAL',	#80
	'//=',	#' = MP_TOKEN_DEL_DBL_SLASH_EQUAL',	#81
	'/=',	#' = MP_TOKEN_DEL_SLASH_EQUAL',	#82
	'%=',	#' = MP_TOKEN_DEL_PERCENT_EQUAL',	#83
	'**=',	#' = MP_TOKEN_DEL_DBL_STAR_EQUAL',	#84
	'MP_TOKEN_DEL_PAREN_OPEN',	#85
	'MP_TOKEN_DEL_PAREN_CLOSE',	#86
	'MP_TOKEN_DEL_BRACKET_OPEN',	#87
	'MP_TOKEN_DEL_BRACKET_CLOSE',	#88
	'MP_TOKEN_DEL_BRACE_OPEN',	#89
	'MP_TOKEN_DEL_BRACE_CLOSE',	#90
	'MP_TOKEN_DEL_COMMA',	#91
	'MP_TOKEN_DEL_COLON',	#92
	'MP_TOKEN_DEL_PERIOD',	#93
	'MP_TOKEN_DEL_SEMICOLON',	#94
	'=',	#' = MP_TOKEN_DEL_EQUAL',	#95
	'->',	#' = MP_TOKEN_DEL_MINUS_MORE',	#95
]

binary_op_to_id = [
	# The following 9+13+13 ops are used in bytecode and changing
	# them requires changing the bytecode version.

	# 9 relational operations, should return a bool; order of first 6 matches corresponding mp_token_kind_t
	'MP_BINARY_OP_LESS',	# 0
	'MP_BINARY_OP_MORE',	# 1
	'MP_BINARY_OP_EQUAL',	# 2
	'MP_BINARY_OP_LESS_EQUAL',	# 3
	'MP_BINARY_OP_MORE_EQUAL',	# 4
	'MP_BINARY_OP_NOT_EQUAL',	# 5
	'MP_BINARY_OP_IN',	# = 6
	'MP_BINARY_OP_IS',	# = 7
	'MP_BINARY_OP_EXCEPTION_MATCH',	# = 8
	
	# 13 inplace arithmetic operations; order matches corresponding mp_token_kind_t
	'MP_BINARY_OP_INPLACE_OR',	# = 9
	'MP_BINARY_OP_INPLACE_XOR',	# = 10
	'MP_BINARY_OP_INPLACE_AND',	# = 11
	'MP_BINARY_OP_INPLACE_LSHIFT',	# = 12
	'MP_BINARY_OP_INPLACE_RSHIFT',	# = 13
	'MP_BINARY_OP_INPLACE_ADD',	# = 14
	'MP_BINARY_OP_INPLACE_SUBTRACT',	# = 15
	'MP_BINARY_OP_INPLACE_MULTIPLY',	# = 16
	'MP_BINARY_OP_INPLACE_MAT_MULTIPLY',	# = 17
	'MP_BINARY_OP_INPLACE_FLOOR_DIVIDE',	# = 18
	'MP_BINARY_OP_INPLACE_TRUE_DIVIDE',	# = 19
	'MP_BINARY_OP_INPLACE_MODULO',	# = 20
	'MP_BINARY_OP_INPLACE_POWER',	# = 21
	
	# 13 normal arithmetic operations; order matches corresponding mp_token_kind_t
	'|',	#MP_BINARY_OP_OR',	# = 22
	'^',	#MP_BINARY_OP_XOR',	# = 23
	'&',	#MP_BINARY_OP_AND',	# = 24
	'<<',	#MP_BINARY_OP_LSHIFT',	#  = 25
	'>>',	#MP_BINARY_OP_RSHIFT',	# = 26
	'+',	#'MP_BINARY_OP_ADD',	#  = 27
	'-',	#MP_BINARY_OP_SUBTRACT',	#  = 28
	'*',	#MP_BINARY_OP_MULTIPLY',	#  = 29
	'MP_BINARY_OP_MAT_MULTIPLY',	# = 30
	'//',	#MP_BINARY_OP_FLOOR_DIVIDE',	# = 31
	'/',	#MP_BINARY_OP_TRUE_DIVIDE',	# = 32
	'%',	#MP_BINARY_OP_MODULO',	# = 33
	'^',	#MP_BINARY_OP_POWER',	# = 34
	
	# Operations below this line don't appear in bytecode, they
	# just identify special methods.
	
	# This is not emitted by the compiler but is supported by the runtime.
	# It must follow immediately after MP_BINARY_OP_POWER.
	'MP_BINARY_OP_DIVMOD',	# = 35
	
	# The runtime will convert MP_BINARY_OP_IN to this operator with swapped args.
	# A type should implement this containment operator instead of MP_BINARY_OP_IN.
	'MP_BINARY_OP_CONTAINS',	# = 36
	
	# 13 MP_BINARY_OP_REVERSE_* operations must be in the same order as MP_BINARY_OP_*	 = 0
	# and be the last ones supported by the runtime.
	'MP_BINARY_OP_REVERSE_OR',	# = 37
	'MP_BINARY_OP_REVERSE_XOR',	# = 38
	'MP_BINARY_OP_REVERSE_AND',	# = 39
	'MP_BINARY_OP_REVERSE_LSHIFT',	# = 40
	'MP_BINARY_OP_REVERSE_RSHIFT',	# = 41
	'MP_BINARY_OP_REVERSE_ADD',	# = 42
	'MP_BINARY_OP_REVERSE_SUBTRACT',	# = 43
	'MP_BINARY_OP_REVERSE_MULTIPLY',	# = 44
	'MP_BINARY_OP_REVERSE_MAT_MULTIPLY',	# = 45
	'MP_BINARY_OP_REVERSE_FLOOR_DIVIDE',	# = 46
	'MP_BINARY_OP_REVERSE_TRUE_DIVIDE',	# = 47
	'MP_BINARY_OP_REVERSE_MODULO',	# = 48
	'MP_BINARY_OP_REVERSE_POWER',	# = 49
	
	# These 2 are not supported by the runtime and must be synthesised by the emitter
	'MP_BINARY_OP_NOT_IN',	# = 50
	'MP_BINARY_OP_IS_NOT',	# = 51
]

class HAULReader_micropy(HAULReader):
	def __init__(self, stream, filename):
		HAULReader.__init__(self, stream, filename)
		
		self.default_extension = 'py'
		
		self.root_pn = self.prepare_mp_parse_tree()
		self.last_line_num = 0
	
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
		return pn
	
	def read_module(self, name:str, namespace:HAULNamespace, pn:mp_parse_node_t=None) -> HAULModule:
		
		if pn is None:
			put('Using root_pn as start node to read_module...')
			pn = self.root_pn
		
		self.last_line_num = 0
		
		assert(MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_file_input_2))
		
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
			if MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_import_name):
				name:str = str(pnn.nodes[0].id_value)
				put('Importing "%s"' % name)
				m.add_import(name)
				
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_funcdef):
				f:HAULFunction = self.read_function(pnn, ns)
				m.add_func(f)
				
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_classdef):
				c:HAULClass = self.read_class(pnn, ns)
				m.add_class(c)
				
			elif MP_PARSE_NODE_IS_TOKEN_KIND(pnn, MP_TOKEN_NEWLINE):
				# Ignore stray newline
				pass
			else:
				# Treat as normal instruction
				i:HAULInstruction = self.read_instruction(pnn, ns, cls=m)
				m.block.add_instruction(i)
			
		return m
	
	def read_function(self, pn:mp_parse_node_t, namespace:HAULNamespace) -> HAULFunction:
		f:HAULFunction = HAULFunction()
		f.origin = pn.source_line	#self.loc()
		name = str(pn.nodes[0].id_value)
		f.id = namespace.add_id(name=name, kind=K_FUNCTION, data_type=T_UNKNOWN, origin=f.origin)
		
		if name == '__init__':
			# __init__ must be able to write to class namespace
			ns = namespace
		else:
			ns = namespace.get_or_create_namespace(name)
		f.namespace = ns
		
		# Args
		#put('args=' + str(self.dump(pn.nodes[1])))
		if MP_PARSE_NODE_IS_ID(pn.nodes[1]):
			# Single argument, e.g. "def foo(bar)"
			i = ns.add_id(name=str(pn.nodes[1].id_value), kind=K_VARIABLE, data_type=T_UNKNOWN, origin=f.origin)
			f.add_arg( i )
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_typedargslist_name):
			put('! RULE_typedargslist_name=' + str(self.dump(pn.nodes[1])))
			#name = str(pn.nodes[1].nodes[0].id_value)
			typ = T_UNKNOWN	#@TODO: str(pn.nodes[1].nodes[1].id_value)
			#@TODO: def_value = str(pn.nodes[1].nodes[2])
			i = ns.add_id(name=str(pn.nodes[1].nodes[0].id_value), kind=K_VARIABLE, data_type=typ, origin=f.origin)
			f.add_arg( i )
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_typedargslist):
			# Multiple arguments, e.g. "def someMethod(self, a,b,c):"
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
		
		f.block = self.read_block(pn.nodes[3], ns)
		return f
	
	def read_class(self, pn:mp_parse_node_t, namespace:HAULNamespace) -> HAULClass:
		#put('Class: ' + self.dump(pn))
		c:HAULClass = HAULClass()
		c.origin = pn.source_line	#self.loc()
		name = str(pn.nodes[0].id_value)
		c.id = namespace.add_id(name=name, kind=K_CLASS, data_type=T_CLASS, origin=c.origin)
		
		ns = namespace.get_or_create_namespace(name)
		
		#@TODO: Read inheritance
		pn_inherit = pn.nodes[1]
		
		c.block = self.read_block(pn.nodes[2], ns, cls=c)
		
		#@FIXME: What's up with nodes[3]? It is always NULL in my test cases
		assert(MP_PARSE_NODE_IS_NULL(pn.nodes[3]))
		
		return c
	
	def read_instruction(self, pn:mp_parse_node_t, namespace:HAULNamespace, cls:HAULClass=None) -> HAULInstruction:
		i = HAULInstruction()
		i.origin = pn.source_line	#self.loc()
		ns = namespace
		
		#put_debug('Line %d' % pn.source_line)
		#put_debug(self.dump(pn))
		self.last_line_num = pn.source_line
		
		if MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_expr_stmt):
			
			# Expression has 2 children. If second child is set, the instruction is a SET instruction
			assert(len(pn.nodes) == 2)
			
			if MP_PARSE_NODE_IS_NULL(pn.nodes[1]):
				# No "right side" => Function call
				# Read as expression and turn it into a call
				e_call = self.read_expression(pn.nodes[0], ns)
				i.call = e_call.call
				
			else:
				# Right side exists => Set instruction
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
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_funcdef):
			f:HAULFunction = self.read_function(pn, ns)
			#@TODFO: This function must be "attributed" to the closest class or module in the hierarchy
			cls.add_func(f)
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_if_stmt):
			# IF instruction
			# if_stmt has 4 children: if-expression, then-block, elif-block, else-block
			assert(len(pn.nodes) == 4)
			
			ctrl = implicitControl(C_IF)
			#put('IF: ' + str(self.dump(pn)))
			ctrl.add_expression(self.read_expression(pn.nodes[0], ns))
			
			ctrl.add_block(self.read_block(pn.nodes[1], ns))
			
			last_if = ctrl
			if not MP_PARSE_NODE_IS_NULL(pn.nodes[2]):
				# elif block(s)
				assert(MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[2], RULE_if_stmt_elif_list))
				# Add all elifs
				for pnn in pn.nodes[2].nodes:
					assert(MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_if_stmt_elif))
					assert(len(pnn.nodes) == 2)
					block_elif = HAULBlock()
					block_elif.ns = ns.get_or_create_namespace('elif_%d' % pnn.source_line)
					
					i_elif = HAULInstruction()
					i_elif.origin = pnn.source_line
					
					ctrl_elif = implicitControl(C_IF)
					ctrl_elif.add_expression(self.read_expression(pnn.nodes[0], ns))
					ctrl_elif.add_block(self.read_block(pnn.nodes[1], ns))
					i_elif.control = ctrl_elif
					
					block_elif.add_instruction(i_elif)
					last_if.add_block(block_elif)
					last_if = ctrl_elif
				
			if not MP_PARSE_NODE_IS_NULL(pn.nodes[3]):
				# Add else block to last if
				last_if.add_block(self.read_block(pn.nodes[3], ns))
			i.control = ctrl
			
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_while_stmt):
			# WHILE instruction
			ctrl = implicitControl(C_WHILE)
			ctrl.add_expression(self.read_expression(pn.nodes[0], ns))
			ctrl.add_block(self.read_block(pn.nodes[1], ns))
			#@TODO: Optional else-block at pn.nodes[2]
			i.control = ctrl
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_for_stmt):
			# FOR instruction
			
			ctrl = implicitControl(C_FOR)
			assert(MP_PARSE_NODE_IS_ID(pn.nodes[0]))
			v = ns.find_id(pn.nodes[0].id_value, ignore_unknown=True)	# for can introduce new variables
			if v is None:
				put('Adding FOR iterator "%s", since it is not yet known in line %d' % (str(pn.nodes[0].id_value), self.last_line_num))
				v = ns.add_id(name=str(pn.nodes[0].id_value), kind=K_VARIABLE, data_type=T_UNKNOWN, origin=i.origin)
			ctrl.add_expression(HAULExpression(var=v))	# 1st expression: Iterator (i.e. variable)
			ctrl.add_expression(self.read_expression(pn.nodes[1], ns))	# 2nd expression: range
			
			ctrl.add_block(self.read_block(pn.nodes[2], ns))
			#@TODO: Optional else-block at pn.nodes[2]
			i.control = ctrl
			
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_return_stmt):
			ctrl = implicitControl(C_RETURN)
			assert(len(pn.nodes) == 1)	# Assume only one return value
			
			e = self.read_expression(pn.nodes[0], namespace=ns)
			ctrl.add_expression(e)
			
			# Retro-actively infer function's return type:
			#if ((INFER_TYPE) and (e.returnType != T_UNKNOWN) and (i != None) and (i.data_type == T_UNKNOWN)):
			#	put_debug('Inferring return type "' + str(e.returnType) + '" for function "' + str(iret) + '" from return statement')
			#	i.data_type = e.returnType
			#	#self.lastFunction.returnType = e.returnType
			i.control = ctrl
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_import_name):
			name:str = str(pn.nodes[0].id_value)
			put('! Unhandled import: Not on module level: "%s"!' % name)
			#m.add_import(name)
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_import_from):
			#name:str = str(pn.nodes[0].id_value)
			put('! Unhandled import (from): Not on module level: %s' % self.dump(pn))
			#m.add_import(name)
		else:
			put('UNKNOWN INSTRUCTION NODE: ' + self.dump(pn))
		
		return i
	
	
	def read_expression(self, pn:mp_parse_node_t, namespace:HAULNamespace, allow_undefined=False):
		e = HAULExpression()
		e.origin = self.last_line_num	#pn.source_line	#self.loc()
		ns = namespace
		
		e.returnType = T_UNKNOWN
		
		#put('@TODO: expression: ' + str(pn))
		if MP_PARSE_NODE_IS_ID(pn):
			if allow_undefined:
				#@TODO: Get type from augmented set!
				e.var = ns.find_id(str(pn.id_value), ignore_unknown=True)	# Just gloss over unknown ids
				if e.var is None:
					put('expression: Introducing previously unknown id "%s" at %d' % (str(pn.id_value), e.origin))
					e.var = ns.add_id(str(pn.id_value), kind=None, origin=e.origin)
			else:
				e.var = ns.find_id(str(pn.id_value), ignore_unknown=False)	# Will stop translation if ID was not found
				#
			
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
				put('expression: UNKNOWN Token as value: ' + str(pn))
				e.value = HAULValue(T_STRING, data_str=mp_token_kind_names[pn.token_value])	#@FIXME: I am just outputting the MP token as a string
				e.returnType = e.value.type
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_comparison):
			#put('UNIMPLEMENTED comparison in expression: ' + str(self.dump(pn)))
			
			e.call = HAULCall()
			# second child must be a token
			assert(MP_PARSE_NODE_IS_TOKEN(pn.nodes[1]))
			# e.g. for "==" = MP_TOKEN_OP_DBL_EQUAL
			#e.call.id = ns.find_id(mp_token_kind_names[pn.nodes[1].token_value], ignore_unknown=True)
			token_id = mp_token_to_id[pn.nodes[1].token_value]
			e.call.id = ns.find_id(token_id, ignore_unknown=True)
			if e.call.id is None:
				put('expression: Adding unknown infix token_id: "%s" (%d / "%s")' % (token_id, pn.nodes[1].token_value, mp_token_kind_names[pn.nodes[1].token_value]))
				e.call.id = ns.add_id(token_id, kind=K_FUNCTION, origin=e.origin)
			
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
				
				# ID, trailer_paren(arg, arg, arg, ...)
				assert(MP_PARSE_NODE_IS_ID(pn.nodes[0]))
				e.call.id = ns.find_id(str(pn.nodes[0].id_value), ignore_unknown=True)
				if e.call.id is None:
					put('expression: Adding unknown function id: "%s"' % str(pn.nodes[0].id_value))
					e.call.id = ns.add_id(str(pn.nodes[0].id_value), kind=K_FUNCTION, origin=e.origin)
				
				# Add args
				if MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1].nodes[0], RULE_arglist):
					# Argument list
					for pnn in pn.nodes[1].nodes[0].nodes:
						e.call.args.append(self.read_expression(pnn, ns))
				elif MP_PARSE_NODE_IS_NULL(pn.nodes[1].nodes[0]):
					# No arguments given
					pass
				elif len(pn.nodes[1].nodes) == 1:
					# One argument given
					e.call.args.append(self.read_expression(pn.nodes[1].nodes[0], ns))
				else:
					put('expression: UNHANDLED type of arguments for call: ' + self.dump(pn.nodes[1]))
				
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_trailer_period):
				# Simple object lookup, e.g. "foo.bar"
				#put('UNIMPLEMENTED OBJECT LOOK_UP: ' + str(pn.nodes[1]))
				e.call = implicitCall(I_OBJECT_LOOKUP)
				v = ns.find_id(str(pn.nodes[0].id_value), ignore_unknown=True)
				e_var = HAULExpression()
				e_var.var = v
				e.call.args = [
					e_var,
					self.read_expression(pn.nodes[1].nodes[0], ns, allow_undefined=allow_undefined)
				]
			
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_trailer_bracket):
				# Array look-up, e.g. "ar[123]"
				e.call = implicitCall(I_ARRAY_LOOKUP)
				v = ns.find_id(str(pn.nodes[0].id_value), ignore_unknown=True)
				assert(len(pn.nodes[1].nodes) == 1)	# Only one node inside the brackets... please?
				e.call.args = [
					HAULExpression(var=v),
					self.read_expression(pn.nodes[1].nodes[0], ns)
				]
			
			elif MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[1], RULE_atom_expr_trailers):
				# Simple invoke, e.g. "foo.startswith(bar)"
				put('expression: atom_expr_trailers: ' + str(self.dump(pn)))
				
				# Start with first item
				e.var = ns.find_id(str(pn.nodes[0].id_value))
				"""
				# Work through the trailers...
				for pnn in pn.nodes[1].nodes:
					if MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_trailer_period):
						# Object lookup
						assert(len(pnn.nodes) == 1)
						e_call = HAULCall()
						e_call.call = implicitCall(I_OBJECT_LOOKUP)
						e_call.args.append(e)
						e_call.args.append(self.read_expression(pnn.nodes[0]))
						e = e_call
						
					elif MP_PARSE_NODE_IS_STRUCT_KIND(pnn, RULE_trailer_paren):
						# Call!
						e_call = HAULCall()
						e_call.ca
				
				e_var.var = v
				e.call.args = [
					e_var,
					self.read_expression(pn.nodes[1].nodes[0], ns),
					self.read_expression(pn.nodes[1].nodes[1], ns)
				]
				"""
				
			else:
				put('expression: UNHANDLED atom_expr_normal: ' + str(self.dump(pn)))
			
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_term)\
		or MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_arith_expr):
			# Handle inline arithmetic, like "1024 * 16"
			e.call = HAULCall()
			
			#if not MP_PARSE_NODE_IS_TOKEN(pn.nodes[1]): put(self.dump(pn))
			assert(MP_PARSE_NODE_IS_TOKEN(pn.nodes[1]))
			token_id = mp_token_to_id[pn.nodes[1].token_value]
			e.call.id = ns.find_id(token_id, ignore_unknown=True)
			if e.call.id is None:
				put('expression: Adding unknown term token_id: "%s" (%d / "%s")' % (token_id, pn.nodes[1].token_value, mp_token_kind_names[pn.nodes[1].token_value]))
				e.call.id = ns.add_id(token_id, kind=K_FUNCTION, origin=e.origin)	# Mark as "INFIX"?
			
			e.call.args.append(self.read_expression(pn.nodes[0], ns))
			e.call.args.append(self.read_expression(pn.nodes[2], ns))
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_atom_bracket):
			# Array constructor, e.g. "[1, 2, 3]"
			#put('atom_bracket: %s' % self.dump(pn))
			e.call = implicitCall(I_ARRAY_CONSTRUCTOR)
			assert(len(pn.nodes) == 1)
			if MP_PARSE_NODE_IS_NULL(pn.nodes[0]):
				pass
			else:
				assert(MP_PARSE_NODE_IS_STRUCT_KIND(pn.nodes[0], RULE_testlist_comp))
				for pnn in pn.nodes[0].nodes:
					e.call.args.append(self.read_expression(pnn, ns))
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_and_test):
			e.call = HAULCall()
			e.call.id = ns.find_id('and')
			for pnn in pn.nodes:
				e.call.args.append(self.read_expression(pnn, ns))
		
		elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_or_test):
			e.call = HAULCall(ns.find_id('or'))
			for pnn in pn.nodes:
				e.call.args.append(self.read_expression(pnn, ns))
		
		#elif MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_const_object):
		elif MP_PARSE_NODE_IS_NULL(pn):
			put('expression: NULL encountered at line %d!' % self.last_line_num)
			#put('UNHANDLED NULL')
			e.value = HAULValue(T_NOTHING)
			
		elif pn.kind_num_nodes & 0xff == RULE_const_object:
			if type(pn.nodes[0]) is int:
				e.value = HAULValue(T_INTEGER, data_int=str(pn.nodes[0]))
			elif type(pn.nodes[0]) is str:
				e.value = HAULValue(T_STRING, data_str=str(pn.nodes[0]))
			elif type(pn.nodes[0]) is mp_binary_op_t_c:
				# Binary operation, see parser.py:mp_binary_op(op, arg0, arg1)
				#binary_op_id = pn.nodes[0].op
				binary_op_id = binary_op_to_id[pn.nodes[0].op]
				id = ns.find_id(binary_op_id, ignore_unknown=True)
				if id is None:
					put('Adding unknown binary op: "%s" in line %d' % (binary_op_id, self.last_line_num))
					id = ns.add_id(binary_op_id, kind=K_FUNCTION, origin=e.origin)
				e.call = HAULCall(id)
				e.call.args.append(HAULExpression(value=HAULValue(T_INTEGER, data_int=pn.nodes[0].arg0)))
				e.call.args.append(HAULExpression(value=HAULValue(T_INTEGER, data_int=pn.nodes[0].arg1)))
			else:
				put('expression: Unhandled const value: ' + self.dump(pn))
		else:
			#put('UNKNOWN EXPRESSION: ' + str(self.dump(pn)))
			put('expression: UNKNOWN (pn.kind=%d): %s' % (pn.kind_num_nodes & 0xff, str(self.dump(pn))))
		return e
	
	
	def read_block(self, pn:mp_parse_node_t, namespace:HAULNamespace, cls:HAULClass=None) -> HAULBlock:
		b:HAULBlock = HAULBlock()
		ns = namespace
		
		if MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_suite_block_stmts):
			# Block of code
			for pnn in pn.nodes:	#pnn:mp_parse_node_t
				i:HAULInstruction = self.read_instruction(pnn, ns, cls=cls)
				b.add_instruction(i)
		else:
			# Single instruction
			i:HAULInstruction = self.read_instruction(pn, ns, cls=cls)
			b.add_instruction(i)
		
		return b
	
	def dump(self, pn:mp_parse_node_t, indent:int=0):
		
		#r = 'pn:\n'
		r = DUMP_INDENT*indent
		
		if pn is None:
			r += 'None\n'
		elif not isinstance(pn, mp_parse_node_t):
			r += 'value: %s (%s)\n' % (str(pn), str(type(pn)))
		elif MP_PARSE_NODE_IS_TOKEN(pn):
			r += 'TOKEN: %s\n' % str(pn)
			#r += '%s\n' % str(pn)
		#elif MP_PARSE_NODE_IS_NULL(pn) and (i == num_nodes-1):
		#	r += 'pn=NULL = END\n' % (DUMP_INDENT * (indent+1))
		#	#continue	# Do not dump trailing NULLs
		elif MP_PARSE_NODE_IS_STRUCT(pn):
			#r += 'root=%s' % pn.dump()
			kind = pn.kind_num_nodes & 0xff
			## Unhandled: Just dump
			r += 'STRUCT %s (%d) {\t// line %d\n' % (
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
			#r += 'pn=%s\n' % str(pn)
			r += '%s\n' % str(pn)
		return r


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