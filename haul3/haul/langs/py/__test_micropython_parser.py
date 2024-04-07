#!/bin/python3
"""
Translation of MicroPython's "py/parser.h/c" to Python
It is based on the "expand_macros" processed "grammar.h".

2024-04-06 Bernhard "HotKey" Slawik

"""

# Verbosity options
LEXER_VERBOSE = True	# Show tokens as they are streamed in
PARSER_VERBOSE_RULES = not True	# Show rule matching
PARSER_VERBOSE_RESULT_TOKEN = not True	# Show result tokens as they are pushed
PARSER_VERBOSE_RESULT_NODE = not True	# Show result nodes as they are pushed
PARSER_VERBOSE_RESULT_POP = not True	# Show parse nodes as they are popped
DUMP_INDENT = '  '	#'\t'
### Glue code

# Set lexer to verbose
if LEXER_VERBOSE:
	import __test_micropython_lexer
	__test_micropython_lexer.MP_LEXER_VERBOSE = True

from __test_micropython_lexer import *

def put(t):
	print(t)


MICROPY_ALLOC_PARSE_RULE_INIT = 16	# Initial size of rule stack (automatically incremented if more is needed)
MICROPY_ALLOC_PARSE_RESULT_INIT = 16	# Initial size of result stack (automatically incremented if more is needed)
MICROPY_ALLOC_PARSE_INTERN_STRING_LEN = 1024 * 16	# Maximum length of strings before raising an Exception

# Define some types for interoperability
size_t = int
uint8_t = int
uint16_t = int
uint32_t = int

MP_QSTRnull = None	#@FIXME: ???
MP_QSTR_const = 'const'	#@FIXME: ????

MP_UNARY_OP_INVERT = -1	#@FIXME: ???
MP_UNARY_OP_POSITIVE = 1	#@FIXME: ???
def mp_unary_op(op, arg):
	return arg	#@FIXME: ????

def mp_parse_num_integer(t):
	if t.startswith('0x'): return int(t, 16)
	return int(t)

# a mp_parse_node_t is:
#  - 0000...0000: no node
#  - xxxx...xxx1: a small integer; bits 1 and above are the signed value, 2's complement
#  - xxxx...xx00: pointer to mp_parse_node_struct_t
#  - xx...xx0010: an identifier; bits 4 and above are the qstr
#  - xx...xx0110: a string; bits 4 and above are the qstr holding the value
#  - xx...xx1010: a token; bits 4 and above are mp_token_kind_t
MP_PARSE_NODE_NULL      = 0
MP_PARSE_NODE_SMALL_INT = 0x1
MP_PARSE_NODE_ID        = 0x02
MP_PARSE_NODE_STRING    = 0x06
MP_PARSE_NODE_TOKEN     = 0x0a
#typedef uintptr_t mp_parse_node_t; // must be pointer size
#mp_parse_node_t = int	#uintptr_t


"""
	### Original C implementation stores parse_nodes as numbers. The lowest bits determine the type, the upper bits are the data/pointer

	class mp_parse_node_struct_t:
		source_line:uint32_t = 0	# line number in source file
		kind_num_nodes:uint32_t = 0	# parse node kind, and number of nodes
		nodes = []	#nodes
		def __init__(self, num_args):
			self.nodes = [ mp_parse_node_t() for i in range(num_args) ]

	# macros for mp_parse_node_t usage
	# some of these evaluate their argument more than once

	def MP_PARSE_NODE_IS_NULL(pn):	return ((pn) == MP_PARSE_NODE_NULL)
	def MP_PARSE_NODE_IS_LEAF(pn):	return ((pn) & 3)
	#return type(pn) is int	#mp_parse_node_struct_t

	def MP_PARSE_NODE_IS_STRUCT(pn): return ((pn) != MP_PARSE_NODE_NULL and ((pn) & 3) == 0)
	#return (pn is not None) and (type(pn) is mp_parse_node_struct_t)
		
	def MP_PARSE_NODE_IS_STRUCT_KIND(pn, k): return ((pn) != MP_PARSE_NODE_NULL and ((pn) & 3) == 0 and MP_PARSE_NODE_STRUCT_KIND((pn)) == (k))
	#return MP_PARSE_NODE_IS_STRUCT(pn) and (MP_PARSE_NODE_STRUCT_KIND(pn) == k)

	def MP_PARSE_NODE_IS_SMALL_INT(pn): return (((pn) & 0x1) == MP_PARSE_NODE_SMALL_INT)
	def MP_PARSE_NODE_IS_ID(pn): return (((pn) & 0x0f) == MP_PARSE_NODE_ID)
	def MP_PARSE_NODE_IS_TOKEN(pn): return (((pn) & 0x0f) == MP_PARSE_NODE_TOKEN)
	def MP_PARSE_NODE_IS_TOKEN_KIND(pn, k): return ((pn) == (MP_PARSE_NODE_TOKEN | ((k) << 4)))

	def MP_PARSE_NODE_LEAF_KIND(pn): return ((pn) & 0x0f)
	def MP_PARSE_NODE_LEAF_ARG(pn): return (((pn)) >> 4)
	def MP_PARSE_NODE_LEAF_SMALL_INT(pn): return (((pn)) >> 1)
	def MP_PARSE_NODE_STRUCT_KIND(pns): return ((pns).kind_num_nodes & 0xff)
	def MP_PARSE_NODE_STRUCT_NUM_NODES(pns): return ((pns).kind_num_nodes >> 8)


	def mp_parse_node_new_small_int(v):
		#put('mp_parse_node_new_small_int: %s (%s)' % (str(v), str(type(v))))
		return v

	def mp_parse_node_new_leaf(kind:size_t, arg:mp_int_t) -> mp_parse_node_t:
		#return (mp_parse_node_t)(kind | ((mp_uint_t)arg << 4));
		return kind | (arg << 4)

	def mp_obj_is_small_int(o):
		return (type(o) is int) and (o < 16)
	def MP_OBJ_SMALL_INT_VALUE(o):
		return int(o)

	MP_OBJ_NEW_SMALL_INT = mp_parse_node_new_small_int
	MP_PARSE_NODE_LEAF_SMALL_INT = lambda o: o
"""

### htk: "Python-ification" of mp_parse_node_t
# Original uses numbers and re-interprets them. We are using class inheritance.
class mp_parse_node_t:
	typ:size_t = -1	#MP_PARSE_NODE_NULL
	def __repr__(self):
		if self.typ == -1: return '--'
		
		#return '%s (0x%02x), %s' % (self.__class__.__name__, self.typ, ', '.join([ '%s=%s'%(k,str(v)) if k.endswith('_value') else '' for k,v in self.__dict__.items() ]))
		return '%s (0x%02x), %s' % (self.__class__.__name__[len('mp_parse_node_'):-2].upper(), self.typ, ', '.join([ '%s=%s'%(k[:-len('_value')],str(v)) if k.endswith('_value') else '' for k,v in self.__dict__.items() ]))

class mp_parse_node_null_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_NULL
	def __repr__(self):
		return 'NULL (0x%02x)' % self.typ

class mp_parse_node_small_int_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_SMALL_INT
	small_int_value:int = 0
	def __init__(self, small_int_value:int):
		self.small_int_value = small_int_value
	def get_arg(self) -> int:
		return self.small_int_value

class mp_parse_node_id_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_ID
	id_value:qstr = None
	def __init__(self, id_value:qstr):
		self.id_value = id_value
	def get_arg(self) -> qstr:
		return self.id_value
	def __repr__(self):
		#return '%s (0x%02x), %s' % (self.__class__.__name__[len('mp_parse_node_'):-2].upper(), self.typ, ', '.join([ '%s=%s'%(k[:-len('_value')],str(v)) if k.endswith('_value') else '' for k,v in self.__dict__.items() ]))
		return 'ID: %s' % self.id_value

class mp_parse_node_string_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_STRING
	string_value:qstr = None
	def __init__(self, string_value:qstr):
		self.string_value = string_value
	def get_arg(self) -> qstr:
		return self.string_value
	def __repr__(self):
		#return '%s (0x%02x), %s' % (self.__class__.__name__[len('mp_parse_node_'):-2].upper(), self.typ, ', '.join([ '%s=%s'%(k[:-len('_value')],str(v)) if k.endswith('_value') else '' for k,v in self.__dict__.items() ]))
		return 'STRING: "%s"' % self.string_value

class mp_parse_node_token_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_TOKEN
	token_value:mp_token_kind_t = None
	def __init__(self, token_value:mp_token_kind_t):
		self.token_value = token_value
	def get_arg(self) -> mp_token_kind_t:
		return self.token_value
	def __repr__(self):
		#return 'TOKEN (0x%02x), token=%d / %s' % (self.typ, self.token_value, mp_token_kind_names[self.token_value])
		return 'TOKEN: %s (%d)' % (mp_token_kind_names[self.token_value], self.token_value)

MP_PARSE_NODE_STRUCT = 0x10	# Must follow xxxx...xx00 rule to be recognized
class mp_parse_node_struct_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_STRUCT	#htk
	source_line:uint32_t = 0	# line number in source file
	kind_num_nodes:uint32_t = 0	# parse node kind, and number of nodes	# Caution! This is BOTH in ONE value (low byte=kind / high byte=num_nodes)
	nodes = []	#nodes
	def __init__(self, num_args):
		self.nodes = [ mp_parse_node_t() for i in range(num_args) ]
	def __repr__(self):
		#return '%s (0x%02x), kind_num_nodes=0x%04x, %s' % (self.__class__.__name__, self.typ, self.kind_num_nodes, ', '.join([ str(n) for n in self.nodes ]))
		return '%s (0x%02x), kind_num_nodes=0x%04x' % (self.__class__.__name__, self.typ, self.kind_num_nodes)
	def dump(self, indent=0):
		#return '%sstruct (line %d)%s' % (source_line, )
		kind = self.kind_num_nodes & 0xff
		#r = '%sSTRUCT %s (in line %d) {' % (
		#r = '%s%s (0x%02x) (in line %d) {' % (
		r = '%sSTRUCT: %s {\t// line %d' % (
			DUMP_INDENT * indent,
			#mp_token_kind_names[kind] if kind in mp_token_kind_names else '???',
			rule_name_table[kind] if kind < len(rule_name_table) else '0x%02X'%kind,
			#kind,
			#self.typ,
			self.source_line
		)
		for pn in self.nodes:
			if not isinstance(pn, mp_parse_node_t):
				r += '\n%s??? %s (%s)' % (DUMP_INDENT * (indent+1), str(pn), str(type(pn)))
			elif MP_PARSE_NODE_IS_STRUCT(pn):
				r += '\n%s' % pn.dump(indent+1)
			else:
				r += '\n%s%s' % (DUMP_INDENT * (indent+1), str(pn))
		r += '\n%s}' % (DUMP_INDENT * indent)
		return r


def MP_PARSE_NODE_IS_NULL(pn):	return (pn.typ == MP_PARSE_NODE_NULL)
def MP_PARSE_NODE_IS_LEAF(pn):	return (pn.typ & 3) > 0
def MP_PARSE_NODE_IS_STRUCT(pn): return ((pn.typ != MP_PARSE_NODE_NULL) and ((pn.typ & 3) == 0))
def MP_PARSE_NODE_IS_STRUCT_KIND(pn, k): return ((pn.typ != MP_PARSE_NODE_NULL) and ((pn.typ & 3) == 0) and (MP_PARSE_NODE_STRUCT_KIND(pn) == k))
def MP_PARSE_NODE_IS_SMALL_INT(pn): return ((pn.typ & 0x1) == MP_PARSE_NODE_SMALL_INT)
def MP_PARSE_NODE_IS_ID(pn): return ((pn.typ & 0x0f) == MP_PARSE_NODE_ID)
def MP_PARSE_NODE_IS_TOKEN(pn): return ((pn.typ & 0x0f) == MP_PARSE_NODE_TOKEN)
def MP_PARSE_NODE_IS_TOKEN_KIND(pn, k): return (MP_PARSE_NODE_IS_TOKEN(pn) and (pn.token_value == k))

def MP_PARSE_NODE_LEAF_KIND(pn): return (pn.typ & 0x0f)
def MP_PARSE_NODE_LEAF_ARG(pn): return pn.get_arg()

def MP_PARSE_NODE_LEAF_SMALL_INT(pn): return pn.small_int_value
def MP_PARSE_NODE_STRUCT_KIND(pns): return (pns.kind_num_nodes & 0xff)
def MP_PARSE_NODE_STRUCT_NUM_NODES(pns): return (pns.kind_num_nodes >> 8)

def mp_obj_is_small_int(o):
	put('mp_obj_is_small_int: o=%s (%s)' % (str(o), str(type(o))))
	return (type(o) is int) and (o < 16)
def MP_OBJ_SMALL_INT_VALUE(o):
	return int(o)


def mp_parse_node_new_small_int(v:int) -> mp_parse_node_small_int_t:	#mp_parse_node_t
	#put('mp_parse_node_new_small_int: %s (%s)' % (str(v), str(type(v))))
	#return v
	return mp_parse_node_small_int_t(v)

def mp_parse_node_new_leaf(kind:size_t, arg:mp_int_t) -> mp_parse_node_t:
	#return (mp_parse_node_t)(kind | ((mp_uint_t)arg << 4));
	#return kind | (arg << 4)
	if kind == MP_PARSE_NODE_NULL:
		return mp_parse_node_t()
	elif kind == MP_PARSE_NODE_SMALL_INT:
		return mp_parse_node_small_int_t(arg)
	elif kind == MP_PARSE_NODE_ID:
		return mp_parse_node_id_t(arg)
	elif kind == MP_PARSE_NODE_STRING:
		return mp_parse_node_string_t(arg)
	elif kind == MP_PARSE_NODE_TOKEN:
		return mp_parse_node_token_t(arg)
	else:
		raise Exception('Unknown mp_parse_node leaf kind: 0x%04X' % kind)

###


class mp_dynamic_compiler_t:
	small_int_bits:int = 32
mp_dynamic_compiler = mp_dynamic_compiler_t()

mp_parse_input_kind_t:int = 0
MP_PARSE_SINGLE_INPUT = 0
MP_PARSE_FILE_INPUT = 1
MP_PARSE_EVAL_INPUT = 2


mp_map_t = dict
mp_obj_t = None


### Constants

