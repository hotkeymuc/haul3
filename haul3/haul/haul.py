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

def put(t):
	print('HAUL:\t' + str(t))

def put_debug(t):
	#put(t)
	pass

def repr_array(a):
	return (', '.join([str(i) for i in a]))

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

class HAULId:
	"Unique identifier (e.g. function name, variable name, ...)"
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
	def __init__(self, name, parent, add_to_parent=True):
		put_debug('Creating new namespace "' + name + '" below "' + str(parent) + '"')
		self.ids = []
		self.name = name
		
		self.parent = parent
		self.nss = []	# Array of child namespaces
		if (add_to_parent) and (parent):
			parent.add_namespace(self)
			#parent.add_id(name=name, kind=K_NAMESPACE)
		self.origin = None
		
	def get_id(self, name, kind=None):
		"Finds the given id in this local namespace"
		for i in self.ids:
			if (i.name == name) and ((kind == None) or (i.kind == kind)): return i
		
		#raise Exception('HAULNamespace error: "' + name + '" was not found in local namespace: ' + str(self.ids))
		return None
	
	def find_id(self, name, kind=None, ignore_unknown=False):
		"Also searches upwards"
		r = self
		while not r == None:
			# Try finding it here
			#put('finding "' + str(name) + '" in namespace "' + str(r) + '"...')
			i = r.get_id(name=name, kind=kind)
			if i == None:
				# If not, search one ns upwards
				r = r.parent
			else:
				#put('found "' + str(name) + '" in namespace "' + str(r) + '"...')
				return i
		
		if not ignore_unknown:
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
		
	def find_or_create_namespace(self, name):
		for ns in self.nss:
			if ns.name == name: return ns
			
		return HAULNamespace(name=name, parent=self)
		
	def find_namespace_of(self, name, kind=None):
		"Which namespace contains name"
		r = self
		while not r == None:
			#put('finding namespace "' + str(idName) + '" in namespace "' + str(r) + '"...')
			#if r.name == idName: return r
			
			# Search direct childs
			for ns in r.nss:
				if (ns.name == name) and ((kind == None) or (ns.kind == kind)):
					return ns
				#else:	put('    != "' + str(ns) + '"')
			r = r.parent
		
		raise Exception('HAULNamespace Error: Namespace for id "' + str(name) + '" was not found starting from "' + str(self) + '"!\n' + rootNamespace.dump())
		return None
	
	def clear(self):
		self.ids = []
		self.nss = []
	
	def dump(self, level=1, skipEmpty=True):
		indent = ''
		for i in xrange(level):
			indent += '  '	#'\t'
		
		r = ''
		r += str(self.name) + '("' + str(self) + '", ' + str(len(self.ids)) + ' ids, ' + str(len(self.nss)) + ' childs):\n'
		for id in self.ids:
			r += indent + '* ' + str(id.name) + ' [' + str(id.kind) + '] = "' + str(id.data_value) + '" [' + str(id.data_type) + ']' + '\n'
			
		for ns in self.nss:
			if ((skipEmpty) and (len(ns.ids) == 0)): continue
			r += indent + '. ' + ns.dump(level+1, skipEmpty)
			
		return r
	
	def __repr__(self):
		r = ''
		if (self.parent): r += str(self.parent) + '.'
		r += str(self.name)
		return r

class HAULValue:
	"Simple value (e.g. of a variable or constant expression)"
	def __init__(self):
		self.type = None	#HAULType
		self.data = None	# binary
	
	def __repr__(self):
		if (type(self.data) is str):
			return '"' + self.data + '"'
		else:
			return str(self.data)
		
	

class HAULClass:
	"One Class declaration"
	def __init__(self, id=None):
		#@TODO: Static values?
		#@TODO: Inheritance?
		self.id = id	#HAULId(name)	#HAULId	name of module
		#self.classes = []	#HAULClass[]	Member types	e.g. classes
		self.funcs = []	#HAULFunction[]	Member functions
		#self.vars = []	#HAULVariable[]	Member variables
		#self.block = None	#HAULBlock (or HAULFunction, or self.funcs[0])
		self.namespace = None	#HAULNamespace()
		
		self.origin = None	#HAULOrigin?
		self.destination = None	# Record offset in output stream
	
	def addFunc(self, func):
		self.funcs.append(func)
	
	def __repr__(self):
		r = '{'
		#r += '"_": "Class"'
		r += '"id": "' + str(self.id) + '"'
		r += ', "vars": [' + (repr_array(self.vars)) + ']'
		r += ', "funcs": [' + (repr_array(self.funcs)) + ']'
		if (self.block): r += ', ' + str(self.block)
		r += '}'
		return r

