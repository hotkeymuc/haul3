#!/bin/python3
#	"""
#	Translation of MicroPython's "py/parser.h/c" to Python
#	It is based on the "expand_macros" processed "grammar.h".
#	
#	2024-04-07 Bernhard "HotKey" Slawik
#	"""

# Verbosity options
LEXER_VERBOSE = not True	# Show tokens as they are streamed in
PARSER_VERBOSE_RULES = not True	# Show rule matching
PARSER_VERBOSE_RESULT_RULE = not True	# Show result rules as they are pushed
PARSER_VERBOSE_RESULT_TOKEN = not True	# Show result tokens as they are pushed
PARSER_VERBOSE_RESULT_NODE = not True	# Show result nodes as they are pushed
PARSER_VERBOSE_RESULT_POP = not True	# Show parse nodes as they are popped
DUMP_INDENT = '  '	#'\t'

MICROPY_ALLOC_PARSE_RULE_INC = 1
MICROPY_ALLOC_PARSE_RULE_INIT = 16	# Initial size of rule stack (automatically incremented if more is needed)
MICROPY_ALLOC_PARSE_RESULT_INIT = 16	# Initial size of result stack (automatically incremented if more is needed)
MICROPY_ALLOC_PARSE_INTERN_STRING_LEN = 1024 * 16	# Maximum length of strings before raising an Exception
MICROPY_ALLOC_PARSE_RESULT_INC = 1
MICROPY_ENABLE_DOC_STRING = True
#MICROPY_COMP_CONST = ???
#MICROPY_COMP_CONST_TUPLE = ???
#MICROPY_DYNAMIC_COMPILER = ???
#MICROPY_OBJ_REPR == MICROPY_OBJ_REPR_D ???
#MICROPY_COMP_CONST_FOLDING = ???
#MICROPY_COMP_MODULE_CONST = ???
#MICROPY_COMP_CONST = ???

### Glue code

# Set lexer to verbose
if LEXER_VERBOSE:
	import __test_micropython_lexer
	__test_micropython_lexer.MP_LEXER_VERBOSE = True


# When running as library:
if __name__ == 'haul.langs.py.__test_micropython_parser':
	from haul.langs.py.__test_micropython_lexer import *
	from haul.langs.py.__test_micropython_grammar import *
else:
	# When running stand-alone:
	from __test_micropython_lexer import *
	from __test_micropython_grammar import *


def put(t:str):
	print(t)

def put2(t:str, u:str) -> None:
	print(t)

# Define some types for interoperability
size_t = int
uint8_t = int
uint16_t = int
uint32_t = int

qstr = str
MP_QSTRnull = None	#@FIXME: ???
MP_QSTR_const = 'const'	#@FIXME: ????
def qstr_from_strn(s:str, l:int) -> qstr:
	return s[:l]

### Part of runtime
# mp_unary_op_t enum:
# These ops may appear in the bytecode. Changing this group
# in any way requires changing the bytecode version.
MP_UNARY_OP_POSITIVE = 0
MP_UNARY_OP_NEGATIVE = 1
MP_UNARY_OP_INVERT = 2
MP_UNARY_OP_NOT = 3

# Following ops cannot appear in the bytecode
MP_UNARY_OP_BOOL = 4	# __bool__
MP_UNARY_OP_LEN = 5	# __len__
MP_UNARY_OP_HASH = 6	# __hash__; must return a small int
MP_UNARY_OP_ABS = 7	# __abs__
MP_UNARY_OP_INT_MAYBE = 8	# __int__; must return MP_OBJ_NULL, or an object satisfying mp_obj_is_int()
MP_UNARY_OP_FLOAT_MAYBE = 9	# __float__
MP_UNARY_OP_COMPLEX_MAYBE = 10	# __complex__
MP_UNARY_OP_SIZEOF = 11	# for sys.getsizeof()
#} mp_unary_op_t;

mp_binary_op_t = int
#typedef enum {
# The following 9+13+13 ops are used in bytecode and changing
# them requires changing the bytecode version.

# 9 relational operations, should return a bool; order of first 6 matches corresponding mp_token_kind_t
MP_BINARY_OP_LESS	= 0
MP_BINARY_OP_MORE	= 1
MP_BINARY_OP_EQUAL	= 2
MP_BINARY_OP_LESS_EQUAL	= 3
MP_BINARY_OP_MORE_EQUAL	= 4
MP_BINARY_OP_NOT_EQUAL	= 5
MP_BINARY_OP_IN	 = 6
MP_BINARY_OP_IS	 = 7
MP_BINARY_OP_EXCEPTION_MATCH	 = 8