if True:	# Allow folding all that stuff away
	### parse.c constants/enums
	RULE_ACT_ARG_MASK = 0x0f
	RULE_ACT_KIND_MASK = 0x30
	RULE_ACT_ALLOW_IDENT = 0x40
	RULE_ACT_ADD_BLANK = 0x80
	RULE_ACT_OR = 0x10
	RULE_ACT_AND = 0x20
	RULE_ACT_LIST = 0x30
	RULE_ARG_KIND_MASK = 0xf000
	RULE_ARG_ARG_MASK = 0x0fff
	RULE_ARG_TOK = 0x1000
	RULE_ARG_RULE = 0x2000
	RULE_ARG_OPT_RULE = 0x3000
	
	
	# enum
	RULE_file_input	= 0
	RULE_file_input_2	= 1
	RULE_decorated	= 2
	RULE_funcdef	= 3
	RULE_simple_stmt_2	= 4
	RULE_expr_stmt	= 5
	RULE_testlist_star_expr	= 6
	RULE_del_stmt	= 7
	RULE_pass_stmt	= 8
	RULE_break_stmt	= 9
	RULE_continue_stmt	= 10
	RULE_return_stmt	= 11
	RULE_yield_stmt	= 12
	RULE_raise_stmt	= 13
	RULE_import_name	= 14
	RULE_import_from	= 15
	RULE_global_stmt	= 16
	RULE_nonlocal_stmt	= 17
	RULE_assert_stmt	= 18
	#if MICROPY_PY_ASYNC_AWAIT
	RULE_async_stmt	= 19
	#endif
	RULE_if_stmt	= 20
	RULE_while_stmt	= 21
	RULE_for_stmt	= 22
	RULE_try_stmt	= 23
	RULE_with_stmt	= 24
	RULE_suite_block_stmts	= 25
	#if MICROPY_PY_ASSIGN_EXPR
	RULE_namedexpr_test	= 26
	#endif
	RULE_test_if_expr	= 27
	RULE_lambdef	= 28
	RULE_lambdef_nocond	= 29
	RULE_or_test	= 30
	RULE_and_test	= 31
	RULE_not_test_2	= 32
	RULE_comparison	= 33
	RULE_star_expr	= 34
	RULE_expr	= 35
	RULE_xor_expr	= 36
	RULE_and_expr	= 37
	RULE_shift_expr	= 38
	RULE_arith_expr	= 39
	RULE_term	= 40
	RULE_factor_2	= 41
	RULE_power	= 42
	#if MICROPY_PY_ASYNC_AWAIT
	RULE_atom_expr_await	= 43
	#else
	#endif
	RULE_atom_expr_normal	= 44
	RULE_atom_paren	= 45
	RULE_atom_bracket	= 46
	RULE_atom_brace	= 47
	RULE_trailer_paren	= 48
	RULE_trailer_bracket	= 49
	RULE_trailer_period	= 50
	#if MICROPY_PY_BUILTINS_SLICE
	RULE_subscriptlist	= 51
	RULE_subscript_2	= 52
	RULE_subscript_3	= 53
	#else
	#RULE_subscriptlist	= 54
	#endif
	RULE_testlist	= 54
	#if MICROPY_PY_BUILTINS_SET
	RULE_dictorsetmaker_item	= 55
	#else
	#RULE_dictorsetmaker_item	= 57
	#endif
	RULE_classdef	= 56
	#if MICROPY_PY_ASSIGN_EXPR
	#else
	#endif
	RULE_yield_expr	= 57
	RULE_const_object	= 58	# special node for a constant, generic Python object
	RULE_generic_colon_test	= 59
	RULE_generic_equal_test	= 60
	RULE_single_input	= 61
	RULE_file_input_3	= 62
	RULE_eval_input	= 63
	RULE_eval_input_2	= 64
	RULE_decorator	= 65
	RULE_decorators	= 66
	#if MICROPY_PY_ASYNC_AWAIT
	RULE_decorated_body	= 67
	RULE_async_funcdef	= 68
	#else
	#RULE_decorated_body	= 71
	#endif
	RULE_funcdefrettype	= 69
	RULE_typedargslist	= 70
	RULE_typedargslist_item	= 71
	RULE_typedargslist_name	= 72
	RULE_typedargslist_star	= 73
	RULE_typedargslist_dbl_star	= 74
	RULE_tfpdef	= 75
	RULE_varargslist	= 76
	RULE_varargslist_item	= 77
	RULE_varargslist_name	= 78
	RULE_varargslist_star	= 79
	RULE_varargslist_dbl_star	= 80
	RULE_vfpdef	= 81
	RULE_stmt	= 82
	RULE_simple_stmt	= 83
	RULE_small_stmt	= 84
	RULE_expr_stmt_2	= 85
	RULE_expr_stmt_augassign	= 86
	RULE_expr_stmt_assign_list	= 87
	RULE_expr_stmt_assign	= 88
	RULE_expr_stmt_6	= 89
	RULE_testlist_star_expr_2	= 90
	RULE_annassign	= 91
	RULE_augassign	= 92
	RULE_flow_stmt	= 93
	RULE_raise_stmt_arg	= 94
	RULE_raise_stmt_from	= 95
	RULE_import_stmt	= 96
	RULE_import_from_2	= 97
	RULE_import_from_2b	= 98
	RULE_import_from_3	= 99
	RULE_import_as_names_paren	= 100
	RULE_one_or_more_period_or_ellipsis	= 101
	RULE_period_or_ellipsis	= 102
	RULE_import_as_name	= 103
	RULE_dotted_as_name	= 104
	RULE_as_name	= 105
	RULE_import_as_names	= 106
	RULE_dotted_as_names	= 107
	RULE_dotted_name	= 108
	RULE_name_list	= 109
	RULE_assert_stmt_extra	= 110
	#if MICROPY_PY_ASYNC_AWAIT
	RULE_compound_stmt	= 111
	RULE_async_stmt_2	= 112
	#else
	#RULE_compound_stmt	= 116
	#endif
	RULE_if_stmt_elif_list	= 113
	RULE_if_stmt_elif	= 114
	RULE_try_stmt_2	= 115
	RULE_try_stmt_except_and_more	= 116
	RULE_try_stmt_except	= 117
	RULE_try_stmt_as_name	= 118
	RULE_try_stmt_except_list	= 119
	RULE_try_stmt_finally	= 120
	RULE_else_stmt	= 121
	RULE_with_stmt_list	= 122
	RULE_with_item	= 123
	RULE_with_item_as	= 124
	RULE_suite	= 125
	RULE_suite_block	= 126
	#if MICROPY_PY_ASSIGN_EXPR
	RULE_namedexpr_test_2	= 127
	#else
	#RULE_namedexpr_test	= 132
	#endif
	RULE_test	= 128
	RULE_test_if_else	= 129
	RULE_test_nocond	= 130
	RULE_not_test	= 131
	RULE_comp_op	= 132
	RULE_comp_op_not_in	= 133
	RULE_comp_op_is	= 134
	RULE_comp_op_is_not	= 135
	RULE_shift_op	= 136
	RULE_arith_op	= 137
	RULE_term_op	= 138
	RULE_factor	= 139
	RULE_factor_op	= 140
	#if MICROPY_PY_ASYNC_AWAIT
	RULE_atom_expr	= 141
	#else
	#RULE_atom_expr	= 147
	#endif
	RULE_atom_expr_trailers	= 142
	RULE_power_dbl_star	= 143
	RULE_atom	= 144
	RULE_atom_2b	= 145
	RULE_testlist_comp	= 146
	RULE_testlist_comp_2	= 147
	RULE_testlist_comp_3	= 148
	RULE_testlist_comp_3b	= 149
	RULE_testlist_comp_3c	= 150
	RULE_trailer	= 151
	#if MICROPY_PY_BUILTINS_SLICE
	RULE_subscript	= 152
	RULE_subscript_3b	= 153
	RULE_subscript_3c	= 154
	RULE_subscript_3d	= 155
	RULE_sliceop	= 156
	#else
	#endif
	RULE_exprlist	= 157
	RULE_exprlist_2	= 158
	RULE_dictorsetmaker	= 159
	#if MICROPY_PY_BUILTINS_SET
	#else
	#endif
	RULE_dictorsetmaker_tail	= 160
	RULE_dictorsetmaker_list	= 161
	RULE_dictorsetmaker_list2	= 162
	RULE_classdef_2	= 163
	RULE_arglist	= 164
	RULE_arglist_2	= 165
	RULE_arglist_star	= 166
	RULE_arglist_dbl_star	= 167
	RULE_argument	= 168
	#if MICROPY_PY_ASSIGN_EXPR
	RULE_argument_2	= 169
	RULE_argument_3	= 170
	#else
	#RULE_argument_2	= 177
	#endif
	RULE_comp_iter	= 171
	RULE_comp_for	= 172
	RULE_comp_if	= 173
	RULE_yield_arg	= 174
	RULE_yield_arg_from	= 175
	
	
	#static const uint8_t rule_act_table[]
	rule_act_table:[uint8_t] = [
		(RULE_ACT_AND | 1 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#if MICROPY_PY_ASYNC_AWAIT
		#else
		#endif
		(RULE_ACT_AND | 8 | RULE_ACT_ADD_BLANK),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_AND | 2),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 1),
		(RULE_ACT_AND | 1),
		(RULE_ACT_AND | 1),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 1),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 4),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 3),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ACT_AND | 2),
		#else
		#endif
		(RULE_ACT_AND | 6),
		(RULE_ACT_AND | 5),
		(RULE_ACT_AND | 7),
		(RULE_ACT_AND | 4),
		(RULE_ACT_AND | 4),
		(RULE_ACT_LIST | 2),
		#if MICROPY_PY_ASSIGN_EXPR
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#else
		#endif
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 4 | RULE_ACT_ADD_BLANK),
		(RULE_ACT_AND | 4 | RULE_ACT_ADD_BLANK),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_AND | 2),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_AND | 2),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ACT_AND | 3),
		#else
		#endif
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 3),
		(RULE_ACT_AND | 3),
		(RULE_ACT_AND | 3),
		(RULE_ACT_AND | 3),
		(RULE_ACT_AND | 3),
		(RULE_ACT_AND | 2),
		#if MICROPY_PY_BUILTINS_SLICE
		(RULE_ACT_LIST | 3),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2),
		#else
		#(RULE_ACT_LIST | 3),
		#endif
		(RULE_ACT_LIST | 3),
		#if MICROPY_PY_BUILTINS_SET
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#else
		#(RULE_ACT_AND | 3),
		#endif
		(RULE_ACT_AND | 5 | RULE_ACT_ADD_BLANK),
		#if MICROPY_PY_ASSIGN_EXPR
		#else
		#endif
		(RULE_ACT_AND | 2),
		0,	# special node for a constant, generic Python object
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 3),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 1),
		(RULE_ACT_AND | 4),
		(RULE_ACT_LIST | 2),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ACT_OR | 3),
		(RULE_ACT_AND | 2),
		#else
		#(RULE_ACT_OR | 2),
		#endif
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_OR | 3),
		(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 3),
		(RULE_ACT_AND | 2),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_OR | 3),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 1 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 8),
		(RULE_ACT_OR | 3),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 3),
		(RULE_ACT_OR | 13),
		(RULE_ACT_OR | 5),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 3),
		(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 2),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ACT_OR | 9),
		(RULE_ACT_OR | 3),
		#else
		#(RULE_ACT_OR | 8),
		#endif
		(RULE_ACT_LIST | 2),
		(RULE_ACT_AND | 4),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 4),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 2),
		(RULE_ACT_AND | 3),
		(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 1),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 4 | RULE_ACT_ALLOW_IDENT),
		#if MICROPY_PY_ASSIGN_EXPR
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#else
		#(RULE_ACT_OR | 1),
		#endif
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 4),
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 9),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 1),
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 5),
		(RULE_ACT_OR | 2),	#@FIXME: It said "rule(factor_2),"!
		(RULE_ACT_OR | 3),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ACT_OR | 2),
		#else
		#(RULE_ACT_OR | 1),
		#endif
		(RULE_ACT_LIST | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 12),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_OR | 3),
		#if MICROPY_PY_BUILTINS_SLICE
		(RULE_ACT_OR | 2),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_AND | 2),
		#else
		#endif
		(RULE_ACT_LIST | 3),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#if MICROPY_PY_BUILTINS_SET
		#else
		#endif
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
		(RULE_ACT_LIST | 3),
		(RULE_ACT_OR | 3),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2),
		(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
		#if MICROPY_PY_ASSIGN_EXPR
		(RULE_ACT_OR | 3),
		(RULE_ACT_AND | 2),
		#else
		#(RULE_ACT_OR | 2),
		#endif
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 5 | RULE_ACT_ADD_BLANK),
		(RULE_ACT_AND | 3),
		(RULE_ACT_OR | 2),
		(RULE_ACT_AND | 2),
	]
	
	#static const uint16_t rule_arg_combined_table[]
	rule_arg_combined_table:[uint16_t] = [
		(RULE_ARG_OPT_RULE | RULE_file_input_2),
		(RULE_ARG_RULE | RULE_file_input_3),
		(RULE_ARG_RULE | RULE_decorators), (RULE_ARG_RULE | RULE_decorated_body),
		#if MICROPY_PY_ASYNC_AWAIT
		#else
		#endif
		(RULE_ARG_TOK | MP_TOKEN_KW_DEF), (RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_typedargslist), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE), (RULE_ARG_OPT_RULE | RULE_funcdefrettype), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
		(RULE_ARG_RULE | RULE_small_stmt), (RULE_ARG_TOK | MP_TOKEN_DEL_SEMICOLON),
		(RULE_ARG_RULE | RULE_testlist_star_expr), (RULE_ARG_OPT_RULE | RULE_expr_stmt_2),
		(RULE_ARG_RULE | RULE_testlist_star_expr_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_TOK | MP_TOKEN_KW_DEL), (RULE_ARG_RULE | RULE_exprlist),
		(RULE_ARG_TOK | MP_TOKEN_KW_PASS),
		(RULE_ARG_TOK | MP_TOKEN_KW_BREAK),
		(RULE_ARG_TOK | MP_TOKEN_KW_CONTINUE),
		(RULE_ARG_TOK | MP_TOKEN_KW_RETURN), (RULE_ARG_OPT_RULE | RULE_testlist),
		(RULE_ARG_RULE | RULE_yield_expr),
		(RULE_ARG_TOK | MP_TOKEN_KW_RAISE), (RULE_ARG_OPT_RULE | RULE_raise_stmt_arg),
		(RULE_ARG_TOK | MP_TOKEN_KW_IMPORT), (RULE_ARG_RULE | RULE_dotted_as_names),
		(RULE_ARG_TOK | MP_TOKEN_KW_FROM), (RULE_ARG_RULE | RULE_import_from_2), (RULE_ARG_TOK | MP_TOKEN_KW_IMPORT), (RULE_ARG_RULE | RULE_import_from_3),
		(RULE_ARG_TOK | MP_TOKEN_KW_GLOBAL), (RULE_ARG_RULE | RULE_name_list),
		(RULE_ARG_TOK | MP_TOKEN_KW_NONLOCAL), (RULE_ARG_RULE | RULE_name_list),
		(RULE_ARG_TOK | MP_TOKEN_KW_ASSERT), (RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_assert_stmt_extra),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ARG_TOK | MP_TOKEN_KW_ASYNC), (RULE_ARG_RULE | RULE_async_stmt_2),
		#else
		#endif
		(RULE_ARG_TOK | MP_TOKEN_KW_IF), (RULE_ARG_RULE | RULE_namedexpr_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_OPT_RULE | RULE_if_stmt_elif_list), (RULE_ARG_OPT_RULE | RULE_else_stmt),
		(RULE_ARG_TOK | MP_TOKEN_KW_WHILE), (RULE_ARG_RULE | RULE_namedexpr_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_OPT_RULE | RULE_else_stmt),
		(RULE_ARG_TOK | MP_TOKEN_KW_FOR), (RULE_ARG_RULE | RULE_exprlist), (RULE_ARG_TOK | MP_TOKEN_KW_IN), (RULE_ARG_RULE | RULE_testlist), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_OPT_RULE | RULE_else_stmt),
		(RULE_ARG_TOK | MP_TOKEN_KW_TRY), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_RULE | RULE_try_stmt_2),
		(RULE_ARG_TOK | MP_TOKEN_KW_WITH), (RULE_ARG_RULE | RULE_with_stmt_list), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
		(RULE_ARG_RULE | RULE_stmt),
		#if MICROPY_PY_ASSIGN_EXPR
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_namedexpr_test_2),
		#else
		#endif
		(RULE_ARG_RULE | RULE_or_test), (RULE_ARG_OPT_RULE | RULE_test_if_else),
		(RULE_ARG_TOK | MP_TOKEN_KW_LAMBDA), (RULE_ARG_OPT_RULE | RULE_varargslist), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_TOK | MP_TOKEN_KW_LAMBDA), (RULE_ARG_OPT_RULE | RULE_varargslist), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test_nocond),
		(RULE_ARG_RULE | RULE_and_test), (RULE_ARG_TOK | MP_TOKEN_KW_OR),
		(RULE_ARG_RULE | RULE_not_test), (RULE_ARG_TOK | MP_TOKEN_KW_AND),
		(RULE_ARG_TOK | MP_TOKEN_KW_NOT), (RULE_ARG_RULE | RULE_not_test),
		(RULE_ARG_RULE | RULE_expr), (RULE_ARG_RULE | RULE_comp_op),
		(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_RULE | RULE_expr),
		(RULE_ARG_RULE | RULE_xor_expr), (RULE_ARG_TOK | MP_TOKEN_OP_PIPE),
		(RULE_ARG_RULE | RULE_and_expr), (RULE_ARG_TOK | MP_TOKEN_OP_CARET),
		(RULE_ARG_RULE | RULE_shift_expr), (RULE_ARG_TOK | MP_TOKEN_OP_AMPERSAND),
		(RULE_ARG_RULE | RULE_arith_expr), (RULE_ARG_RULE | RULE_shift_op),
		(RULE_ARG_RULE | RULE_term), (RULE_ARG_RULE | RULE_arith_op),
		(RULE_ARG_RULE | RULE_factor), (RULE_ARG_RULE | RULE_term_op),
		(RULE_ARG_RULE | RULE_factor_op), (RULE_ARG_RULE | RULE_factor),
		(RULE_ARG_RULE | RULE_atom_expr), (RULE_ARG_OPT_RULE | RULE_power_dbl_star),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ARG_TOK | MP_TOKEN_KW_AWAIT), (RULE_ARG_RULE | RULE_atom), (RULE_ARG_OPT_RULE | RULE_atom_expr_trailers),
		#else
		#endif
		(RULE_ARG_RULE | RULE_atom), (RULE_ARG_OPT_RULE | RULE_atom_expr_trailers),
		(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_atom_2b), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
		(RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_OPEN), (RULE_ARG_OPT_RULE | RULE_testlist_comp), (RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_CLOSE),
		(RULE_ARG_TOK | MP_TOKEN_DEL_BRACE_OPEN), (RULE_ARG_OPT_RULE | RULE_dictorsetmaker), (RULE_ARG_TOK | MP_TOKEN_DEL_BRACE_CLOSE),
		(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_arglist), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
		(RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_OPEN), (RULE_ARG_RULE | RULE_subscriptlist), (RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_CLOSE),
		(RULE_ARG_TOK | MP_TOKEN_DEL_PERIOD), (RULE_ARG_TOK | MP_TOKEN_NAME),
		#if MICROPY_PY_BUILTINS_SLICE
		(RULE_ARG_RULE | RULE_subscript), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_subscript_3),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_OPT_RULE | RULE_subscript_3b),
		#else
		#(RULE_ARG_RULE | RULE_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		#endif
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		#if MICROPY_PY_BUILTINS_SET
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_generic_colon_test),
		#else
		#(RULE_ARG_RULE | RULE_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test),
		#endif
		(RULE_ARG_TOK | MP_TOKEN_KW_CLASS), (RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_classdef_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
		#if MICROPY_PY_ASSIGN_EXPR
		#else
		#endif
		(RULE_ARG_TOK | MP_TOKEN_KW_YIELD), (RULE_ARG_OPT_RULE | RULE_yield_arg),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_TOK | MP_TOKEN_DEL_EQUAL), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_TOK | MP_TOKEN_NEWLINE), (RULE_ARG_RULE | RULE_simple_stmt), (RULE_ARG_RULE | RULE_compound_stmt),
		(RULE_ARG_TOK | MP_TOKEN_NEWLINE), (RULE_ARG_RULE | RULE_stmt),
		(RULE_ARG_RULE | RULE_testlist), (RULE_ARG_OPT_RULE | RULE_eval_input_2),
		(RULE_ARG_TOK | MP_TOKEN_NEWLINE),
		(RULE_ARG_TOK | MP_TOKEN_OP_AT), (RULE_ARG_RULE | RULE_dotted_name), (RULE_ARG_OPT_RULE | RULE_trailer_paren), (RULE_ARG_TOK | MP_TOKEN_NEWLINE),
		(RULE_ARG_RULE | RULE_decorator),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ARG_RULE | RULE_classdef), (RULE_ARG_RULE | RULE_funcdef), (RULE_ARG_RULE | RULE_async_funcdef),
		(RULE_ARG_TOK | MP_TOKEN_KW_ASYNC), (RULE_ARG_RULE | RULE_funcdef),
		#else
		#(RULE_ARG_RULE | RULE_classdef), (RULE_ARG_RULE | RULE_funcdef),
		#endif
		(RULE_ARG_TOK | MP_TOKEN_DEL_MINUS_MORE), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_RULE | RULE_typedargslist_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_typedargslist_name), (RULE_ARG_RULE | RULE_typedargslist_star), (RULE_ARG_RULE | RULE_typedargslist_dbl_star),
		(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_colon_test), (RULE_ARG_OPT_RULE | RULE_generic_equal_test),
		(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_OPT_RULE | RULE_tfpdef),
		(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_colon_test),
		(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_colon_test),
		(RULE_ARG_RULE | RULE_varargslist_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_varargslist_name), (RULE_ARG_RULE | RULE_varargslist_star), (RULE_ARG_RULE | RULE_varargslist_dbl_star),
		(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_equal_test),
		(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_OPT_RULE | RULE_vfpdef),
		(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_TOK | MP_TOKEN_NAME),
		(RULE_ARG_TOK | MP_TOKEN_NAME),
		(RULE_ARG_RULE | RULE_compound_stmt), (RULE_ARG_RULE | RULE_simple_stmt),
		(RULE_ARG_RULE | RULE_simple_stmt_2), (RULE_ARG_TOK | MP_TOKEN_NEWLINE),
		
		#@FIXME: It said "rule(assert_stmt), rule(expr_stmt)"
		#(RULE_ARG_RULE | RULE_del_stmt), (RULE_ARG_RULE | RULE_pass_stmt), (RULE_ARG_RULE | RULE_flow_stmt), (RULE_ARG_RULE | RULE_import_stmt), (RULE_ARG_RULE | RULE_global_stmt), (RULE_ARG_RULE | RULE_nonlocal_stmt), rule(assert_stmt), rule(expr_stmt),
		(RULE_ARG_RULE | RULE_del_stmt), (RULE_ARG_RULE | RULE_pass_stmt), (RULE_ARG_RULE | RULE_flow_stmt), (RULE_ARG_RULE | RULE_import_stmt), (RULE_ARG_RULE | RULE_global_stmt), (RULE_ARG_RULE | RULE_nonlocal_stmt), (RULE_ARG_RULE | RULE_assert_stmt), (RULE_ARG_RULE | RULE_expr_stmt),
		
		(RULE_ARG_RULE | RULE_annassign), (RULE_ARG_RULE | RULE_expr_stmt_augassign), (RULE_ARG_RULE | RULE_expr_stmt_assign_list),
		(RULE_ARG_RULE | RULE_augassign), (RULE_ARG_RULE | RULE_expr_stmt_6),
		(RULE_ARG_RULE | RULE_expr_stmt_assign),
		(RULE_ARG_TOK | MP_TOKEN_DEL_EQUAL), (RULE_ARG_RULE | RULE_expr_stmt_6),
		(RULE_ARG_RULE | RULE_yield_expr), (RULE_ARG_RULE | RULE_testlist_star_expr),
		(RULE_ARG_RULE | RULE_star_expr), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_expr_stmt_assign),
		
		#@FIXME: It said "tok(DEL_AMPERSAND_EQUAL), tok(DEL_PIPE_EQUAL), tok(DEL_CARET_EQUAL), tok(DEL_DBL_LESS_EQUAL), tok(DEL_DBL_MORE_EQUAL), tok(DEL_DBL_STAR_EQUAL), tok(DEL_DBL_SLASH_EQUAL)"
		#(RULE_ARG_TOK | MP_TOKEN_DEL_PLUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_MINUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_STAR_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_AT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_SLASH_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_PERCENT_EQUAL), tok(DEL_AMPERSAND_EQUAL), tok(DEL_PIPE_EQUAL), tok(DEL_CARET_EQUAL), tok(DEL_DBL_LESS_EQUAL), tok(DEL_DBL_MORE_EQUAL), tok(DEL_DBL_STAR_EQUAL), tok(DEL_DBL_SLASH_EQUAL),
		(RULE_ARG_TOK | MP_TOKEN_DEL_PLUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_MINUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_STAR_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_AT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_SLASH_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_PERCENT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_AMPERSAND_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_PIPE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_CARET_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_LESS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_MORE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_STAR_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_SLASH_EQUAL),
		
		(RULE_ARG_RULE | RULE_break_stmt), (RULE_ARG_RULE | RULE_continue_stmt), (RULE_ARG_RULE | RULE_return_stmt), (RULE_ARG_RULE | RULE_raise_stmt), (RULE_ARG_RULE | RULE_yield_stmt),
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_raise_stmt_from),
		(RULE_ARG_TOK | MP_TOKEN_KW_FROM), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_RULE | RULE_import_name), (RULE_ARG_RULE | RULE_import_from),
		(RULE_ARG_RULE | RULE_dotted_name), (RULE_ARG_RULE | RULE_import_from_2b),
		(RULE_ARG_RULE | RULE_one_or_more_period_or_ellipsis), (RULE_ARG_OPT_RULE | RULE_dotted_name),
		(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_RULE | RULE_import_as_names_paren), (RULE_ARG_RULE | RULE_import_as_names),
		(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_RULE | RULE_import_as_names), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
		(RULE_ARG_RULE | RULE_period_or_ellipsis),
		(RULE_ARG_TOK | MP_TOKEN_DEL_PERIOD), (RULE_ARG_TOK | MP_TOKEN_ELLIPSIS),
		(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_as_name),
		(RULE_ARG_RULE | RULE_dotted_name), (RULE_ARG_OPT_RULE | RULE_as_name),
		(RULE_ARG_TOK | MP_TOKEN_KW_AS), (RULE_ARG_TOK | MP_TOKEN_NAME),
		(RULE_ARG_RULE | RULE_import_as_name), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_dotted_as_name), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_DEL_PERIOD),
		(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COMMA), (RULE_ARG_RULE | RULE_test),
		#if MICROPY_PY_ASYNC_AWAIT
		
		#@FIXME: It said "rule(classdef), rule(decorated), rule(async_stmt)"
		#(RULE_ARG_RULE | RULE_if_stmt), (RULE_ARG_RULE | RULE_while_stmt), (RULE_ARG_RULE | RULE_for_stmt), (RULE_ARG_RULE | RULE_try_stmt), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_funcdef), rule(classdef), rule(decorated), rule(async_stmt),
		(RULE_ARG_RULE | RULE_if_stmt), (RULE_ARG_RULE | RULE_while_stmt), (RULE_ARG_RULE | RULE_for_stmt), (RULE_ARG_RULE | RULE_try_stmt), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_funcdef), (RULE_ARG_RULE | RULE_classdef), (RULE_ARG_RULE | RULE_decorated), (RULE_ARG_RULE | RULE_async_stmt),
		
		(RULE_ARG_RULE | RULE_funcdef), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_for_stmt),
		#else
		#(RULE_ARG_RULE | RULE_if_stmt), (RULE_ARG_RULE | RULE_while_stmt), (RULE_ARG_RULE | RULE_for_stmt), (RULE_ARG_RULE | RULE_try_stmt), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_funcdef), rule(classdef), rule(decorated),
		#endif
		(RULE_ARG_RULE | RULE_if_stmt_elif),
		(RULE_ARG_TOK | MP_TOKEN_KW_ELIF), (RULE_ARG_RULE | RULE_namedexpr_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
		(RULE_ARG_RULE | RULE_try_stmt_except_and_more), (RULE_ARG_RULE | RULE_try_stmt_finally),
		(RULE_ARG_RULE | RULE_try_stmt_except_list), (RULE_ARG_OPT_RULE | RULE_else_stmt), (RULE_ARG_OPT_RULE | RULE_try_stmt_finally),
		(RULE_ARG_TOK | MP_TOKEN_KW_EXCEPT), (RULE_ARG_OPT_RULE | RULE_try_stmt_as_name), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_as_name),
		(RULE_ARG_RULE | RULE_try_stmt_except),
		(RULE_ARG_TOK | MP_TOKEN_KW_FINALLY), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
		(RULE_ARG_TOK | MP_TOKEN_KW_ELSE), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
		(RULE_ARG_RULE | RULE_with_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_with_item_as),
		(RULE_ARG_TOK | MP_TOKEN_KW_AS), (RULE_ARG_RULE | RULE_expr),
		(RULE_ARG_RULE | RULE_suite_block), (RULE_ARG_RULE | RULE_simple_stmt),
		(RULE_ARG_TOK | MP_TOKEN_NEWLINE), (RULE_ARG_TOK | MP_TOKEN_INDENT), (RULE_ARG_RULE | RULE_suite_block_stmts), (RULE_ARG_TOK | MP_TOKEN_DEDENT),
		#if MICROPY_PY_ASSIGN_EXPR
		(RULE_ARG_TOK | MP_TOKEN_OP_ASSIGN), (RULE_ARG_RULE | RULE_test),
		#else
		#(RULE_ARG_RULE | RULE_test),
		#endif
		(RULE_ARG_RULE | RULE_lambdef), (RULE_ARG_RULE | RULE_test_if_expr),
		(RULE_ARG_TOK | MP_TOKEN_KW_IF), (RULE_ARG_RULE | RULE_or_test), (RULE_ARG_TOK | MP_TOKEN_KW_ELSE), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_RULE | RULE_lambdef_nocond), (RULE_ARG_RULE | RULE_or_test),
		(RULE_ARG_RULE | RULE_not_test_2), (RULE_ARG_RULE | RULE_comparison),
		
		#@FIXME: It said "tok(KW_IN)"
		#(RULE_ARG_TOK | MP_TOKEN_OP_LESS), (RULE_ARG_TOK | MP_TOKEN_OP_MORE), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_LESS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_MORE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_NOT_EQUAL), tok(KW_IN), (RULE_ARG_RULE | RULE_comp_op_not_in), (RULE_ARG_RULE | RULE_comp_op_is),
		(RULE_ARG_TOK | MP_TOKEN_OP_LESS), (RULE_ARG_TOK | MP_TOKEN_OP_MORE), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_LESS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_MORE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_NOT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_KW_IN), (RULE_ARG_RULE | RULE_comp_op_not_in), (RULE_ARG_RULE | RULE_comp_op_is),
		
		(RULE_ARG_TOK | MP_TOKEN_KW_NOT), (RULE_ARG_TOK | MP_TOKEN_KW_IN),
		(RULE_ARG_TOK | MP_TOKEN_KW_IS), (RULE_ARG_OPT_RULE | RULE_comp_op_is_not),
		(RULE_ARG_TOK | MP_TOKEN_KW_NOT),
		(RULE_ARG_TOK | MP_TOKEN_OP_DBL_LESS), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_MORE),
		(RULE_ARG_TOK | MP_TOKEN_OP_PLUS), (RULE_ARG_TOK | MP_TOKEN_OP_MINUS),
		(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_TOK | MP_TOKEN_OP_AT), (RULE_ARG_TOK | MP_TOKEN_OP_SLASH), (RULE_ARG_TOK | MP_TOKEN_OP_PERCENT), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_SLASH),
		(RULE_ARG_RULE | RULE_factor_2), (RULE_ARG_RULE | RULE_power),
		(RULE_ARG_TOK | MP_TOKEN_OP_PLUS), (RULE_ARG_TOK | MP_TOKEN_OP_MINUS), (RULE_ARG_TOK | MP_TOKEN_OP_TILDE),
		#if MICROPY_PY_ASYNC_AWAIT
		(RULE_ARG_RULE | RULE_atom_expr_await), (RULE_ARG_RULE | RULE_atom_expr_normal),
		#else
		#(RULE_ARG_RULE | RULE_atom_expr_normal),
		#endif
		(RULE_ARG_RULE | RULE_trailer),
		(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_RULE | RULE_factor),
		
		#@FIXME: It said "tok(KW_TRUE), tok(KW_FALSE)"
		#(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_INTEGER), (RULE_ARG_TOK | MP_TOKEN_FLOAT_OR_IMAG), (RULE_ARG_TOK | MP_TOKEN_STRING), (RULE_ARG_TOK | MP_TOKEN_BYTES), (RULE_ARG_TOK | MP_TOKEN_ELLIPSIS), tok(KW_NONE), tok(KW_TRUE), tok(KW_FALSE), (RULE_ARG_RULE | RULE_atom_paren), (RULE_ARG_RULE | RULE_atom_bracket), (RULE_ARG_RULE | RULE_atom_brace),
		(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_INTEGER), (RULE_ARG_TOK | MP_TOKEN_FLOAT_OR_IMAG), (RULE_ARG_TOK | MP_TOKEN_STRING), (RULE_ARG_TOK | MP_TOKEN_BYTES), (RULE_ARG_TOK | MP_TOKEN_ELLIPSIS), (RULE_ARG_TOK | MP_TOKEN_KW_NONE), (RULE_ARG_TOK | MP_TOKEN_KW_TRUE), (RULE_ARG_TOK | MP_TOKEN_KW_FALSE), (RULE_ARG_RULE | RULE_atom_paren), (RULE_ARG_RULE | RULE_atom_bracket), (RULE_ARG_RULE | RULE_atom_brace),
		
		(RULE_ARG_RULE | RULE_yield_expr), (RULE_ARG_RULE | RULE_testlist_comp),
		(RULE_ARG_RULE | RULE_testlist_comp_2), (RULE_ARG_OPT_RULE | RULE_testlist_comp_3),
		(RULE_ARG_RULE | RULE_star_expr), (RULE_ARG_RULE | RULE_namedexpr_test),
		(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_testlist_comp_3b),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COMMA), (RULE_ARG_OPT_RULE | RULE_testlist_comp_3c),
		(RULE_ARG_RULE | RULE_testlist_comp_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_trailer_paren), (RULE_ARG_RULE | RULE_trailer_bracket), (RULE_ARG_RULE | RULE_trailer_period),
		#if MICROPY_PY_BUILTINS_SLICE
		(RULE_ARG_RULE | RULE_subscript_3), (RULE_ARG_RULE | RULE_subscript_2),
		(RULE_ARG_RULE | RULE_subscript_3c), (RULE_ARG_RULE | RULE_subscript_3d),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_OPT_RULE | RULE_test),
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_sliceop),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_OPT_RULE | RULE_test),
		#else
		#endif
		(RULE_ARG_RULE | RULE_exprlist_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_star_expr), (RULE_ARG_RULE | RULE_expr),
		(RULE_ARG_RULE | RULE_dictorsetmaker_item), (RULE_ARG_OPT_RULE | RULE_dictorsetmaker_tail),
		#if MICROPY_PY_BUILTINS_SET
		#else
		#endif
		(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_dictorsetmaker_list),
		(RULE_ARG_TOK | MP_TOKEN_DEL_COMMA), (RULE_ARG_OPT_RULE | RULE_dictorsetmaker_list2),
		(RULE_ARG_RULE | RULE_dictorsetmaker_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_arglist), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
		(RULE_ARG_RULE | RULE_arglist_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
		(RULE_ARG_RULE | RULE_arglist_star), (RULE_ARG_RULE | RULE_arglist_dbl_star), (RULE_ARG_RULE | RULE_argument),
		(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_RULE | RULE_test),
		(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_argument_2),
		#if MICROPY_PY_ASSIGN_EXPR
		(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_generic_equal_test), (RULE_ARG_RULE | RULE_argument_3),
		(RULE_ARG_TOK | MP_TOKEN_OP_ASSIGN), (RULE_ARG_RULE | RULE_test),
		#else
		#(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_generic_equal_test),
		#endif
		(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_comp_if),
		(RULE_ARG_TOK | MP_TOKEN_KW_FOR), (RULE_ARG_RULE | RULE_exprlist), (RULE_ARG_TOK | MP_TOKEN_KW_IN), (RULE_ARG_RULE | RULE_or_test), (RULE_ARG_OPT_RULE | RULE_comp_iter),
		(RULE_ARG_TOK | MP_TOKEN_KW_IF), (RULE_ARG_RULE | RULE_test_nocond), (RULE_ARG_OPT_RULE | RULE_comp_iter),
		(RULE_ARG_RULE | RULE_yield_arg_from), (RULE_ARG_RULE | RULE_testlist),
		(RULE_ARG_TOK | MP_TOKEN_KW_FROM), (RULE_ARG_RULE | RULE_test),
	]
	
	#enum
	# Fixed offsets with this script:
	#	s = ...
	#	o = 0
	#	for l in s.split('\n'):
	#		if l.strip() == '': continue
	#		if l.startswith('#'):
	#			print(l)
	#			continue
	#		#print(l)
	#		name = l.split('=')[0].strip()
	#		pad = int(name.split('_')[0][3:])
	#		l2 = '%s = %d' % (name, o)
	#		o += pad
	#		print(l2)
	PAD1_file_input = 0
	PAD1_file_input_2 = 1
	PAD2_decorated = 2
	#if MICROPY_PY_ASYNC_AWAIT
	#else
	#endif
	PAD8_funcdef = 4
	PAD2_simple_stmt_2 = 12
	PAD2_expr_stmt = 14
	PAD2_testlist_star_expr = 16
	PAD2_del_stmt = 18
	PAD1_pass_stmt = 20
	PAD1_break_stmt = 21
	PAD1_continue_stmt = 22
	PAD2_return_stmt = 23
	PAD1_yield_stmt = 25
	PAD2_raise_stmt = 26
	PAD2_import_name = 28
	PAD4_import_from = 30
	PAD2_global_stmt = 34
	PAD2_nonlocal_stmt = 36
	PAD3_assert_stmt = 38
	#if MICROPY_PY_ASYNC_AWAIT
	PAD2_async_stmt = 41
	#else
	#endif
	PAD6_if_stmt = 43
	PAD5_while_stmt = 49
	PAD7_for_stmt = 54
	PAD4_try_stmt = 61
	PAD4_with_stmt = 65
	PAD1_suite_block_stmts = 69
	#if MICROPY_PY_ASSIGN_EXPR
	PAD2_namedexpr_test = 70
	#else
	#endif
	PAD2_test_if_expr = 72
	PAD4_lambdef = 74
	PAD4_lambdef_nocond = 78
	PAD2_or_test = 82
	PAD2_and_test = 84
	PAD2_not_test_2 = 86
	PAD2_comparison = 88
	PAD2_star_expr = 90
	PAD2_expr = 92
	PAD2_xor_expr = 94
	PAD2_and_expr = 96
	PAD2_shift_expr = 98
	PAD2_arith_expr = 100
	PAD2_term = 102
	PAD2_factor_2 = 104
	PAD2_power = 106
	#if MICROPY_PY_ASYNC_AWAIT
	PAD3_atom_expr_await = 108
	#else
	#endif
	PAD2_atom_expr_normal = 111
	PAD3_atom_paren = 113
	PAD3_atom_bracket = 116
	PAD3_atom_brace = 119
	PAD3_trailer_paren = 122
	PAD3_trailer_bracket = 125
	PAD2_trailer_period = 128
	#if MICROPY_PY_BUILTINS_SLICE
	PAD2_subscriptlist = 130
	PAD2_subscript_2 = 132
	PAD2_subscript_3 = 134
	#else
	#PAD2_subscriptlist	= 54
	#endif
	PAD2_testlist = 136
	#if MICROPY_PY_BUILTINS_SET
	PAD2_dictorsetmaker_item = 138
	#else
	#PAD3_dictorsetmaker_item	= 57
	#endif
	PAD5_classdef = 140
	#if MICROPY_PY_ASSIGN_EXPR
	#else
	#endif
	PAD2_yield_expr = 145
	# RULES have "const_object" here: special node for a constant, generic Python object
	PAD2_generic_colon_test = 147
	PAD2_generic_equal_test = 149
	PAD3_single_input = 151
	PAD2_file_input_3 = 154
	PAD2_eval_input = 156
	PAD1_eval_input_2 = 158
	PAD4_decorator = 159
	PAD1_decorators = 163
	#if MICROPY_PY_ASYNC_AWAIT
	PAD3_decorated_body = 164
	PAD2_async_funcdef = 167
	#else
	#PAD2_decorated_body	= 70
	#endif
	PAD2_funcdefrettype = 169
	PAD2_typedargslist = 171
	PAD3_typedargslist_item = 173
	PAD3_typedargslist_name = 176
	PAD2_typedargslist_star = 179
	PAD3_typedargslist_dbl_star = 181
	PAD2_tfpdef = 184
	PAD2_varargslist = 186
	PAD3_varargslist_item = 188
	PAD2_varargslist_name = 191
	PAD2_varargslist_star = 193
	PAD2_varargslist_dbl_star = 195
	PAD1_vfpdef = 197
	PAD2_stmt = 198
	PAD2_simple_stmt = 200
	PAD8_small_stmt = 202
	PAD3_expr_stmt_2 = 210
	PAD2_expr_stmt_augassign = 213
	PAD1_expr_stmt_assign_list = 215
	PAD2_expr_stmt_assign = 216
	PAD2_expr_stmt_6 = 218
	PAD2_testlist_star_expr_2 = 220
	PAD3_annassign = 222
	PAD13_augassign = 225
	PAD5_flow_stmt = 238
	PAD2_raise_stmt_arg = 243
	PAD2_raise_stmt_from = 245
	PAD2_import_stmt = 247
	PAD2_import_from_2 = 249
	PAD2_import_from_2b = 251
	PAD3_import_from_3 = 253
	PAD3_import_as_names_paren = 256
	PAD1_one_or_more_period_or_ellipsis = 259
	PAD2_period_or_ellipsis = 260
	PAD2_import_as_name = 262
	PAD2_dotted_as_name = 264
	PAD2_as_name = 266
	PAD2_import_as_names = 268
	PAD2_dotted_as_names = 270
	PAD2_dotted_name = 272
	PAD2_name_list = 274
	PAD2_assert_stmt_extra = 276
	#if MICROPY_PY_ASYNC_AWAIT
	PAD9_compound_stmt = 278
	PAD3_async_stmt_2 = 287
	#else
	#PAD8_compound_stmt	= 115
	#endif
	PAD1_if_stmt_elif_list = 290
	PAD4_if_stmt_elif = 291
	PAD2_try_stmt_2 = 295
	PAD3_try_stmt_except_and_more = 297
	PAD4_try_stmt_except = 300
	PAD2_try_stmt_as_name = 304
	PAD1_try_stmt_except_list = 306
	PAD3_try_stmt_finally = 307
	PAD3_else_stmt = 310
	PAD2_with_stmt_list = 313
	PAD2_with_item = 315
	PAD2_with_item_as = 317
	PAD2_suite = 319
	PAD4_suite_block = 321
	#if MICROPY_PY_ASSIGN_EXPR
	PAD2_namedexpr_test_2 = 325
	#else
	#PAD1_namedexpr_test	= 131
	#endif
	PAD2_test = 327
	PAD4_test_if_else = 329
	PAD2_test_nocond = 333
	PAD2_not_test = 335
	PAD9_comp_op = 337
	PAD2_comp_op_not_in = 346
	PAD2_comp_op_is = 348
	PAD1_comp_op_is_not = 350
	PAD2_shift_op = 351
	PAD2_arith_op = 353
	PAD5_term_op = 355
	PAD2_factor = 360
	PAD3_factor_op = 362
	#if MICROPY_PY_ASYNC_AWAIT
	PAD2_atom_expr = 365
	#else
	#PAD1_atom_expr	= 146
	#endif
	PAD1_atom_expr_trailers = 367
	PAD2_power_dbl_star = 368
	PAD12_atom = 370
	PAD2_atom_2b = 382
	PAD2_testlist_comp = 384
	PAD2_testlist_comp_2 = 386
	PAD2_testlist_comp_3 = 388
	PAD2_testlist_comp_3b = 390
	PAD2_testlist_comp_3c = 392
	PAD3_trailer = 394
	#if MICROPY_PY_BUILTINS_SLICE
	PAD2_subscript = 397
	PAD2_subscript_3b = 399
	PAD2_subscript_3c = 401
	PAD2_subscript_3d = 403
	PAD2_sliceop = 405
	#else
	#endif
	PAD2_exprlist = 407
	PAD2_exprlist_2 = 409
	PAD2_dictorsetmaker = 411
	#if MICROPY_PY_BUILTINS_SET
	#else
	#endif
	PAD2_dictorsetmaker_tail = 413
	PAD2_dictorsetmaker_list = 415
	PAD2_dictorsetmaker_list2 = 417
	PAD3_classdef_2 = 419
	PAD2_arglist = 422
	PAD3_arglist_2 = 424
	PAD2_arglist_star = 427
	PAD2_arglist_dbl_star = 429
	PAD2_argument = 431
	#if MICROPY_PY_ASSIGN_EXPR
	PAD3_argument_2 = 433
	PAD2_argument_3 = 436
	#else
	#PAD2_argument_2	= 176
	#endif
	PAD2_comp_iter = 438
	PAD5_comp_for = 440
	PAD3_comp_if = 445
	PAD2_yield_arg = 448
	PAD2_yield_arg_from = 450
	
	
	#static const uint8_t rule_arg_offset_table[]
	rule_arg_offset_table:[uint8_t] = [
		PAD1_file_input & 0xff,
		PAD1_file_input_2 & 0xff,
		PAD2_decorated & 0xff,
		#if MICROPY_PY_ASYNC_AWAIT
		#else
		#endif
		PAD8_funcdef & 0xff,
		PAD2_simple_stmt_2 & 0xff,
		PAD2_expr_stmt & 0xff,
		PAD2_testlist_star_expr & 0xff,
		PAD2_del_stmt & 0xff,
		PAD1_pass_stmt & 0xff,
		PAD1_break_stmt & 0xff,
		PAD1_continue_stmt & 0xff,
		PAD2_return_stmt & 0xff,
		PAD1_yield_stmt & 0xff,
		PAD2_raise_stmt & 0xff,
		PAD2_import_name & 0xff,
		PAD4_import_from & 0xff,
		PAD2_global_stmt & 0xff,
		PAD2_nonlocal_stmt & 0xff,
		PAD3_assert_stmt & 0xff,
		#if MICROPY_PY_ASYNC_AWAIT
		PAD2_async_stmt & 0xff,
		#else
		#endif
		PAD6_if_stmt & 0xff,
		PAD5_while_stmt & 0xff,
		PAD7_for_stmt & 0xff,
		PAD4_try_stmt & 0xff,
		PAD4_with_stmt & 0xff,
		PAD1_suite_block_stmts & 0xff,
		#if MICROPY_PY_ASSIGN_EXPR
		PAD2_namedexpr_test & 0xff,
		#else
		#endif
		PAD2_test_if_expr & 0xff,
		PAD4_lambdef & 0xff,
		PAD4_lambdef_nocond & 0xff,
		PAD2_or_test & 0xff,
		PAD2_and_test & 0xff,
		PAD2_not_test_2 & 0xff,
		PAD2_comparison & 0xff,
		PAD2_star_expr & 0xff,
		PAD2_expr & 0xff,
		PAD2_xor_expr & 0xff,
		PAD2_and_expr & 0xff,
		PAD2_shift_expr & 0xff,
		PAD2_arith_expr & 0xff,
		PAD2_term & 0xff,
		PAD2_factor_2 & 0xff,
		PAD2_power & 0xff,
		#if MICROPY_PY_ASYNC_AWAIT
		PAD3_atom_expr_await & 0xff,
		#else
		#endif
		PAD2_atom_expr_normal & 0xff,
		PAD3_atom_paren & 0xff,
		PAD3_atom_bracket & 0xff,
		PAD3_atom_brace & 0xff,
		PAD3_trailer_paren & 0xff,
		PAD3_trailer_bracket & 0xff,
		PAD2_trailer_period & 0xff,
		#if MICROPY_PY_BUILTINS_SLICE
		PAD2_subscriptlist & 0xff,
		PAD2_subscript_2 & 0xff,
		PAD2_subscript_3 & 0xff,
		#else
		#PAD2_subscriptlist & 0xff,
		#endif
		PAD2_testlist & 0xff,
		#if MICROPY_PY_BUILTINS_SET
		PAD2_dictorsetmaker_item & 0xff,
		#else
		#PAD3_dictorsetmaker_item & 0xff,
		#endif
		PAD5_classdef & 0xff,
		#if MICROPY_PY_ASSIGN_EXPR
		#else
		#endif
		PAD2_yield_expr & 0xff,
		0,
		PAD2_generic_colon_test & 0xff,
		PAD2_generic_equal_test & 0xff,
		PAD3_single_input & 0xff,
		PAD2_file_input_3 & 0xff,
		PAD2_eval_input & 0xff,
		PAD1_eval_input_2 & 0xff,
		PAD4_decorator & 0xff,
		PAD1_decorators & 0xff,
		#if MICROPY_PY_ASYNC_AWAIT
		PAD3_decorated_body & 0xff,
		PAD2_async_funcdef & 0xff,
		#else
		#PAD2_decorated_body & 0xff,
		#endif
		PAD2_funcdefrettype & 0xff,
		PAD2_typedargslist & 0xff,
		PAD3_typedargslist_item & 0xff,
		PAD3_typedargslist_name & 0xff,
		PAD2_typedargslist_star & 0xff,
		PAD3_typedargslist_dbl_star & 0xff,
		PAD2_tfpdef & 0xff,
		PAD2_varargslist & 0xff,
		PAD3_varargslist_item & 0xff,
		PAD2_varargslist_name & 0xff,
		PAD2_varargslist_star & 0xff,
		PAD2_varargslist_dbl_star & 0xff,
		PAD1_vfpdef & 0xff,
		PAD2_stmt & 0xff,
		PAD2_simple_stmt & 0xff,
		PAD8_small_stmt & 0xff,
		PAD3_expr_stmt_2 & 0xff,
		PAD2_expr_stmt_augassign & 0xff,
		PAD1_expr_stmt_assign_list & 0xff,
		PAD2_expr_stmt_assign & 0xff,
		PAD2_expr_stmt_6 & 0xff,
		PAD2_testlist_star_expr_2 & 0xff,
		PAD3_annassign & 0xff,
		PAD13_augassign & 0xff,
		PAD5_flow_stmt & 0xff,
		PAD2_raise_stmt_arg & 0xff,
		PAD2_raise_stmt_from & 0xff,
		PAD2_import_stmt & 0xff,
		PAD2_import_from_2 & 0xff,
		PAD2_import_from_2b & 0xff,
		PAD3_import_from_3 & 0xff,
		PAD3_import_as_names_paren & 0xff,
		PAD1_one_or_more_period_or_ellipsis & 0xff,
		PAD2_period_or_ellipsis & 0xff,
		PAD2_import_as_name & 0xff,
		PAD2_dotted_as_name & 0xff,
		PAD2_as_name & 0xff,
		PAD2_import_as_names & 0xff,
		PAD2_dotted_as_names & 0xff,
		PAD2_dotted_name & 0xff,
		PAD2_name_list & 0xff,
		PAD2_assert_stmt_extra & 0xff,
		#if MICROPY_PY_ASYNC_AWAIT
		PAD9_compound_stmt & 0xff,
		PAD3_async_stmt_2 & 0xff,
		#else
		#PAD8_compound_stmt & 0xff,
		#endif
		PAD1_if_stmt_elif_list & 0xff,
		PAD4_if_stmt_elif & 0xff,
		PAD2_try_stmt_2 & 0xff,
		PAD3_try_stmt_except_and_more & 0xff,
		PAD4_try_stmt_except & 0xff,
		PAD2_try_stmt_as_name & 0xff,
		PAD1_try_stmt_except_list & 0xff,
		PAD3_try_stmt_finally & 0xff,
		PAD3_else_stmt & 0xff,
		PAD2_with_stmt_list & 0xff,
		PAD2_with_item & 0xff,
		PAD2_with_item_as & 0xff,
		PAD2_suite & 0xff,
		PAD4_suite_block & 0xff,
		#if MICROPY_PY_ASSIGN_EXPR
		PAD2_namedexpr_test_2 & 0xff,
		#else
		#PAD1_namedexpr_test & 0xff,
		#endif
		PAD2_test & 0xff,
		PAD4_test_if_else & 0xff,
		PAD2_test_nocond & 0xff,
		PAD2_not_test & 0xff,
		PAD9_comp_op & 0xff,
		PAD2_comp_op_not_in & 0xff,
		PAD2_comp_op_is & 0xff,
		PAD1_comp_op_is_not & 0xff,
		PAD2_shift_op & 0xff,
		PAD2_arith_op & 0xff,
		PAD5_term_op & 0xff,
		PAD2_factor & 0xff,
		PAD3_factor_op & 0xff,
		#if MICROPY_PY_ASYNC_AWAIT
		PAD2_atom_expr & 0xff,
		#else
		#PAD1_atom_expr & 0xff,
		#endif
		PAD1_atom_expr_trailers & 0xff,
		PAD2_power_dbl_star & 0xff,
		PAD12_atom & 0xff,
		PAD2_atom_2b & 0xff,
		PAD2_testlist_comp & 0xff,
		PAD2_testlist_comp_2 & 0xff,
		PAD2_testlist_comp_3 & 0xff,
		PAD2_testlist_comp_3b & 0xff,
		PAD2_testlist_comp_3c & 0xff,
		PAD3_trailer & 0xff,
		#if MICROPY_PY_BUILTINS_SLICE
		PAD2_subscript & 0xff,
		PAD2_subscript_3b & 0xff,
		PAD2_subscript_3c & 0xff,
		PAD2_subscript_3d & 0xff,
		PAD2_sliceop & 0xff,
		#else
		#endif
		PAD2_exprlist & 0xff,
		PAD2_exprlist_2 & 0xff,
		PAD2_dictorsetmaker & 0xff,
		#if MICROPY_PY_BUILTINS_SET
		#else
		#endif
		PAD2_dictorsetmaker_tail & 0xff,
		PAD2_dictorsetmaker_list & 0xff,
		PAD2_dictorsetmaker_list2 & 0xff,
		PAD3_classdef_2 & 0xff,
		PAD2_arglist & 0xff,
		PAD3_arglist_2 & 0xff,
		PAD2_arglist_star & 0xff,
		PAD2_arglist_dbl_star & 0xff,
		PAD2_argument & 0xff,
		#if MICROPY_PY_ASSIGN_EXPR
		PAD3_argument_2 & 0xff,
		PAD2_argument_3 & 0xff,
		#else
		#PAD2_argument_2 & 0xff,
		#endif
		PAD2_comp_iter & 0xff,
		PAD5_comp_for & 0xff,
		PAD3_comp_if & 0xff,
		PAD2_yield_arg & 0xff,
		PAD2_yield_arg_from & 0xff,
	]
	
	#@FIXME: This checks all "PADx_xxx" if it is >= 0x100. If it is, it is set to the first "RULE_xxx"
	# e.g. = (PAD2_yield_arg >= 0x100 ? RULE_yield_arg : 0)
	FIRST_RULE_WITH_OFFSET_ABOVE_255 = RULE_import_as_names_paren
	
	#if MICROPY_DEBUG_PARSE_RULE_NAME
	#static const char *const rule_name_table[]
	rule_name_table:[str] = [
		"file_input",
		"file_input_2",
		"decorated",
		#if MICROPY_PY_ASYNC_AWAIT
		#else
		#endif
		"funcdef",
		"simple_stmt_2",
		"expr_stmt",
		"testlist_star_expr",
		"del_stmt",
		"pass_stmt",
		"break_stmt",
		"continue_stmt",
		"return_stmt",
		"yield_stmt",
		"raise_stmt",
		"import_name",
		"import_from",
		"global_stmt",
		"nonlocal_stmt",
		"assert_stmt",
		#if MICROPY_PY_ASYNC_AWAIT
		"async_stmt",
		#else
		#endif
		"if_stmt",
		"while_stmt",
		"for_stmt",
		"try_stmt",
		"with_stmt",
		"suite_block_stmts",
		#if MICROPY_PY_ASSIGN_EXPR
		"namedexpr_test",
		#else
		#endif
		"test_if_expr",
		"lambdef",
		"lambdef_nocond",
		"or_test",
		"and_test",
		"not_test_2",
		"comparison",
		"star_expr",
		"expr",
		"xor_expr",
		"and_expr",
		"shift_expr",
		"arith_expr",
		"term",
		"factor_2",
		"power",
		#if MICROPY_PY_ASYNC_AWAIT
		"atom_expr_await",
		#else
		#endif
		"atom_expr_normal",
		"atom_paren",
		"atom_bracket",
		"atom_brace",
		"trailer_paren",
		"trailer_bracket",
		"trailer_period",
		#if MICROPY_PY_BUILTINS_SLICE
		"subscriptlist",
		"subscript_2",
		"subscript_3",
		#else
		#"subscriptlist",
		#endif
		"testlist",
		#if MICROPY_PY_BUILTINS_SET
		"dictorsetmaker_item",
		#else
		#"dictorsetmaker_item",
		#endif
		"classdef",
		#if MICROPY_PY_ASSIGN_EXPR
		#else
		#endif
		"yield_expr",
		"",
		"generic_colon_test",
		"generic_equal_test",
		"single_input",
		"file_input_3",
		"eval_input",
		"eval_input_2",
		"decorator",
		"decorators",
		#if MICROPY_PY_ASYNC_AWAIT
		"decorated_body",
		"async_funcdef",
		#else
		#"decorated_body",
		#endif
		"funcdefrettype",
		"typedargslist",
		"typedargslist_item",
		"typedargslist_name",
		"typedargslist_star",
		"typedargslist_dbl_star",
		"tfpdef",
		"varargslist",
		"varargslist_item",
		"varargslist_name",
		"varargslist_star",
		"varargslist_dbl_star",
		"vfpdef",
		"stmt",
		"simple_stmt",
		"small_stmt",
		"expr_stmt_2",
		"expr_stmt_augassign",
		"expr_stmt_assign_list",
		"expr_stmt_assign",
		"expr_stmt_6",
		"testlist_star_expr_2",
		"annassign",
		"augassign",
		"flow_stmt",
		"raise_stmt_arg",
		"raise_stmt_from",
		"import_stmt",
		"import_from_2",
		"import_from_2b",
		"import_from_3",
		"import_as_names_paren",
		"one_or_more_period_or_ellipsis",
		"period_or_ellipsis",
		"import_as_name",
		"dotted_as_name",
		"as_name",
		"import_as_names",
		"dotted_as_names",
		"dotted_name",
		"name_list",
		"assert_stmt_extra",
		#if MICROPY_PY_ASYNC_AWAIT
		"compound_stmt",
		"async_stmt_2",
		#else
		#"compound_stmt",
		#endif
		"if_stmt_elif_list",
		"if_stmt_elif",
		"try_stmt_2",
		"try_stmt_except_and_more",
		"try_stmt_except",
		"try_stmt_as_name",
		"try_stmt_except_list",
		"try_stmt_finally",
		"else_stmt",
		"with_stmt_list",
		"with_item",
		"with_item_as",
		"suite",
		"suite_block",
		#if MICROPY_PY_ASSIGN_EXPR
		"namedexpr_test_2",
		#else
		#"namedexpr_test",
		#endif
		"test",
		"test_if_else",
		"test_nocond",
		"not_test",
		"comp_op",
		"comp_op_not_in",
		"comp_op_is",
		"comp_op_is_not",
		"shift_op",
		"arith_op",
		"term_op",
		"factor",
		"factor_op",
		#if MICROPY_PY_ASYNC_AWAIT
		"atom_expr",
		#else
		#"atom_expr",
		#endif
		"atom_expr_trailers",
		"power_dbl_star",
		"atom",
		"atom_2b",
		"testlist_comp",
		"testlist_comp_2",
		"testlist_comp_3",
		"testlist_comp_3b",
		"testlist_comp_3c",
		"trailer",
		#if MICROPY_PY_BUILTINS_SLICE
		"subscript",
		"subscript_3b",
		"subscript_3c",
		"subscript_3d",
		"sliceop",
		#else
		#endif
		"exprlist",
		"exprlist_2",
		"dictorsetmaker",
		#if MICROPY_PY_BUILTINS_SET
		#else
		#endif
		"dictorsetmaker_tail",
		"dictorsetmaker_list",
		"dictorsetmaker_list2",
		"classdef_2",
		"arglist",
		"arglist_2",
		"arglist_star",
		"arglist_dbl_star",
		"argument",
		#if MICROPY_PY_ASSIGN_EXPR
		"argument_2",
		"argument_3",
		#else
		#"argument_2",
		#endif
		"comp_iter",
		"comp_for",
		"comp_if",
		"yield_arg",
		"yield_arg_from",
	]

