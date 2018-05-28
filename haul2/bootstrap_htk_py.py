# This is htk_php.py, it is a bootstrapping htk for developing HAL2
# It can be seen as a prototype of a HTK written in a different language than HAL2, so it can be executed directly
'''

Hint: Just implement what is needed!
i.e.: If the target language has similarities to HAL, then just give a F about correctly parsing the language tree. Saves instructions.

'''
from bootstrap_htk import *
from bootstrap_lib import *
from src.htk.py.lib import *
from bootstrap_tokenizer import *

# Write meta info all over the code
DEBUG_ORIGIN = not True

'''
class Packager_py(Packager):
	def __init__(self):
		pass
	def package(self, codeStream, resStreams, outStream):
		pass
'''

# Translates a list of tokens into a specific language. Requires the list to have a certain form (see: Parser)
class Translator_py(Translator):
	def __init__(self):
		self.vars = []
		#self.blockOfs = []
		self.tokenStream = None
	
	def translate(self, tokenStream, streamOut):
		#self.tokens = tokens
		self.tokenStream = tokenStream
		#self.blockOfs = []
		self.vars = []
		
		#@todo: Put all lib function in an array (inside lib iteself. - yo dog!)
		#self.registerVar("res_getAll", "func", 0)
		#self.seekBlockOfs(0, 0)
		self.translateBlock(streamOut, 0, 0)
		return
	
	'''
	# Real compiler/linker shizzle
	def registerBlockOfs(self, tid, ofs):
		#put("registerBlockOfs(" + str(tid) + ") = " +str(ofs))  #str(self.tellBlockOfs()))
		while (len(self.blockOfs) <= tid): self.blockOfs.append(0)
		#self.blockOfs[tid] = self.tellBlockOfs()
		self.blockOfs[tid] = ofs
	
	def getBlockOfs(self, tid):
		#put("getBlockOfs(" + str(tid) + ") = " + str(self.blockOfs[tid]))
		if (tid >= len(self.blockOfs)):
			put("Block index out of range (" + str(tid) + " VS " + str(len(self.blockOfs)) + ")")
			sys.exit(1)
		return self.blockOfs[tid]
	'''
	def registerVar(self, varName, varType, tid):
		self.vars.append([varName, varType])
	
	def getVar(self, varName):
		for var in self.vars:
			if (var[0] == varName): return var
		return None
	
	
	def translateType(self, t, level=0):
		r = ''
		#if (t.state == TOKEN_LOOKUP):
		#    r = r + '[' + self.translateType(self.getToken(), level+1) + ']'
		if (t.state == TOKEN_LOOKUP):
			r = r + '[]'
			# Skip the recursive stuff
			self.translateType(self.getToken(), level+1)
		else:                           # This might be an expression within a lookup *sigh*
			r = r + str(t.data)
		return r
	
	def translateVariable(self, t, level=0, tid=0):
		r = ''
		if (t.state == TOKEN_VARIABLE):
			#if (level == 0): r = '$'    # PHP uses $instance->key1->key2, so only add a dollar in the first variable
			r = r + t.data
		else:			# This might be an expression within a lookup OR a function call
			#put("translateVariable: Unknown token (must be VARIABLE)")
			r = r + self.translateToken(t, tid)
			#r = r + self.translateExpression(t, tid)
		t = self.peekToken()            # Just a simple variable or do we need to dive in deeper?
		if (t.state == TOKEN_LOOKUP):
			t = self.getToken()
			if (t.data == '.'):           # I don't want to introduce a new "state" to distinguish array from object lookups, so I use the raw input byte. Ouch.
				r = r + '.' + self.translateVariable(self.getToken(), level+1, tid)
			if (t.data == '['):
				#r = r + '[' + self.translateVariable(self.getToken(), 0, tid) + ']'
				r = r + '[' + self.translateToken(self.getToken(), tid) + ']'
		return r
	def translateToken(self, t, tid=-1):
		if (t.state == TOKEN_INFIX):
			if (t.data == '='): return ' == '
			else: return ' ' + t.data + ' '
		elif (t.state == TOKEN_COMMENT):        return '# ' + t.data + ''
		elif (t.state == TOKEN_COMMENT_BLOCK):  return '\'\'\' ' + CR + t.data + CR + ' \'\'\''
		elif (t.state == TOKEN_VARIABLE):       return self.translateVariable(t, 0, tid)
		elif (t.state == TOKEN_NUMBER):         return t.data
		elif (t.state == TOKEN_STRING):         return '\"' + t.data + '\"'    #addslashes(t.data).'"'
		elif (t.state == TOKEN_TYPE):           return '' #'\'\'\' Type: ' + t.data + ' \'\'\''
		elif (t.state == TOKEN_LIMIT):          return ', '
		elif (t.state == TOKEN_EXPR_STOR):
			## Cache this new expression for later use (since it may be defined in a place wother than the EXPR_LOAD)
			## Sleek: Just remember where it was, skip it, translate it on-demand
			#self.registerBlockOfs(t.data, t.origin)
			#self.skipBlock()
			#return ''
			return '(' + self.translateExpression(t.data) + ')'
		
		elif (t.state == TOKEN_EXPR_LOAD):
			#i = t.origin    #self.tellBlockOfs()
			#self.seekBlockOfs(self.getBlockOfs(t.data)+1, t.data)
			#l = self.translateExpression(t.data)
			#self.seekBlockOfs(i+1, tid)
			#return '(' + l + ')'
			return ''

		elif (t.state == TOKEN_IDENTIFIER):
			# Translate identifiers in expressions, like "not"
			if (t.data == '='): return ' == '
			elif (t.data == 'and'): return ' and '
			elif (t.data == 'or'): return ' or '
			elif (t.data == 'xor'): return ' xor '
			elif (t.data == 'not'): return ' not '
			elif (t.data == 'true'): return 'True'
			elif (t.data == 'false'): return 'False'
			elif (t.data == 'null'): return 'None'
			
			elif (t.data == 'arr_len'): return 'len'
			elif (t.data == 'str_len'): return 'len'
			elif (t.data == 'ord'): return 'ord'
			elif (t.data == 'chr'): return 'chr'
			elif (t.data == 'str'): return 'str'
			
			elif (t.data == 'new'):
				t = self.getToken()
				return self.translateType(t, 0)
			else:
				put ('Passing identifier ' + str(t.data) + ' at byte ' + str(t.origin) + ' (' + t.originText + ')')
				return t.data   # + ' '
		else:
			put ('unexpected token ' + stateNames[t.state] + ' ' + str(t.data) + ' at byte ' + str(t.origin) + ' (' + t.originText + ')')
			return '\'\'\' unexpected token ' + stateNames[t.state] + ' "' + str(t.data) + ' at byte ' + str(t.origin) + ' (' + t.originText + ')' + ' \'\'\''
		#
	#
	def translateExpression(self, tid):
		r = ''
		while ((not self.eof())):
			t = self.getToken()
			#put('TranslatingE ' + str(t.origin) + ': ' + stateNames[t.state] + '   ' + str(t.data))
			
			if (t.state == TOKEN_EXPR_END):
				return r
			elif (t.state == TOKEN_LOOKUP):
				return self.translateType(t, 0)
			else:
				r = r + self.translateToken(t, tid)
		return r
	
	def translateBlock(self, stream, level=0, tid=0):
		#global stateNames
		
		indent = ''
		for i in range(0, level): indent = indent + chr(9)
		line = ''
		while (not self.eof()):
			t = self.getToken()
			if (t == None): return
			put_debug('Translating ' + str(t.origin) + ': ' + stateNames[t.state] + '   ' + str(t.data)); # + " ....... [and following ones]")
			tType = t.state
			tData = t.data
			if (tType == TOKEN_COMMENT):
				stream.putString(indent + line + '#' + tData + CR)
				line = ''
			elif (tType == TOKEN_IDENTIFIER):
				if (tData == 'var'):
					# Introduce variable
					t = self.getToken()
					varName = t.data
					
					t = self.getToken()
					varType = self.translateType(t, 0)
					self.registerVar(varName, varType, tid)
					
					t = self.peekToken()
					#if ((not t.state == TOKEN_EOI) or (isArray) or (level > 0)):
					if ((not t.state == TOKEN_EOI) or (level > 0)):
						#if (level > 0): line = line + 'var '            #@fixme: Only declare variables inside classes. This just makes sure they aren't declared in root. Fix this!!!
						#line = line + '' + varName
						#if ((isArray) and (t.state == TOKEN_EOI)):
						#    line = line + varName + ' = []'                  # Arrays need to be initialized.
						#elif
						if (not t.state == TOKEN_EOI):
							line = line + varName + ' = ';
						else:
							line = line + varName + ' = None'
					else:
						line = line + '# var ' + varType + ' ' + varName + '';
				elif (tData == 'set'):
					t = self.getToken()
					line = line + self.translateVariable(t, 0, tid) + ' = '
				elif (tData == 'if'):
					line = line + 'if '
				elif (tData == 'else'):
					line = line + 'else '
				elif (tData == 'elseif'):
					line = line + 'elif '
				elif (tData == 'for'):
					varName = self.translateVariable(self.getToken(), 0, tid)
					forStart = self.translateToken(self.getToken(), tid)
					#self.getToken()
					forLen = self.translateToken(self.getToken(), tid)
					#line = line + 'for ' + varName + ' in range(' + self.translateToken(self.getToken(), tid) + ', ' + self.translateToken(self.getToken(), tid) + ')'
					line = line + 'for ' + varName + ' in range(' + forStart + ', ' + forLen + ')'
					
				elif (tData == 'func'):
					
					t = self.getToken()
					varName = t.data
					if (level > 0):
						if (varName == "create"): varName = "__init__"
					line = line + 'def ' + varName
					
					t = self.getToken()
					varType = self.translateType(t)
					# Is ignored in python
					
					i = 0
					t = self.peekToken()
					line = line + '('
					if (level > 0):
						# If it's a class: Auto pre-pend "self" as first parameter
						line = line + 'this'
						i = i + 1
					while (not t.state == TOKEN_BLOCK_STOR):
						if (i > 0):
							line = line + ', '
						t = self.getToken()
						line = line + str(t.data)
						
						t = self.getToken()
						self.translateType(t)
						# argument type gets ignores
						
						t = self.peekToken()
						if (t.state == TOKEN_LIMIT):
							# Skip comma
							self.getToken()
							t = self.peekToken()
						
						i = i + 1
					line = line + ')'
					# Continue translating the method body
					#line = line + self.translateBlock(level+1, t.data)
					
				elif (tData == 'return'):
					line = line + 'return '
				elif (tData == 'contnue'):
					line = line + 'continue'
				elif (tData == 'class'):
					# Here we go...
					t = self.getToken()
					varName = t.data
					
					self.registerVar(varName, 'class', tid)
					line = line + 'class ' + varName
					
					t = self.peekToken()
					if (t.state == TOKEN_TYPE):
						line = line + '(' + t.data + ')'
				
				elif (tData == 'arr_add'):
					t = self.getToken()
					varName = self.translateVariable(t, 0, tid)
					t = self.getToken()
					line = line + varName + '.append(' + self.translateToken(t, tid) + ')'
				elif (tData == 'arr_del'):
					t = self.getToken()
					varName = self.translateVariable(t, 0, tid)
					t = self.getToken()
					line = line + varName + '.pop(' + self.translateToken(t, tid) + ')'
				elif (tData == "str_append"):
					t = self.getToken()
					varName = self.translateVariable(t, 0, tid)
					t = self.getToken()
					line = line + (varName + ' = ' + varName + ' + ' + self.translateToken(t, tid))
				elif (tData == 'print'):
					#$t = self.getToken()
					line = line + 'print'
				else:
					v = self.getVar(t.data)
					if (v == None):
						#put('Unknown identifier "' + str(t.data) + '" in source at ' + str(t.origin))
						#line = line + ('/* Unknown identifier "' + t.data + '" */')
						#line = line + '??' + t.data	 + '??';
						line = line + self.translateToken(t, tid)
					else:
						line = line + t.data;
				#
			elif (tType == TOKEN_EOI):
				if (DEBUG_ORIGIN): stream.putString(indent + '# DEBUG_ORIGIN(' + str(t.origin) + ')' + CR)
				if (len(line) > 0): stream.putString(indent + line + CR)
				line = ''
			elif (tType == TOKEN_BLOCK_STOR):
				stream.putString(indent + line + ':' + CR)
				
				## Just register the position, skip the block (quick and intelligently), come back to it later (BLOCK_LOAD)
				#self.registerBlockOfs(tData, t.origin)
				#self.skipBlock()
				# Sleek: On-demand
				#i = self.ofs    # Stor current pos
				#i = t.origin    #self.tellBlockOfs()    # Store current pos
				#self.seekBlockOfs(self.getBlockOfs(tData)+1, tData)  # Seek to block pos
				self.translateBlock(stream, level+1, tData) # Translate
				#self.seekBlockOfs(i+1, tid)
				line = ''
				continue
			elif (tType == TOKEN_BLOCK_LOAD):
				## Sleek: On-demand
				#stream.putString(indent + line + ':' + CR)
				##i = self.ofs    # Stor current pos
				#i = t.origin    #self.tellBlockOfs()    # Store current pos
				#self.seekBlockOfs(self.getBlockOfs(tData)+1, tData)  # Seek to block pos
				#self.translateBlock(stream, level+1, tData) # Translate
				#self.seekBlockOfs(i+1, tid)
				#line = ''
				continue
			elif (tType == TOKEN_BLOCK_END):
				if (len(line) > 0): stream.putString(line + CR)
				return
			else:
				line = line + self.translateToken(t, tid)
			#
		#
		if (len(line) > 0):
			stream.putString(line + ';' + CR)
		return
	#
#