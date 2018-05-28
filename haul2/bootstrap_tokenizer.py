'''
HAL Tokenzier
This module reads and tokenizes HAL2 (HotKey's Average Language 2) source,
and "streams" it to a parser/translator.
Used to convert HAL into another language using a HTK ("HAL Translation Kernel" or "HAL Token Konverter" :) )

'''
from src.htk.py.lib import *

TOKEN_IDLE = 0
TOKEN_COMMENT = 1
TOKEN_COMMENT_BLOCK = 2
TOKEN_NEXT = 3
TOKEN_NUMBER = 4
TOKEN_IDENTIFIER = 5
TOKEN_VARIABLE = 6
TOKEN_TYPE = 7
TOKEN_STRING = 8
TOKEN_ESCAPE = 9

TOKEN_INFIX = 10
TOKEN_LOOKUP = 11
TOKEN_EXPR_STOR = 12
TOKEN_EXPR_LOAD = 13
TOKEN_EXPR_END = 14

TOKEN_BLOCK_STOR = 15
TOKEN_BLOCK_LOAD = 16
TOKEN_BLOCK_END = 17
TOKEN_EOI = 18
TOKEN_LIMIT = 19

stateNames = [
	'IDLE',
	'COMMENT',
	'COMMENT_BLOCK',
	'NEXT',
	'NUMBER',
	'IDENTIFIER',
	'VARIABLE',
	'TYPE',
	'STRING',
	'ESCAPE',

	'INFIX',
	'LOOKUP',
	'EXPR_STOR',
	'EXPR_LOAD',
	'EXPR_END',
	
	'BLOCK_STOR',
	'BLOCK_LOAD',
	'BLOCK_END',
	'EOI',
	'LIMIT'
]

class Token:
	def __init__(self, state, data, origin, tid=0, originText=""):
		self.state = state
		self.data = data
		self.origin = origin
		self.originText = originText
		self.tid = tid