class HAULInstruction:
	"One instruction"
	def __init__(self, call=None, control=None, comment=None):
		self.call = call	#HAULCall Iff this instruction is a function call
		self.control = control	#HAULControl	Iff this instruction is a Control Instruction
		self.comment = comment
		
		self.origin = None
		self.destination = None	# Record offset in output stream
		
	def __repr__(self):
		r = '{'
		#r += '"_": "Instruction"'
		if (self.call != None): r += '"call": ' + str(self.call)
		if (self.control != None): r += '"control": ' + str(self.control)
		r += '}'
		return r

class HAULControl:
	"Control Instruction (e.g. IF, SWITCH, WHILE, FOR, ...)"
	def __init__(self, controlType=None):
		#self.id = id	#HAULId
		self.controlType = controlType
		self.exprs = []	#HAULExpression[]	e.g. the expression used in a FOR-loop
		self.blocks = []	#HAULBlock[]	e.g. the code fragments between THEN, ELSE and ENDIF
	
	def addBlock(self, block):
		self.blocks.append(block)
	def addExpr(self, expr):
		self.exprs.append(expr)
	
	def __repr__(self):
		r = '{'
		#r += '"_": "Control"'
		r += '"controlType": "' + str(self.controlType) + '">'
		r += ', "exprs": [' + (repr_array(self.exprs)) + ']'
		r += ', "blocks": [' + (repr_array(self.exprs)) + ']'
		r += '}'
		return r

class HAULFunction:
	"Function declaration"
	def __init__(self):
		#scope = None	# if variable is a class method/function
		self.id = None	#HAULId	Function/Method name
		self.returnType = None	#HAULType	Return type
		self.args = []	#HAULVariable[]
		self.block = None	#HAULBlock	The implementation of this function, including local variables
		
		self.namespace = None	#HAULNamespace	# Use the block origin!
		self.origin = None	#HAULOrigin?
		self.destination = None	# Record offset in output stream
		
		self.user = None	# User defined, e.g. for parsing
	
	def addArg(self, arg):
		self.args.append(arg)
	
	def __repr__(self):
		r = '{'
		#r += '"_": "Function"'
		r += '"id": "' + str(self.id) + '"'
		r += ', "returnType": ' + str(self.returnType)
		r += ', "args": [' + (repr_array(self.args)) + ']'
		r += ', "block": ' + str(self.block)
		r += '}'
		return r

class HAULCall:
	"Function call"
	def __init__(self, id = None):	#, args):
		self.id = id	#HAULId	If code-scope call - or only use this?
		#builtIn = None	# If built-in function
		self.args = []	#HAULExpression[]
		#type = None	#HAULType	Return Type
		#self.args = args
		
	def getType(self):
		return self.id.data_type
	
	def __repr__(self):
		r = '{'
		#r += '"_": "Call"'
		r += '"id": "' + str(self.id) + '"'
		r += ', "args": [' + (','.join([str(v) for v in self.args])) + ']'
		r += '}'
		return r

class HAULExpression:
	"One expression of any kind."
	def __init__(self, value=None, var=None, call=None):
		#@TODO: Add Array- and Class-Field accessors!!!!
		#type = None	# can be derived from the field used!
		self.value = value	#HAULValue	Iff constant expression
		self.var = var	#HAULVariable	Iff "value-of-variable"	/	GetVar
		self.call = call	#HAULCall	Iff expression is (returnValue of) a function call
		
		self.returnType = None	#HAULType?	Return type
		
	def getType(self):
		# Guess the type of this expression
		if not self.value == None: return self.value.getType()
		if not self.var == None: return self.var.getType()
		if not self.call == None: return self.call.getType()
		put('Could not get type of expression: ' + str(self))
		return None
	
	def __repr__(self):
		r = '{'
		#r += '"_": "Expression"'
		if not self.value == None: r += '"value": ' + str(self.value)
		if not self.var == None: r += '"var": ' + str(self.var)
		if not self.call == None: r += '"call": ' + str(self.call)
		r += '}'
		return r

class HAULBlock:
	"A Block of Instructions"
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
			self.instrs_count += 1
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
		#r += '"_": "Block"'
		r += '"instrs": [' + (repr_array(self.instrs)) + ']'
		r += '}'
		return r