# 13 inplace arithmetic operations; order matches corresponding mp_token_kind_t
MP_BINARY_OP_INPLACE_OR	 = 9
MP_BINARY_OP_INPLACE_XOR	 = 10
MP_BINARY_OP_INPLACE_AND	 = 11
MP_BINARY_OP_INPLACE_LSHIFT	 = 12
MP_BINARY_OP_INPLACE_RSHIFT	 = 13
MP_BINARY_OP_INPLACE_ADD	 = 14
MP_BINARY_OP_INPLACE_SUBTRACT	 = 15
MP_BINARY_OP_INPLACE_MULTIPLY	 = 16
MP_BINARY_OP_INPLACE_MAT_MULTIPLY	 = 17
MP_BINARY_OP_INPLACE_FLOOR_DIVIDE	 = 18
MP_BINARY_OP_INPLACE_TRUE_DIVIDE	 = 19
MP_BINARY_OP_INPLACE_MODULO	 = 20
MP_BINARY_OP_INPLACE_POWER	 = 21

# 13 normal arithmetic operations; order matches corresponding mp_token_kind_t
MP_BINARY_OP_OR	 = 22
MP_BINARY_OP_XOR	 = 23
MP_BINARY_OP_AND	 = 24
MP_BINARY_OP_LSHIFT	 = 25
MP_BINARY_OP_RSHIFT	 = 26
MP_BINARY_OP_ADD	 = 27
MP_BINARY_OP_SUBTRACT	 = 28
MP_BINARY_OP_MULTIPLY	 = 29
MP_BINARY_OP_MAT_MULTIPLY	 = 30
MP_BINARY_OP_FLOOR_DIVIDE	 = 31
MP_BINARY_OP_TRUE_DIVIDE	 = 32
MP_BINARY_OP_MODULO	 = 33
MP_BINARY_OP_POWER	 = 34

# Operations below this line don't appear in bytecode, they
# just identify special methods.

# This is not emitted by the compiler but is supported by the runtime.
# It must follow immediately after MP_BINARY_OP_POWER.
MP_BINARY_OP_DIVMOD	 = 35

# The runtime will convert MP_BINARY_OP_IN to this operator with swapped args.
# A type should implement this containment operator instead of MP_BINARY_OP_IN.
MP_BINARY_OP_CONTAINS	 = 36

# 13 MP_BINARY_OP_REVERSE_* operations must be in the same order as MP_BINARY_OP_*	 = 0
# and be the last ones supported by the runtime.
MP_BINARY_OP_REVERSE_OR	 = 37
MP_BINARY_OP_REVERSE_XOR	 = 38
MP_BINARY_OP_REVERSE_AND	 = 39
MP_BINARY_OP_REVERSE_LSHIFT	 = 40
MP_BINARY_OP_REVERSE_RSHIFT	 = 41
MP_BINARY_OP_REVERSE_ADD	 = 42
MP_BINARY_OP_REVERSE_SUBTRACT	 = 43
MP_BINARY_OP_REVERSE_MULTIPLY	 = 44
MP_BINARY_OP_REVERSE_MAT_MULTIPLY	 = 45
MP_BINARY_OP_REVERSE_FLOOR_DIVIDE	 = 46
MP_BINARY_OP_REVERSE_TRUE_DIVIDE	 = 47
MP_BINARY_OP_REVERSE_MODULO	 = 48
MP_BINARY_OP_REVERSE_POWER	 = 49

# These 2 are not supported by the runtime and must be synthesised by the emitter
MP_BINARY_OP_NOT_IN	 = 50
MP_BINARY_OP_IS_NOT	 = 51
#} mp_binary_op_t;

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


#	### Original C implementation stores parse_nodes as numbers. The lowest bits determine the type, the upper bits are the data/pointer
#	
#	class mp_parse_node_struct_t:
#		source_line:uint32_t = 0	# line number in source file
#		kind_num_nodes:uint32_t = 0	# parse node kind, and number of nodes
#		nodes = []	#nodes
#		def __init__(self, num_args):
#			self.nodes = [ mp_parse_node_t() for i in range(num_args) ]
#	
#	# macros for mp_parse_node_t usage
#	# some of these evaluate their argument more than once
#	
#	def MP_PARSE_NODE_IS_NULL(pn):	return ((pn) == MP_PARSE_NODE_NULL)
#	def MP_PARSE_NODE_IS_LEAF(pn):	return ((pn) & 3)
#	#return type(pn) is int	#mp_parse_node_struct_t
#
#	def MP_PARSE_NODE_IS_STRUCT(pn): return ((pn) != MP_PARSE_NODE_NULL and ((pn) & 3) == 0)
#	#return (pn is not None) and (type(pn) is mp_parse_node_struct_t)
#	
#	def MP_PARSE_NODE_IS_STRUCT_KIND(pn, k): return ((pn) != MP_PARSE_NODE_NULL and ((pn) & 3) == 0 and MP_PARSE_NODE_STRUCT_KIND((pn)) == (k))
#	#return MP_PARSE_NODE_IS_STRUCT(pn) and (MP_PARSE_NODE_STRUCT_KIND(pn) == k)
#	
#	def MP_PARSE_NODE_IS_SMALL_INT(pn): return (((pn) & 0x1) == MP_PARSE_NODE_SMALL_INT)
#	def MP_PARSE_NODE_IS_ID(pn): return (((pn) & 0x0f) == MP_PARSE_NODE_ID)
#	def MP_PARSE_NODE_IS_TOKEN(pn): return (((pn) & 0x0f) == MP_PARSE_NODE_TOKEN)
#	def MP_PARSE_NODE_IS_TOKEN_KIND(pn, k): return ((pn) == (MP_PARSE_NODE_TOKEN | ((k) << 4)))
#	
#	def MP_PARSE_NODE_LEAF_KIND(pn): return ((pn) & 0x0f)
#	def MP_PARSE_NODE_LEAF_ARG(pn): return (((pn)) >> 4)
#	def MP_PARSE_NODE_LEAF_SMALL_INT(pn): return (((pn)) >> 1)
#	def MP_PARSE_NODE_STRUCT_KIND(pns): return ((pns).kind_num_nodes & 0xff)
#	def MP_PARSE_NODE_STRUCT_NUM_NODES(pns): return ((pns).kind_num_nodes >> 8)
#	
#	def mp_parse_node_new_small_int(v):
#		return v
#	
#	def mp_parse_node_new_leaf(kind:size_t, arg:mp_int_t) -> mp_parse_node_t:
#		return kind | (arg << 4)
#	