### Code
#rule_id = RULE_yield_arg_from
#print('rule_id=%d' % rule_id)
#print('rule_name="%s"' % rule_name_table[rule_id])
#o = rule_arg_offset_table[rule_id] + 0x100 if rule_id >= FIRST_RULE_WITH_OFFSET_ABOVE_255 else 0
#print('rule_act=%d' % rule_act_table[rule_id])
#print('rule_arg=%s...' % ', '.join([ '0x%04X'%a for a in rule_arg_combined_table[o:o+6] ]))
#print('rule_arg_offset=%d' % o)
#print('PAD=%d' % PAD2_yield_arg_from)


#typedef struct _rule_stack_t
class rule_stack_t:
	src_line:size_t = (8 * 4 - 8)	#(8 * sizeof(size_t) - 8)
	rule_id:size_t = 8
	arg_i:size_t = 0

#typedef struct _mp_parse_chunk_t {
class mp_parse_chunk_t:
	alloc:size_t = 0
	#union {
	used:size_t = 0
	next:None	#struct _mp_parse_chunk_t *next;
	#} union_;
	data:[byte] = []	#byte data[];
	def __repr__(self):
		#return 'mp_parse_chunk_t: data=%s, next=%s' % (str(self.data))
		return self.dump()
	def dump(self, indent=0):
		return '%schunk: data=%s, next=%s' % (str(self.data), '--' if self.next is None else '\n'+self.next.dump(indent+1))


