#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from haul.haul import *
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
		
		self.lastIfBlock = [None]	# Used for ELIF handling (adding one block to a previous one)
		self.lastFunction = None	#@FIXME: Used to infer function returnType based on the type of a return statement
	
	#@fun raiseParseError
	#@arg text str
	#@arg token HAULToken
	def raiseParseError(self, text, token):
		#raise Exception('HAULReader parse error: ' + text + ' at file "' + self.filename + '", line ' + str(self.originLine) + ', pos ' + str(self.originPos) + ' (at "' + token.data + '")')
		# How to make SciTE recognize an error in a Python file:
		#' + text + '
		#raise Exception('HAULReader parse error: File "' + self.filename + '", line ' + str(token.originLine) + ', col ' + str(token.originPos) + ', byte ' + str(token.originByte) + ' at token "' + token.data + '": ' + text)
		put('HAULReader parse error: File "' + self.filename + '", line ' + str(token.originLine) + ', col ' + str(token.originPos) + ', byte ' + str(token.originByte) + ' at token "' + token.data + '": ' + text)
		raise HAULParseError(text, token)
	
	def getAll(self, pats):
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
	
	#@fun getNextToken HAULToken
	def getNextToken(self, skipBlank=True):
		self.ofsGet = self.ofs
		
		if (self.peekNext != None):
			r = self.peekNext
			self.peekNext = None
			return r
		
		if self.eof(): return None
		r = HAULToken()
		
		r.originByte = self.ofs
		r.originLine = self.lineNum
		r.originPos = self.linePos
		c = self.peek()
		
		if (skipBlank == True):
			while ((self.eof() == False) and (c in PAT_BLANK)):
				self.get()
				c = self.peek()
		
		# Identify tokens by their first character (this could be done much nicer and dynamically)
		if (c in PAT_BLANK):
			r.type = TOKEN_BLANK
			r.data = self.getAll(PAT_BLANK)
		elif (c in PAT_EOL):
			r.type = TOKEN_EOL
			r.data = self.getAll(PAT_EOL)
		elif (c in PAT_NUM_1):
			r.type = TOKEN_NUM
			#r.data = self.getAll(PAT_NUM_N)
			
			#if (not(c in PAT_NUM_N)):	# Skip it
			#	self.get()
			
			# Identify int/float/hex/...
			s = self.get()
			s = s + self.getAll(PAT_NUM_N)
			
			if (s == '-'):
				put('Started as a num ("' + str(c) + '"), but isnt: "' + str(s) + '" in ' + str(r))
				# Wrong
				r.type = TOKEN_UNKNOWN
				r.data = c
			else:
				if ('.' in s):
					# Float
					r.data = float(s)
				elif ((len(s) > 2) and (s[0] == '0') and (s[1] == 'x')):
					# hex int
					#put('Line ' + str(self.lineNum) + ', guessing hex for string "%s"' % (s))
					r.data = int(s, 16)
				else:
					# int
					r.data = int(s)
					
				
				# Handle minus
				if (c == '-'):
					r.data = -1 * r.data
				
			
		elif (c in PAT_IDENT_1):
			r.type = TOKEN_IDENT
			r.data = self.getAll(PAT_IDENT_N)
		else:
			r.data = self.get()
		
		return r
	
	
	#@fun peekNextToken HAULToken
	def peekNextToken(self, skipBlank=True):
		if (self.peekNext == None):
			self.peekNext = self.getNextToken(skipBlank=skipBlank)
		return self.peekNext
	
	def peekAssertData(self, check, msg):
		t = self.peekNextToken()
		if (t.data != check):
			self.raiseParseError(msg, t)
		return t
	def getAssertData(self, check, msg):
		t = self.peekAssertData(check, msg)
		self.getNextToken()
		return t
	def peekAssertType(self, check, msg):
		t = self.peekNextToken()
		if (t.type != check):
			self.raiseParseError(msg, t)
		return t
	def getAssertType(self, check, msg):
		t = self.peekAssertType(check, msg)
		self.getNextToken()
		return t
	
	def readLine(self, skipBlank=False):
		l = ''
		t = self.getNextToken(skipBlank=skipBlank)
		l = l + str(t.data)
		c = self.peek()
		while ((c in PAT_EOL) == False) and (self.eof() == False):
			l = l + self.get()
			c = self.peek()
		return l
	
	def getType(self, t):
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
		
	
	def readType(self, namespace):
		t = self.getNextToken()
		return self.getType(t.data)
	
	#@fun readVarDef HAULId
	#@arg namespace HAULNamespace
	def readVarDef(self, namespace):
		t = self.getNextToken()
		#v = HAULVariable()
		#v.origin = self.loc()
		#v.token = t
		
		t2 = self.peekNextToken()
		i = None
		if (t2.data == ':'):
			# Type hinting (Python3 style)
			t2 = self.getNextToken()
			typ = self.readType(namespace=ns)
			i = namespace.add_id(name=t.data, kind=K_VARIABLE, data_type=typ, origin=self.loc())
		else:
			i = namespace.find_id(name=t.data, kind=K_VARIABLE, ignore_unknown=True)
		
		if (i == None):
			put_debug('Yet unknown argument "' + str(t.data) + '" may be inferred.')
			i = namespace.add_id(name=t.data, kind=K_VARIABLE, data_type=T_UNKNOWN, origin=self.loc())
		
		return i
	
	
	def readArgs(self, namespace, bracket=')'):
		"Read argument list"
		r = []
		t = self.peekNextToken()
		
		while ((self.eof() == False) and (t.type == TOKEN_EOL)):
			self.getNextToken()
			t = self.peekNextToken()
		
		while ((self.eof() == False) and (t.data != bracket)):
			
			#@TODO: When reading call arguments we need to look inside the functions namespace for the names of the args
			#r.append(self.readExpression(namespace=namespace_target, namespaceLocal=namespace))
			r.append(self.readExpression(namespace=namespace, allowUnknown=True))
			
			t = self.peekNextToken()
			
			# Default value?
			if (t.data == '='):
				#put('function argument with default value!')
				self.getNextToken()
				
				t = self.readExpression(namespace=namespace)
				
				#@FIXME: Put this information into the namespace! Mark this argument as "optional"
				put('Not yet implemented: Skipping default value for arg: ' + str(t))
				t = self.peekNextToken()
			
			
			# Skip comma
			if (t.data == ','):
				self.getNextToken()
				t = self.peekNextToken()
			
			while ((self.eof() == False) and (t.type == TOKEN_EOL)):
				self.getNextToken()
				t = self.peekNextToken()
			
			
			# Until brackets closed
		#self.getNextToken()	# Skip trailing bracket
		self.getAssertData(bracket, 'Expected ending bracket "' + bracket + '"')
		#put('args=' + str(r))
		return r
		#return copy.copy(r)
	
	def readDict(self, namespace):
		"Read dict entries"
		r = []
		t = self.peekNextToken()
		#while (not self.eof()) and (not t.data == ')'):
		while ((self.eof() == False) and (t.data != '}')):
			put_debug('Reading dict key...')
			r.append(self.readExpression(namespace=namespace))
			
			self.getAssertData(':', 'Expected colon for dict')
			put_debug('Reading dict value...')
			
			r.append(self.readExpression(namespace=namespace))
			
			t = self.peekNextToken()
			
			# Skip comma
			if (t.data == ','):
				self.getNextToken()
				t = self.peekNextToken()
			# Skip comment
			while ((t.type == TOKEN_UNKNOWN) and (t.data[0] == L_COMMENT)):
				comment = self.readLine()
				self.getNextToken()
				t = self.peekNextToken()
				#put('next token: ' + str(t))
			
			# Until brackets closed
		#self.getNextToken()	# Skip trailing bracket
		#put('args=' + str(r))
		return r
		#return copy.copy(r)
	
	def readExpression(self, namespace, checkInfix=True, checkCall=True, namespaceLocal=None, allowUnknown=False):
		#put('readExpression() in ' + str(namespace))
		
		#@var e HAULExpression
		e = HAULExpression()
		e.origin = self.loc()
		e.returnType = '?'
		
		t = self.getNextToken()
		put_debug('readExpression():	ns=' + str(namespace) + ' t=' + str(t))
		#e.token = t
		ns = namespace
		
		# Determine type of expression
		if (t.data == '('):
			put_debug('sub-expression (brackets)')
			e = self.readExpression(namespace=ns)	# Spawn...
			put_debug('end of sub-expression(s)')
			
			self.getAssertData(')', 'Expected closing bracket which started at ' + str(t))	# Check and skip trailing bracket
			
		elif (t.data == '['):
			put_debug('array constructor')
			
			#self.getNextToken()	# Skip bracket
			e.call = implicitCall(I_ARRAY_CONSTRUCTOR)
			e.returnType = T_ARRAY
			
			t2 = self.peekNextToken()
			if (t2.data != ']'):
				e.call.args = self.readArgs(namespace=ns, bracket=']')
				#t2 = self.peekNextToken()
			else:
				#self.raiseParseError('Expected closing array bracket', t2)
				self.getNextToken()	# Skip trailing bracket
			
		elif (t.data == '{'):
			put_debug('Dict constructor')
			e.call = implicitCall(I_DICT_CONSTRUCTOR)
			e.returnType = T_DICT
			
			e.call.args = self.readDict(namespace=ns)
			self.getNextToken()	# Skip trailing bracket
			put_debug('dict returned: ' + str(e.call.args))
			
			
		elif ((t.data == '"') or (t.data == "'")):
			# Read string
			#put('string')
			
			e.value = HAULValue()
			e.value.type = T_STRING
			e.value.data = ''
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
				e.value.data = e.value.data + c
			
			# Check for triple quotes
			t2 = self.peekNextToken()
			if ((e.value.data == '') and (t2.data == t.data)):
				put_debug('Triple quote!')
				# Scan until line that only consists of triple quote
				tq = t.data + t.data + t.data
				t = ''
				while (t[0:3] != tq):
					self.getNextToken()
					t = self.readLine()
					put_debug('Block comment: Skipping line "' + tq + '" != "' + t + '"')
					e.value.data = e.value.data + t
					
				put_debug('End of triple quote')
			
		elif (t.type == TOKEN_EOL):
			#self.getNextToken()	# Skip Character
			e = self.readExpression(namespace=ns)
			
		elif (t.type == TOKEN_NUM):
			
			e.value = HAULValue()
			
			if type(t.data) is float:
				e.value.type = T_FLOAT
			else:
				e.value.type = T_INTEGER
			
			e.value.data = t.data
			e.returnType = e.value.type
			
		elif (t.type == TOKEN_IDENT):
			# Determine if var or call... Normally you would check the identifiers. But let's simply check for an open bracket...
			t2 = self.peekNextToken()
			
			#@TODO: Handle multiple brackets, like test[4][3](123)[2,2]()
			if (checkCall == True) and (t2.data == '('):
				# Call!
				put_debug('call...')
				self.getNextToken()	# Skip bracket
				
				e.call = HAULCall()	
				
				e.call.id = ns.find_id(t.data, ignore_unknown=True)
				if (e.call.id == None):
					self.raiseParseError('Unknown call to "' + str(t.data) + '"', t)
				# If ns.find_id returns kind=K_FUNCTION it is a standard call, if it is K_TYPE it is an instantiation (call of constructor)!
				
				e.returnType = e.call.id.data_type
				
				if (e.call.id.kind == K_TYPE):	#@FIXME: K_CLASS!
					put('Instantiation of class ' + e.call.id.name + ', calling the __init__ function')
					# Use actual class name as type
					#e.returnType = e.call.id.name
				
				#@TODO: Shift namespace to the call so we can handle named arguments
				#ns_target = e.call.id.namespace
				
				e.call.args = self.readArgs(namespace=ns, bracket=')')	#, namespace_target=ns_target)
				
				
			elif (t2.data == '['):
				# Array look-up
				put('Array look-up...')
				self.getNextToken()	# Skip bracket
				
				# Wrap current expression
				e.call = implicitCall(I_ARRAY_LOOKUP)
				
				if (namespaceLocal != None):
					v = namespaceLocal.find_id(t.data)
				else:
					v = ns.find_id(t.data)
				
				
				e_var = HAULExpression(var=v)
				
				t = self.peekNextToken()
				if (t.data == ':'):
					# Start omitted, use 0
					e_index = HAULExpression(value=0)
				else:
					e_index = self.readExpression(namespace=ns)
				
				e.call.args = [
					e_var,
					e_index
				]
				#@FIXME: Need to return the array base type!
				e.returnType = v.data_type	# This might result in "array", but we need the array base type!
				#v.data_array_type
				
				t = self.peekNextToken()
				if (t.data == ':'):
					put_debug('Array slicing...')
					self.getNextToken() # Consume
					e.call = implicitCall(I_ARRAY_SLICE)
					
					t = self.peekNextToken()
					if (t.data == ']'):
						# End omitted, use len
						e_index2 = implicitCall(I_ARRAY_LEN)
						e_index2.args.append(e_var)
					else:
						e_index2 = self.readExpression(namespace=ns)
					e.call.args.append(e_index2)
				
				self.getAssertData(']', 'Expected closing "]" bracket after index')
				
			elif (t2.data == '.'):
				# Object look-up
				put_debug('Object look-up... ' + str(t) + ' in ' + str(namespace) + ' / ' + str(namespaceLocal))
				self.getNextToken()	# Skip dot
				
				e.call = implicitCall(I_OBJECT_LOOKUP)
				
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
					self.raiseParseError('Object lookup failed, because "' + str(t.data) + '" is unknown at ' + str(ns), t)
				
				e_object.var = v
				e_object.returnType = v.data_type
				
				# When doing a object look-up, the name space shifts to the looked-up value. Alternatively we could store it as "run-time look-up/late binding"
				put_debug('Variable "' + str(v.name) + '" is a ' + str(v.kind)+ ' of type "' + str(v.data_type) + '". Shifting namespace for object look-up...')
				
				if (v.data_type == T_CLASS):
					put_debug('Calling method of a class type - static access!')
					ns_shifted = v.namespace
					"""
					ns_shifted = ns.find_namespace_of(v.name)
					if (ns_shifted == None):
						self.raiseParseError('Static access on "' + str(v.name) + '" failed, because its namespace is unknown at ' + str(ns), t)
					"""
				else:
					ns_shifted = ns.find_namespace_of(v.data_type)
					if (ns_shifted == None):
						self.raiseParseError('Object lookup for "' + str(v.name) + '" failed, because namespace for type "' + str(v.data_type) + '" is unknown at ' + str(ns), t)
				
				
				"""
				if (v.kind == K_MODULE):
					
					t2 = self.peekNextToken()	# Name of the method
					put('Call to module "' + str(v.data) + '", auto-creating stub "' + t2.data + '" in namespace...')
					
					# Add the call dynamically to the namespace!
					i = ns_shifted.add_id(name=t2.data, kind=K_FUNCTION, data=t2.data, origin=self.loc())
					# Now it is ready to be found
				"""
				
				# Normal call
				#put_debug('Using local namespace ("' + str(ns_shifted) + '") for finding target ids...')
				# Use local namespace for further resolution of ids
				#self.readExpression(namespace=ns_shifted, checkInfix=False, checkCall=False)	# the field identifier can not be a function call itself and may not contain infixes
				e_member = self.readExpression(namespace=ns, namespaceLocal=ns_shifted, checkInfix=False, checkCall=False)
				
				e.call.args = [
					e_object,
					e_member
				]
				
				# Use the return value of that member
				e.returnType = e_member.returnType
				
				t2 = self.peekNextToken()
				#@TODO: Handle multiple brackets, like test[4][3](123)[2,2]()
				if (t2.data == '('):
					# (method) Call! Convert the look-up into a call(look-up, params...)
					put_debug('Object-lookup (method) call...')
					self.getNextToken()	# Skip bracket
					
					e_lookup = e
					
					# Create new outer expression
					e = HAULExpression()
					
					c_invoke = implicitCall(I_OBJECT_CALL)
					
					# Merge lookup and actual arguments
					c_invoke.args = [e_lookup]
					args = self.readArgs(namespace=ns, bracket=')')
					for arg in args:
						c_invoke.args.append(arg)
					#self.getNextToken()	# Skip bracket
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
				
				e.var = v
				
				if (e.var is None):
					# Variable/id was not found
					
					if (allowUnknown):
						put('Yet unknown id "' + str(t.data) + '", may be inferred.')
						# Add to-be-inferred variable
						i = ns2.add_id(name=t.data, kind=K_VARIABLE, data_type=T_UNKNOWN, origin=self.loc())
						e.var = i
						
					else:
						self.raiseParseError('Undefined id "' + str(t.data) + '"  at ' + str(ns2), t)
						
				e.returnType = e.var.data_type
			
		else:
			self.raiseParseError('Unknown structure of expression', t)
		
		# Check for trailing infix
		if (checkInfix == True):
			t2 = self.peekNextToken()
			if (t2) and any(t2.data in p for p in PAT_INFIX):
				# Yes,  there is a trailing infix
				iId = t2.data
				
				# Try longer infixes
				iId2 = iId
				while any(iId2 in p for p in PAT_INFIX):
					iId = iId2
					self.getNextToken()	# Skip old char, its stored in iId
					
					# Next letter
					t2 = self.peekNextToken()
					iId2 = iId2 + str(t2.data)
				
				#put('Longest infix found: "' + iId + '", next up: ' + str(t2))
				
				# Wrap current expression
				eNew = HAULExpression()
				eNew.call = HAULCall()
				eNew.call.id = ns.find_id(iId)
				
				e1 = HAULExpression(value=e.value, var=e.var, call=e.call)
				e1.returnType = e.returnType
				
				e2 = self.readExpression(namespace=ns)
				eNew.call.args = [
					e1,
					e2
				]
				
				# Determine type of it (type inference)
				#@TODO: Search for the widest type
				#@FIXME: Just look in the internal namespace. The return value is stored there (T_INHERIT, T_BOOLEAN, ...)
				if (iId in ['+', '-', '*', '/', 'and', 'or', 'not']):
					#if (e1.returnType == e2.returnType):
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
				
				t2 = self.peekNextToken()
				#put('End of trailing infix argument and outer expression. Next: ' + str(t2))
				
				return eNew
		
		return e
	
	def readInstr(self, namespace, scanOnly=False, module=None):
		#put_debug('readInstr()')
		i = HAULInstruction()
		i.origin = self.loc()
		
		# Skip until next instruction is found
		t = self.peekNextToken()
		put_debug('readInstr() ' + str(t))
		qs = 0
		while (t.type != TOKEN_IDENT):
			#put('Skipping to next identifier, skipping "' + t.data + '"...')
			self.getNextToken()
			if (str(t.data)[0] == L_COMMENT):
				self.readAnnotation(namespace=namespace)
			
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
			
			t = self.peekNextToken()
		
		t = self.peekAssertType(TOKEN_IDENT, 'Expected identifier at start of instruction')
		ns = namespace
		#i.token = t
		
		
		# Control instructions
		if (t.data == L_IF) or (t.data == L_ELIF) or (t.data == L_ELSE):
			put_debug('IF block(s) start...' + str(t))
			
			if (t.data == L_ELIF) or (t.data == L_ELSE):
				c = self.lastIfBlock[-1]
				i = None	# Do not create a new one!
			else:
				c = implicitControl(C_IF)
				self.lastIfBlock[-1] = c
				
			
			#@FIXME: This might not work right
			while (t.data == L_IF) or (t.data == L_ELIF):
				put_debug('if/elif block in ns=' + str(ns) + '	' + str(t))
				self.getNextToken()	# Ok, digest
				
				# read condition
				c.addExpr(self.readExpression(namespace=ns))
				
				t = self.getAssertData(':', 'Expected ":" after if-expression')
				# read block
				c.addBlock(self.readBlock(namespace=ns, blockName='__ifBlock' + str(self.loc())))
				
				
				#@FIXME The end of elif is not clean. Often times, the class it is in gets falsely terminated here!
				t = self.peekNextToken()
			
			
			if (t.data == L_ELSE):
				put_debug('ELSE block ' + str(t))
				self.getNextToken()	# Skip "else"
				t = self.getAssertData(':', 'Expected ":" after else-expression')
				c.addBlock(self.readBlock(namespace=ns, blockName='__elseBlock' + str(self.loc())))
			
			if (i):
				i.control = c
			put_debug('IF/ELIF/ELSE control end.')
		
		elif (t.data == L_FOR):
			self.getNextToken()	# Ok, digest
			
			c = implicitControl(C_FOR)
			
			# read expression and block
			e_iter = self.readExpression(namespace=ns)
			
			# Only support "in"
			if ((e_iter.call == None) or (e_iter.call.id.name != 'in') or (len(e_iter.call.args) != 2)):
				self.raiseParseError('Only "X in Y" is supported as iterator in for loops', t)
			
			# Transform
			c.addExpr(e_iter.call.args[0])
			c.addExpr(e_iter.call.args[1])
			
			t = self.getAssertData(':', 'Expected ":" after for-syntax')
			
			c.addBlock(self.readBlock(namespace=ns, blockName='__forBlock' + str(self.loc())))
			
			i.control = c
			
		elif (t.data == L_WHILE):
			self.getNextToken()	# Ok, digest
			
			c = implicitControl(C_WHILE)
			
			# read expression and block
			c.addExpr(self.readExpression(namespace=ns))
			
			t = self.getAssertData(':', 'Expected ":" after while-syntax')
			
			c.addBlock(self.readBlock(namespace=ns, blockName='__whileBlock' + str(self.loc())))
			
			i.control = c
			
			
		elif (t.data == L_BREAK):
			self.getNextToken()	# Ok, digest
			c = implicitControl(C_BREAK)
			i.control = c
			
		elif (t.data == L_CONTINUE):
			self.getNextToken()	# Ok, digest
			c = implicitControl(C_CONTINUE)
			i.control = c
			
		elif (t.data == L_RETURN):
			self.getNextToken()	# Ok, digest
			
			c = implicitControl(C_RETURN)
			
			t = self.peekNextToken()
			if (t.type != TOKEN_EOL):	# Handle empty returns
				# read expression to return
				e = self.readExpression(namespace=ns)
				c.addExpr(e)
				
				# The returnType of that expression can be used to infer function returnType
				# Find closest returnType namespace entry
				
				if BLOCKS_HAVE_LOCAL_NAMESPACE:
					iret = namespace.find_id(A_RETTYPE, ignore_unknown=True)
				else:
					# Assume the current namespace is called like the function we are in
					iret = namespace.find_id(namespace.name, ignore_unknown=True)
					
				if (INFER_TYPE) and (e.returnType != T_UNKNOWN) and (iret != None) and (iret.data_type == T_UNKNOWN):
					put('Inferring return type "' + str(e.returnType) + '" for function "' + str(iret.namespace) + '"')
					iret.data_type = e.returnType
					self.lastFunction.returnType = e.returnType
					
				
			
			i.control = c
			
		elif (t.data == L_RAISE):
			self.getNextToken()	# Ok, digest
			c = implicitControl(C_RAISE)
			# read expression to return
			c.addExpr(self.readExpression(namespace=ns))
			i.control = c
			
			"""
		elif (t.data == L_FUNC):
			self.raiseParseError('HAULParseError: Cannot use inline functions, yet. Please put them before any main-block instruction ', t)
		elif (t.data == L_CLASS):
			self.raiseParseError('HAULParseError: Cannot use inline classes, yet. Please put them before any main-block instruction ', t)
			"""
		elif (t.data == L_FUNC):
			put_debug('readModule():	reading function block...')
			#module.addFunc(self.readFunc(namespace=module.namespace, scanOnly=scanOnly))
			module.addFunc(self.readFunc(namespace=namespace, scanOnly=scanOnly))
			put_debug('readModule():	finished function block.')
			#lastAnnotOrigin = -1
			
		elif (t.data == L_CLASS):
			put_debug('readModule():	reading class block...')
			module.addClass(self.readClass(namespace=namespace, scanOnly=scanOnly))
			put_debug('readModule():	finished class block.')
			#lastAnnotOrigin = -1
		
		
		else:
			# Custom instruction (function call or variable access)
			put_debug('Custom function call or assignment: ' + str(t))
			
			# Let "readExpression" consume the token as the "left side"
			e = self.readExpression(namespace=ns, checkInfix=False, allowUnknown=INFER_TYPE)	# We only accept var/identifier, but may infer some stuff
			
			#put('Instruction starts with: ' + str(e))
			
			# Check for Variable-assignment instruction (else this is just a call)
			t2 = self.peekNextToken()
			
			#@FIXME: This check won't recognize dot-chains like "self.test[123] = ..." as a var-set! Instead it will think the "=" is an infix
			
			if (t2 != None) and (t2.data == '='):
				put_debug('Set variable...')
				self.getNextToken()	# Consume "="
				
				i.call = implicitCall(I_VAR_SET)
				
				# Read the "right side"
				e2 = self.readExpression(namespace=ns, allowUnknown=False)
				
				# Type inference
				if (INFER_TYPE) and (e.var != None) and (e.returnType == T_UNKNOWN):
					put('Inferring type "' + e2.returnType + '" for variable "' + str(e.var) + '"')
					e.var.kind = K_VARIABLE
					e.var.data_type = e2.returnType
				
				
				i.call.args = [
					e,
					e2
				]
				
				# Check if variable is a K_CONST
				if (e.var != None):
					if (e.var.kind == K_CONST):
						#put('It is a const! This may only be set once')
						# Set constant value
						e.var.value = e2
				
			else:
				# Just a call
				i.call = e.call
		return i
		#return copy.copy(i)
	
	def readBlock(self, namespace, scanOnly=False, blockName='__someBlock', module=None):
		put_debug('readBlock()...')
		b = HAULBlock(scanOnly=scanOnly)
		b.origin = self.loc()
		b.name = blockName
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			# Option A: Introduce dedicated namespace for local values
			b.namespace = namespace.get_or_create_namespace(blockName)
			ns = b.namespace	# Write all new entries inside this block to the block namespace (better, i.e. for Java)
		else:
			# Option B: Re-use parent namespace
			#b.namespace = None
			ns = namespace	# Write all new entries to the parent namespace (simpler)
		
		self.lastIfBlock.append(None)	# Stack it up, remove it afterwards
		
		# Skip initial EOL
		t = self.peekNextToken(skipBlank=False)
		while (not self.eof()) and (t.type == TOKEN_EOL):
			self.getNextToken(skipBlank=False)
			t = self.peekNextToken(skipBlank=False)
		
		t = self.peekNextToken(skipBlank=False)
		if (not t.type == TOKEN_BLANK):
			#self.raiseParseError('Expected initial indent blanks', t)
			indent = 0
		else:
			indent = len(t.data)
			
		#put('readBlock():	Initial blank: "' + t.data + '" (' + str(indent) + ')')
		
		b.instrs = []
		# Parse instructions until blank length changes
		while (not self.eof()) and ((indent == 0) or ((t.type == TOKEN_BLANK) and (len(t.data) == indent))):
			
			if (t.type == TOKEN_BLANK):
				self.getNextToken()	# Skip BLANK
			
			
			t = self.peekNextToken()
			#put('readBlock()...	t=' + str(t))
			
			# Skip EOL...
			if (t.type == TOKEN_EOL):
				self.getNextToken()
			
			elif (t.type == TOKEN_UNKNOWN) and (t.data[0] == L_COMMENT):
				# Skip/handle comments at start of line
				self.getNextToken()
				t = self.peekNextToken()
				if ((t.type == TOKEN_UNKNOWN) and (t.data[0] == L_ANNOTATION)):
					self.readAnnotation(namespace=ns)
					
				else:
					comment = self.readLine()
					put_debug('readBlock():	Comment: "' + str(comment) + '"')
					b.addComment(comment)
			
			elif (t.type == TOKEN_UNKNOWN) and (t.data[0] == '"'):
				#@TODO: Handle it properly. Double/triple quotes
				comment = self.readLine()
				put_debug('readBlock():	Doc Comment: "' + str(comment) + '"')
				b.addComment(comment)
			
			else:
				# Read instruction
				i = self.readInstr(namespace=ns, module=module)
				if (i != None):
					b.addInstr(i)
				else:
					# May be last mega-indented statement of block
					# Do not break! It may also be an elif block that was able to add its contents to a previous instruction!
					put('No (new) instruction could be read. Might be recovered elif block or indentation error')
					#break
				
				# Skip comments at end of line
				t = self.peekNextToken(skipBlank=False)
				if (indent == 0) and (t != None) and (t.data[0] == L_COMMENT):
					#This check is needed. Or else it may SKIP an annotation that is following an end-of-block at root-level.
					pass
				else:
					t = self.peekNextToken()
					while (not self.eof()) and (t.data[0] == L_COMMENT):
						if (i.comment == None): i.comment = ''
						else: i.comment = i.comment + '\n'
						i.comment = i.comment + self.readLine()
						t = self.peekNextToken()
					#
				#
			
			# Skip EOL...
			t = self.peekNextToken(skipBlank=False)
			while (not self.eof()) and (t.type == TOKEN_EOL):
				self.getNextToken(skipBlank=False)
				t = self.peekNextToken(skipBlank=False)
			#put('readBlock():	t=' + str(t))
		
		put_debug('readBlock() End of block at ' + str(self.peekNextToken()))
		if (not self.eof()) and (t.type == TOKEN_BLANK) and (len(t.data) != indent):
			put_debug('...because expected indent=' + str(indent) + ', while t=' + str(t))
		
		self.lastIfBlock.pop()	# Restore lastIfBlock-stack
		
		return b
		#return copy.copy(b)
	
	def readFunc(self, namespace, scanOnly=False):
		put_debug('readFunc()')
		
		f = HAULFunction()
		f.origin = self.loc()
		self.lastFunction = f
		
		t = self.getAssertData(L_FUNC, 'Expected "' + L_FUNC + '"')
		
		# Function name
		t = self.getNextToken()
		
		# Get return type from previous annotation
		i = namespace.get_id(t.data)
		if i != None:
			if i.kind != K_FUNCTION:
				self.raiseParseError('readFunc: Id "' + str(t.data) + '" is already defined as non-function', t)
			# Has already been annotated
		else:
			# Function is yet unknown
			i = namespace.add_id(t.data, kind=K_FUNCTION, data_type=T_UNKNOWN, origin=self.loc())
		
		f.id = i
		f.returnType = i.data_type
		f.data_function = f
		
		if (self.tempNs):
			# Use the annotated one
			put_debug('Using annotated temp namespace...')
			f.namespace = self.tempNs
			#f.origin = self.tempNs.origin	# Shift to include the origin of the annotation!
			self.tempNs = None
		else:
			# Create new one / Re-use
			#if (scanOnly):	f.namespace = HAULNamespace(name=t.data, parent=namespace)
			#else:			f.namespace = namespace.findNamespace(t.data)
			f.namespace = namespace.get_or_create_namespace(t.data)
		
		ns = f.namespace
		# Use parent namespace
		#ns = namespace
		
		
		# open bracket
		self.getAssertData('(', 'Expected argument list brackets')
		
		# Read argument definitions
		t = self.peekNextToken()
		while (not self.eof()) and (not t.data == ')'):
			vd = self.readVarDef(namespace=ns)
			f.addArg(vd)
			t = self.peekNextToken()
			
			# Default value (not yet implemented)
			if (t.data == '='):
				put_debug('Handling argument definition with default value')
				self.getNextToken()
				
				t = self.readExpression(namespace=namespace)
				# Put this information into the namespace!
				if (INFER_TYPE) and (vd.data_type == T_UNKNOWN):
					put('Inferring type "' + str(t.returnType) + '" for argument "' + str(vd) + '"')
					vd.data_type = t.returnType
				
				put_debug('Default value!')
				#put('Expression: ' + str(t))
				#put('Expression.value: ' + str(t.value))
				#put('Expression.var: ' + str(t.var))
				#put('VarDef: ' + str(vd))
				# Store default value in namespace
				if (t.value != None):
					vd.data_value = t.value
				if (t.var != None):
					vd.data_value = HAULValue(type=t.var.data_type, data=t.var.data_value)
				
				t = self.peekNextToken()
			
			if (t.data == ','): t = self.getNextToken()
			t = self.peekNextToken()
		
		t = self.getAssertData(')', 'Expected ")"')
		t = self.getAssertData(':', 'Expected ":"')
		
		t = self.getNextToken()#
		# if t.data == ':':	Return type hinting!
		if (not t.type == TOKEN_EOL): self.raiseParseError('Expected EOL', t)
		
		# Read function body
		f.block = self.readBlock(namespace=ns, scanOnly=scanOnly, blockName=f.id.name+'__functionBody')
		return f
	
	def readClass(self, namespace, scanOnly=False):
		put('readClass()')
		
		c = HAULClass()
		c.origin = self.loc()
		t = self.getAssertData(L_CLASS, 'Expected "' + L_CLASS + '"')
		
		
		# Class name
		t = self.getNextToken()
		
		#c.id = namespace.add_id(name=t.data, kind=K_TYPE, data_type=T_CLASS, origin=self.loc())
		c.id = namespace.add_id(name=t.data, kind=K_CLASS, data_type=T_CLASS, origin=self.loc())
		c.id.data_class = c
		
		if (self.tempNs):
			c.namespace = self.tempNs
			self.tempNs = None
			c.namespace.parent = namespace
		else:
			#if (scanOnly):	c.namespace = HAULNamespace(name=t.data, parent=namespace)
			#else:	c.namespace = namespace.findNamespace(t.data)
			c.namespace = namespace.get_or_create_namespace(t.data)
			
		ns = c.namespace
		
		# Auto-register "self", "__init__"
		ns.add_id(name=L_SELF, kind=K_VARIABLE, data_type=t.data, origin=self.loc())
		ns.add_id(name=L_INIT, kind=K_FUNCTION, data_type=t.data, origin=self.loc())
		
		
		
		t = self.peekNextToken()
		if (t.data == '('):
			# Inheritance
			put_debug('Inheritance...')
			self.getNextToken()	# Skip bracket
			
			self.inherits = self.readArgs(namespace=namespace, bracket=')')
			
			#@TODO: Implemen: Find the parent class, add reference to its namespace
			put('Inheritance is not yet correctly implemented!')
			
			for e_inh in self.inherits:
				if (e_inh.var == None):
					self.raiseParseError('Could not inherit from ' + str(e_inh) + ', because it needs to be a class', t)
				
				put('Inheriting from class "' + e_inh.var.name + '"...')
				#ns_inh = e_inh.var.namespace
				ns_inh = namespace.find_namespace(e_inh.var.name)
				if (ns_inh == None):
					put(namespace.dump())
					self.raiseParseError('Could not inherit from "' + str(e_inh.var.name) + '", because its namespace is unknown, starting from ' + str(namespace), t)
				
				# Merge its ids
				for id in ns_inh.ids:
					if (id.kind == K_VARIABLE) or (id.kind == K_FUNCTION):
						put('Inheriting "' + str(id.name) + '" from "' + ns_inh.name + '" into class')
						# Clone to current namespace
						i = ns.add_id(name=id.name, kind=id.kind, origin=id.origin, data_type=id.data_type, data_value=id.data_value)
						i.data_function = id.data_function
						i.data_class = id.data_class
						i.data_module = id.data_module
					
				
			
		
		
		t = self.getAssertData(':', 'Expected ":" after class declaration')
		t = self.getAssertType(TOKEN_EOL, 'Expected EOL after class head')
		
		#t = self.peekAssertType(TOKEN_BLANK, 'Expected initial indent in class')
		t = self.peekNextToken(skipBlank=False)
		if (not t.type == TOKEN_BLANK): self.raiseParseError('Expected initial indent in class', t)
		
		#@TODO: Read variables
		#@TODO: Read static variables?
		#@TODO: Read methods
		indent = len(t.data)
		put_debug('readClass():	Initial blank: "' + t.data + '" (' + str(indent) + ')')
		
		#@TODO: Re-use readModule() for parsing a class?!
		
		self.lastIfBlock.append(None)
		# Parse stuff until blank length changes
		while (not self.eof()) and ((t.type == TOKEN_BLANK) and (len(t.data) == indent)):
			self.getNextToken()	# Skip BLANK
			
			t = self.peekNextToken()
			if (t.type == TOKEN_IDENT):
				if (t.data == L_FUNC):
					put_debug('readClass():	reading method...')
					c.addFunc(self.readFunc(namespace=ns, scanOnly=scanOnly))
					put_debug('readClass():	finished method')
				else:
					# Out-of-bounds instructions
					i = self.readInstr(namespace=ns, scanOnly=scanOnly)
					if (i != None): m.block.addInstr(i)
					
			else:
				if (t.data == '"'):
					# Class comment
					comment = self.readExpression(namespace=ns)
					put_debug('readClass():	Doc-Comment')	#: "' + str(comment.data[:20]) + '..."')
					self.getNextToken()	# Skip EOL
					
				elif (t.data == L_COMMENT):
					# Comment
					self.getNextToken()
					t = self.peekNextToken()
					if (t.data[0] == L_ANNOTATION):
						self.readAnnotation(namespace=ns)
					else:
						comment = self.readLine()
						put_debug('readClass():	Comment: "' + str(comment) + '"')
						t = self.peekNextToken(skipBlank=False)
						if (t.type == TOKEN_EOL):
							self.getNextToken()	# Skip EOL
					
				else:
					put_debug('readClass():	Skipping ' + str(t))
					self.getNextToken(skipBlank=False)
				
			t = self.peekNextToken(skipBlank=False)
			#put('readClass():	t after line of class=' + str(t))
			
		put_debug('readClass():	End of class definition: Exptected indent=' + str(indent) + ' at ' + str(t))
		self.lastIfBlock.pop()
		#self.popIdRegistry()
		return c
		
	
	def readModule(self, name=None, namespace=None, scanOnly=False):
		put_debug('readModule()')
		
		if (name == None):
			name = nameByFilename(self.filename)
		
		# If no parent namespace is given: Use the root
		if (namespace == None):
			namespace = self.rootNamespace
		
		m = HAULModule(scanOnly=scanOnly)
		m.name = name
		m.origin = self.loc()
		
		if (scanOnly):
			#@TODO: registerGlobal=False so it gets de-allocated when done?
			m.namespace = HAULNamespace(name=m.name, parent=namespace)
			namespace.add_namespace(m.namespace)
		else:
			m.namespace = namespace.get_or_create_namespace(m.name)
			
		m.namespace.data_module = m
		
		ns = m.namespace
		
		while not self.eof():
			t = self.peekNextToken()
			#put('readModule():	next token	' + str(t))
			
			if (t.type == TOKEN_EOL):
				self.getNextToken()
				
			elif (t.type == TOKEN_BLANK):
				self.getNextToken()
				
			elif (t.type == TOKEN_IDENT):
				
				# Root level identifier
				if (t.data == L_FUNC):
					put_debug('readModule():	reading function block...')
					m.addFunc(self.readFunc(namespace=m.namespace, scanOnly=scanOnly))
					put_debug('readModule():	finished function block.')
					#lastAnnotOrigin = -1
					
				elif (t.data == L_CLASS):
					put_debug('readModule():	reading class block...')
					m.addClass(self.readClass(namespace=ns, scanOnly=scanOnly))
					put_debug('readModule():	finished class block.')
					#lastAnnotOrigin = -1
					
				elif (t.data == L_IMPORT):
					self.getNextToken()
					inc = self.getNextToken()
					imp_name = inc.data
					put('readModule():	Import "' + imp_name + '"')
					
					"""
					if not imp_name in LIB_NAMESPACES:
						self.raiseParseError('Unknown import "' + imp_name + '" not in list of known libraries.', t)
						return None
					imp_ns = LIB_NAMESPACES[imp_name]
					# Add library import to local namespace
					"""
					imp_ns = namespace.get_namespace(imp_name)
					if (imp_ns == None):
						self.raiseParseError('Unknown import "' + imp_name + '" not in namespace.', t)
					
					put('Importing library namespace of "' + imp_name + '"...')
					ns.add_id(name=imp_name, kind=K_MODULE, data_type=T_MODULE, origin=self.loc())
					#ns.add_namespace(imp_name)
					
					m.addImport(imp_name)
				
				elif (t.data == L_FROM):
					self.getNextToken()
					
					imp_name = ''
					t2 = self.peekNextToken()
					while (t2.data != L_IMPORT) and (t2.type != TOKEN_EOL):
						t2 = self.getNextToken()
						imp_name = imp_name + t2.data
						t2 = self.peekNextToken()
					put_debug('readModule():	Import from "' + imp_name + '"')
					
					self.getAssertData(L_IMPORT, 'Expected "' + L_IMPORT + '" after "' + L_FROM + '"')
					
					"""
					if not imp_name in LIB_NAMESPACES:
						self.raiseParseError('Unknown import "' + imp_name + '" not in list of known libraries.', t)
						return None
					
					m.addImport(imp_name)
					imp_ns = LIB_NAMESPACES[imp_name]
					"""
					
					imp_ns = namespace.get_namespace(imp_name)
					if (imp_ns == None):
						self.raiseParseError('Unknown import "' + imp_name + '" not in namespace.', t)
					
					# Read list of things to import
					imp_list = []
					imp_all = False
					t2 = self.getNextToken(skipBlank=True)
					while t2.type != TOKEN_EOL:
						if (t2.data != ','):
							imp_list.append(str(t2.data))
							if (t2.data == '*'):
								imp_all = True
						t2 = self.getNextToken(skipBlank=True)
					
					for id in imp_ns.ids:
						if (imp_all) or (id.name in imp_list):
							put('Importing "' + str(id.name) + '" from "' + imp_name + '" into local namespace')
							# Clone to current namespace
							i = ns.add_id(name=id.name, kind=id.kind, origin=id.origin, data_type=id.data_type, data_value=id.data_value)
							i.data_function = id.data_function
							i.data_class = id.data_class
							i.data_module = id.data_module
					
					# Also add sub-namespaces
					for imp_nss in imp_ns.nss:
						ns.add_namespace(imp_nss)
					#ns.add_namespace(...)
				
				else:
					# Read main block
					m.block = self.readBlock(namespace=ns, scanOnly=scanOnly, blockName='__main', module=m)	# + str(self.loc()))
					# It might miss an annotation at the beginning of the main block!
					""""
					if (lastAnnotOrigin >= 0):
						m.block.origin = lastAnnotOrigin
						lastAnnotOrigin = -1
					"""
				
			elif (t.data == '"'):
				put_debug('Root level comment')
				comment = self.readExpression(namespace=ns)
				#put('readModule():	Doc-Comment: "' + str(comment.value) + '"')
				#self.getNextToken()	# Skip EOL
				
			elif (t.data[0] == L_COMMENT):
				#o = self.ofsGet
				
				self.getNextToken()
				t = self.peekNextToken()
				if (len(t.data) > 0) and (t.data[0] == L_ANNOTATION):
					
					#@FIXME: This annotation might be the first var in root main block! In that case the annotation belongs to the BLOCK, not the MODULE!
					#if (lastAnnotOrigin == -1): lastAnnotOrigin = o
					
					#self.readAnnotation(namespace=m.block.namespace)
					self.readAnnotation(namespace=m.namespace)
				else:
					comment = self.readLine()
					put_debug('readModule():	Comment: "' + str(comment) + '"')
					#t = self.peekNextToken()
					#if (t.type == TOKEN_EOL):
					#	self.getNextToken()
				
			else:
				put('readModule():	Skipping unknown ' + str(t))
				self.getNextToken()
		return m
		
	def readAnnotation(self, namespace):
		self.getNextToken()	# Skip "@"
		comment = self.readLine()
		put_debug('readAnnotation(): "' + str(comment) + '"')
		
		ns = namespace
		
		# Annotations
		parts = comment.split(' ')
		
		if (parts[0] == K_FUNCTION):
			put_debug('readAnnotation():	Creating temporary namespace for function annotation inside ns=' + str(namespace))
			self.tempNs = namespace.get_or_create_namespace(parts[1])
			
			# Auto-add return type
			if (len(parts) > 2):
				#self.tempNs.add_id(name=A_RETTYPE, kind=K_VARIABLE, data_type=self.getType(parts[2]), origin=self.loc())
				namespace.add_id(name=parts[1], kind=K_FUNCTION, data_type=self.getType(parts[2]), origin=self.loc())
			
		elif (parts[0] == A_ARGUMENT):
			# Arguments need to be declared in a forward manner, that's why a "temporary namespace" is used which is checked on function declaration
			if (self.tempNs == None):
				raiseParseError('Argument annotation without matching function annotation', t)
			
			#self.tempNs.add_id(name=parts[1], kind=K_ARGUMENT, data=parts[2], origin=self.loc())
			self.tempNs.add_id(name=parts[1], kind=K_VARIABLE, data_type=self.getType(parts[2]), origin=self.loc())
			
			# Also add to parent ns (needed for streaming, so we know the function arguments from within the parent declaration)
			#ns.add_id(name=parts[1], kind=K_ARGUMENT, data=parts[2] + ' (redundant argument declaration in parent namespace)')
			
			
		elif (parts[0] == K_VARIABLE):
			put_debug('Variable annotation: ' + str(parts))
			ns.add_id(name=parts[1], kind=K_VARIABLE, data_type=self.getType(parts[2]), origin=self.loc())
			
		elif (parts[0] == K_CONST):
			#put('Const annotation! ' + str(parts))
			ns.add_id(name=parts[1], kind=K_CONST, data_type=self.getType(parts[2]), data_value=parts[3], origin=self.loc())
		
		self.getNextToken()	# Skip EOL
		return comment

