#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
	HAUL
	HotKey's Amphibious Unambiguous Language
	HotKey's Average Universal Language
	
	XXX HAUL3 - HotKey's Averaging Language

2013-01-04
	This was made way after SR1 and SR2
	Currently it is just a lexer, parser and generator

TODO:
	* Store class/object constructors as I_CLASS_NEW instead of python-style standard function call "ClassName()"
	* Warum ueberhaupt noch module.classes, module.funcs - das kann doch alles in den namespace!?
	* Fields, arrays, generics!
"""

#AUTO_CREATE_UNKNOWN_IDS = True	# Required for type inference. Turn off for debugging the parser. Is stricter, breaks faster that way.

#@fun put
#@arg t str
def put(t):
	print('HAUL:\t' + str(t))

#@fun put_debug
#@arg t str
def put_debug(t):
	#put(t)
	pass

def repr_array(a):
	#return (', '.join([str(i) for i in a]))
	
	r = ''
	
	#@var i obj
	for i in a:
		if (len(r) > 0):
			r = r + ', '
		r = r + str(i)
	return r
	

class Stream:
	def eof(self):
		return True
	def seek(self, o):
		pass
	def peek(self):
		return None
	def get(self):
		return None
	def put(self, t):
		pass
	

# Guess the type of a new variable by looking at the return type of the right side
INFER_TYPE = True
BLOCKS_HAVE_LOCAL_NAMESPACE = False

# Kinds of namespae entries
K_MODULE = 'mod'
#K_NAMESPACE = 'ns'
K_FUNCTION = 'fun'
#K_CONTROL = 'ctrl'
K_TYPE = 'typ'
K_VARIABLE = 'var'
K_CONST = 'const'
K_CLASS = 'class'

#K_RETURN = 'ret'	# Moved to function declaration
#K_VALUE = 'val'
A_ARGUMENT = 'arg'	# Could re-use "variable" instead
A_RETTYPE = 'res'
A_SELF = 'self'
A_INIT = '__init__'


# Types
T_NOTHING = '#void'
T_UNKNOWN = '#unknown'
T_INHERIT = '#inherit'	# e.g. "+" inherits the returnType from its arguments

T_BOOLEAN = '#bool'
#T_BYTE = '#byte'
T_INTEGER = '#int'
T_FLOAT = '#float'
T_STRING = '#str'
T_ARRAY = '#arr'
T_OBJECT = '#obj'
T_FUNCTION = '#func'
T_CLASS = '#class'
T_MODULE = '#mod'

T_HANDLE = '#hnd'

class HAULId:
	"Unique identifier (e.g. function name, variable name, ...)"
	#@var name str
	#@var namespace HAULNamespace
	#@var kind str
	#@var data_type str
	#@var data_value HAULValue
	#@var data_function HAULFunction
	#@var data_class HAULClass
	#@var data_module HAULModule
	
	#@var origin int
	#@var user str
	
	#@fun __init__
	#@arg name str
	#@arg namespace obj
	def __init__(self, name, namespace, kind, origin=None, data_type=None, data_value=None):
		self.name = name
		self.namespace = namespace
		self.kind = kind
		
		self.data_type = data_type	# type for K_VARIABLE or K_CONST, return value for K_FUNCTION
		self.data_value = data_value	# primitive value for K_CONST, default value for K_VARIABLE
		self.data_function = None	# HAULFunction for K_FUNCTION
		self.data_class = None	# HAULClass for K_CLASS
		self.data_module = None	# HAULModule for K_MODULE
		
		self.origin = origin	# For scanning and debugging
		self.user = None	# User data, can be used e.g. for Assembly to keep track of memory location
		
	
	def __repr__(self):
		#return str(self.name)
		return str(self.namespace) + ':' + str(self.name)
		

class HAULNamespace:
	"Keeps track of all identifiers"
	#@var ids arr HAULId
	#@var name str
	#@var parent HAULNamespace
	#@var nss arr HAULNamespace
	#@var origin int
	
	def __init__(self, name, parent):
		put_debug('Creating new namespace "' + name + '" below "' + str(parent) + '"')
		self.ids = []
		self.name = name
		
		self.parent = parent
		self.nss = []	# Array of child namespaces
		self.origin = None
		
	
	def get_id(self, name, kind=None):
		"Finds the given id in this local namespace"
		#@var i HAULId
		for i in self.ids:
			if (i.name == name) and ((kind == None) or (i.kind == kind)): return i
		
		#raise Exception('HAULNamespace error: "' + name + '" was not found in local namespace: ' + str(self.ids))
		return None
	
	def find_id(self, name, kind=None, ignore_unknown=False):
		"Also searches upwards"
		
		#@var r HAULNamespace
		r = self
		while not (r == None):
			# Try finding it here
			#put('finding "' + str(name) + '" in namespace "' + str(r) + '"...')
			i = r.get_id(name=name, kind=kind)
			if (i == None):
				# If not, search one ns upwards
				r = r.parent
			else:
				#put('found "' + str(name) + '" in namespace "' + str(r) + '"...')
				return i
		
		if (ignore_unknown == False):
			raise Exception('HAULNamespace Error: Id "' + str(name) + '" (kind=' + str(kind) + ') is not defined in any namespace starting at "' + str(self) + '"!')
		
		return None
	
	def add_id(self, name, kind, origin=None, data_type=None, data_value=None):
		#if (data != None) and (not isinstance(data, str)): raise Exception('addId() must be called with string data, not "' + str(type(data)) + '"')
		
		# Check if already exists
		i = self.get_id(name=name, kind=kind)
		if (i != None):
			#raise Exception('HAULNamespaceError: "' + (name) + '" is already present in current namespace!')
			put('HAULNamespace Info: "' + (name) + '" is already present in current namespace.')
			return i
		#if (not self.find_id(name) == None): put('HAULNamespaceWarning: "' + (name) + '" hides previous declaration.')
		
		put_debug('Registering id "' + name + '" (' + str(kind) + ') as "' + str(data_type) + '" in namespace "' + str(self) + '"')
		
		i = HAULId(name=name, namespace=self, kind=kind, origin=origin, data_type=data_type, data_value=data_value)
		self.ids.append(i)
		return i
	
	def add_namespace(self, ns):
		self.nss.append(ns)
	
	def get_namespace(self, name):
		#@var ns HAULNamespace
		for ns in self.nss:
			if ns.name == name: return ns
		
		return None
	
	def find_namespace(self, name):
		#@var r HAULNamespace
		#@var ns HAULNamespace
		r = self
		while not (r == None):
			# Try finding it here
			#put('finding "' + str(name) + '" in namespace "' + str(r) + '"...')
			i = r.get_namespace(name)
			if (i == None):
				# If not, search one ns upwards
				r = r.parent
			else:
				#put('found "' + str(name) + '" in namespace "' + str(r) + '"...')
				return i
		return None
	
	def get_or_create_namespace(self, name):
		#@var ns HAULNamespace
		ns = self.get_namespace(name)
		if (ns != None): return ns
		
		# Create
		ns = HAULNamespace(name=name, parent=self)
		# Add to parent
		self.add_namespace(ns)
		return ns
	
	def find_namespace_of(self, name, kind=None):
		"Which namespace contains name"
		#@var r HAULNamespace
		r = self
		while (r != None):
			#put('finding namespace "' + str(idName) + '" in namespace "' + str(r) + '"...')
			#if r.name == idName: return r
			
			# Search direct childs
			#@var ns HAULNamespace
			for ns in r.nss:
				if (ns.name == name) and ((kind == None) or (ns.kind == kind)):
					return ns
				#else:	put('    != "' + str(ns) + '"')
			r = r.parent
		
		#raise Exception('HAULNamespace Error: Namespace for id "' + str(name) + '" was not found starting from "' + str(self) + '"!')	#\n' + rootNamespace.dump())
		return None
	
	def clear(self):
		self.ids = []
		self.nss = []
	
	def dump(self, level=1, skipEmpty=True):
		#@var i int
		
		indent = ''
		for i in xrange(level):
			indent = indent + '  '	#'\t'
			
		
		r = str(self.name) + '("' + str(self) + '", ' + str(len(self.ids)) + ' ids, ' + str(len(self.nss)) + ' childs):\n'
		#@var id HAULId
		for id in self.ids:
			r = r + indent + '* ' + str(id.name) + ' [' + str(id.kind) + '] = ' + str(id.data_value) + ' [' + str(id.data_type) + ']' + '\n'
			
		
		#@var ns HAULNamespace
		for ns in self.nss:
			if ((skipEmpty) and (len(ns.ids) == 0)): continue
			r = r + indent + '. ' + ns.dump(level+1, skipEmpty)
			
		return r
	
	def __repr__(self):
		r = ''
		if (self.parent): r = r + str(self.parent) + '.'
		r = r + str(self.name)
		return r

class HAULValue:
	"Simple value (e.g. of a variable or constant expression)"
	#@var type HAULType
	#@var data obj
	
	def __init__(self, type=None, data=None):
		self.type = None	#HAULType
		self.data = None	# binary
		
	
	def __repr__(self):
		if (self.type == T_STRING):
			return '"' + self.data + '"'
		else:
			return str(self.data)
		
	

class HAULClass:
	"One Class declaration"
	#@var id HAULId
	#@var funcs arr HAULFunction
	#@var namespace HAULNamespace
	#@var inherits arr HAULId
	
	#@var origin int
	#@var destination int
	
	def __init__(self, id=None):
		#@TODO: Static values?
		self.id = id
		#self.classes = []
		self.funcs = []
		#self.vars = []
		#self.block = None
		self.namespace = None	#HAULNamespace()
		self.inherits = []
		
		self.origin = None	#HAULOrigin?
		self.destination = None	# Record offset in output stream
	
	def addFunc(self, func):
		self.funcs.append(func)
	
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Class"'
		r = r + '"id": "' + str(self.id) + '"'
		#r = r + ', "vars": [' + (repr_array(self.vars)) + ']'
		r = r + ', "funcs": [' + (repr_array(self.funcs)) + ']'
		#if (self.block): r = r + ', ' + str(self.block)
		r = r + '}'
		return r

class HAULInstruction:
	"One instruction"
	#@var call HAULCall
	#@var control HAULControl
	#@var comment str
	
	#@var origin int
	#@var destination int
	
	def __init__(self, call=None, control=None, comment=None):
		self.call = call
		self.control = control
		self.comment = comment
		
		self.origin = None
		self.destination = None	# Record offset in output stream
		
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Instruction"'
		if (self.call != None): r = r + '"call": ' + str(self.call)
		if (self.control != None): r = r + '"control": ' + str(self.control)
		r = r + '}'
		return r

class HAULControl:
	"Control Instruction (e.g. IF, SWITCH, WHILE, FOR, ...)"
	#@var controlType str
	#@var exprs arr HAULExpression
	#@var blocks arr HAULBlock
	
	def __init__(self, controlType=None):
		#self.id = id	#HAULId
		self.controlType = controlType
		self.exprs = []
		self.blocks = []
	
	def addBlock(self, block):
		self.blocks.append(block)
	
	def addExpr(self, expr):
		self.exprs.append(expr)
	
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Control"'
		r = r + '"controlType": "' + str(self.controlType) + '">'
		r = r + ', "exprs": [' + (repr_array(self.exprs)) + ']'
		r = r + ', "blocks": [' + (repr_array(self.blocks)) + ']'
		r = r + '}'
		return r

class HAULFunction:
	"Function declaration"
	#@var id HAULId
	#@var returnType HAULType
	#@var args arr HAULExpression
	#@var block HAULBlock
	#@var namespace HAULNamespace
	
	#@var origin int
	#@var destination int
	#@var user str
	
	def __init__(self):
		#scope = None	# if variable is a class method/function
		self.id = None
		self.returnType = None
		self.args = []
		self.block = None	# The implementation of this function, including local variables
		
		self.namespace = None
		self.origin = None
		self.destination = None
		
		self.user = None	# User defined, e.g. for parsing
	
	def addArg(self, arg):
		self.args.append(arg)
	
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Function"'
		r = r + '"id": "' + str(self.id) + '"'
		r = r + ', "returnType": ' + str(self.returnType)
		r = r + ', "args": [' + (repr_array(self.args)) + ']'
		r = r + ', "block": ' + str(self.block)
		r = r + '}'
		return r

class HAULCall:
	"Function call"
	#@var id HAULId
	#@var args arr HAULExpression
	
	def __init__(self, id=None):
		self.id = id
		self.args = []
		
	def getType(self):
		return self.id.data_type
	
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Call"'
		r = r + '"id": "' + str(self.id) + '"'
		r = r + ', "args": [' + (repr_array(self.args)) + ']'
		r = r + '}'
		return r

class HAULExpression:
	"One expression of any kind."
	#@var value HAULValue
	#@var var HAULId
	#@var call HAULCall
	#@var returnType HAULType
	
	def __init__(self, value=None, var=None, call=None):
		self.value = value
		self.var = var
		self.call = call
		self.returnType = None
		
	def getType(self):
		# Guess the type of this expression
		if (self.value != None): return self.value.getType()
		if (self.var != None): return self.var.getType()
		if (self.call != None): return self.call.getType()
		put('Could not get type of expression: ' + str(self))
		return None
	
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Expression"'
		if (self.value != None): r = r + '"value": ' + str(self.value)
		if (self.var != None): r = r + '"var": ' + str(self.var)
		if (self.call != None): r = r + '"call": ' + str(self.call)
		r = r + '}'
		return r

class HAULBlock:
	"A Block of Instructions"
	#@var instrs arr HAULInstruction
	#@var name str
	
	#@var namespace HAULNamespace
	
	#@var scanOnly bool
	#@var origin int
	#@var destination int
	#@var instrs_count int
	
	def __init__(self, scanOnly=False):
		self.instrs = []
		#self.vars = []	#HAULVariable[]	Local variables
		#self.funcs = []	#HAULFunction[]	Local functions
		#self.classes = []	#HAULClass[]	Local types
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			self.namespace = None	#HAULNamespace()
		
		self.name = None	# For better debugging and namespacing. Not really needed
		self.origin = None	#HAULOrigin?
		self.destination = None	# Record offset in output stream
		self.scanOnly = scanOnly
		self.instrs_count = 0
		
	def addInstr(self, instr):
		if self.scanOnly:
			self.instrs_count = self.instrs_count + 1
		else:
			self.instrs.append(instr)
	
	def addComment(self, comment):
		if self.scanOnly:
			pass
		else:
			i = HAULInstruction(comment=comment)
			self.instrs.append(i)
	
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Block"'
		r = r + '"instrs": [' + (repr_array(self.instrs)) + ']'
		r = r + '}'
		return r


class HAULModule:
	"One Module of Code"
	#@var name str
	#@var namespace HAULNamespace
	#@var classes arr HAULClass
	#@var funcs arr HAULFunction
	#@var imports arr str
	#@var block HAULBlock
	
	#@var origin int
	#@var destination int
	#@var scanOnly bool
	#@var classes_origins arr int
	#@var funcs_origins arr int
	
	def __init__(self, scanOnly=False):
		self.name = '?'
		self.namespace = None
		
		self.classes = []
		self.funcs = []
		self.imports = []	#HAULModule[]? or just strings?
		self.block = None
		
		self.origin = None
		self.destination = None	# Record offset in output stream
		self.scanOnly = scanOnly
		self.classes_origins = []
		self.funcs_origins = []
		
	
	#@fun addClass
	#@arg t HAULClass
	def addClass(self, t):
		if self.scanOnly:
			self.classes_origins.append(t.origin)
		else:
			self.classes.append(t)
		
	
	#@fun addFunc
	#@arg func HAULFunction
	def addFunc(self, func):
		if self.scanOnly:
			self.funcs_origins.append(func.origin)
		else:
			self.funcs.append(func)
		
	
	#@fun addImport
	#@arg imp str
	def addImport(self, imp):
		self.imports.append(imp)
		
	
	def __repr__(self):
		r = '{'
		#r = r + '"_": "Module"'
		r = r + '"name": "' + str(self.name) + '"'
		r = r + ', "classes": [' + (repr_array(self.classes)) + ']'
		r = r + ', "funcs": [' + (repr_array(self.funcs)) + ']'
		if (self.block):
			r = r + ', "block": ' + str(self.block)
		r = r + '}'
		return r
	

############################################################
############################################################
############################################################



# Controls
C_IF = '#if'
C_ELIF = '#elif'
C_ELSE = '#else'
C_FOR = '#for'
C_WHILE = '#while'
C_RETURN = '#return'
C_BREAK = '#break'
C_CONTINUE = '#continue'
C_RAISE = '#raise'

def implicitControl(controlType):
	return HAULControl(controlType)



#@var rootNamespace HAULNamespace
#@var ns HAULNamespace
rootNamespace = HAULNamespace('root', parent=None)
ns = rootNamespace

# Some things we should handle internally (or put into external library)
ns.add_id('pass', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('print', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('str', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('chr', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('ord', kind=K_FUNCTION, data_type=T_INTEGER)
ns.add_id('len', kind=K_FUNCTION, data_type=T_INTEGER)

ns.add_id('str_pos', kind=K_FUNCTION, data_type=T_INTEGER)
ns.add_id('str_compare', kind=K_FUNCTION, data_type=T_BOOLEAN)

ns.add_id('=', kind=K_FUNCTION, data_type=T_NOTHING)	# This is used for complex assignments, like dot-chains (e.g. "self.test.data[123] = ...")
ns.add_id('==', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('!=', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('>', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('<', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('>=', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('<=', kind=K_FUNCTION, data_type=T_BOOLEAN)

ns.add_id('not', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('and', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('or', kind=K_FUNCTION, data_type=T_BOOLEAN)
ns.add_id('in', kind=K_FUNCTION, data_type=T_BOOLEAN)

ns.add_id('&', kind=K_FUNCTION, data_type=T_INTEGER)
ns.add_id('|', kind=K_FUNCTION, data_type=T_INTEGER)
ns.add_id('^', kind=K_FUNCTION, data_type=T_INTEGER)

ns.add_id('+', kind=K_FUNCTION, data_type=T_INHERIT)	# Ambiguous for floats, strings, arrays!
ns.add_id('-', kind=K_FUNCTION, data_type=T_INHERIT)
ns.add_id('*', kind=K_FUNCTION, data_type=T_INHERIT)
ns.add_id('/', kind=K_FUNCTION, data_type=T_INHERIT)
ns.add_id('%', kind=K_FUNCTION, data_type=T_INHERIT)
ns.add_id('>>', kind=K_FUNCTION, data_type=T_INHERIT)
ns.add_id('<<', kind=K_FUNCTION, data_type=T_INHERIT)
#ns.add_id('+=', kind=K_FUNCTION, data_type='#incBy')
#ns.add_id('-=', kind=K_FUNCTION, data_type='#decBy')

ns.add_id('.', kind=K_FUNCTION, data_type=T_UNKNOWN)	# Or pointer / unsure?
#ns.add_id('in', kind=K_FUNCTION, data_type=T_ARRAY) # or T_BOOLEAN

ns.add_id('untyped', kind=K_TYPE, data_type=T_UNKNOWN)
ns.add_id('bool', kind=K_TYPE, data_type=T_BOOLEAN)
ns.add_id('byte', kind=K_TYPE, data_type=T_INTEGER)	# T_BYTE
ns.add_id('int', kind=K_TYPE, data_type=T_INTEGER)
ns.add_id('float', kind=K_TYPE, data_type=T_FLOAT)
ns.add_id('String', kind=K_TYPE, data_type=T_STRING)
ns.add_id('Dict', kind=K_TYPE, data_type=T_OBJECT)


ns.add_id('xrange', kind=K_FUNCTION, data_type=T_INTEGER)


#T_NONE = '#none'
ns.add_id('None', kind=K_CONST, data_type=T_NOTHING, data_value=None)
ns.add_id('True', kind=K_CONST, data_type=T_BOOLEAN, data_value=True)
ns.add_id('False', kind=K_CONST, data_type=T_BOOLEAN, data_value=False)
ns.add_id('Exception', kind=K_FUNCTION, data_type=T_OBJECT)


# Internal array functions
ns = HAULNamespace(T_ARRAY, parent=rootNamespace)
rootNamespace.add_namespace(ns)
ns.add_id('append', kind=K_FUNCTION, data_type=T_NOTHING)
I_ARRAY_SLICE = ns.add_id('slice', kind=K_FUNCTION, data_type=T_ARRAY)
I_ARRAY_LEN = ns.add_id('len', kind=K_FUNCTION, data_type=T_INTEGER)

# Internal string functions
ns = HAULNamespace(T_STRING, parent=rootNamespace)
rootNamespace.add_namespace(ns)
ns.add_id('replace', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('index', kind=K_FUNCTION, data_type=T_INTEGER)
ns.add_id('rfind', kind=K_FUNCTION, data_type=T_INTEGER)

# Internal handle functions (files, pipes, ...)
ns = HAULNamespace(T_HANDLE, parent=rootNamespace)
ns.add_id('read', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('write', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('close', kind=K_FUNCTION, data_type=T_NOTHING)
rootNamespace.add_id('open', kind=K_FUNCTION, data_type=T_HANDLE)
rootNamespace.add_namespace(ns)

# Internal Exceptions
ns = HAULNamespace('Exception', parent=rootNamespace)
rootNamespace.add_namespace(ns)
ns.add_id('message', kind=K_VARIABLE, data_type=T_STRING)


"""
# Prepare known/internal libraries
LIB_NAMESPACES = {}