### htk: "Python-ification" of mp_parse_node_t
# Original uses numbers and re-interprets them. We are using class inheritance.
class mp_parse_node_t:
	typ:size_t = -1	#MP_PARSE_NODE_NULL
	def __repr__(self):
		if self.typ == -1: return '--'
		
		return '%s (0x%02x), %s' % (self.__class__.__name__[len('mp_parse_node_'):-2].upper(), self.typ, ', '.join([ '%s=%s'%(k[:-len('_value')],str(v)) if k.endswith('_value') else '' for k,v in self.__dict__.items() ]))

class mp_parse_node_null_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_NULL
	def __repr__(self):
		#return 'NULL (0x%02x)' % self.typ
		return 'NULL'

class mp_parse_node_small_int_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_SMALL_INT
	small_int_value:int = 0
	def __init__(self, small_int_value:int):
		self.small_int_value = small_int_value
	def get_arg(self) -> int:
		return self.small_int_value
	def __repr__(self):
		#return '%s (0x%02x), %s' % (self.__class__.__name__[len('mp_parse_node_'):-2].upper(), self.typ, ', '.join([ '%s=%s'%(k[:-len('_value')],str(v)) if k.endswith('_value') else '' for k,v in self.__dict__.items() ]))
		return 'SMALL_INT: %d / 0x%02x' % (self.small_int_value, self.small_int_value)

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
MP_PARSE_NODE_STRUCT_DEFAULT_NODES = 8
class mp_parse_node_struct_t(mp_parse_node_t):
	typ:size_t = MP_PARSE_NODE_STRUCT	#htk
	source_line:uint32_t = 0	# line number in source file
	kind_num_nodes:uint32_t = 0	# parse node kind, and number of nodes	# Caution! This is BOTH in ONE value (low byte=kind / high byte=num_nodes)
	nodes = []	#nodes
	
	def __init__(self, num_args=MP_PARSE_NODE_STRUCT_DEFAULT_NODES):
		self.nodes = [ mp_parse_node_t() for i in range(num_args) ]
	
	def __repr__(self):
		#return '%s (0x%02x), kind_num_nodes=0x%04x' % (self.__class__.__name__, self.typ, self.kind_num_nodes)
		kind = self.kind_num_nodes & 0xff
		num_nodes = self.kind_num_nodes >> 8
		#return '%s (0x%02x), kind=%s (%d), num_nodes=%d' % (self.__class__.__name__, self.typ, rule_name_table[kind] if kind < len(rule_name_table) else '0x%02X'%kind, kind, num_nodes)
		return 'STRUCT: kind=%s (%d), num_nodes=%d' % (rule_name_table[kind] if kind < len(rule_name_table) else '0x%02X'%kind, kind, num_nodes)
	
	def dump(self, indent=0):
		kind = self.kind_num_nodes & 0xff
		r = '%sSTRUCT: %s {\t// line %d' % (
			DUMP_INDENT * indent,
			rule_name_table[kind] if kind < len(rule_name_table) else '0x%02X'%kind,
			self.source_line
		)
		
		num_nodes = self.kind_num_nodes >> 8
		for i,pn in enumerate(self.nodes[:num_nodes]):
			if not isinstance(pn, mp_parse_node_t):
				r += '\n%s??? %s (%s)' % (DUMP_INDENT * (indent+1), str(pn), str(type(pn)))
			elif MP_PARSE_NODE_IS_NULL(pn) and (i == num_nodes-1):
				continue	# Do not dump trailing NULLs
			elif MP_PARSE_NODE_IS_STRUCT(pn):
				# Recurse
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


