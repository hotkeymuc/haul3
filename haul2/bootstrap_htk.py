# This is htk.py, it is a bootstrapping htk prototype for developing HAL2
'''
class Packager:
	def __init__(self):
		pass
	def package(self, codeStream, resStreams, outStream):
		pass
'''


# Translates a list of tokens into a specific language. Requires the list to have a certain form (see: Parser)
class Translator:
	def __init__(self):
		self.tokenStream = None
		pass
	
	def translate(self, tokenStream, streamOut):
		self.tokenStream = tokenStream
		return
	
	def eof(self):
		return self.tokenStream.eof()
	
	def peekToken(self):
		#if (self.eof()): return None
		#return self.tokens[self.ofs]
		return self.tokenStream.peekToken()
	def getToken(self):
		t = self.tokenStream.getToken()
		if (t == None):
			#put("Translator.getToken(): EOF.")
			return None
		#r = self.peekToken()
		#self.ofs = self.ofs + 1
		#return r
		#put('reading ' + str(t.origin) + ': ' + stateNames[t.state] + '   ' + str(t.data))
		return t
	
	'''
	def tellBlockOfs(self):
	    return self.tokenStream.tellByte()
	def seekBlockOfs(self, ofs, tid):
		#put("seekBlockOfs: " + str(ofs))
		#self.ofs = ofs
		self.tokenStream.seekToByte(ofs, tid)
		#put("seekBlockOfs: new=" + str(self.tokenStream.tellByte()) + " --> " + str(ofs))
	'''
	
	def skipBlock(self, l=0):
		while (not self.eof()):
			t = self.getToken()
			#put("Skipping (" + str(l) + "): " + stateNames[t.state])
			if (t.state == TOKEN_BLOCK_END): return                 # Skip until end of block
			elif (t.state == TOKEN_EXPR_END): return                 # Skip until end of block
			elif (t.state == TOKEN_BLOCK_STOR): self.skipBlock(l+1)    # Also skip all nested blocks
			elif (t.state == TOKEN_EXPR_STOR): self.skipBlock(l+1)    # Also skip all nested blocks
	#
#