# HIO
ns = HAULNamespace('hio', parent=None)
ns.add_id('put', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('put_direct', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('shout', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('get', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('int_str', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('float_str', kind=K_FUNCTION, data_type=T_STRING)
LIB_NAMESPACES['hio'] = ns
"""


# Implicit function calls. They are "so internal" that they don't need to be exposed to a global namespace, but are handled directly by the parser
implicitNamespace = HAULNamespace('#implicit', parent=None)
ns = implicitNamespace

I_VAR_SET = ns.add_id('#set', kind=K_FUNCTION, data_type=T_NOTHING)
I_ARRAY_CONSTRUCTOR = ns.add_id('#A_new', kind=K_FUNCTION, data_type=T_OBJECT)
I_ARRAY_LOOKUP = ns.add_id('#A_lookUp', kind=K_FUNCTION, data_type=T_UNKNOWN)
I_OBJECT_LOOKUP = ns.add_id('#O_lookUp', kind=K_FUNCTION, data_type=T_UNKNOWN)
I_OBJECT_CALL = ns.add_id('#O_call', kind=K_FUNCTION, data_type=T_UNKNOWN)
I_DICT_CONSTRUCTOR = ns.add_id('#D_new', kind=K_FUNCTION, data_type=T_OBJECT)
#I_UNKNOWN = HAULId('#?', ns, kind=K_CONST, data_type=T_UNKNOWN)



def implicitCall(id):
	return HAULCall(id)



TOKEN_UNKNOWN = 0
TOKEN_BLANK = 1
TOKEN_EOL = 2
TOKEN_NUM = 3
TOKEN_IDENT = 4

TOKEN_NAMES = ['unknown', 'blank', 'EOL', 'number', 'identifier']

class HAULToken:
	#@var type int
	#@var data str
	#@var originByte int
	#@var originLine int
	#@var originPos int
	
	def __init__(self, type=TOKEN_UNKNOWN, data=''):
		self.type = type
		self.data = data
		self.originByte = 0
		self.originLine = 0
		self.originPos = 0
	def __repr__(self):
		return '<HAULToken ' + TOKEN_NAMES[self.type] + ' "' + str(self.data) + '" originLine="' + str(self.originLine) + '" originPos="' + str(self.originPos) + '" />'

class HAULParseError(Exception):
	#@var message str
	#@var token HAULToken
	
	def __init__(self, message, token):
		self.message = message
		self.token = token

class HAULReader:
	#@var stream Stream
	#@var filename str
	#@var ofs int
	#@var ofsGet int
	#@var lineNum int
	#@var linePos int
	#@var peekNext HAULToken
	#@var rootNamespace HAULNamespace
	
	#@var tempNs HAULNamespace
	
	
	def __init__(self, stream, filename):
		self.stream = stream
		self.filename = filename	# For useful error messages
		
		self.ofs = 0
		self.ofsGet = 0	# Without peeks
		self.lineNum = 1
		self.linePos = 1
		self.peekNext = None
		
		#self.rootNamespace = HAULNamespace(name=filename, parent=rootNamespace)	# Root namespace
		self.rootNamespace = rootNamespace
		
		#self.annot = None	# Current annotation
		self.tempNs = None	# For storing function annotations before function actually created (forward annotation)
		
	
	# Expose/proxy stream methods
	def eof(self):
		return self.stream.eof()
	
	def loc(self):
		return self.ofsGet
	
	def seek(self, ofs):
		self.stream.seek(ofs)
		
		# Reset reader
		self.peekNext = None
		self.ofs = ofs
		self.ofsGet = ofs
		self.lineNum = -1
		self.linePos = -1
	
	def peek(self):
		return self.stream.peek()
	
	def get(self):
		r = self.stream.get()
		if r == None: return None
		
		# Update stats
		self.ofs = self.stream.ofs
		if (r == '\n'):
			self.lineNum = self.lineNum + 1
			self.linePos = 1
		else:
			self.linePos = self.linePos + 1
		return r
	
	#@fun readModule HAULModule
	def readModule(self):
		return None
	#@fun readBlock HAULBlock
	def readBlock(self):
		return None
	#@fun readClass HAULClass
	def readClass(self):
		return None
	#@fun readFunc HAULFunction
	def readFunc(self):
		return None
	#@fun readExpression HAULExpression
	def readExpression(self):
		return None
	


class HAULWriter:
	#@var streamOut Stream
	#@var defaultExtension str
	
	def __init__(self, streamOut):
		self.streamOut = streamOut
		self.defaultExtension = 'txt'
	
	def write(self, t):
		"Write to output stream."
		self.streamOut.put(t)
	
	def writeComment(self, t):
		"Add a comment to the file"
		self.streamOut.put('// ' + t + '\n')
	
	def writeModule(self, m):
		pass
	def writeClass(self, c):
		pass
	def writeFunc(self, f):
		pass
	def writeBlock(self, b):
		pass
	def writePost(self):
		"Post-process"
		pass
	
	#@fun stream
	#@arg reader HAULReader
	def stream(self, reader, namespace=None, monolithic=False):
		"Write to output stream what the reader provides. Returns the module object"
		
		#@var ns HAULNamespace
		ns = rootNamespace
		if (namespace != None): ns = namespace
		
		if monolithic:
			### Cheap (greedy: read whole input file into AST, then translate)
			m = reader.readModule(namespace=ns)
			self.writeModule(m)
		
		else:
			#@var i int
			#@var name str
			name = reader.filename.replace('.', '_')
			
			### Smart (streaming: scan input file, then seek to individual items and translate them)
			put('>>> Using Smart (streaming) translation...')
			put('Pre-processing file...')
			m = reader.readModule(name=name, namespace=ns, scanOnly=True)
			put('Done pre-processing.')
			
			put('Namespace after scanning:\n' + rootNamespace.dump())
			#m.namespace.clear()
			
			
			#Write a module sequencially, given a partially parsed (scanned) module instance containing file origins
			ns = m.namespace
			
			#@TODO: Write imports...
			
			self.writeComment('Using HAULWriter smart translation. The order of items is static for ALL languages at the moment!')
			
			#@var origin int
			
			put('Writing classes...')
			for origin in (m.classes_origins):
				put('Seeking to origin of class (' + str(origin) + ')...')
				reader.seek(origin)
				c = reader.readClass(namespace=ns)
				self.writeClass(c)
			
			put('Writing functions...')
			for origin in m.funcs_origins:
				put('Seeking to origin of function (' + str(origin) + ')...')
				reader.seek(origin)
				f = reader.readFunc(namespace=ns)
				self.writeFunc(f)
			
			put('Writing main block...')
			#ns = m.block.namespace
			origin = m.block.origin
			reader.seek(origin)
			b = reader.readBlock(namespace=ns, name=m.block.name)
			self.writeBlock(b)
			
			self.writeComment('This file might be incomplete, because smart (streaming) translation is not fully tested, yet! Use cheap (greedy) translation instead!\n')
			self.writePost()
		
		#put('Final namespace:\n' + rootNamespace.dump())
		return m
		
	