### mp_obj_t stuff...
mp_obj_t = None
mp_const_true = True
mp_const_false = False
mp_const_none = None

def mp_obj_is_true(o:mp_obj_t) -> bool:
	return o == mp_const_true
def mp_obj_is_int(o:mp_obj_t) -> bool:
	return type(o) is int
def mp_obj_int_sign(o:mp_obj_t) -> int:
	return 0 if o == 0 else 1 if o > 0 else -1
def mp_obj_is_small_int(o) -> bool:
	#@FIXME: When is it "small"?
	#put('mp_obj_is_small_int: o=%s (%s)' % (str(o), str(type(o))))
	return (type(o) is int)	and (o < 128)

def mp_parse_node_extract_const_object(pns:mp_parse_node_struct_t) -> mp_obj_t:
	#@FIXME: Don't know how to "wrap" mp_obj_t into mp_parse_node_struct_t
	put('Dont know how to extract object, yet...')
	return pns

class mp_obj_tuple_t:
	items:[mp_obj_t] = []
	def __init__(self, n:size_t, items:[mp_obj_t]):
		if items is None:
			self.items = [ None for i in range(n) ]
		else:
			self.items = items
def mp_obj_new_tuple(n:size_t, items:[mp_obj_t]) -> mp_obj_t:
	return mp_obj_tuple_t(n, items)

class mp_binary_op_t_c:
	op:mp_binary_op_t = 0
	arg0 = None
	arg1 = None
	def __init__(self, op, arg0, arg1):
		self.op = op
		self.arg0 = arg0
		self.arg1 = arg1

def mp_binary_op(op:mp_binary_op_t, arg0:int, arg1:int) -> mp_binary_op_t_c:
	#return (op, arg0, arg1)
	return mp_binary_op_t_c(op, arg0, arg1)


def MP_OBJ_SMALL_INT_VALUE(o):
	return int(o)
def MP_OBJ_NEW_SMALL_INT(i):
	return i
def MP_OBJ_NEW_QSTR(s) -> qstr:
	return s
def MP_OBJ_TO_PTR(o):
	return o
def MP_OBJ_FROM_PTR(p) -> mp_obj_t:
	return p



def mp_parse_node_new_small_int(v:int) -> mp_parse_node_small_int_t:	#mp_parse_node_t
	#put('mp_parse_node_new_small_int: %s (%s)' % (str(v), str(type(v))))
	#return v
	return mp_parse_node_small_int_t(v)

def mp_parse_node_new_leaf(kind:size_t, arg:mp_int_t) -> mp_parse_node_t:
	#return (mp_parse_node_t)(kind | ((mp_uint_t)arg << 4));
	#return kind | (arg << 4)
	if kind == MP_PARSE_NODE_NULL:
		return mp_parse_node_null_t()
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


class rule_stack_t:
	src_line:size_t = (8 * 4 - 8)	#(8 * sizeof(size_t) - 8)
	rule_id:size_t = 8
	arg_i:size_t = 0

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


class mp_parse_tree_t:
	root:mp_parse_node_t = None
	chunk:mp_parse_chunk_t = None
	
	def __repr__(self):
		#return 'mp_parse_tree_t: root=%s%s' % ('--' if self.root is None else str(self.root), '' if self.chunk is None else '\n'+self.chunk.dump(indent=1))
		#r = 'mp_parse_tree_t: root=%s\n%s' % ('--' if self.root is None else str(self.root), '' if self.chunk is None else '\n'+self.chunk.dump(indent=1))
		r = 'mp_parse_tree_t: chunk="%s"\n' % ('' if self.chunk is None else '\n'+self.chunk.dump(indent=1))
		if self.root is None:
			r += 'root=None'
		elif MP_PARSE_NODE_IS_STRUCT(self.root):
			r += 'root=%s' % self.root.dump()
		else:
			r += 'root=%s' % str(self.root)
		return r

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


def get_rule_arg_offset(r_id:uint8_t) -> uint16_t:
	off:size_t = rule_arg_offset_table[r_id]
	if (r_id >= FIRST_RULE_WITH_OFFSET_ABOVE_255):
		off |= 0x100
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
def parser_free_parse_node_struct(parser:parser_t, pns:mp_parse_node_struct_t):
	chunk:mp_parse_chunk_t = parser.cur_chunk
	
	if ((chunk.data <= pns) and (pns < chunk.data + chunk.union_.used)):
		num_bytes:size_t = sizeof(mp_parse_node_struct_t) + sizeof(mp_parse_node_t) * MP_PARSE_NODE_STRUCT_NUM_NODES(pns)
		chunk.union_.used -= num_bytes
#
#endif