#typedef struct _mp_parse_t {
class mp_parse_tree_t:
	root:mp_parse_node_t = None
	#struct _mp_parse_chunk_t *chunk;
	chunk:mp_parse_chunk_t = None
	def __repr__(self):
		#return 'mp_parse_tree_t: root=%s%s' % ('--' if self.root is None else str(self.root), '' if self.chunk is None else '\n'+self.chunk.dump(indent=1))
		r = 'mp_parse_tree_t: root=%s%s' % ('--' if self.root is None else str(self.root), '' if self.chunk is None else '\n'+self.chunk.dump(indent=1))
		if self.root is None:
			r += 'root=None'
		elif MP_PARSE_NODE_IS_STRUCT(self.root):
			r += 'root=%s' % self.root.dump()
		else:
			r += 'root=%s' % str(self.root)
		return r

#typedef struct _parser_t {
class parser_t:
	rule_stack_alloc:size_t = 0
	rule_stack_top:size_t = 0
	rule_stack:rule_stack_t = None
	
	result_stack_alloc:size_t = 0
	result_stack_top:size_t = 0
	result_stack:mp_parse_node_t = None
	lexer:mp_lexer_t = None
	tree:mp_parse_tree_t = mp_parse_tree_t()
	cur_chunk:mp_parse_chunk_t = None
	#if MICROPY_COMP_CONST
	consts:mp_map_t = dict()	#{}
	#endif