class Tokenizer:
	def __init__(self, stream):
		self.stream = stream_code_read(stream)  # We need a stream with "peekByte" and line numbering
		#self.parser = parser
		self.tidMax = 0
		
		# Parser state (formerly local variables of tokenizer method)
		self.state = TOKEN_IDLE
		self.level = 0
		self.tid = 0
		self.stateLastBeforeEscape = TOKEN_NEXT
		self.data = ''
		self.tokenQueue = []
		self.tids = [0]
	# Return current byte offset
	def tellByte(self):
		return self.stream.ofs
	def seekToByte(self, byteOfs, tid=0):
		self.stream.seek(byteOfs)
		self.state = TOKEN_IDLE
		self.level = 0
		self.tid = tid
		self.stateLastBeforeEscape = TOKEN_NEXT
		self.data = ''
		self.tokenQueue = []
		self.tids = [0]
		
	def eof(self):
		return ((self.stream.eof()) and (len(self.tokenQueue) == 0))
		
	# Ring buffer: Sometimes one byte might produce more than one token, so we have to buffer that
	def memToken(self, token):
		self.tokenQueue.append(token)
	def getToken(self):
		if (len(self.tokenQueue) == 0):
			if (not self.queueNextTokens()):
				return None
		return self.tokenQueue.pop(0)
	def peekToken(self):
		if (len(self.tokenQueue) == 0):
			if (not self.queueNextTokens()):
				return None
		return self.tokenQueue[0]
		
	# Parse the stream until the next token is found
	def queueNextTokens(self):
		while (not self.stream.eof()) and (len(self.tokenQueue) == 0):
			origin = self.stream.ofs
			originText = 'l' + str(self.stream.lineNum) + 'c' + str(self.stream.linePos)
			b = self.stream.getByte()
			bn = self.stream.peekByte()
			
			if (self.state == TOKEN_COMMENT_BLOCK):
				if ( (b == ord('*')) and (bn == ord('/')) ):
					b = self.stream.getByte()
					self.memToken(Token(self.state, self.data, origin, self.tid, originText))
					self.state = self.stateLastBeforeEscape
					self.data = ''
					continue
				self.data = self.data + chr(b)
				continue
			if ((b == ord('/')) and (bn == ord('*')) ):
				b = self.stream.getByte()
				if (not self.data == ''):
					self.memToken(Token(self.state, self.data, origin, self.tid, originText))
				self.stateLastBeforeEscape = self.state
				self.state = TOKEN_COMMENT_BLOCK
				self.data = ''
				continue
			if (self.state == TOKEN_COMMENT):
				if (b == 10):
					self.memToken(Token(TOKEN_COMMENT, self.data, origin, self.tid, originText))
					self.data = ''
					self.state = TOKEN_NEXT
					continue
				else:
					self.data = self.data + chr(b)
					continue
			if (self.state == TOKEN_ESCAPE):
				if (b == ord('t')):	b = 9
				elif (b == ord('n')):	b = 10
				elif (b == ord('r')):	b = 13
				elif (b == ord('0')):	b = 0
				# Everything else gets piped through
				self.data = self.data + chr(b)
				self.state = self.stateLastBeforeEscape
				continue
			elif (b == ord('\\')):
				self.stateLastBeforeEscape = self.state
				self.state = TOKEN_ESCAPE
				continue
			
			if (self.state == TOKEN_STRING):
				if (b == ord('"')):
					self.memToken(Token(TOKEN_STRING, self.data, origin, self.tid, originText))
					self.data = ''
					self.state = TOKEN_NEXT
					continue
				else:
					self.data = self.data + chr(b)
					continue
			
			if ((self.state == TOKEN_IDLE) or (self.state == TOKEN_NEXT)):
				# Searching for something useful to start with...
				
				# Numbers...
				if ((b >= ord("0")) and (b <= ord("9"))):
					self.state = TOKEN_NUMBER
					self.data = chr(b)
					continue
				# Identifiers...
				if ( ((b >= ord('a')) and (b <= ord('z'))) or ((b >= ord('A')) and (b <= ord('Z'))) ):
					self.state = TOKEN_IDENTIFIER
					self.data = chr(b)
					continue
				if ( (b == ord('#')) ):
					self.state = TOKEN_COMMENT
					self.data = ''
					continue
				if ( (b == ord('$')) ):
					self.state = TOKEN_VARIABLE
					self.data = ''
					continue
				if ( (b == ord('_')) ):
					self.state = TOKEN_TYPE
					self.data = ''
					continue
				if ( (b == ord('"')) ):
					self.state = TOKEN_STRING
					self.data = ''
					continue
			#
			
			# Check for chars that close the current token. I'd prefer a nice regexp or something, but for now...
			if (\
				(b == ord(',')) or (b == ord(';')) or (b == ord('(')) or (b == ord(')'))\
				or (b == ord('{')) or (b == ord('}'))\
				or (b == ord('.')) or (b == ord('[')) or (b == ord(']'))\
				\
				or (b == 9) or (b == 10) or (b == 13) or (b == 32)\
				\
				or (b == ord('+')) or (b == ord('-')) or (b == ord('*')) or (b == ord('/'))\
				or (b == ord('>')) or (b == ord('=')) or (b == ord('<')) or (b == ord('&')) or (b == ord('|')) or (b == ord('^')) or (b == ord('%'))\
			):
				# Close (and store) previous token
				if (not self.data == ''):
					self.memToken(Token(self.state, self.data, origin, self.tid, originText))
					self.data = ''
				self.state = TOKEN_NEXT
				
				if (b == ord('[')):
					self.memToken(Token(TOKEN_LOOKUP, chr(b), origin, self.tid, originText))
					#@TODO: Add begin-expression (and end-expression on "]")
					#continue
				
				# Expression
				if (b == ord('(')): #or (b == ord('[')):
					#put("Start-of-expression at " + str(origin))
					self.tidMax = self.tidMax + 1
					t = self.tidMax
					self.memToken(Token(TOKEN_EXPR_STOR, t, origin, t, originText))
					
					# Enter next level...
					self.level = self.level + 1
					self.tids.append(self.tid)
					self.tid = t
					continue
				if (b == ord(')')): # or (b == ord(']')):
					#put("End-of-expression at " + str(origin))
					self.memToken(Token(TOKEN_EXPR_END, self.tid, origin, self.tid, originText))
					
					# Return to previous level...
					t = self.tid
					self.level = self.level - 1
					self.tid = self.tids.pop()
					
					self.memToken(Token(TOKEN_EXPR_LOAD, t, origin, self.tid, originText))
					continue
				
				# Block (is actually the exact same as for expressions... So: optimize at will!
				if (b == ord('{')):
					#put("Start-of-code block at " + str(origin))
					self.tidMax = self.tidMax + 1
					t = self.tidMax
					self.memToken(Token(TOKEN_BLOCK_STOR, t, origin, t, originText))
					
					# Enter the next level...
					self.level = self.level + 1
					self.tids.append(self.tid)
					self.tid = t
					continue
				if (b == ord('}')):
					#put("End-of-code block at " + str(origin))
					self.memToken(Token(TOKEN_BLOCK_END, self.tid, origin, self.tid, originText))
					
					# Return to previous level...
					t = self.tid
					self.level = self.level - 1
					self.tid = self.tids.pop()
					
					self.memToken(Token(TOKEN_BLOCK_LOAD, t, origin, self.tid, originText))
					continue
					
				# Delimiters
				if (b == ord('.')):
					self.memToken(Token(TOKEN_LOOKUP, chr(b), origin, self.tid, originText))
					continue
				if (b == ord(',')):
					self.memToken(Token(TOKEN_LIMIT, chr(b), origin, self.tid, originText))
					continue
				if (b == ord(';')):
					#put(indent + 'End-of-instruction.')
					self.memToken(Token(TOKEN_EOI, chr(b), origin, self.tid, originText))
					#self.stateLastInstructionStart = len(self.stateTokens)
					continue
				if (b == 10): #/*|| ($c == 13)*/) {
					#put('Next line: "' + self.stream.peekLine() + '"')
					continue
				# Infixes
				if ((b == ord('+')) or (b == ord('-')) or (b == ord('*')) or (b == ord('/'))\
				or (b == ord('>')) or (b == ord('=')) or (b == ord('<')) or (b == ord('&')) or (b == ord('|')) or (b == ord('^')) or (b == ord('%'))):
					#put($indent.'Infix: '.chr($b));
					if (bn == ord('=')):
						# Handle greater-or-equal, ...
						self.stream.getByte()
						self.memToken(Token(TOKEN_INFIX, chr(b)+chr(bn), origin, self.tid, originText))
					else:
						self.memToken(Token(TOKEN_INFIX, chr(b), origin, self.tid, originText))
					continue
				continue
			self.data = self.data + chr(b)
		#
		# End-of-stream but a token still there?
		if (self.stream.eof()) and (not self.data == ''):
			self.memToken(Token(self.state, self.data, origin, self.tid, originText))
			self.data = ''
			#put("Unexpected end of file. Wow, finally _I_ get to write this string somewhere :-)")
		#
		return (len(self.tokenQueue) > 0)
		
	'''
	# Tokenizes the whole stream at once, calling the parsers callback "handleToken()"
	def tokenize(self, parser, level=0, tid=0):
		while (not self.stream.eof()):
			t = self.getToken()
			if (t == None): break
			#put("TOKEN: " + stateNames[t.state] + " " + str(t.data))
			parser.handleToken(t.state, t.data, t.origin, t.tid, self.level)
			
			if (t.state == TOKEN_BLOCK_END): return
			elif (t.state == TOKEN_EXPR_END): return
			elif (t.state == TOKEN_BLOCK_STOR): self.tokenize(parser, level+1, tid+1)
			elif (t.state == TOKEN_EXPR_STOR): self.tokenize(parser, level+1, tid+1)
			
		# Also interpret the remaining bytes
		if (not self.data == ''):
			# Output!
			#put(indent + 'self.state: ' + self.stateNames[self.state] + ',	value="' + self.data + '"')
			#self.parser.handleToken(self.state, self.data, origin, self.tid, self.level)
			t = Token(self.state, self.data, origin, self.tid)
			parser.handleToken(t.state, t.data, t.origin, self.tid, self.level)
		#self.parser.handleBlock(self.stateTokens, self.tid, self.level)
		#put("Unexpected end of file. Wow, finally _I_ get to write this string somewhere :-)")
	#
	'''
#