def push_rule(parser:parser_t, src_line:size_t, rule_id:uint8_t, arg_i:size_t):
	
	#	if (parser.rule_stack_top >= parser.rule_stack_alloc):
	#		rs:rule_stack_t = m_renew(rule_stack_t, parser.rule_stack, parser.rule_stack_alloc, parser.rule_stack_alloc + MICROPY_ALLOC_PARSE_RULE_INC)
	#		parser.rule_stack = rs
	#		parser.rule_stack_alloc += MICROPY_ALLOC_PARSE_RULE_INC
	
	while (parser.rule_stack_top >= parser.rule_stack_alloc):
		parser.rule_stack.append(rule_stack_t())
		parser.rule_stack_alloc += MICROPY_ALLOC_PARSE_RULE_INC
	
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
			return (
				(arg == MP_TOKEN_KW_NONE)
				or (arg == MP_TOKEN_KW_FALSE)
				or (arg == MP_TOKEN_KW_TRUE)
				or (arg == MP_TOKEN_ELLIPSIS)
			)
		#
	elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_const_object)):
		return True
	elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_atom_paren)):
		pns:mp_parse_node_struct_t = pn
		return MP_PARSE_NODE_IS_NULL(pns.nodes[0])
	
	return False
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

def mp_parse_node_is_const_false(pn:mp_parse_node_t) -> bool:
	return parse_node_is_const_bool(pn, False)

def mp_parse_node_is_const_true(pn:mp_parse_node_t) -> bool:
	return parse_node_is_const_bool(pn, True)

#	#def mp_parse_node_extract_list(pn:mp_parse_node_t, pn_kind:size_t, nodes:[mp_parse_node_t]) -> size_t:
#	def mp_parse_node_extract_list(pn:mp_parse_node_t, pn_kind:size_t) -> (size_t, [mp_parse_node_t]):
#		if (MP_PARSE_NODE_IS_NULL(pn)):
#			return 0, None
#		elif (MP_PARSE_NODE_IS_LEAF(pn)):
#			return 1, pn
#		else:
#			pns:mp_parse_node_struct_t = pn
#			if (MP_PARSE_NODE_STRUCT_KIND(pns) != pn_kind):
#				return 1, pn
#			else:
#				return MP_PARSE_NODE_STRUCT_NUM_NODES(pns), pns.nodes
#		#
#	#


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
	
	
	#	if (parser.result_stack_top >= parser.result_stack_alloc):
	#		stack:mp_parse_node_t = m_renew(mp_parse_node_t, parser.result_stack, parser.result_stack_alloc, parser.result_stack_alloc + MICROPY_ALLOC_PARSE_RESULT_INC)
	#		parser.result_stack = stack
	#		parser.result_stack_alloc += MICROPY_ALLOC_PARSE_RESULT_INC
	
	while (parser.result_stack_top >= parser.result_stack_alloc):
		parser.result_stack.append(mp_parse_node_t())	# * MICROPY_ALLOC_PARSE_RESULT_INC
		parser.result_stack_alloc += MICROPY_ALLOC_PARSE_RESULT_INC
	
	parser.result_stack[parser.result_stack_top] = pn
	parser.result_stack_top += 1
#

def make_node_const_object(parser:parser_t, src_line:size_t, obj:mp_obj_t) -> mp_parse_node_t:
	#pn:mp_parse_node_struct_t = parser_alloc(parser, sizeof(mp_parse_node_struct_t) + sizeof(mp_obj_t))
	pn:mp_parse_node_struct_t = mp_parse_node_struct_t(2)
	pn.source_line = src_line
	
	#if MICROPY_OBJ_REPR == MICROPY_OBJ_REPR_D
	#pn.kind_num_nodes = RULE_const_object | (2 << 8)
	#pn.nodes[0] = obj % 0x100000000	#(uint64_t)obj
	#pn.nodes[1] = obj >> 32	#(uint64_t)obj >> 32;
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
		#if (((val ^ (val << 1)) & 0xffffffff80000000) != 0):
		#	return make_node_const_object(parser, src_line, obj)
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
			qst = qstr_from_strn(lex.vstr, len(lex.vstr))
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

#@FIXME: Constant table... For what and how?
#	mp_constants_table:[mp_rom_map_elem_t] = [
#		#if MICROPY_PY_ERRNO
#		[ MP_ROM_QSTR(MP_QSTR_errno), MP_ROM_PTR(mp_module_errno) ],
#		#endif
#		#if MICROPY_PY_UCTYPES
#		[ MP_ROM_QSTR(MP_QSTR_uctypes), MP_ROM_PTR(mp_module_uctypes) ],
#		#endif
#		MICROPY_PORT_CONSTANTS
#	]
#	static MP_DEFINE_CONST_MAP(mp_constants_map, mp_constants_table);

mp_constants_map = dict()
mp_constants_map[qstr('errno')] = None	# Pointer to something else

#endif

#if MICROPY_COMP_CONST_FOLDING_COMPILER_WORKAROUND
#MP_NOINLINE
#endif