#static void push_result_rule(parser_t *parser, size_t src_line, uint8_t rule_id, size_t num_args);

#static const uint16_t *get_rule_arg(uint8_t r_id) {
def get_rule_arg_offset(r_id:uint8_t) -> uint16_t:
	off:size_t = rule_arg_offset_table[r_id]
	if (r_id >= FIRST_RULE_WITH_OFFSET_ABOVE_255):
		off |= 0x100
	#return rule_arg_combined_table[off]	#&rule_arg_combined_table[off];
	return off	#&rule_arg_combined_table[off];

#static void *parser_alloc(parser_t *parser, size_t num_bytes) {
#@FIXME: Change calling convention on caller to TWO return values
def parser_alloc(parser:parser_t, num_bytes:size_t) -> (mp_parse_chunk_t, size_t):
	chunk:mp_parse_chunk_t = parser.cur_chunk
	if ((chunk is not None) and (chunk.union_.used + num_bytes > chunk.alloc)):
		new_data:mp_parse_chunk_t = m_renew_maybe(
			byte,
			chunk,
			sizeof(mp_parse_chunk_t) + chunk.alloc,
			sizeof(mp_parse_chunk_t) + chunk.alloc + num_bytes, False
		)
		if (new_data is None):
			m_renew_maybe(
				byte,
				chunk,
				sizeof(mp_parse_chunk_t) + chunk.alloc,
				sizeof(mp_parse_chunk_t) + chunk.union_.used, False
			)
			chunk.alloc = chunk.union_.used
			chunk.union_.next = parser.tree.chunk
			parser.tree.chunk = chunk
			chunk = None
		else:
			chunk.alloc += num_bytes
		#
	#
	if (chunk is None):
		alloc:size_t = MICROPY_ALLOC_PARSE_CHUNK_INIT
		if (alloc < num_bytes):
			alloc = num_bytes
		chunk:mp_parse_chunk_t = m_new(byte, sizeof(mp_parse_chunk_t) + alloc)
		chunk.alloc = alloc
		chunk.union_.used = 0
		parser.cur_chunk = chunk
	
	#byte *ret = chunk->data + chunk->union_.used;
	ret = chunk.data, chunk.union_.used
	chunk.union_.used += num_bytes
	return ret
#

#if MICROPY_COMP_CONST_TUPLE
#static void parser_free_parse_node_struct(parser_t *parser, mp_parse_node_struct_t *pns) {
def parser_free_parse_node_struct(parser:parser_t, pns:mp_parse_node_struct_t):
	chunk:mp_parse_chunk_t = parser.cur_chunk
	
	#@FIXME: if ((chunk.data <= (byte *)pns) and ((byte *)pns < chunk.data + chunk.union_.used)):
	if ((chunk.data <= pns) and (pns < chunk.data + chunk.union_.used)):
		num_bytes:size_t = sizeof(mp_parse_node_struct_t) + sizeof(mp_parse_node_t) * MP_PARSE_NODE_STRUCT_NUM_NODES(pns)
		chunk.union_.used -= num_bytes
#
#endif

