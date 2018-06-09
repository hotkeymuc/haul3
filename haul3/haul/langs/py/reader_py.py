#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from haul.core import *
from haul.utils import *

# Patterns for tokenizing Python
PAT_BLANK = [' ', '\t']
PAT_EOL = ['\n', '\r']

PAT_NUM_1 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']
PAT_NUM_N = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'x','a','b','c','d','e','f']

PAT_IDENT_1 = [
	'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
	'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
	'_'
]
PAT_IDENT_N = [
	'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
	'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
	'_'
]


PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '^',
	'>', '<', '==', '>=', '<=', '!=',
	'<<', '>>',
	'in',
]
#'+=', '-='
def is_potential_infix(t):
	# pythonic: return any(iId2 in p for p in PAT_INFIX)
	#@var p str
	for p in PAT_INFIX:
		if (p.startswith(t)): return True
	return False



# Control structures
L_IF = 'if'
L_ELIF = 'elif'
L_ELSE = 'else'
L_FOR = 'for'
L_WHILE = 'while'
L_RETURN = 'return'
L_BREAK = 'break'
L_CONTINUE = 'continue'
L_RAISE = 'raise'

# Other language stuff
L_FUNC = 'def'
L_CLASS = 'class'
L_IMPORT = 'import'
L_FROM = 'from'
L_COMMENT = '#'
L_ANNOTATION = '@'

L_SELF = 'self'
L_INIT = '__init__'
#L_NONE = 'None'


def put(t):
	print('HAULReader_py:\t' + str(t))

def put_debug(t):
	"Very verbose output"
	#put(t)
	pass