def fold_logical_constants(parser:parser_t, rule_id:uint8_t, num_args:size_t) -> (bool, size_t):
	if (rule_id == RULE_or_test or rule_id == RULE_and_test):
		copy_to:size_t = num_args;
		i:size_t = copy_to
		while (i > 0):
			i -= 1
			pn:mp_parse_node_t = peek_result(parser, i)
			parser.result_stack[parser.result_stack_top - copy_to] = pn
			if (i == 0):
				# always need to keep the last value
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
		copy_to -= 1	# copy_to now contains number of args to pop
		
		# pop and discard all the short-circuited expressions
		for i in range(copy_to):
			#put("    pop... i=%d, copy_to=%d\n" % (i, copy_to));
			pop_result(parser)
		
		num_args -= copy_to
		return num_args == 1, num_args
		
	elif (rule_id == RULE_not_test_2):
		# folding for unary logical op: not
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
		
		i:ssize_t = num_args - 2
		while (i >= 0):
			pn = peek_result(parser, i)
			arg1:mp_obj_t = None
			r, arg1 = mp_parse_node_get_int_maybe(pn)
			if (not r):
				return False
			
			if (op == MP_BINARY_OP_POWER) and (mp_obj_int_sign(arg1) < 0):
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
		
		i:ssize_t = num_args - 2
		while (i >= 1):
			pn = peek_result(parser, i - 1)
			arg1:mp_obj_t
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
				# code to assign dynamic constants: id = const(value)
				
				# get the id
				id:qstr = MP_PARSE_NODE_LEAF_ARG(pn0)
				
				# get the value
				pn_value:mp_parse_node_t = pn1.nodes[1].nodes[0]
				if (not mp_parse_node_is_const(pn_value)):
					raise Exception('SyntaxError: not a constant at line %s' % str(pn1.source_line))
				#
				value:mp_obj_t = mp_parse_node_convert_to_obj(pn_value)
				
				# store the value in the table of dynamic constants
				elem:mp_map_elem_t = mp_map_lookup(parser.consts, MP_OBJ_NEW_QSTR(id), MP_MAP_LOOKUP_ADD_IF_NOT_FOUND)
				assert(elem.value == MP_OBJ_NULL)
				elem.value = value
				
				# If the constant starts with an underscore then treat it as a private
				# variable and don't emit any code to store the value to the id.
				if (qstr_str(id)[0] == '_'):
					pop_result(parser)	# pop const(value)
					pop_result(parser)	# pop id
					push_result_rule(parser, 0, RULE_pass_stmt, 0)	# replace with "pass"
					return True
				
				# replace const(value) with value
				pop_result(parser)
				push_result_node(parser, pn_value)
				
				# finished folding this assignment, but we still want it to be part of the tree
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
	
	# success folding this rule
	
	i:size_t = num_args
	while (i > 0):
		#put(" fold end: i=%d, num_args=%d" % (i, num_args));
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
	tup:mp_obj_tuple_t = MP_OBJ_TO_PTR(mp_obj_new_tuple(num_args, None))
	i = num_args
	while (i > 0):
		pn:mp_parse_node_t = pop_result(parser)
		i -= 1
		tup.items[i] = mp_parse_node_convert_to_obj(pn)
		if (MP_PARSE_NODE_IS_STRUCT(pn)):
			parser_free_parse_node_struct(parser, pm)	#(mp_parse_node_struct_t *)pn);
		#
	#
	push_result_node(parser, make_node_const_object(parser, src_line, MP_OBJ_FROM_PTR(tup)))
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
#endif