#static void push_rule(parser_t *parser, size_t src_line, uint8_t rule_id, size_t arg_i) {
def push_rule(parser:parser_t, src_line:size_t, rule_id:uint8_t, arg_i:size_t):
	"""
	if (parser.rule_stack_top >= parser.rule_stack_alloc):
		rs:rule_stack_t = m_renew(rule_stack_t, parser.rule_stack, parser.rule_stack_alloc, parser.rule_stack_alloc + MICROPY_ALLOC_PARSE_RULE_INC)
		parser.rule_stack = rs
		parser.rule_stack_alloc += MICROPY_ALLOC_PARSE_RULE_INC
	"""
	while (parser.rule_stack_top >= parser.rule_stack_alloc):
		parser.rule_stack.append(rule_stack_t())
		parser.rule_stack_alloc += 1
	
	rs:rule_stack_t = parser.rule_stack[parser.rule_stack_top]
	parser.rule_stack_top += 1
	rs.src_line = src_line
	rs.rule_id = rule_id
	rs.arg_i = arg_i
#
def push_rule_from_arg(parser:parser_t, arg:size_t):
	assert(((arg & RULE_ARG_KIND_MASK) == RULE_ARG_RULE) or ((arg & RULE_ARG_KIND_MASK) == RULE_ARG_OPT_RULE))
	rule_id:size_t = arg & RULE_ARG_ARG_MASK
	push_rule(parser, parser.lexer.tok_line, rule_id, 0)

#def pop_rule(parser:parser_t, size_t *arg_i, size_t *src_line) -> uint8_t:
def pop_rule(parser:parser_t) -> (uint8_t, size_t, size_t):
	parser.rule_stack_top -= 1
	rule_id:uint8_t = parser.rule_stack[parser.rule_stack_top].rule_id
	arg_i:size_t = parser.rule_stack[parser.rule_stack_top].arg_i
	src_line:size_t = parser.rule_stack[parser.rule_stack_top].src_line
	return rule_id, arg_i, src_line


#if MICROPY_COMP_CONST_TUPLE
def peek_rule(parser:parser_t, n:size_t) -> uint8_t:
	assert(parser.rule_stack_top > n)
	return parser.rule_stack[parser.rule_stack_top - 1 - n].rule_id
#endif

#def mp_parse_node_get_int_maybe(pn:mp_parse_node_t, mp_obj_t *o) -> bool:
def mp_parse_node_get_int_maybe(pn:mp_parse_node_t) -> (bool, mp_obj_t):
	if (MP_PARSE_NODE_IS_SMALL_INT(pn)):
		return True, MP_OBJ_NEW_SMALL_INT(MP_PARSE_NODE_LEAF_SMALL_INT(pn))
	elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_const_object)):
		pns:mp_parse_node_struct_t = pn
		o:mp_obj_t = mp_parse_node_extract_const_object(pns)
		return mp_obj_is_int(o), o
	else:
		return False, None
	#
#

#if MICROPY_COMP_CONST_TUPLE or MICROPY_COMP_CONST
def mp_parse_node_is_const(pn:mp_parse_node_t) -> bool:
	if (MP_PARSE_NODE_IS_SMALL_INT(pn)):
		return True
	elif (MP_PARSE_NODE_IS_LEAF(pn)):
		kind:uintptr_t = MP_PARSE_NODE_LEAF_KIND(pn)
		if (kind == MP_PARSE_NODE_STRING):
			return True
		elif (kind == MP_PARSE_NODE_TOKEN):
			arg:uintptr_t = MP_PARSE_NODE_LEAF_ARG(pn)
			return (arg == MP_TOKEN_KW_NONE)\
				or (arg == MP_TOKEN_KW_FALSE)\
				or (arg == MP_TOKEN_KW_TRUE)\
				or (arg == MP_TOKEN_ELLIPSIS)
		#
	elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_const_object)):
		return True
	elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_atom_paren)):
		pns:mp_parse_node_struct_t = pn
		return MP_PARSE_NODE_IS_NULL(pns.nodes[0])
	
	return False;
#

def mp_parse_node_convert_to_obj(pn:mp_parse_node_t) -> mp_obj_t:
	assert(mp_parse_node_is_const(pn))
	if (MP_PARSE_NODE_IS_SMALL_INT(pn)):
		arg:mp_int_t = MP_PARSE_NODE_LEAF_SMALL_INT(pn)
		#if MICROPY_DYNAMIC_COMPILER
		sign_mask:mp_uint_t = -(1 << (mp_dynamic_compiler.small_int_bits - 1))
		if (not((arg & sign_mask) == 0 or (arg & sign_mask) == sign_mask)):
			return mp_obj_new_int_from_ll(arg)
		#endif
		return MP_OBJ_NEW_SMALL_INT(arg)
	elif (MP_PARSE_NODE_IS_LEAF(pn)):
		kind:uintptr_t = MP_PARSE_NODE_LEAF_KIND(pn)
		arg:uintptr_t = MP_PARSE_NODE_LEAF_ARG(pn)
		if (kind == MP_PARSE_NODE_STRING):
			return MP_OBJ_NEW_QSTR(arg)
		else:
			assert(MP_PARSE_NODE_LEAF_KIND(pn) == MP_PARSE_NODE_TOKEN)
			"""
			match(arg):
				case MP_TOKEN_KW_NONE:
					return mp_const_none
				case MP_TOKEN_KW_FALSE:
					return mp_const_false
				case MP_TOKEN_KW_TRUE:
					return mp_const_true
				case _:
					assert(arg == MP_TOKEN_ELLIPSIS)
					return MP_OBJ_FROM_PTR(mp_const_ellipsis_obj)
			#
			"""
			if arg == MP_TOKEN_KW_NONE:
				return mp_const_none
			elif arg == MP_TOKEN_KW_FALSE:
				return mp_const_false
			elif arg == MP_TOKEN_KW_TRUE:
				return mp_const_true
			else:
				assert(arg == MP_TOKEN_ELLIPSIS)
				return MP_OBJ_FROM_PTR(mp_const_ellipsis_obj)
			#
		#
	elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_const_object)):
		pns:mp_parse_node_struct_t = pn
		return mp_parse_node_extract_const_object(pns)
	else:
		assert(MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_atom_paren))
		assert(MP_PARSE_NODE_IS_NULL((pn).nodes[0]))
		return mp_const_empty_tuple
	#
#
#endif

def parse_node_is_const_bool(pn:mp_parse_node_t, value:bool) -> bool:
	#if MICROPY_COMP_CONST_TUPLE or MICROPY_COMP_CONST
	return mp_parse_node_is_const(pn) and mp_obj_is_true(mp_parse_node_convert_to_obj(pn)) == value
	#else
	#return MP_PARSE_NODE_IS_TOKEN_KIND(pn, MP_TOKEN_KW_TRUE if value else MP_TOKEN_KW_FALSE)
	#or (MP_PARSE_NODE_IS_SMALL_INT(pn) and !!MP_PARSE_NODE_LEAF_SMALL_INT(pn) == value);
	#endif
#

def mp_parse_node_is_const_false(pn:mp_parse_node_t) -> bool:
	return parse_node_is_const_bool(pn, False)
#

def mp_parse_node_is_const_true(pn:mp_parse_node_t) -> bool:
	return parse_node_is_const_bool(pn, True)
#

#def mp_parse_node_extract_list(pn:mp_parse_node_t, pn_kind:size_t, nodes:[mp_parse_node_t]) -> size_t:
#@FIXME: Change calling convention on caller to TWO return values
def mp_parse_node_extract_list(pn:mp_parse_node_t, pn_kind:size_t) -> (size_t, [mp_parse_node_t]):
	if (MP_PARSE_NODE_IS_NULL(pn)):
		return 0, None
	elif (MP_PARSE_NODE_IS_LEAF(pn)):
		return 1, pn
	else:
		pns:mp_parse_node_struct_t = pn	#(mp_parse_node_struct_t *)(*pn);
		if (MP_PARSE_NODE_STRUCT_KIND(pns) != pn_kind):
			return 1, pn;
		else:
			return MP_PARSE_NODE_STRUCT_NUM_NODES(pns), pns.nodes
	#
#

"""
#if MICROPY_DEBUG_PRINTERS
def mp_parse_node_print(prnt:mp_print_t, pn:mp_parse_node_t, indent:size_t):
	if (MP_PARSE_NODE_IS_STRUCT(pn)):
		mp_printf(prnt, "[% 4d] ", (int)((mp_parse_node_struct_t *)pn).source_line)
	else:
		mp_printf(prnt, " ")
	for (i in range(indent):
		mp_printf(prnt, " ")
	if (MP_PARSE_NODE_IS_NULL(pn)):
		mp_printf(prnt, "NULL\n")
	elif (MP_PARSE_NODE_IS_SMALL_INT(pn)):
		arg:mp_int_t = MP_PARSE_NODE_LEAF_SMALL_INT(pn)
		mp_printf(prnt, "int(" INT_FMT ")\n", arg)
	elif (MP_PARSE_NODE_IS_LEAF(pn)):
		arg:uintptr_t = MP_PARSE_NODE_LEAF_ARG(pn)
		match(MP_PARSE_NODE_LEAF_KIND(pn)):
			case MP_PARSE_NODE_ID:
				mp_printf(prnt, "id(%s)\n", qstr_str(arg))
			case MP_PARSE_NODE_STRING:
				mp_printf(prnt, "str(%s)\n", qstr_str(arg));
			case _:
				assert(MP_PARSE_NODE_LEAF_KIND(pn) == MP_PARSE_NODE_TOKEN)
				mp_printf(prnt, "tok(%u)\n", (uint)arg);
		#
	else:
		pns:mp_parse_node_struct_t = pn	#(mp_parse_node_struct_t *)pn;
		if (MP_PARSE_NODE_STRUCT_KIND(pns) == RULE_const_object):
			obj:mp_obj_t = mp_parse_node_extract_const_object(pns)
			#if MICROPY_OBJ_REPR == MICROPY_OBJ_REPR_D
			mp_printf(prnt, "literal const(%016llx)=", obj)
			#else
			mp_printf(prnt, "literal const(%p)=", obj)
			#endif
			mp_obj_print_helper(prnt, obj, PRINT_REPR)
			mp_printf(prnt, "\n")
		else:
			n:size_t = MP_PARSE_NODE_STRUCT_NUM_NODES(pns)
			#if MICROPY_DEBUG_PARSE_RULE_NAME
			mp_printf(prnt, "%s(%u) (n=%u)\n", rule_name_table[MP_PARSE_NODE_STRUCT_KIND(pns)], MP_PARSE_NODE_STRUCT_KIND(pns), n)
			#else
			#mp_printf(print, "rule(%u) (n=%u)\n", (uint)MP_PARSE_NODE_STRUCT_KIND(pns), (uint)n);
			#endif
			for i in range(n):
				mp_parse_node_print(prnt, pns.nodes[i], indent + 2)
			#
		#
	#
#
#endif
"""

def pop_result(parser:parser_t) -> mp_parse_node_t:
	assert(parser.result_stack_top > 0)
	parser.result_stack_top -= 1
	pn = parser.result_stack[parser.result_stack_top]
	
	if PARSER_VERBOSE_RESULT_POP:
		put('pop_result: %s' % str(pn))
	return pn
#

def peek_result(parser:parser_t, pos:size_t) -> mp_parse_node_t:
	assert(parser.result_stack_top > pos)
	return parser.result_stack[parser.result_stack_top - 1 - pos]
#

def push_result_node(parser:parser_t, pn:mp_parse_node_t):
	if PARSER_VERBOSE_RESULT_NODE:
		put('push_result_node: %s' % str(pn))
	if not isinstance(pn, mp_parse_node_t):
		raise Exception('push_result_node: node is not a mp_parse_node_t, but %s: %s' % (str(type(pn)), str(pn)))
	"""
	if (parser.result_stack_top >= parser.result_stack_alloc):
		stack:mp_parse_node_t = m_renew(mp_parse_node_t, parser.result_stack, parser.result_stack_alloc, parser.result_stack_alloc + MICROPY_ALLOC_PARSE_RESULT_INC)
		parser.result_stack = stack
		parser.result_stack_alloc += MICROPY_ALLOC_PARSE_RESULT_INC
	#
	"""
	while (parser.result_stack_top >= parser.result_stack_alloc):
		parser.result_stack.append(mp_parse_node_t())	# * MICROPY_ALLOC_PARSE_RESULT_INC
		parser.result_stack_alloc += 1	# MICROPY_ALLOC_PARSE_RESULT_INC
	
	parser.result_stack[parser.result_stack_top] = pn
	parser.result_stack_top += 1
#

def make_node_const_object(parser:parser_t, src_line:size_t, obj:mp_obj_t) -> mp_parse_node_t:
	#pn:mp_parse_node_struct_t = parser_alloc(parser, sizeof(mp_parse_node_struct_t) + sizeof(mp_obj_t))
	pn:mp_parse_node_struct_t = mp_parse_node_struct_t(16)	#@FIXME: How big?
	pn.source_line = src_line
	
	#@FIXME: Which one is it?
	#if MICROPY_OBJ_REPR == MICROPY_OBJ_REPR_D
	pn.kind_num_nodes = RULE_const_object | (2 << 8)
	pn.nodes[0] = obj % 0x100000000	#(uint64_t)obj
	pn.nodes[1] = obj >> 32	#(uint64_t)obj >> 32;
	#else
	pn.kind_num_nodes = RULE_const_object | (1 << 8)
	pn.nodes[0] = obj	#(uintptr_t)obj
	#endif
	return pn	#(mp_parse_node_t)pn;
#

def make_node_const_object_optimised(parser:parser_t, src_line:size_t, obj:mp_obj_t) -> mp_parse_node_t:
	if (mp_obj_is_small_int(obj)):
		val:mp_int_t = MP_OBJ_SMALL_INT_VALUE(obj)
		#if MICROPY_OBJ_REPR == MICROPY_OBJ_REPR_D
		if (((val ^ (val << 1)) & 0xffffffff80000000) != 0):
			return make_node_const_object(parser, src_line, obj)
		#endif
		#if MICROPY_DYNAMIC_COMPILER
		sign_mask:mp_uint_t = -(1 << (mp_dynamic_compiler.small_int_bits - 1))
		if (not ((val & sign_mask) == 0 or (val & sign_mask) == sign_mask)):
			return make_node_const_object(parser, src_line, obj)
		#endif
		return mp_parse_node_new_small_int(val)
	else:
		return make_node_const_object(parser, src_line, obj)
	#
#

def push_result_token(parser:parser_t, rule_id:uint8_t):
	pn:mp_parse_node_t = None
	lex:mp_lexer_t = parser.lexer
	
	if PARSER_VERBOSE_RESULT_TOKEN:
		put('push_result_token: rule_id=%d, lex=%s' % (rule_id, str(lex)))
	
	if (lex.tok_kind == MP_TOKEN_NAME):
		id:qstr = lex.vstr	#@FIXME: qstr_from_strn(lex.vstr, le(nlex.vstr))
		#if MICROPY_COMP_CONST
		# if name is a standalone identifier, look it up in the table of dynamic constants
		#elem:mp_map_elem_t = mp_map_lookup(parser.consts, MP_OBJ_NEW_QSTR(id), MP_MAP_LOOKUP) if rule_id == RULE_atom else None
		elem:mp_map_elem_t = parser.consts[id] if id in parser.consts else None
		
		if ((rule_id == RULE_atom) and (elem is not None)):
			pn = make_node_const_object_optimised(parser, lex.tok_line, elem.value)
		else:
			pn = mp_parse_node_new_leaf(MP_PARSE_NODE_ID, id)
		#else
		#(void)rule_id;
		#pn = mp_parse_node_new_leaf(MP_PARSE_NODE_ID, id)
		#endif
	elif (lex.tok_kind == MP_TOKEN_INTEGER):
		#o:mp_obj_t = mp_parse_num_integer(lex.vstr, str(lex.vstr), 0, lex)
		o:mp_obj_t = mp_parse_num_integer(lex.vstr)
		pn = make_node_const_object_optimised(parser, lex.tok_line, o)
	elif (lex.tok_kind == MP_TOKEN_FLOAT_OR_IMAG):
		o:mp_obj_t = mp_parse_num_float(lex.vstr, len(lex.vstr), True, lex)
		pn = make_node_const_object(parser, lex.tok_line, o)
	elif (lex.tok_kind == MP_TOKEN_STRING):
		qst:qstr = MP_QSTRnull
		if (len(lex.vstr) <= MICROPY_ALLOC_PARSE_INTERN_STRING_LEN):
			qst = str(lex.vstr)	#qstr_from_strn(lex.vstr, len(lex.vstr))
		else:
			#qst = qstr_find_strn(lex.vstr, len(lex.vstr));
			raise Exception('String too long (%d > max %d)' % (len(lex.vstr), MICROPY_ALLOC_PARSE_INTERN_STRING_LEN))
		
		if (qst != MP_QSTRnull):
			pn = mp_parse_node_new_leaf(MP_PARSE_NODE_STRING, qst)
		else:
			o:mp_obj_t = mp_obj_new_str_copy(mp_type_str, lex.vstr, len(lex.vstr))
			pn = make_node_const_object(parser, lex.tok_line, o)
		#
	elif (lex.tok_kind == MP_TOKEN_BYTES):
		o:mp_obj_t = mp_obj_new_bytes(lex.vstr, len(lex.vstr))
		pn = make_node_const_object(parser, lex.tok_line, o)
	else:
		pn = mp_parse_node_new_leaf(MP_PARSE_NODE_TOKEN, lex.tok_kind)
	#
	push_result_node(parser, pn)