class HAULReader_py(HAULReader):
	#@var lastIfBlock arr HAULBlock
	#@var lastFunction HAULFunction
	
	def __init__(self, stream, filename):
		HAULReader.__init__(self, stream, filename)
		
		self.default_extension = 'py'
		self.lastIfBlock = [None]	# Used for ELIF handling (adding one block to a previous one)
		self.lastFunction = None	#@FIXME: Used to infer function returnType based on the type of a return statement
	
	
	def get_all_matching(self, pats):
		"Return string as long as pattern matches"
		r = ''
		c = self.peek()
		while (self.eof() == False):
			found = False
			#@var pat str
			for pat in pats:
				if (pat == c):
					found = True
					break
				
			
			if (found == False):
				break
			
			r = r + self.get()
			c = self.peek()
		return r
	
	#@fun get_next HAULToken
	def get_next(self, skip_blank=True):
		#self.ofsGet = self.ofs
		
		if (self.peekNext != None):
			r = self.peekNext
			self.peekNext = None
			return r
		
		if self.eof(): return None
		r = HAULToken()
		
		c = self.peek()
		
		if (skip_blank == True):
			while ((self.eof() == False) and (c in PAT_BLANK)):
				self.get()
				c = self.peek()
		
		r.originByte = self.stream.ofs
		r.originLine = self.line_num
		r.originPos = self.line_col
		
		# Identify tokens by their first character (this could be done much nicer and dynamically)
		if (c in PAT_BLANK):
			r.type = TOKEN_BLANK
			r.data = self.get_all_matching(PAT_BLANK)
		elif (c in PAT_EOL):
			r.type = TOKEN_EOL
			r.data = self.get_all_matching(PAT_EOL)
		elif (c in PAT_NUM_1):
			# Determine int/float
			r.type = TOKEN_UNKNOWN
			#r.data = self.get_all_matching(PAT_NUM_N)
			
			#if (not(c in PAT_NUM_N)):	# Skip it
			#	self.get()
			
			# Identify int/float/hex/...
			s = self.get()
			s = s + self.get_all_matching(PAT_NUM_N)
			
			if (s == '-'):
				put_debug('Started as a num ("' + str(c) + '"), but isnt: "' + str(s) + '" in ' + str(r))
				# Wrong
				r.type = TOKEN_UNKNOWN
				r.data = s
			else:
				if ('.' in s):
					# Float
					r.type = TOKEN_NUM_FLOAT
					#r.data = float(s)
					r.data = s
				elif ((len(s) > 2) and (s[0] == '0') and (s[1] == 'x')):
					# Convert hex to int
					r.type = TOKEN_NUM_INT
					r.data = str(int(s, 16))
				else:
					# int
					r.type = TOKEN_NUM_INT
					r.data = s
					
				
			
		elif (c in PAT_IDENT_1):
			r.type = TOKEN_IDENT
			r.data = self.get_all_matching(PAT_IDENT_N)
		else:
			r.data = self.get()
		
		#put_debug(str(r))
		return r
	
	
	#@fun peek_next HAULToken
	def peek_next(self, skip_blank=True):
		if (self.peekNext == None):
			self.peekNext = self.get_next(skip_blank=skip_blank)
		return self.peekNext
	
	def peek_assert_data(self, check, msg):
		t = self.peek_next()
		if (t.data != check):
			self.raise_parse_error(msg, t)
		return t
	def get_assert_data(self, check, msg):
		t = self.peek_assert_data(check, msg)
		self.get_next()
		return t
	def peek_assert_type(self, check, msg):
		t = self.peek_next()
		if (t.type != check):
			self.raise_parse_error(msg, t)
		return t
	def get_assert_type(self, check, msg):
		t = self.peek_assert_type(check, msg)
		self.get_next()
		return t
	
	#@fun read_line str
	def read_line(self, skip_blank=False):
		l = ''
		t = self.get_next(skip_blank=skip_blank)
		if (t == None): return l
		
		l = l + str(t.data)
		c = self.peek()
		while ((c in PAT_EOL) == False) and (self.eof() == False):
			l = l + self.get()
			c = self.peek()
		return l
	
	def type_by_string(self, t):
		if   (t == 'None'): return T_NOTHING
		elif (t == 'int'): return T_INTEGER
		elif (t == 'float'): return T_FLOAT
		elif (t == 'str'): return T_STRING
		elif (t == 'bool'): return T_BOOLEAN
		elif (t == 'obj'): return T_OBJECT
		elif (t == 'arr'): return T_ARRAY	#@TODO: of which type?
		else:
			put_debug('Assuming "' + str(t) + '" is a class name, interpreting as type')
			return str(t)
		#return T_UNKNOWN
		
	
	def read_type(self, namespace):
		t = self.get_next()
		return self.type_by_string(t.data)
	
	#@fun read_var_def HAULId
	#@arg namespace HAULNamespace
	def read_var_def(self, namespace):
		t = self.get_next()
		#v = HAULVariable()
		#v.origin = self.loc()
		#v.token = t
		
		t2 = self.peek_next()
		i = None
		if (t2.data == ':'):
			# Type hinting (Python3 style)
			t2 = self.get_next()
			typ = self.read_type(namespace=ns)
			i = namespace.add_id(name=t.data, kind=K_VARIABLE, data_type=typ, origin=self.loc())
		else:
			i = namespace.find_id(name=t.data, kind=K_VARIABLE, ignore_unknown=True)
			#i = namespace.get_id(name=t.data, kind=K_VARIABLE)
		
		if (i == None):
			put_debug('Yet unknown argument "' + str(t.data) + '" may be inferred.')
			i = namespace.add_id(name=t.data, kind=K_VARIABLE, data_type=T_UNKNOWN, origin=self.loc())
		
		return i
	
	#@fun read_annotation str
	#@arg namespace HAULNamespace
	def read_annotation(self, namespace):
		self.get_next()	# Skip "@"
		
		t = self.peek_next()
		
		comment = self.read_line()
		put_debug('read_annotation(): "' + str(comment) + '"')
		
		ns = namespace
		
		# Annotations
		d = ' '
		parts = comment.split(d)
		
		if (parts[0] == K_FUNCTION):
			put_debug('read_annotation():	Creating temporary namespace for function annotation inside ns=' + str(namespace))
			self.tempNs = namespace.get_or_create_namespace(parts[1])
			
			# Auto-add return type
			if (len(parts) > 2):
				#self.tempNs.add_id(name=A_RETTYPE, kind=K_VARIABLE, data_type=self.type_by_string(parts[2]), origin=self.loc())
				namespace.add_id(name=parts[1], kind=K_FUNCTION, data_type=self.type_by_string(parts[2]), origin=self.loc(), overwrite=True)
			
		elif (parts[0] == A_ARGUMENT):
			# Arguments need to be declared in a forward manner, that's why a "temporary namespace" is used which is checked on function declaration
			if (self.tempNs == None):
				self.raise_parse_error('Argument annotation without matching function annotation', t)
			
			if (len(parts) < 3):
				self.raise_parse_error('Incomplete argument annotation: "' + str(comment) + '"', t)
			
			#self.tempNs.add_id(name=parts[1], kind=K_ARGUMENT, data=parts[2], origin=self.loc())
			self.tempNs.add_id(name=parts[1], kind=K_VARIABLE, data_type=self.type_by_string(parts[2]), origin=self.loc())
			
			# Also add to parent ns (needed for streaming, so we know the function arguments from within the parent declaration)
			#ns.add_id(name=parts[1], kind=K_ARGUMENT, data=parts[2] + ' (redundant argument declaration in parent namespace)')
			
			
		elif (parts[0] == K_VARIABLE):
			put_debug('Var annotation: ' + str(parts))
			if (len(parts) < 3):
				self.raise_parse_error('Incomplete variable annotation: "' + str(comment) + '"', t)
			ns.add_id(name=parts[1], kind=K_VARIABLE, data_type=self.type_by_string(parts[2]), origin=self.loc(), overwrite=True)
			
		elif (parts[0] == K_CONST):
			#put('Const annotation: ' + str(parts))
			if (len(parts) < 4):
				self.raise_parse_error('Incomplete const annotation: "' + str(comment) + '"', t)
			ns.add_id(name=parts[1], kind=K_CONST, data_type=self.type_by_string(parts[2]), data_value=parts[3], origin=self.loc())
		
		self.get_next()	# Skip EOL
		return comment
	
	def read_args(self, namespace, bracket=')'):
		"Read argument list"
		r = []
		t = self.peek_next()
		
		while ((self.eof() == False) and (t.type == TOKEN_EOL)):
			self.get_next()
			t = self.peek_next()
		
		while ((self.eof() == False) and (t.data != bracket)):
			
			#@TODO: When reading call arguments we need to look inside the functions namespace for the names of the args
			# In the meantime we use "allow_undefined=True" to allow inferring
			#r.append(self.read_expression(namespace=namespace_target, namespaceLocal=namespace))
			r.append(self.read_expression(namespace=namespace, allow_undefined=True))
			
			t = self.peek_next()
			
			# Default value?
			if (t.data == '='):
				#put('function argument with default value!')
				self.get_next()
				
				e_val = self.read_expression(namespace=namespace)
				
				#@FIXME: Put this information into the namespace! Mark this argument as "optional"
				put('Not yet implemented: Skipping default value for arg: ' + str(e_val))
				t = self.peek_next()
			
			
			# Skip comma
			if (t.data == ','):
				self.get_next()
				t = self.peek_next()
			
			while ((self.eof() == False) and (t.type == TOKEN_EOL)):
				self.get_next()
				t = self.peek_next()
			
			
			# Until brackets closed
		#self.get_next()	# Skip trailing bracket
		self.get_assert_data(bracket, 'Expected ending bracket "' + bracket + '"')
		#put('args=' + str(r))
		return r
		#return copy.copy(r)
	
	def read_dict(self, namespace):
		"Read dict entries"
		r = []
		t = self.peek_next()
		#while (self.eof() == False) and (not t.data == ')'):
		while ((self.eof() == False) and (t.data != '}')):
			put_debug('Reading dict key...')
			r.append(self.read_expression(namespace=namespace))
			
			self.get_assert_data(':', 'Expected colon for dict')
			put_debug('Reading dict value...')
			
			r.append(self.read_expression(namespace=namespace))
			
			t = self.peek_next()
			
			# Skip comma
			if (t.data == ','):
				self.get_next()
				t = self.peek_next()
			# Skip comment
			while ((t.type == TOKEN_UNKNOWN) and (t.data[0] == L_COMMENT)):
				comment = self.read_line()
				self.get_next()
				t = self.peek_next()
				#put('next token: ' + str(t))
			
			# Until brackets closed
		#self.get_next()	# Skip trailing bracket
		#put('args=' + str(r))
		return r
		#return copy.copy(r)
	
	#@fun read_expression HAULExpression
	#@arg namespace HAULNamespace
	#@arg namespaceLocal HAULNamespace
	def read_expression(self, namespace, checkInfix=True, checkCall=True, namespaceLocal=None, allow_undefined=False):
		#put('read_expression() in ' + str(namespace))
		
		#@var e HAULExpression
		e = HAULExpression()
		e.origin = self.loc()
		e.returnType = '?'
		
		t = self.get_next()
		put_debug('read_expression():	ns=' + str(namespace) + ' t=' + str(t))
		#e.token = t
		ns = namespace
		
		#@var v HAULId
		
		# Determine type of expression
		if (t.data == '('):
			put_debug('sub-expression (brackets)')
			e = self.read_expression(namespace=ns)	# Spawn...
			put_debug('end of sub-expression(s)')
			
			self.get_assert_data(')', 'Expected closing bracket which started at ' + str(t))	# Check and skip trailing bracket
			
		elif (t.data == '['):
			put_debug('array constructor')
			
			#self.get_next()	# Skip bracket
			e.call = implicitCall(I_ARRAY_CONSTRUCTOR)
			e.returnType = T_ARRAY
			
			t2 = self.peek_next()
			if (t2.data != ']'):
				e.call.args = self.read_args(namespace=ns, bracket=']')
				#t2 = self.peek_next()
			else:
				#self.raise_parse_error('Expected closing array bracket', t2)
				self.get_next()	# Skip trailing bracket
				
			
		elif (t.data == '{'):
			put_debug('Dict constructor')
			e.call = implicitCall(I_DICT_CONSTRUCTOR)
			e.returnType = T_DICT
			
			e.call.args = self.read_dict(namespace=ns)
			self.get_next()	# Skip trailing bracket
			put_debug('dict returned: ' + str(e.call.args))
			
			
		elif ((t.data == '"') or (t.data == "'")):
			# Read string
			#put('string')
			
			e.value = HAULValue(T_STRING, data_str='')
			e.returnType = e.value.type
			
			delimiter = t.data
			escape = False
			c = ''
			while (self.eof() == False):
				c = self.get()
				if (c == delimiter): break
				if (c == '\\'):
					c = self.get()
					if (c == 'n'): c = '\n'
					elif (c == 'r'): c = '\r'
					elif (c == 't'): c = '\t'
				e.value.data_str = e.value.data_str + c
			
			# Check for triple quotes
			t2 = self.peek_next()
			if ((e.value.data_str == '') and (t2.data == t.data)):
				put_debug('Triple quote!')
				# Scan until line that only consists of triple quote
				tq = t.data + t.data + t.data
				t = ''
				while (t[0:3] != tq):
					self.get_next()
					t = self.read_line()
					put_debug('Block comment: Skipping line "' + tq + '" != "' + t + '"')
					e.value.data_str = e.value.data_str + t
					
				put_debug('End of triple quote')
			
		elif (t.type == TOKEN_EOL):
			#self.get_next()	# Skip Character
			e = self.read_expression(namespace=ns)
			
		elif (t.type == TOKEN_NUM_INT):
			e.value = HAULValue(T_INTEGER, data_int=int(t.data))
			e.returnType = e.value.type
		elif (t.type == TOKEN_NUM_FLOAT):
			e.value = HAULValue(T_FLOAT, data_float=float(t.data))
			e.returnType = e.value.type
		elif (t.type == TOKEN_IDENT):
			# Determine if var or call... Normally you would check the identifiers. But let's simply check for an open bracket...
			t2 = self.peek_next()
			
			#@TODO: Handle multiple brackets, like test[4][3](123)[2,2]()
			if ((t2 != None) and (checkCall == True) and (t2.data == '(')):
				# Call!
				put_debug('call...')
				# Skip bracket
				self.get_next()
				
				e.call = HAULCall()	
				
				e.call.id = ns.find_id(t.data, ignore_unknown=True)
				if (e.call.id == None):
					self.raise_parse_error('Unknown call to "' + str(t.data) + '"', t)
				
				if (e.call.id.kind == K_CLASS):
					# Use class name as type
					e.returnType = e.call.id.name
				else:
					e.returnType = e.call.id.data_type
				
				# Check for class instantiation
				if (e.call.id.kind == K_CLASS):
					#put('Instantiation of class ' + e.call.id.name + ', need to call the __init__ function')
					#@TODO: We could explicitly add a call to the __init__ function
					pass
					
				
				#@TODO: Shift namespace to the call so we can handle named arguments
				#ns_target = e.call.id.namespace
				
				#, namespace_target=ns_target)
				e.call.args = self.read_args(namespace=ns, bracket=')')
				
			
			elif (t2.data == '['):
				# Array look-up
				put_debug('Array look-up on ' + str(t) + '...')
				# Skip bracket
				self.get_next()
				
				# Wrap current expression
				e.call = implicitCall(I_ARRAY_LOOKUP)
				
				# Find base variable
				if (namespaceLocal != None):
					v = namespaceLocal.find_id(t.data)
				else:
					v = ns.find_id(t.data)
				
				e_var = HAULExpression(var=v)
				
				# Construct slice
				
				# Check start of slice
				t = self.peek_next()
				if (t.data == ':'):
					e.call.id = I_ARRAY_SLICE
					# Start omitted, use 0
					e_index = HAULExpression(value=0)
				else:
					e_index = self.read_expression(namespace=ns)
				
				
				e.call.args = [
					e_var,
					e_index
				]
				
				#@FIXME: Need to return the array base type!
				e.returnType = v.data_type	# This might result in "array", but we need the array base type!
				#v.data_array_type
				
				# Check end of slice
				t = self.peek_next()
				if (t.data == ':'):
					put_debug('Array slicing...')
					self.get_next() # Consume
					#e.call = implicitCall(I_ARRAY_SLICE)
					e.call.id = I_ARRAY_SLICE
					
					t = self.peek_next()
					if (t.data == ']'):
						# End omitted: Insert implicit I_ARRAY_LEN
						e_index2 = HAULExpression(call=implicitCall(I_ARRAY_LEN))
						e_index2.call.args.append(e_var)
					else:
						e_index2 = self.read_expression(namespace=ns)
					e.call.args.append(e_index2)
				
				self.get_assert_data(']', 'Expected closing "]" bracket after index')
				
			elif (t2.data == '.'):
				# Object look-up
				put_debug('Object look-up... ' + str(t) + ' in ' + str(namespace) + ' / ' + str(namespaceLocal))
				self.get_next()	# Skip dot
				
				e.call = implicitCall(I_OBJECT_LOOKUP)
				
				#@var e_object HAULExpression
				e_object = HAULExpression()
				#v = HAULVariable()
				#v.id = ns.find_id(t.data)
				
				v = None
				
				# Try local one first
				if (namespaceLocal != None):
					v = namespaceLocal.find_id(t.data, ignore_unknown=True)
				
				if (v == None):
					v = ns.find_id(t.data, ignore_unknown=True)
				
				if (v == None) or (v.data_type == T_UNKNOWN):
					self.raise_parse_error('Object lookup failed, because "' + str(t.data) + '" is unknown at ' + str(ns), t)
				
				e_object.var = v
				e_object.returnType = v.data_type
				
				# When doing a object look-up, the name space shifts to the looked-up value. Alternatively we could store it as "run-time look-up/late binding"
				put_debug('Variable "' + str(v.name) + '" is a ' + str(v.kind)+ ' of type "' + str(v.data_type) + '". Shifting namespace for object look-up...')
				
				#@var ns_shifted HAULNamespace
				
				#if (v.data_type == T_CLASS):
				if (v.kind == K_CLASS):
					put_debug('Calling method of a class type - static access!')
					ns_shifted = v.namespace
					
				elif (v.kind == K_MODULE):
					#put_debug('"{}" is a module, shifting into...'.format(v.name))
					ns_shifted = ns.find_namespace(v.name)
					
				else:
					ns_shifted = ns.find_namespace_of(v.data_type)
				
				if (ns_shifted == None):
					self.raise_parse_error('Object lookup for "' + str(v.name) + '" failed, because namespace for kind "' + str(v.kind) + '", type "' + str(v.data_type) + '" is unknown at ' + str(ns), t)
				
				
				# Normal call
				#put_debug('Using local namespace ("' + str(ns_shifted) + '") for finding target ids...')
				# Use local namespace for further resolution of ids
				#self.read_expression(namespace=ns_shifted, checkInfix=False, checkCall=False)	# the field identifier can not be a function call itself and may not contain infixes
				e_member = self.read_expression(namespace=ns, namespaceLocal=ns_shifted, checkInfix=False, checkCall=False)
				
				e.call.args = [
					e_object,
					e_member
				]
				
				# Use the return value of that member
				e.returnType = e_member.returnType
				
				t2 = self.peek_next()
				#@TODO: Handle multiple brackets, like test[4][3](123)[2,2]()
				if (t2.data == '('):
					# (method) Call! Convert the look-up into a call(look-up, params...)
					put_debug('Object-lookup (method) call...')
					self.get_next()	# Skip bracket
					
					e_lookup = e
					
					# Create new outer expression
					e = HAULExpression()
					
					c_invoke = implicitCall(I_OBJECT_CALL)
					
					# Merge lookup and actual arguments
					c_invoke.args = [e_lookup]
					args = self.read_args(namespace=ns, bracket=')')
					#@var arg HAULExpression
					for arg in args:
						c_invoke.args.append(arg)
					#self.get_next()	# Skip bracket
					e.call = c_invoke
					e.origin = e_lookup.origin
					e.returnType = e_member.returnType
					
			else:
				# Var
				#put('var...')
				# Find the variable (or at least try)
				
				v = None
				if (namespaceLocal != None):
					ns2 = namespaceLocal
					v = ns2.find_id(t.data, ignore_unknown=True)
				
				if (v == None):
					ns2 = namespace
					v = ns2.find_id(t.data, ignore_unknown=True)
				
				if (v == None):
					# Variable/id was not found
					ns2 = namespace
					
					if (allow_undefined):
						put_debug('Yet unknown id "' + str(t.data) + '", may be inferred.')
						# Add to-be-inferred variable
						v = ns2.add_id(name=t.data, kind=K_VARIABLE, data_type=T_UNKNOWN, origin=self.loc())
						
					else:
						self.raise_parse_error('Undefined id "' + str(t.data) + '" at ' + str(ns2), t)
						
				
				e.var = v
				
				if (e.var.data_type == T_CLASS):
					# Use class name instead
					e.returnType = e.var.name
				else:
					e.returnType = e.var.data_type
				
			
		else:
			self.raise_parse_error('Unexpected token for an expression', t)
		
		# Check for trailing infix
		if (checkInfix == True):
			
			t2 = self.peek_next()
			
			#if (t2) and any(t2.data in p for p in PAT_INFIX):
			if (t2) and (is_potential_infix(t2.data)):
				# Yes,  there is a trailing infix
				iId = t2.data
				
				# Try longer infixes
				iId2 = iId
				while (is_potential_infix(iId2)):
					iId = iId2
					self.get_next()	# Skip old char, its stored in iId
					
					# Next letter
					t2 = self.peek_next()
					iId2 = iId2 + str(t2.data)
				
				#put('Longest infix found: "' + iId + '", next up: ' + str(t2))
				
				e_right = self.read_expression(namespace=ns)
				
				# Wrap current expression
				#@var eNew HAULExpression
				eNew = HAULExpression()
				eNew.call = HAULCall()
				eNew.call.id = ns.find_id(iId)
				
				# Check if we can chain multiple "+" operations together
				if ((iId == '+') and (e_right.call) and (e_right.call.id.name == '+')):
					put_debug('Chaining infixed "+" terms together')
					
					eNew.call.args.append(e)
					
					#@var ea HAULExpression
					for ea in e_right.call.args:
						eNew.call.args.append(ea)
					
				else:
					# Clone old left side
					e_left = HAULExpression(value=e.value, var=e.var, call=e.call)
					e_left.returnType = e.returnType
					
					eNew.call.args = [
						e_left,
						e_right
					]
				
				# Determine type of it (type inference)
				#@TODO: Search for the widest type
				#@FIXME: Just look in the internal namespace. The return value is stored there (T_INHERIT, T_BOOLEAN, ...)
				if (iId in ['+', '-', '*', '/', 'and', 'or', 'not']):
					#if (e_left.returnType == e_right.returnType):
					#	Return type of first
					eNew.returnType = e.returnType
					#else:
					#	@TODO: Return the WIDER one, maybe insert a call to an internal cast-function
					
				elif (iId in ['>', '<', '==', '!=', '<=', '>=']):
					# Comparisons return a boolean value
					eNew.returnType = T_BOOLEAN
				else:
					# Maybe the call itself has a return type?
					eNew.returnType = eNew.call.id.data_type
				
				t2 = self.peek_next()
				#put('End of trailing infix argument and outer expression. Next: ' + str(t2))
				
				return eNew
		
		return e
	
	#@fun read_instruction HAULInstruction
	#@arg namespace HAULNamespace
	#@arg module HAULModule
	def read_instruction(self, namespace, scan_only=False, module=None):
		#put_debug('read_instruction()')
		i = HAULInstruction()
		i.origin = self.loc()
		
		# Skip until next instruction is found
		t = self.peek_next()
		put_debug('read_instruction() Seeking next identifier starting at ' + str(t))
		qs = 0
		while (t.type != TOKEN_IDENT):
			#put('Skipping to next identifier, skipping "' + t.data + '"...')
			self.get_next()
			if (t.data[0] == L_COMMENT):
				self.read_annotation(namespace=namespace)
			
			elif (t.data == '"'): qs = qs + 1
			else: qs = 0
			
			if (qs == 3):
				put_debug('Skipping triple block quote')
				
				# Skip triple quote
				qs = 0
				while (qs < 3):
					c = self.get()
					if (c == '"'): qs = qs + 1
					else: qs = 0
				qs = 0
			
			t = self.peek_next()
		
		t = self.peek_assert_type(TOKEN_IDENT, 'Expected identifier at start of instruction')
		ns = namespace
		#i.token = t
		
		
		# Control instructions
		#@var ctrl HAULControl
		ctrl = None
		
		if (t.data == L_IF) or (t.data == L_ELIF) or (t.data == L_ELSE):
			put_debug('IF block(s) start...' + str(t))
			
			if (t.data == L_ELIF) or (t.data == L_ELSE):
				ctrl = self.lastIfBlock[-1]
				i = None	# Do not create a new one!
			else:
				ctrl = implicitControl(C_IF)
				self.lastIfBlock[-1] = ctrl
				
			
			#@FIXME: This might not work right
			while (t.data == L_IF) or (t.data == L_ELIF):
				put_debug('if/elif block in ns=' + str(ns) + '	' + str(t))
				self.get_next()	# Ok, digest
				
				# read condition
				ctrl.add_expression(self.read_expression(namespace=ns))
				
				t = self.get_assert_data(':', 'Expected ":" after if-expression')
				# read block
				ctrl.add_block(self.read_block(namespace=ns, blockName='__ifBlock' + str(self.loc())))
				
				
				#@FIXME The end of elif is not clean. Often times, the class it is in gets falsely terminated here!
				t = self.peek_next()
			
			
			if (t.data == L_ELSE):
				put_debug('ELSE block ' + str(t))
				self.get_next()	# Skip "else"
				t = self.get_assert_data(':', 'Expected ":" after else-expression')
				ctrl.add_block(self.read_block(namespace=ns, blockName='__elseBlock' + str(self.loc())))
			
			if (i):
				i.control = ctrl
			put_debug('IF/ELIF/ELSE control end.')
		
		elif (t.data == L_FOR):
			self.get_next()	# Ok, digest
			
			ctrl = implicitControl(C_FOR)
			
			# read expression and block
			e_iter = self.read_expression(namespace=ns)
			
			# Only support "in"
			if ((e_iter.call == None) or (e_iter.call.id.name != 'in') or (len(e_iter.call.args) != 2)):
				self.raise_parse_error('Only "X in Y" is supported as iterator in for loops', t)
			
			# Transform
			ctrl.add_expression(e_iter.call.args[0])
			ctrl.add_expression(e_iter.call.args[1])
			
			t = self.get_assert_data(':', 'Expected ":" after for-syntax')
			
			ctrl.add_block(self.read_block(namespace=ns, blockName='__forBlock' + str(self.loc())))
			
			i.control = ctrl
			
		elif (t.data == L_WHILE):
			self.get_next()	# Ok, digest
			
			ctrl = implicitControl(C_WHILE)
			
			# read expression and block
			ctrl.add_expression(self.read_expression(namespace=ns))
			
			t = self.get_assert_data(':', 'Expected ":" after while-syntax')
			
			ctrl.add_block(self.read_block(namespace=ns, blockName='__whileBlock' + str(self.loc())))
			
			i.control = ctrl
			
			
		elif (t.data == L_BREAK):
			self.get_next()	# digest
			i.control = implicitControl(C_BREAK)
			
		elif (t.data == L_CONTINUE):
			self.get_next()	# digest
			i.control = implicitControl(C_CONTINUE)
			
		elif (t.data == L_RETURN):
			self.get_next()	# digest
			
			ctrl = implicitControl(C_RETURN)
			
			t = self.peek_next()
			if (t.type != TOKEN_EOL):
				# Handle empty returns
				
				# read expression to return
				e = self.read_expression(namespace=ns)
				ctrl.add_expression(e)
				
				# The returnType of that expression can be used to infer function returnType
				# Find closest returnType namespace entry
				
				#@var iret HAULId
				if (BLOCKS_HAVE_LOCAL_NAMESPACE == True):
					iret = namespace.find_id(A_RETTYPE, ignore_unknown=True)
					
				else:
					# Assume the current namespace is called like the function we are in
					iret = namespace.find_id(namespace.name, ignore_unknown=True)
					
				
				if ((INFER_TYPE) and (e.returnType != T_UNKNOWN) and (iret != None) and (iret.data_type == T_UNKNOWN)):
					put_debug('Inferring return type "' + str(e.returnType) + '" for function "' + str(iret) + '" from return statement')
					iret.data_type = e.returnType
					self.lastFunction.returnType = e.returnType
					
				
			
			i.control = ctrl
			
		elif (t.data == L_RAISE):
			self.get_next()	# Ok, digest
			ctrl = implicitControl(C_RAISE)
			# read expression to return
			ctrl.add_expression(self.read_expression(namespace=ns))
			i.control = ctrl
			
		
		#elif (t.data == L_FUNC): self.raise_parse_error('HAULParseError: Cannot use inline functions, yet. Please put them before any main-block instruction ', t)
		#elif (t.data == L_CLASS): self.raise_parse_error('HAULParseError: Cannot use inline classes, yet. Please put them before any main-block instruction ', t)
		elif (t.data == L_FUNC):
			put_debug('read_module():	reading root function block...')
			module.addFunc(self.read_function(namespace=namespace, scan_only=scan_only))
			
		elif (t.data == L_CLASS):
			put_debug('read_module():	reading root class block...')
			module.add_class(self.read_class(namespace=namespace, scan_only=scan_only))
		
		else:
			# Custom instruction (function call or variable access)
			put_debug('Custom function call or assignment: ' + str(t))
			
			# Let "read_expression" consume the token as the "left side"
			e = self.read_expression(namespace=ns, checkInfix=False, allow_undefined=INFER_TYPE)	# We only accept var/identifier, but may infer some stuff
			
			#put('Instruction starts with: ' + str(e))
			
			# Check for Variable-assignment instruction (else this is just a call)
			t2 = self.peek_next()
			
			#@FIXME: This check won't recognize dot-chains like "self.test[123] = ..." as a var-set! Instead it will think the "=" is an infix
			
			#@TODO: Check for +=, -=, *=, /=, ...
			
			if (t2 != None) and (t2.data == '='):
				put_debug('Set variable...')
				self.get_next()	# Consume "="
				
				i.call = implicitCall(I_VAR_SET)
				
				# Read the "right side"
				e_right = self.read_expression(namespace=ns, allow_undefined=False)
				
				# Type inference
				if (INFER_TYPE) and (e.var != None) and (e.returnType == T_UNKNOWN):
					put_debug('Inferring type "' + e_right.returnType + '" for variable "' + str(e.var) + '"')
					e.var.kind = K_VARIABLE
					e.var.data_type = e_right.returnType
				
				
				i.call.args = [
					e,
					e_right
				]
				
				# Check if variable is a K_CONST
				if (e.var != None):
					if (e.var.kind == K_CONST):
						if ((e.var.data_type != T_UNKNOWN) and (e.var.data_type != None)):
							#@TODO: It may have been annotated, so check if the value differs
							put_debug('Re-setting constant ' + str(e.var) + ' which already has a value!')
							pass
						
						if (e_right.value == None):
							self.raise_parse_error('Constant ' + str(e.var) + ' can only be assigned a value, not a ' + str(e_right), t)
						# Set constant value
						e.var.data_value = e_right.value
						e.var.data_type = e_right.returnType
					
				
			else:
				# Just a call
				i.call = e.call
		return i
		#return copy.copy(i)
	
	#@fun read_block HAULBlock
	#@arg namespace HAULNamespace
	#@arg module HAULModule
	def read_block(self, namespace, scan_only=False, blockName='__someBlock', module=None):
		put_debug('read_block()...')
		b = HAULBlock(scan_only=scan_only)
		b.origin = self.loc()
		#put(self.line_num)
		b.name = blockName
		
		if (BLOCKS_HAVE_LOCAL_NAMESPACE == True):
			# Option A: Introduce dedicated namespace for local values
			ns  = namespace.get_or_create_namespace(blockName)
			b.namespace = ns	# Write all new entries inside this block to the block namespace (better, i.e. for Java)
		else:
			# Option B: Re-use parent namespace
			#b.namespace = None
			ns = namespace	# Write all new entries to the parent namespace (simpler)
		
		self.lastIfBlock.append(None)	# Stack it up, remove it afterwards
		
		# Skip initial EOL
		
		# Check this block's indentation level
		#@var indent int
		
		t = self.peek_next(skip_blank=False)
		while (self.eof() == False) and (t.type == TOKEN_EOL):
			self.get_next(skip_blank=False)
			t = self.peek_next(skip_blank=False)
		
		t = self.peek_next(skip_blank=False)
		if (t.type != TOKEN_BLANK):
			#self.raise_parse_error('Expected initial indent blanks', t)
			indent = 0
		else:
			indent = len(t.data)
		#put('read_block():	Initial blank level: ' + str(indent))
		
		b.instrs = []
		
		# Parse instructions until blank length changes
		# I expect t to be the current indentation token (or first instruction if at root level)
		while ((self.eof() == False) and ((indent == 0) or ((t.type == TOKEN_BLANK) and (len(t.data) == indent)))):
			
			if (t.type == TOKEN_BLANK):
				self.get_next()	# Skip current BLANK indent
			elif (indent == 0):
				# Do not expect to have a blank in root level
				pass
			else:
				self.raise_parse_error('Expected to be at an indentation (' + str(indent) + '), but I am not!', t)
			
			
			t = self.peek_next()
			#put('read_block()...	t=' + str(t))
			
			if (t.type == TOKEN_EOL):
				# Empty line
				pass
			
			elif (t.type == TOKEN_UNKNOWN) and (t.data[0] == L_COMMENT):
				# Comments at start of line
				# Consume comment token
				self.get_next()
				t = self.peek_next()
				if ((t.type == TOKEN_UNKNOWN) and (t.data[0] == L_ANNOTATION)):
					self.read_annotation(namespace=ns)
					
				else:
					comment = self.read_line()
					put_debug('read_block():	Comment: "' + str(comment) + '"')
					b.add_comment(comment)
			
			elif (t.type == TOKEN_UNKNOWN) and ((t.data[0] == '"') or (t.data[0] == "'")):
				# Block-level string is a block comment
				#comment = self.read_line()
				
				# Treat it as a string expression
				e = self.read_expression(namespace=ns)
				if (e.value.type != T_STRING):
					self.raise_parse_error('Expected comment to be a string value, but got "' + str(e) + '"', t)
				
				comment = e.value.data_str
				put_debug('read_block():	Doc Comment: "' + str(comment) + '"')
				b.add_comment(comment)
			
			else:
				# Read instruction
				i = self.read_instruction(namespace=ns, module=module)
				
				#t = self.peek_next(skip_blank=False)
				#put('After read_instruction we are at ' + str(t))
				
				if (i != None):
					b.add_instruction(i)
				else:
					# May be last mega-indented statement of block
					# Do not break! It may also be an elif block that was able to add its contents to a previous instruction!
					t = self.peek_next(skip_blank=False)
					put_debug('No (new) instruction could be read. Might be recovered elif block or indentation error at ' + str(t))
					#break
				
				
				
				# Comments at end of line
				t = self.peek_next(skip_blank=False)
				if ((indent == 0) and (t != None) and (len(t.data) > 0) and (t.data[0] == L_COMMENT)):
					#This check is needed. Or else it may SKIP an annotation that is following an end-of-block at root-level.
					pass
				else:
					
					#@FIXME: This seems weird...
					
					t = self.peek_next()
					while (self.eof() == False) and (t.data[0] == L_COMMENT):
						if (i.comment == None): i.comment = ''
						else: i.comment = i.comment + '\n'
						i.comment = i.comment + self.read_line()
						t = self.peek_next()
					#
				#
			
			# Skip EOL...
			t = self.peek_next(skip_blank=False)
			while (self.eof() == False) and (t.type == TOKEN_EOL):
				self.get_next(skip_blank=False)
				t = self.peek_next(skip_blank=False)
			# I am now at the beginning of a new line/end of block
		
		put_debug('read_block() End of block ' + str(b.name) + ' at ' + str(self.peek_next()))
		if (self.eof() == False) and (t.type == TOKEN_BLANK) and (len(t.data) != indent):
			put_debug('...because expected indent=' + str(indent) + ', while actually=' + str(len(t.data)) + ' at ' + str(t))
		
		self.lastIfBlock.pop()	# Restore lastIfBlock-stack
		
		return b
		#return copy.copy(b)
	
	#@fun read_function HAULFunction
	#@arg namespace HAULNamespace
	def read_function(self, namespace, scan_only=False):
		put_debug('read_function()')
		
		f = HAULFunction()
		f.origin = self.loc()
		self.lastFunction = f
		
		t = self.get_assert_data(L_FUNC, 'Expected "' + L_FUNC + '"')
		
		# Function name
		t = self.get_next()
		
		# Get return type from previous annotation
		i = namespace.get_id(t.data)
		if (i != None):
			if i.kind != K_FUNCTION:
				self.raise_parse_error('read_function(): Function name "' + str(t.data) + '" is already defined as a non-function: ' + str(i), t)
			put_debug('Function "' + str(t.data) + '" is already known (either from import or annotation)')
		else:
			# Function is yet unknown
			i = namespace.add_id(t.data, kind=K_FUNCTION, data_type=T_UNKNOWN, origin=self.loc())
		
		f.id = i
		if (i.data_type == T_CLASS):
			# Return class name
			f.returnType = i.name
		else:
			f.returnType = i.data_type
		f.id.data_function = f
		
		
		if (self.tempNs):
			# Use the annotated one
			put_debug('Using annotated temp namespace...')
			f.namespace = self.tempNs
			#f.origin = self.tempNs.origin	# Shift to include the origin of the annotation!
			self.tempNs = None
		else:
			# Create new one / Re-use
			#if (scan_only):	f.namespace = HAULNamespace(name=t.data, parent=namespace)
			#else:			f.namespace = namespace.findNamespace(t.data)
			f.namespace = namespace.get_or_create_namespace(f.id.name)
		
		# Everything else goes into the functions own namespace
		ns = f.namespace
		
		# Use parent namespace
		#ns = namespace
		
		
		# open bracket
		self.get_assert_data('(', 'Expected argument list brackets')
		
		# Read argument definitions
		t = self.peek_next()
		while (self.eof() == False) and (t.data != ')'):
			#@var vd HAULId
			vd = self.read_var_def(namespace=ns)
			
			#put('Argument was defined as ' + str(vd))
			t = self.peek_next()
			
			# Default value (not yet implemented)
			if (t.data == '='):
				put_debug('Handling argument definition with default value')
				self.get_next()
				
				# Search in parent namespace
				e_val = self.read_expression(namespace=namespace)
				
				# Put this information into the namespace!
				if ((INFER_TYPE) and ((vd.data_type == T_UNKNOWN) or (vd.data_type == None))):
					put_debug('Inferring type "' + str(e_val.returnType) + '" for argument "' + str(vd) + '"')
					vd.data_type = e_val.returnType
				
				#put('Default value for parameter "' + str(vd.name) + '": ' + str(e_val))
				#put('Expression: ' + str(e_val))
				#put('Expression.value: ' + str(e_val.value))
				#put('Expression.var: ' + str(e_val.var))
				#put('VarDef: ' + str(vd))
				# Store default value in namespace
				if ((e_val.value != None) and (vd.data_value == None)):
					#vd.data_type = e_val.value.type
					vd.data_value = e_val.value
				
				if ((e_val.var != None) and (vd.data_value == None)):
					#HAULValue(type=e_val.var.data_type, data=e_val.var.data_value)
					#if (e_val.var.kind != K_CONST):
					if ((e_val.var.data_value == None) or (e_val.var.data_value.type == None)):
						self.raise_parse_error('Cannot determine default value for parameter "' + str(vd.name) + '", because variable ' + str(e_val.var) + ' has no (constant) value', t)
					
					put_debug('Converting default value for parameter "' + str(vd.name) + '" from variable ' + str(e_val.var) + ' to value ' + str(e_val.var.data_value))
					vd.data_value = e_val.var.data_value
					#vd.data_type = e_val.var.data_value.type
				
				t = self.peek_next()
			
			f.add_arg(vd)
			
			if (t.data == ','): t = self.get_next()
			t = self.peek_next()
		
		t = self.get_assert_data(')', 'Expected ")"')
		t = self.get_assert_data(':', 'Expected ":"')
		
		t = self.get_next()
		# if t.data == ':':	Return type hinting!
		if (t.type != TOKEN_EOL): self.raise_parse_error('Expected EOL', t)
		
		# Read function body
		f.block = self.read_block(namespace=ns, scan_only=scan_only, blockName=f.id.name+'__funcBody')
		return f
	
	
	#@fun read_class HAULClass
	#@arg namespace HAULNamespace
	def read_class(self, namespace, scan_only=False):
		put_debug('read_class()')
		
		c = HAULClass()
		c.origin = self.loc()
		t = self.get_assert_data(L_CLASS, 'Expected "' + L_CLASS + '"')
		
		
		# Class name
		t = self.get_next()
		
		#c.id = namespace.add_id(name=t.data, kind=K_TYPE, data_type=T_CLASS, origin=self.loc())
		c.id = namespace.add_id(name=t.data, kind=K_CLASS, data_type=T_CLASS, origin=self.loc())
		c.id.data_class = c
		
		if (self.tempNs):
			c.namespace = self.tempNs
			self.tempNs = None
			c.namespace.parent = namespace
		else:
			#if (scan_only):	c.namespace = HAULNamespace(name=t.data, parent=namespace)
			#else:	c.namespace = namespace.findNamespace(t.data)
			c.namespace = namespace.get_or_create_namespace(t.data)
			
		ns = c.namespace
		
		# Auto-register "self", "__init__"
		put_debug('Adding default class entries to namespace...')
		ns.add_id(name=L_SELF, kind=K_VARIABLE, data_type=t.data, origin=self.loc(), overwrite=True)
		ns.add_id(name=L_INIT, kind=K_FUNCTION, data_type=t.data, origin=self.loc(), overwrite=True)
		
		
		t = self.peek_next()
		if (t.data == '('):
			# Inheritance
			put_debug('Inheritance...')
			self.get_next()	# Skip bracket
			
			#@FIXME: Use something else for that (array of strings?)
			#c.inherits = self.read_args(namespace=namespace, bracket=')')
			c.inherits = []
			t2 = self.peek_next()
			while (t2.data != ')'):
				if (t2.data != ','):
					c.inherits.append(t2.data)
				self.get_next()
				t2 = self.peek_next()
			self.get_assert_data(')', 'Expected ")" after inheritance list')
			
			# Inheritance
			#@var inh_name str
			for inh_name in c.inherits:
				
				put('Inheriting from class "' + inh_name + '" into class "' + c.id.name + '"...')
				#ns_inh = e_inh.var.namespace
				ns_inh = namespace.find_namespace(inh_name)
				if (ns_inh == None):
					put(namespace.dump())
					self.raise_parse_error('Could not inherit from "' + str(inh_name) + '" into class "' + c.id.name + '", because namespace of the former is unknown, starting from ' + str(namespace), t)
				
				# Merge its ids
				#@var id HAULId
				for id in ns_inh.ids:
					# Skip internals
					if (id.name == L_SELF): continue
					if (id.name == L_INIT): continue
					
					if (id.kind == K_VARIABLE) or (id.kind == K_FUNCTION):
						put_debug('Inheriting "' + str(id.name))
						## Clone to current namespace
						#i = ns.add_id(name=id.name, kind=id.kind, origin=id.origin, data_type=id.data_type, data_value=id.data_value)
						#i.data_function = id.data_function
						#i.data_class = id.data_class
						#i.data_module = id.data_module
						ns.add_foreign_id(id)
					
				
			
		
		
		t = self.get_assert_data(':', 'Expected ":" after class declaration')
		t = self.get_assert_type(TOKEN_EOL, 'Expected EOL after class head')
		
		#t = self.peek_assert_type(TOKEN_BLANK, 'Expected initial indent in class')
		t = self.peek_next(skip_blank=False)
		if (t.type != TOKEN_BLANK): self.raise_parse_error('Expected initial indent in class', t)
		
		#@TODO: Read variables
		#@TODO: Read static variables?
		#@TODO: Read methods
		indent = len(t.data)
		put_debug('read_class():	Initial blank: "' + t.data + '" (' + str(indent) + ')')
		
		#@TODO: Re-use read_module() for parsing a class?!
		
		self.lastIfBlock.append(None)
		# Parse stuff until blank length changes
		while (self.eof() == False) and ((t.type == TOKEN_BLANK) and (len(t.data) == indent)):
			self.get_next()	# Skip BLANK
			
			t = self.peek_next()
			if (t.type == TOKEN_IDENT):
				if (t.data == L_FUNC):
					put_debug('read_class():	reading method...')
					c.addFunc(self.read_function(namespace=ns, scan_only=scan_only))
					put_debug('read_class():	finished method')
				else:
					# Out-of-bounds instructions
					put('Out-of-bound instructions!')
					i = self.read_instruction(namespace=ns, scan_only=scan_only)
					if (i != None):
						if (c.block == None):
							# Create block
							c.block = HAULBlock()
							c.name = '#oob'
							c.origin = self.loc()
						c.block.add_instruction(i)
					
			else:
				if (t.data == '"'):
					# Class comment
					comment = self.read_expression(namespace=ns)
					put_debug('read_class():	Doc-Comment')	#: "' + str(comment.data[:20]) + '..."')
					self.get_next()	# Skip EOL
					
				elif (t.data == L_COMMENT):
					# Comment
					self.get_next()
					t = self.peek_next()
					if (t.data[0] == L_ANNOTATION):
						self.read_annotation(namespace=ns)
					else:
						comment = self.read_line()
						put_debug('read_class():	Comment: "' + str(comment) + '"')
						t = self.peek_next(skip_blank=False)
						if (t.type == TOKEN_EOL):
							self.get_next()	# Skip EOL
					
				else:
					put_debug('read_class():	Skipping ' + str(t))
					self.get_next(skip_blank=False)
				
			t = self.peek_next(skip_blank=False)
			#put('read_class():	t after line of class=' + str(t))
			
		put_debug('read_class():	End of class definition: Exptected indent=' + str(indent) + ' at ' + str(t))
		self.lastIfBlock.pop()
		#self.popIdRegistry()
		return c
		
	#@fun read_module HAULModule
	#@arg namespace HAULNamespace
	#@arg name str
	def read_module(self, namespace, name, scan_only=False):
		put_debug('read_module()')
		
		m = HAULModule(scan_only=scan_only)
		m.name = name
		m.origin = self.loc()
		
		if (scan_only):
			#@TODO: registerGlobal=False so it gets de-allocated when done?
			m.namespace = HAULNamespace(name=m.name, parent=namespace)
			namespace.add_namespace(m.namespace)
		else:
			m.namespace = namespace.get_or_create_namespace(m.name)
			
		#m.namespace.data_module = m
		
		ns = m.namespace
		
		while (self.eof() == False):
			t = self.peek_next()
			#put('read_module():	next token	' + str(t))
			
			if (t.type == TOKEN_EOL):
				self.get_next()
				
			elif (t.type == TOKEN_BLANK):
				self.get_next()
				
			elif (t.type == TOKEN_IDENT):
				
				# Root level identifier
				if (t.data == L_FUNC):
					put_debug('read_module():	reading function block...')
					m.addFunc(self.read_function(namespace=m.namespace, scan_only=scan_only))
					put_debug('read_module():	finished function block.')
					#lastAnnotOrigin = -1
					
				elif (t.data == L_CLASS):
					put_debug('read_module():	reading class block...')
					m.add_class(self.read_class(namespace=ns, scan_only=scan_only))
					put_debug('read_module():	finished class block.')
					#lastAnnotOrigin = -1
					
				elif (t.data == L_IMPORT):
					self.get_next()
					inc = self.get_next()
					imp_name = inc.data
					put('Importing "' + imp_name + '"')
					
					imp_ns = namespace.get_namespace(imp_name)
					if (imp_ns == None):
						self.raise_parse_error('Unknown import "' + imp_name + '" is not in namespace.', t)
					
					ns.add_id(name=imp_name, kind=K_MODULE, data_type=T_MODULE, origin=self.loc())
					#ns.add_namespace(imp_name)
					
					m.add_import(imp_name)
				
				elif (t.data == L_FROM):
					self.get_next()
					
					imp_name = ''
					t2 = self.peek_next()
					while (t2.data != L_IMPORT) and (t2.type != TOKEN_EOL):
						t2 = self.get_next()
						imp_name = imp_name + t2.data
						t2 = self.peek_next()
					self.get_assert_data(L_IMPORT, 'Expected "' + L_IMPORT + '" after "' + L_FROM + '"')
					
					put('Importing from "' + imp_name + '"')
					
					imp_ns = namespace.get_namespace(imp_name)
					if (imp_ns == None):
						self.raise_parse_error('Unknown import "' + imp_name + '" not in namespace.', t)
					
					# Read list of things to import
					imp_list = []
					imp_all = False
					t2 = self.get_next(skip_blank=True)
					while t2.type != TOKEN_EOL:
						if (t2.data != ','):
							imp_list.append(str(t2.data))
							if (t2.data == '*'):
								imp_all = True
						t2 = self.get_next(skip_blank=True)
					
					#@var id HAULId
					for id in imp_ns.ids:
						if (imp_all == True) or (id.name in imp_list):
							put_debug('Importing "' + str(id.name) + '" from "' + imp_name + '" into local namespace')
							
							## Clone to current namespace
							#i = ns.add_id(name=id.name, kind=id.kind, origin=id.origin, data_type=id.data_type, data_value=id.data_value)
							#i.data_function = id.data_function
							#i.data_class = id.data_class
							#i.data_module = id.data_module
							
							ns.add_foreign_id(id)
							
					
					# Also add sub-namespaces
					#@var imp_nss HAULNamespace
					for imp_nss in imp_ns.nss:
						ns.add_namespace(imp_nss)
					#ns.add_namespace(...)
					
					m.add_import(imp_name)
					
				
				else:
					# Read main block
					m.block = self.read_block(namespace=ns, scan_only=scan_only, blockName='__main', module=m)	# + str(self.loc()))
					# It might miss an annotation at the beginning of the main block!
					
				
			elif (t.data == '"'):
				put_debug('Root level comment')
				comment = self.read_expression(namespace=ns)
				#put('read_module():	Doc-Comment: "' + str(comment.value) + '"')
				#self.get_next()	# Skip EOL
				
			elif (t.data[0] == L_COMMENT):
				#o = self.ofsGet
				
				self.get_next()
				t = self.peek_next()
				if (len(t.data) > 0) and (t.data[0] == L_ANNOTATION):
					
					#@FIXME: This annotation might be the first var in root main block! In that case the annotation belongs to the BLOCK, not the MODULE!
					#if (lastAnnotOrigin == -1): lastAnnotOrigin = o
					
					#self.read_annotation(namespace=m.block.namespace)
					self.read_annotation(namespace=m.namespace)
				else:
					comment = self.read_line()
					put_debug('read_module():	Comment: "' + str(comment) + '"')
					#t = self.peek_next()
					#if (t.type == TOKEN_EOL):
					#	self.get_next()
				
			else:
				put('read_module():	Skipping unknown ' + str(t))
				self.get_next()
		return m
		