def push_result_rule(parser:parser_t, src_line:size_t, rule_id:uint8_t, num_args:size_t):
	# Simplify and optimise certain rules, to reduce memory usage and simplify the compiler.
	if PARSER_VERBOSE_RESULT_RULE:
		put('push_result_rule %s (%d)' % (rule_name_table[rule_id], rule_id))
	
	if (rule_id == RULE_atom_paren):
		# Remove parenthesis around a single expression if possible.
		# This atom_paren rule always has a single argument, and after this
		# optimisation that argument is either NULL or testlist_comp.
		pn:mp_parse_node_t = peek_result(parser, 0)
		if (MP_PARSE_NODE_IS_NULL(pn)):
			# need to keep parenthesis for ()
			pass
		elif (MP_PARSE_NODE_IS_STRUCT_KIND(pn, RULE_testlist_comp)):
			# need to keep parenthesis for (a, b, ...)
			pass
		else:
			# parenthesis around a single expression, so it's just the expression
			return
		#
	elif (rule_id == RULE_testlist_comp):
		# The testlist_comp rule can be the sole argument to either atom_parent
		# or atom_bracket, for (...) and [...] respectively.
		assert(num_args == 2)
		pn:mp_parse_node_t = peek_result(parser, 0)
		if (MP_PARSE_NODE_IS_STRUCT(pn)):
			pns:mp_parse_node_struct_t = pn	#(mp_parse_node_struct_t *)pn;
			if (MP_PARSE_NODE_STRUCT_KIND(pns) == RULE_testlist_comp_3b):
				# tuple of one item, with trailing comma
				pop_result(parser)
				num_args -= 1
			elif (MP_PARSE_NODE_STRUCT_KIND(pns) == RULE_testlist_comp_3c):
				# tuple of many items, convert testlist_comp_3c to testlist_comp
				pop_result(parser)
				assert(pn == peek_result(parser, 0))
				pns.kind_num_nodes = rule_id | MP_PARSE_NODE_STRUCT_NUM_NODES(pns) << 8
				return
			elif (MP_PARSE_NODE_STRUCT_KIND(pns) == RULE_comp_for):
				# generator expression
				pass
			else:
				# tuple with 2 items
				pass
			#
		else:
			# tuple with 2 items
			pass
		#
	elif (rule_id == RULE_testlist_comp_3c):
		# steal first arg of outer testlist_comp rule
		num_args += 1
	#
	
	#if MICROPY_COMP_CONST_FOLDING
	#if (fold_logical_constants(parser, rule_id, &num_args)) {
	r, num_args = fold_logical_constants(parser, rule_id, num_args)
	if (r):
		# we folded this rule so return straight away
		return
	if (fold_constants(parser, rule_id, num_args)):
		# we folded this rule so return straight away
		return
	
	#endif
	
	#if MICROPY_COMP_CONST_TUPLE
	if (build_tuple(parser, src_line, rule_id, num_args)):
		# we built a tuple from this rule so return straight away
		return
	#endif
	
	#pn:mp_parse_node_struct_t = parser_alloc(parser, sizeof(mp_parse_node_struct_t) + sizeof(mp_parse_node_t) * num_args)
	pn:mp_parse_node_struct_t = mp_parse_node_struct_t(num_args)
	pn.source_line = src_line
	pn.kind_num_nodes = (rule_id & 0xff) | (num_args << 8)
	i:size_t = num_args
	#put(' 1048:  num_args=%d' % num_args)
	while (i > 0):
		#put(" 1049:  i=%d" % i)
		pn.nodes[i - 1] = pop_result(parser)
		i -= 1
	
	if (rule_id == RULE_testlist_comp_3c):
		# need to push something non-null to replace stolen first arg of testlist_comp
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
	parser.result_stack = [ mp_parse_node_null_t() for i in range(parser.result_stack_alloc) ]	#@FIXME: m_new(mp_parse_node_t, parser.result_stack_alloc)
	parser.lexer = lex
	parser.tree.chunk = None
	parser.cur_chunk = None
	#if MICROPY_COMP_CONST
	parser.consts = dict()	#{}	#@FIXME: mp_map_init(parser.consts, 0)
	#endif
	top_level_rule:size_t
	if input_kind == MP_PARSE_SINGLE_INPUT:
		top_level_rule = RULE_single_input
	elif input_kind == MP_PARSE_EVAL_INPUT:
		top_level_rule = RULE_eval_input
	else:
		top_level_rule = RULE_file_input
	
	push_rule(parser, lex.tok_line, top_level_rule, 0)
	backtrack:bool = False
	while (True):
		#next_rule:
		next_rule:bool = False
		
		if (parser.rule_stack_top == 0):
			put('Reached end of rule_stack')
			break
		
		# Pop the next rule to process it
		i:size_t = 0
		rule_src_line:size_t = 0
		rule_id:uint8_t = 0
		rule_id, i, rule_src_line = pop_rule(parser)
		rule_act:uint8_t = rule_act_table[rule_id]
		rule_arg_idx:uint16_t = get_rule_arg_offset(rule_id)
		
		n:size_t = rule_act & RULE_ACT_ARG_MASK
		
		if PARSER_VERBOSE_RULES:
			put('depth=%d %s %s (%d) n=%d, i=%d, bt=%s, at	%s' % (parser.rule_stack_top, ' '*parser.rule_stack_top, rule_name_table[rule_id], rule_id, n, i, str(backtrack), str(lex)))
		
		rule_act_masked = rule_act & RULE_ACT_KIND_MASK
		if rule_act_masked == RULE_ACT_OR:
			if (i > 0 and not backtrack):
				#goto next_rule;
				next_rule = True
				continue
			else:
				backtrack = False
			
			while(i < n):
				kind:uint16_t = rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_KIND_MASK
				#put('%d / %d, rule_arg_idx=%d, kind=%04x' % (i, n, rule_arg_idx, kind))
				
				if (kind == RULE_ARG_TOK):
					if (lex.tok_kind == (rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_ARG_MASK)):
						#put('TOK match for rule_id=%d' % rule_id)
						push_result_token(parser, rule_id)
						
						mp_lexer_to_next(lex)
						
						#goto next_rule;
						next_rule = True
						break
					#
				else:
					assert(kind == RULE_ARG_RULE)
					if (i + 1 < n):
						push_rule(parser, rule_src_line, rule_id, i + 1)	# save this or-rule
					
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
				if ((rule_arg_combined_table[rule_arg_idx + i - 1] & RULE_ARG_KIND_MASK) == RULE_ARG_OPT_RULE):
					# an optional rule that failed, so continue with next arg
					push_result_node(parser, mp_parse_node_null_t())	#push_result_node(parser, MP_PARSE_NODE_NULL)
					backtrack = False
				else:
					# a mandatory rule that failed, so propagate backtrack
					if (i > 1):
						# already eaten tokens so can't backtrack
						mp_raise_syntax_error(lex)
					else:
						#goto next_rule
						next_rule = True
						continue
					#
				#
			#
			while(i < n):
				if ((rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
					tok_kind:mp_token_kind_t = rule_arg_combined_table[rule_arg_idx + i] & RULE_ARG_ARG_MASK
					if (lex.tok_kind == tok_kind):
						if (tok_kind == MP_TOKEN_NAME):
							push_result_token(parser, rule_id)
						mp_lexer_to_next(lex)
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
					push_rule(parser, rule_src_line, rule_id, i + 1)	# save this and-rule
					push_rule_from_arg(parser, rule_arg_combined_table[rule_arg_idx + i])	# push child of and-rule
					#goto next_rule
					next_rule = True
					break
				i += 1
			#
			if (next_rule): continue
			
			assert(i == n)
			
			# matched the rule, so now build the corresponding parse_node
			
			if not MICROPY_ENABLE_DOC_STRING:
				if (input_kind != MP_PARSE_SINGLE_INPUT and rule_id == RULE_expr_stmt and peek_result(parser, 0).typ == MP_PARSE_NODE_NULL):
					p:mp_parse_node_t = peek_result(parser, 1)
					if ((MP_PARSE_NODE_IS_LEAF(p) and (not MP_PARSE_NODE_IS_ID(p)))
					or MP_PARSE_NODE_IS_STRUCT_KIND(p, RULE_const_object)):
						pop_result(parser)	# MP_PARSE_NODE_NULL
						pop_result(parser)	# const expression (leaf or RULE_const_object)
						# Pushing the "pass" rule here will overwrite any RULE_const_object
						# entry that was on the result stack, allowing the GC to reclaim
						# the memory from the const object when needed.
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
				if ((rule_arg_combined_table[rule_arg_idx + x] & RULE_ARG_KIND_MASK) == RULE_ARG_TOK):
					tok_kind:mp_token_kind_t = rule_arg_combined_table[rule_arg_idx + x] & RULE_ARG_ARG_MASK
					if (tok_kind == MP_TOKEN_NAME):
						i += 1
						num_not_nil += 1
					#
				else:
					if (peek_result(parser, i).typ != MP_PARSE_NODE_NULL):
						num_not_nil += 1
					#
					i += 1
				#
			#
			if (num_not_nil == 1 and (rule_act & RULE_ACT_ALLOW_IDENT)):
				# this rule has only 1 argument and should not be emitted
				pn:mp_parse_node_t = mp_parse_node_null_t()	#MP_PARSE_NODE_NULL
				for x in range(i):
					pn2:mp_parse_node_t = pop_result(parser)
					if (pn2.typ != MP_PARSE_NODE_NULL):
						pn = pn2
					#
				#
				push_result_node(parser, pn)
			else:
				# this rule must be emitted
				
				if (rule_act & RULE_ACT_ADD_BLANK):
					# and add an extra blank node at the end (used by the compiler to store data)
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
							mp_lexer_to_next(lex)
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
		mp_raise_syntax_error(lex)
	#
	assert(parser.result_stack_top == 1)
	parser.tree.root = parser.result_stack[0]
	#m_del(rule_stack_t, parser.rule_stack, parser.rule_stack_alloc)
	#m_del(mp_parse_node_t, parser.result_stack, parser.result_stack_alloc)
	#nlr_pop_jump_callback(true)
	return parser.tree
#

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
	tree.chunk = None
#

if __name__ == '__main__':
	#filename = '__test_micropython_lexer.py'
	filename = '__test_micropython_parser.py'
	#filename = 'micropython_minimal/test.py'
	
	put('Loading "%s"...' % filename)
	with open(filename, 'r') as h: code = h.read()
	if code[-1] == '\x04': code = code[:-1]
	#filename = 'test_input'
	#code = 'a=1'
	
	put('Setting up reader and lexer...')
	reader = mp_reader_t(code)
	lex = mp_lexer_new(src_name=filename, reader=reader)
	
	put('Parsing...')
	t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_FILE_INPUT)
	#t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_SINGLE_INPUT)
	put('Result Tree:')
	put(str(t))
	
	put('EOF')
	