#

#if MICROPY_COMP_CONST_FOLDING
#if MICROPY_COMP_MODULE_CONST

"""
#@FIXME: Constant table... For what and how?

#const mp_rom_map_elem_t mp_constants_table[] = {
mp_constants_table:[mp_rom_map_elem_t] = [
	#if MICROPY_PY_ERRNO
	[ MP_ROM_QSTR(MP_QSTR_errno), MP_ROM_PTR(mp_module_errno) ],
	#endif
	#if MICROPY_PY_UCTYPES
	[ MP_ROM_QSTR(MP_QSTR_uctypes), MP_ROM_PTR(mp_module_uctypes) ],
	#endif
	MICROPY_PORT_CONSTANTS
]

static MP_DEFINE_CONST_MAP(mp_constants_map, mp_constants_table);
"""
#@TODO: Constants??
mp_constants_map = dict()
mp_constants_map[qstr('errno')] = None	# Pointer to something else

#endif

#if MICROPY_COMP_CONST_FOLDING_COMPILER_WORKAROUND
#MP_NOINLINE
#endif

#@FIXME: Change calling convention on caller to TWO return values
def fold_logical_constants(parser:parser_t, rule_id:uint8_t, num_args:size_t) -> (bool, size_t):
	if (rule_id == RULE_or_test or rule_id == RULE_and_test):
		copy_to:size_t = num_args;
		i:size_t = copy_to
		while (i > 0):
			i -= 1
			pn:mp_parse_node_t = peek_result(parser, i)
			parser.result_stack[parser.result_stack_top - copy_to] = pn
			if (i == 0):
				break
			
			if (rule_id == RULE_or_test):
				if (mp_parse_node_is_const_true(pn)):
					break
				elif (not mp_parse_node_is_const_false(pn)):
					copy_to -= 1
			else:
				if (mp_parse_node_is_const_false(pn)):
					break
				elif (not mp_parse_node_is_const_true(pn)):
					copy_to -= 1
			#
		#
		copy_to -= 1
		for i in range(copy_to):
			pop_result(parser)
		num_args -= copy_to
		return num_args == 1, num_args
	elif (rule_id == RULE_not_test_2):
		pn:mp_parse_node_t = peek_result(parser, 0)
		if (mp_parse_node_is_const_false(pn)):
			pn = mp_parse_node_new_leaf(MP_PARSE_NODE_TOKEN, MP_TOKEN_KW_TRUE)
		elif (mp_parse_node_is_const_true(pn)):
			pn = mp_parse_node_new_leaf(MP_PARSE_NODE_TOKEN, MP_TOKEN_KW_FALSE)
		else:
			return False, num_args
		pop_result(parser)
		push_result_node(parser, pn)
		return True, num_args
	#
	return False, num_args
#

def fold_constants(parser:parser_t, rule_id:uint8_t, num_args:size_t) -> bool:
	arg0:mp_obj_t = None
	if (rule_id == RULE_expr
	or rule_id == RULE_xor_expr
	or rule_id == RULE_and_expr
	or rule_id == RULE_power):
		pn:mp_parse_node_t = peek_result(parser, num_args - 1)
		#if (not mp_parse_node_get_int_maybe(pn, &arg0)) {
		r,arg0 = mp_parse_node_get_int_maybe(pn)
		if (not r):
			return False
		
		op:mp_binary_op_t = None
		if (rule_id == RULE_expr):
			op = MP_BINARY_OP_OR
		elif (rule_id == RULE_xor_expr):
			op = MP_BINARY_OP_XOR
		elif (rule_id == RULE_and_expr):
			op = MP_BINARY_OP_AND
		else:
			op = MP_BINARY_OP_POWER
		
		#for (ssize_t i = num_args - 2; i >= 0; --i) {
		i:ssize_t = num_args - 2
		while (i >= 0):
			pn = peek_result(parser, i)
			arg1:mp_obj_t = None
			#if (!mp_parse_node_get_int_maybe(pn, &arg1)) {
			r, arg1 = mp_parse_node_get_int_maybe(pn)
			if (not r):
				return False
			
			if (op == MP_BINARY_OP_POWER and mp_obj_int_sign(arg1) < 0):
				return False
			
			arg0 = mp_binary_op(op, arg0, arg1)
			i -= 1
		#
	elif (rule_id == RULE_shift_expr
		or rule_id == RULE_arith_expr
		or rule_id == RULE_term):
		pn:mp_parse_node_t = peek_result(parser, num_args - 1)
		#if (!mp_parse_node_get_int_maybe(pn, &arg0)) {
		r, arg0 = mp_parse_node_get_int_maybe(pn)
		if (not r):
			return False
		
		#for (ssize_t i = num_args - 2; i >= 1; i -= 2) {
		i:ssize_t = num_args - 2
		while (i >= 1):
			pn = peek_result(parser, i - 1)
			arg1:mp_obj_t
			#if (!mp_parse_node_get_int_maybe(pn, &arg1)) {
			r, arg1 = mp_parse_node_get_int_maybe(pn)
			if (not r):
				return False
			
			tok:mp_token_kind_t = MP_PARSE_NODE_LEAF_ARG(peek_result(parser, i))
			if (tok == MP_TOKEN_OP_AT or tok == MP_TOKEN_OP_SLASH):
				return False
			
			op:mp_binary_op_t = MP_BINARY_OP_LSHIFT + (tok - MP_TOKEN_OP_DBL_LESS)
			rhs_sign:int = mp_obj_int_sign(arg1)
			if (op <= MP_BINARY_OP_RSHIFT):
				if (rhs_sign < 0):
					return False
			elif (op >= MP_BINARY_OP_FLOOR_DIVIDE):
				if (rhs_sign == 0):
					return False
			#
			arg0 = mp_binary_op(op, arg0, arg1)
			i -= 2
		#
	elif (rule_id == RULE_factor_2):
		pn:mp_parse_node_t = peek_result(parser, 0)
		#if (!mp_parse_node_get_int_maybe(pn, &arg0)) {
		r, arg0 = mp_parse_node_get_int_maybe(pn)
		if (not r):
			return False
		
		tok:mp_token_kind_t = MP_PARSE_NODE_LEAF_ARG(peek_result(parser, 1))
		op:mp_unary_op_t = None
		if (tok == MP_TOKEN_OP_TILDE):
			op = MP_UNARY_OP_INVERT
		else:
			assert(tok == MP_TOKEN_OP_PLUS or tok == MP_TOKEN_OP_MINUS)
			op = MP_UNARY_OP_POSITIVE + (tok - MP_TOKEN_OP_PLUS)
		
		arg0 = mp_unary_op(op, arg0)
		#if MICROPY_COMP_CONST
	elif (rule_id == RULE_expr_stmt):
		pn1:mp_parse_node_t = peek_result(parser, 0)
		if (not MP_PARSE_NODE_IS_NULL(pn1)
		and (not (MP_PARSE_NODE_IS_STRUCT_KIND(pn1, RULE_expr_stmt_augassign))
		or MP_PARSE_NODE_IS_STRUCT_KIND(pn1, RULE_expr_stmt_assign_list))):
			pn0:mp_parse_node_t = peek_result(parser, 1)
			if (MP_PARSE_NODE_IS_ID(pn0)
			and MP_PARSE_NODE_IS_STRUCT_KIND(pn1, RULE_atom_expr_normal)
			and MP_PARSE_NODE_IS_ID(pn1.nodes[0])	#((mp_parse_node_struct_t *)pn1).nodes[0]
			and MP_PARSE_NODE_LEAF_ARG(pn1.nodes[0]) == MP_QSTR_const	#((mp_parse_node_struct_t *)pn1).nodes[0]) == MP_QSTR_const
			and MP_PARSE_NODE_IS_STRUCT_KIND(pn1.nodes[1], RULE_trailer_paren)	# ((mp_parse_node_struct_t *)pn1).nodes[1], RULE_trailer_paren
			):
				id:qstr = MP_PARSE_NODE_LEAF_ARG(pn0)
				pn_value:mp_parse_node_t = pn1.nodes[1].nodes[0]
				if (not mp_parse_node_is_const(pn_value)):
					#exc:mp_obj_t = mp_obj_new_exception_msg(mp_type_SyntaxError,
					#MP_ERROR_TEXT("not a constant"));
					#mp_obj_exception_add_traceback(exc, parser.lexer.source_name,
					#((mp_parse_node_struct_t *)pn1).source_line, MP_QSTRnull);
					#nlr_raise(exc);
					raise Exception('SyntaxError: not a constant at %s' % str(pn1.source_line))
				#
				value:mp_obj_t = mp_parse_node_convert_to_obj(pn_value)
				elem:mp_map_elem_t = mp_map_lookup(parser.consts, MP_OBJ_NEW_QSTR(id), MP_MAP_LOOKUP_ADD_IF_NOT_FOUND)
				assert(elem.value == MP_OBJ_NULL)
				elem.value = value
				if (qstr_str(id)[0] == '_'):
					pop_result(parser)
					pop_result(parser)
					push_result_rule(parser, 0, RULE_pass_stmt, 0)
					return True
				
				pop_result(parser)
				push_result_node(parser, pn_value)
				return False
			#
		#
		return False
		#endif
		#if MICROPY_COMP_MODULE_CONST
	elif (rule_id == RULE_atom_expr_normal):
		pn0:mp_parse_node_t = peek_result(parser, 1)
		pn1:mp_parse_node_t = peek_result(parser, 0)
		if (not (MP_PARSE_NODE_IS_ID(pn0)
		and MP_PARSE_NODE_IS_STRUCT_KIND(pn1, RULE_trailer_period))):
			return False
		
		pns1:mp_parse_node_struct_t = pn1	#(mp_parse_node_struct_t *)pn1;
		assert(MP_PARSE_NODE_IS_ID(pns1.nodes[0]))
		q_base:qstr = MP_PARSE_NODE_LEAF_ARG(pn0)
		q_attr:qstr = MP_PARSE_NODE_LEAF_ARG(pns1.nodes[0])
		#elem:mp_map_elem_t = mp_map_lookup(mp_constants_map, MP_OBJ_NEW_QSTR(q_base), MP_MAP_LOOKUP)
		elem = mp_constants_map[q_base] if q_base in mp_constants_map else None
		if (elem is None):
			return False
		
		dest:[mp_obj_t] = [ None, None ]
		mp_load_method_maybe(elem.value, q_attr, dest)
		if (not (dest[0] != MP_OBJ_NULL and mp_obj_is_int(dest[0]) and dest[1] == MP_OBJ_NULL)):
			return False
		
		arg0 = dest[0]
		#endif
	else:
		return False
	
	i:size_t = num_args
	while (i > 0):
		pop_result(parser)
		i -= 1
	
	push_result_node(parser, make_node_const_object_optimised(parser, 0, arg0))
	return True
#
#endif

#if MICROPY_COMP_CONST_TUPLE
def build_tuple_from_stack(parser:parser_t, src_line:size_t, num_args:size_t) -> bool:
	i:size_t = num_args
	while (i > 0):
		i -= 1
		pn:mp_parse_node_t = peek_result(parser, i)
		if (not mp_parse_node_is_const(pn)):
			return False
		#
	#
	tuple:mp_obj_tuple_t = MP_OBJ_TO_PTR(mp_obj_new_tuple(num_args, None))
	i = num_args
	while (i > 0):
		pn:mp_parse_node_t = pop_result(parser)
		i -= 1
		tuple.items[i] = mp_parse_node_convert_to_obj(pn)
		if (MP_PARSE_NODE_IS_STRUCT(pn)):
			parser_free_parse_node_struct(parser, pm)	#(mp_parse_node_struct_t *)pn);
		#
	#
	push_result_node(parser, make_node_const_object(parser, src_line, MP_OBJ_FROM_PTR(tuple)))
	return True
#

def build_tuple(parser:parser_t, src_line:size_t, rule_id:uint8_t, num_args:size_t) -> bool:
	if (rule_id == RULE_testlist_comp):
		if (peek_rule(parser, 0) == RULE_atom_paren):
			return build_tuple_from_stack(parser, src_line, num_args)
		
	
	if (rule_id == RULE_testlist_comp_3c):
		assert(peek_rule(parser, 0) == RULE_testlist_comp_3b)
		assert(peek_rule(parser, 1) == RULE_testlist_comp)
		if (peek_rule(parser, 2) == RULE_atom_paren):
			if (build_tuple_from_stack(parser, src_line, num_args)):
				parser.rule_stack_top -= 2
				return True
			#
		#
	#
	if (rule_id == RULE_testlist_star_expr
		or rule_id == RULE_testlist
		or rule_id == RULE_subscriptlist):
		return build_tuple_from_stack(parser, src_line, num_args)
	#
	return False
#
#endif

def push_result_rule(parser:parser_t, src_line:size_t, rule_id:uint8_t, num_args:size_t):
	if (rule_id == RULE_atom_paren):
		pn:mp_parse_node_t = peek_result(parser, 0)
		if (MP_PARSE_NODE_IS_NULL(pn)):
			pass
		elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_testlist_comp)):
			pass
		else:
			return
		#
	elif (rule_id == RULE_testlist_comp):
		assert(num_args == 2)
		pn:mp_parse_node_t = peek_result(parser, 0)
		if (MP_PARSE_NODE_IS_STRUCT(pn)):
			pns:mp_parse_node_struct_t = pn	#(mp_parse_node_struct_t *)pn;
			if (MP_PARSE_NODE_STRUCT_KIND(pns) == RULE_testlist_comp_3b):
				pop_result(parser)
				num_args -= 1
			elif (MP_PARSE_NODE_STRUCT_KIND(pns) == RULE_testlist_comp_3c):
				pop_result(parser)
				assert(pn == peek_result(parser, 0))
				pns.kind_num_nodes = rule_id | MP_PARSE_NODE_STRUCT_NUM_NODES(pns) << 8
				return
			elif (MP_PARSE_NODE_STRUCT_KIND(pns) == RULE_comp_for):
				pass
			else:
				pass
			#
		else:
			pass
		#
	elif (rule_id == RULE_testlist_comp_3c):
		num_args += 1
	#
	
	#if MICROPY_COMP_CONST_FOLDING
	#if (fold_logical_constants(parser, rule_id, &num_args)) {
	r, num_args = fold_logical_constants(parser, rule_id, num_args)
	if (r):
		return
	
	if (fold_constants(parser, rule_id, num_args)):
		return
	
	#endif
	#if MICROPY_COMP_CONST_TUPLE
	if (build_tuple(parser, src_line, rule_id, num_args)):
		return
	
	#endif
	#pn:mp_parse_node_struct_t = parser_alloc(parser, sizeof(mp_parse_node_struct_t) + sizeof(mp_parse_node_t) * num_args)
	pn:mp_parse_node_struct_t = mp_parse_node_struct_t(num_args)
	pn.source_line = src_line
	pn.kind_num_nodes = (rule_id & 0xff) | (num_args << 8)
	i:size_t = num_args
	while (i > 0):
		pn.nodes[i - 1] = pop_result(parser)
		i -= 1
	
	if (rule_id == RULE_testlist_comp_3c):
		push_result_node(parser, pn)	#(mp_parse_node_t)pn)
	
	push_result_node(parser, pn)	#(mp_parse_node_t)pn);
#