class HAULModule:
	"One Module of Code"
	def __init__(self, scanOnly=False):
		self.name = '?'
		
		self.namespace = None	#HAULNamespace
		
		self.classes = []	#HAULClass[]	Global types	e.g. classes (and primitives?)
		self.funcs = []	#HAULFunction[]	Global functions
		self.imports = []	#HAULModule[]? or just strings?
		self.block = None	#HAULBlock (or HAULFunction, or self.funcs[0])
		
		self.origin = None	#HAULOrigin?
		self.destination = None	# Record offset in output stream
		self.scanOnly = scanOnly
		self.classes_origins = []
		self.funcs_origins = []
		
		
	def addClass(self, t):
		if self.scanOnly:
			self.classes_origins.append(t.origin)
		else:
			self.classes.append(t)
		
	def addFunc(self, func):
		if self.scanOnly:
			self.funcs_origins.append(func.origin)
		else:
			self.funcs.append(func)
		
	def addImport(self, imp):
		self.imports.append(imp)
		
	def __repr__(self):
		r = '{'
		#r += '"_": "Module"'
		r += '"name": "' + str(self.name) + '"'
		r += ', "classes": [' + (repr_array(self.classes)) + ']'
		r += ', "funcs": [' + (repr_array(self.funcs)) + ']'
		if (self.block): r += ', "block": ' + str(self.block)
		r += '}'
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
ns.add_id('None', kind=K_CONST, data_type=T_NOTHING)
ns.add_id('True', kind=K_CONST, data_type=T_BOOLEAN)
ns.add_id('False', kind=K_CONST, data_type=T_BOOLEAN)
ns.add_id('Exception', kind=K_FUNCTION, data_type=T_OBJECT)





# Prepare known/internal libraries
LIB_NAMESPACES = {}

# HIO
ns = HAULNamespace('hio', parent=None, add_to_parent=False)
ns.add_id('put', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('put_direct', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('shout', kind=K_FUNCTION, data_type=T_NOTHING)
ns.add_id('get', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('int_str', kind=K_FUNCTION, data_type=T_STRING)
ns.add_id('float_str', kind=K_FUNCTION, data_type=T_STRING)
LIB_NAMESPACES['hio'] = ns



# Implicit function calls. They are "so internal" that they don't need to be exposed to a global namespace, but are handled directly by the parser
implicitNamespace = HAULNamespace('#implicit', parent=None, add_to_parent=False)
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

TOKEN_NAMES = [
	'unknown', 'blank', 'EOL', 'number', 'identifier'
]

class HAULToken:
	def __init__(self, type=TOKEN_UNKNOWN, data=''):
		self.type = type
		self.data = data
		self.originByte = 0
		self.originLine = 0
		self.originPos = 0
	def __repr__(self):
		return '<HAULToken ' + TOKEN_NAMES[self.type] + ' "' + str(self.data) + '" originLine="' + str(self.originLine) + '" originPos="' + str(self.originPos) + '" />'

class HAULParseError(Exception):
	def __init__(self, message, token):
		self.message = message
		self.token = token

class HAULReader:
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
		self.tempNs = None	# For storing function annotations before function actually created
		
	
	### Expose/proxy stream methods
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
			self.lineNum += 1
			self.linePos = 1
		else:
			self.linePos += 1
		return r


class HAULWriter:
	def __init__(self, streamOut):
		self.streamOut = streamOut
		self.defaultExtension = 'txt'
	
	def write(self, t):
		"Write to output stream."
		self.streamOut.put(t)
	
	def writeComment(self, t):
		"Add a comment to the file"
		self.streamOut.put('// ' + t + '\n')
	
	def stream(self, reader, monolithic=False):
		"Write to output stream what the reader provides. Returns the module object"
		
		if monolithic:
			### Cheap (greedy: read whole input file into AST, then translate)
			m = reader.readModule()
			self.writeModule(m)
		
		else:
			ns = rootNamespace
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
			
			put('Writing classes...')
			for i in xrange(len(m.classes_origins)):
				origin = m.classes_origins[i]
				put('Seeking to origin of class (' + str(origin) + ')...')
				reader.seek(origin)
				c = reader.readClass(namespace=ns)
				self.writeClass(c)
			
			put('Writing functions...')
			for i in xrange(len(m.funcs_origins)):
				origin = m.funcs_origins[i]
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
		
	
	def writePost(self):
		"Post-process"
		pass
	