def mp_parse(lex:mp_lexer_t, input_kind:mp_parse_input_kind_t) -> mp_parse_tree_t:
	###MP_DEFINE_NLR_JUMP_CALLBACK_FUNCTION_1(ctx, mp_lexer_free, lex)
	###nlr_push_jump_callback(&ctx.callback, mp_call_function_1_from_nlr_jump_callback)
	
	parser:parser_t = parser_t()
	parser.rule_stack_alloc = MICROPY_ALLOC_PARSE_RULE_INIT
	parser.rule_stack_top = 0
	parser.rule_stack = [ rule_stack_t() for i in range(parser.rule_stack_alloc) ]	#@FIXME: m_new(rule_stack_t, parser.rule_stack_alloc)
	parser.result_stack_alloc = MICROPY_ALLOC_PARSE_RESULT_INIT
	parser.result_stack_top = 0
	parser.result_stack = [ MP_PARSE_NODE_NULL for i in range(parser.result_stack_alloc) ]	#@FIXME: m_new(mp_parse_node_t, parser.result_stack_alloc)
	parser.lexer = lex
	parser.tree.chunk = None
	parser.cur_chunk = None
	#if MICROPY_COMP_CONST
	parser.consts = dict()	#{}	#@FIXME: mp_map_init(parser.consts, 0)
	#endif
	top_level_rule:size_t
	"""
	match(input_kind):
		case MP_PARSE_SINGLE_INPUT:
			top_level_rule = RULE_single_input
		case MP_PARSE_EVAL_INPUT:
			top_level_rule = RULE_eval_input
		case _:
			top_level_rule = RULE_file_input
	#
	"""
	if input_kind == MP_PARSE_SINGLE_INPUT:
		top_level_rule = RULE_single_input
	elif input_kind == MP_PARSE_EVAL_INPUT:
		top_level_rule = RULE_eval_input
	else:
		top_level_rule = RULE_file_input
	#
	
	push_rule(parser, lex.tok_line, top_level_rule, 0)
	backtrack:bool = False
	while (True):
		#next_rule:
		#put('next_rule')
		next_rule:bool = False
		
		if (parser.rule_stack_top == 0):
			put('Reached end of rule_stack')
			break
		
		# Pop the next rule to process it
		i:size_t = 0
		rule_src_line:size_t = 0
		rule_id:uint8_t = 0
		#uint8_t rule_id = pop_rule(&parser, &i, &rule_src_line);
		rule_id, i, rule_src_line = pop_rule(parser)
		
		#put('rule_id=%d / len=%d' % (rule_id, len(rule_act_table)))
		rule_act:uint8_t = rule_act_table[rule_id]
		
		#rule_arg:uint16_t = get_rule_arg(rule_id)
		rule_arg_idx:uint16_t = get_rule_arg_offset(rule_id)
		
		n:size_t = rule_act & RULE_ACT_ARG_MASK
		"""
		#if 0
		printf("depth=" UINT_FMT " ", parser.rule_stack_top);
		for (int j = 0; j < parser.rule_stack_top; ++j) {
			printf(" ");
		}
		printf("%s n=" UINT_FMT " i=" UINT_FMT " bt=%d\n", rule_name_table[rule_id], n, i, backtrack);
		#endif
		"""
		if PARSER_VERBOSE_RULES:
			put('depth=%d %s %s (%d) n=%d, i=%d, bt=%s, at	%s' % (parser.rule_stack_top, ' '*parser.rule_stack_top, rule_name_table[rule_id], rule_id, n, i, str(backtrack), str(lex)))
		
		#match(rule_act & RULE_ACT_KIND_MASK):
		rule_act_masked = rule_act & RULE_ACT_KIND_MASK
		#match(rule_act & RULE_ACT_KIND_MASK):
		if rule_act_masked == RULE_ACT_OR:
			if (i > 0 and not backtrack):
				#goto next_rule;
				next_rule = True
				continue
			else:
				backtrack = False
			
			#for (; i < n; ++i) {
			while(i < n):
				#kind:uint16_t = rule_arg[i] & RULE_ARG_KIND_MASK
				kind:uint16_t = rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_KIND_MASK
				
				#put('%d / %d, rule_arg_idx=%d, kind=%04x' % (i, n, rule_arg_idx, kind))
				
				if (kind == RULE_ARG_TOK):
					#put('TOK current=%s' % lex.tok_kind)
					#if (lex.tok_kind == (rule_arg[i] & RULE_ARG_ARG_MASK)):
					if (lex.tok_kind == (rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_ARG_MASK)):
						#put('TOK match for rule_id=%d' % rule_id)
						push_result_token(parser, rule_id)
						
						#put('mp_lexer_to_next...')
						mp_lexer_to_next(lex)
						#put(str(lex))
						
						#goto next_rule;
						next_rule = True
						break
					#
				else:
					assert(kind == RULE_ARG_RULE)
					if (i + 1 < n):
						push_rule(parser, rule_src_line, rule_id, i + 1)	# save this or-rule
					
					#push_rule_from_arg(parser, rule_arg[i])
					push_rule_from_arg(parser, rule_arg_combined_table[rule_arg_idx + i])	# push child of or-rule
					#goto next_rule;
					next_rule = True
					break
				#
				i += 1
			#
			if (next_rule): continue
			backtrack = True
			
		elif rule_act_masked == RULE_ACT_AND:
			
			# failed, backtrack if we can, else syntax error
			
			if (backtrack):
				assert(i > 0)
				#if ((rule_arg[i - 1] & RULE_ARG_KIND_MASK) == RULE_ARG_OPT_RULE):
				if ((rule_arg_combined_table[rule_arg_idx + i - 1] & RULE_ARG_KIND_MASK) == RULE_ARG_OPT_RULE):
					# an optional rule that failed, so continue with next arg
					push_result_node(parser, mp_parse_node_null_t())	#push_result_node(parser, MP_PARSE_NODE_NULL)
					backtrack = False
				else:
					# a mandatory rule that failed, so propagate backtrack
					if (i > 1):
						# already eaten tokens so can't backtrack
						#goto syntax_error
						mp_raise_syntax_error(lex)
					else:
						#goto next_rule
						next_rule = True
						continue
					#
				#
			#
			while(i < n):
				#if ((rule_arg[i] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
				if ((rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
					#tok_kind:mp_token_kind_t = rule_arg[i] & RULE_ARG_ARG_MASK
					tok_kind:mp_token_kind_t = rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_ARG_MASK
					if (lex.tok_kind == tok_kind):
						if (tok_kind == MP_TOKEN_NAME):
							push_result_token(parser, rule_id)
						#
						#put('mp_lexer_to_next...')
						mp_lexer_to_next(lex)
						#put(str(lex))
					else:
						if (i > 0):
							#goto syntax_error
							mp_raise_syntax_error(lex)
						else:
							backtrack = True
							#goto next_rule;
							next_rule = True
							break
						#
					#
				else:
					push_rule(parser, rule_src_line, rule_id, i + 1)
					#push_rule_from_arg(parser, rule_arg[i])
					push_rule_from_arg(parser, rule_arg_combined_table[rule_arg_idx + i])
					#goto next_rule
					next_rule = True
					break
				#
				i += 1
			#
			if (next_rule): continue
			
			assert(i == n)
			#if !MICROPY_ENABLE_DOC_STRING
			if (input_kind != MP_PARSE_SINGLE_INPUT and rule_id == RULE_expr_stmt and peek_result(parser, 0) == MP_PARSE_NODE_NULL):
				p:mp_parse_node_t = peek_result(parser, 1)
				if ((MP_PARSE_NODE_IS_LEAF(p) and not MP_PARSE_NODE_IS_ID(p))
				or MP_PARSE_NODE_IS_STRUCT_KIND(p, RULE_const_object)):
					pop_result(parser)
					pop_result(parser)
					push_result_rule(parser, rule_src_line, RULE_pass_stmt, 0)
					break
				#
			#
			#endif
			i = 0
			num_not_nil:size_t = 0
			#for (size_t x = n; x > 0;) {
			x:size_t = n
			while(x > 0):
				x -= 1
				#if ((rule_arg[x] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
				if ((rule_arg_combined_table[rule_arg_idx + x] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
					#tok_kind:mp_token_kind_t = rule_arg[x] & RULE_ARG_ARG_MASK
					tok_kind:mp_token_kind_t = rule_arg_combined_table[rule_arg_idx + x] & RULE_ARG_ARG_MASK
					if (tok_kind == MP_TOKEN_NAME):
						i += 1
						num_not_nil += 1
					#
				else:
					if (peek_result(parser, i) != MP_PARSE_NODE_NULL):
						num_not_nil += 1
					#
					i += 1
				#
			#
			if (num_not_nil == 1 and (rule_act & RULE_ACT_ALLOW_IDENT)):
				pn:mp_parse_node_t = MP_PARSE_NODE_NULL
				for x in range(i):
					pn2:mp_parse_node_t = pop_result(parser)
					if (pn2 != MP_PARSE_NODE_NULL):
						pn = pn2
					#
				#
				push_result_node(parser, pn)
			else:
				if (rule_act & RULE_ACT_ADD_BLANK):
					push_result_node(parser, mp_parse_node_null_t())	#push_result_node(parser, MP_PARSE_NODE_NULL)
					i += 1
				#
				push_result_rule(parser, rule_src_line, rule_id, i)
			#
			
		
		else:
			assert((rule_act & RULE_ACT_KIND_MASK) == RULE_ACT_LIST)
			had_trailing_sep:bool = False
			
			if (backtrack):
				
				#list_backtrack:	# I copied the code block instead of using goto list_backtrack
				
				had_trailing_sep = False
				if (n == 2):
					if (i == 1):
						#goto next_rule;
						next_rule = True
						continue
					else:
						backtrack = False
					#
				else:
					if (i == 1):
						#goto next_rule;
						next_rule = True
						continue
					elif ((i & 1) == 1):
						if (n == 3):
							had_trailing_sep = True
							backtrack = False
						else:
							#goto syntax_error
							mp_raise_syntax_error(lex)
						#
					else:
						backtrack = False
					#
				#
			else:
				# Not backtracking
				while True:
					#arg:size_t = rule_arg[i & 1 & n]
					arg:size_t = rule_arg_combined_table[rule_arg_idx + (i & 1 & n)]
					if ((arg & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
						if (lex.tok_kind == (arg & RULE_ARG_ARG_MASK)):
							if (i & 1 & n):
								pass
							else:
								push_result_token(parser, rule_id)
							#
							#put('mp_lexer_to_next...')
							mp_lexer_to_next(lex)
							#put(str(lex))
							i += 1
						else:
							i += 1;
							backtrack = True
							
							#goto list_backtrack	#@FIXME: This jumps to a completely different code above...
							### I am using a modified copy of the code above!
							#list_backtrack:
							
							had_trailing_sep = False
							if (n == 2):
								if (i == 1):
									#goto next_rule;
									next_rule = True
									break	# break to get out of endless while
								else:
									backtrack = False
								#
							else:
								if (i == 1):
									#goto next_rule;
									next_rule = True
									break	# break to get out of endless while
								elif ((i & 1) == 1):
									if (n == 3):
										had_trailing_sep = True
										backtrack = False
									else:
										#goto syntax_error
										mp_raise_syntax_error(lex)
									#
								else:
									backtrack = False
								#
							###
							break	# Must break this block (because the code above has no loop)
							### end of copy
							
						#
					else:
						assert((arg & RULE_ARG_KIND_MASK) == RULE_ARG_RULE)
						push_rule(parser, rule_src_line, rule_id, i + 1)
						push_rule_from_arg(parser, arg)
						#goto next_rule
						next_rule = True
						break	# break to get out of endless while
					#
				# end of while True
				if next_rule: continue
			#
			
			assert(i >= 1)
			i -= 1
			#if ((n & 1) and (rule_arg[1] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
			if ((n & 1) and (rule_arg_combined_table[rule_arg_idx + 1] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
				i = (i + 1) // 2
			
			if (i == 1):
				if (had_trailing_sep):
					push_result_rule(parser, rule_src_line, rule_id, i)
				else:
					pass
				#
			else:
				push_result_rule(parser, rule_src_line, rule_id, i)
			#
			
		# end of match(rule_act_table)
	# end of next_rule-loop
	
	#if MICROPY_COMP_CONST
	parser.consts = None	#@FIXME: mp_map_deinit(parser.consts)
	#endif
	if (parser.cur_chunk is not None):
		m_renew_maybe(byte, parser.cur_chunk,
			sizeof(mp_parse_chunk_t) + parser.cur_chunk.alloc,
			sizeof(mp_parse_chunk_t) + parser.cur_chunk.union_.used,
			False);
		parser.cur_chunk.alloc = parser.cur_chunk.union_.used
		parser.cur_chunk.union_.next = parser.tree.chunk
		parser.tree.chunk = parser.cur_chunk
	#
	if (
		lex.tok_kind != MP_TOKEN_END	# check we are at the end of the token stream
		or parser.result_stack_top == 0	# check that we got a node (can fail on empty input)
	):
		"""
		syntax_error:;
		mp_obj_t exc;
		if (lex.tok_kind == MP_TOKEN_INDENT) {
			exc = mp_obj_new_exception_msg(&mp_type_IndentationError,
			MP_ERROR_TEXT("unexpected indent"));
		} else if (lex.tok_kind == MP_TOKEN_DEDENT_MISMATCH) {
			exc = mp_obj_new_exception_msg(&mp_type_IndentationError,
			MP_ERROR_TEXT("unindent doesn't match any outer indent level"));
			#if MICROPY_PY_FSTRINGS
		} else if (lex.tok_kind == MP_TOKEN_MALFORMED_FSTRING) {
			exc = mp_obj_new_exception_msg(&mp_type_SyntaxError,
			MP_ERROR_TEXT("malformed f-string"));
		} else if (lex.tok_kind == MP_TOKEN_FSTRING_RAW) {
			exc = mp_obj_new_exception_msg(&mp_type_SyntaxError,
			MP_ERROR_TEXT("raw f-strings are not supported"));
			#endif
		} else {
			exc = mp_obj_new_exception_msg(&mp_type_SyntaxError,
			MP_ERROR_TEXT("invalid syntax"));
		}
		mp_obj_exception_add_traceback(exc, lex.source_name, lex.tok_line, MP_QSTRnull);
		nlr_raise(exc);
		"""
		mp_raise_syntax_error(lex)
	#
	assert(parser.result_stack_top == 1)
	parser.tree.root = parser.result_stack[0]
	#m_del(rule_stack_t, parser.rule_stack, parser.rule_stack_alloc)
	#m_del(mp_parse_node_t, parser.result_stack, parser.result_stack_alloc)
	#nlr_pop_jump_callback(true)
	return parser.tree
#

# This is my version for Python
def mp_raise_syntax_error(lex):
	if (lex.tok_kind == MP_TOKEN_INDENT):
		raise Exception('mp_type_IndentationError: unexpected indent at %s' % str(lex))
	elif (lex.tok_kind == MP_TOKEN_DEDENT_MISMATCH):
		raise Exception('mp_type_IndentationError: unindent doesn\'t match any outer indent level at %s' % str(lex))
		#if MICROPY_PY_FSTRINGS
	elif (lex.tok_kind == MP_TOKEN_MALFORMED_FSTRING):
		raise Exception('mp_type_SyntaxError: malformed f-string at %s' % str(lex))
	elif (lex.tok_kind == MP_TOKEN_FSTRING_RAW):
		raise Exception('mp_type_SyntaxError: raw f-strings are not supported at %s' % str(lex))
		#endif
	else:
		raise Exception('mp_type_SyntaxError: invalid syntax at %s' % str(lex))
#

def mp_parse_tree_clear(tree:mp_parse_tree_t):
	chunk:mp_parse_chunk_t = tree.chunk
	while (chunk is not None):
		next:mp_parse_chunk_t = chunk.union_.next
		m_del(byte, chunk, sizeof(mp_parse_chunk_t) + chunk.alloc)
		chunk = next
	#
	tree.chunk = None
#

###

if __name__ == '__main__':
	#filename = '__t.py'
	#filename = '__test_micropython_lexer.py'
	filename = '__test_micropython_parser.py'
	
	put('Loading "%s"...' % filename)
	with open(filename, 'r') as h: code = h.read()
	
	#filename = 'test_input'
	#code = 'a=1'
	
	put('Setting up reader and lexer...')
	reader = mp_reader_t(code)
	lex = mp_lexer_new(src_name=filename, reader=reader)
	
	put('Parsing...')
	t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_FILE_INPUT)
	put('Result Tree:')
	put(str(t))
	
	put('EOF')
	