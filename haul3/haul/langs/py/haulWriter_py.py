#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
from haul.haul import *

def put(t):
	print('HAULWriter_py:\t' + str(t))


ADD_TYPE_HINTS = False	# For debugging: Add returnType hints for all (sub)expressions

DIALECT_2 = 2
DIALECT_3 = 3

PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '||', '^'
	'>', '<', '==', '>=', '<=', '!=',
	'<<', '>>',
	#'in',	# confusion with for ... in
	#'+=', '-='
]

class HAULWriter_py(HAULWriter):
	"Writes Python code"
	
	def __init__(self, streamOut, dialect=DIALECT_2):
		HAULWriter.__init__(self, streamOut)
		self.defaultExtension = 'py'
		self.dialect = dialect
		self.writeComment('Translated from HAUL3 to Python on ' + str(datetime.datetime.now()) )
		
	def writeComment(self, t):
		"Add a comment to the file"
		self.streamOut.put('# ' + t + '\n')
		
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def writeNamespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.writeIndent(indent)
			self.writeComment('Namespace "' + str(ns) + '"')
			for id in sorted(ns.ids):
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				self.writeIndent(indent)
				self.write('#@' + str(id.kind) + '\t' + str(id.name))
				if (id.data_type != None):
					#self.write('\t' + str(id.data_type))
					self.write('\t')
					self.writeType(id.data_type)
					if (id.data_value != None):
						#self.write('\t' + str(id.data_value))
						self.write('\t')
						self.writeValue(id.data_value)
				self.write('\n')
		
	def writeFunc(self, f, indent=0):
		f.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeNamespace(f.namespace, indent)
		
		self.writeIndent(indent)
		self.write('def ')
		self.write(f.id.name)
		self.write('(')
		for i in xrange(len(f.args)):
			if (i > 0): self.write(', ')
			#self.writeExpression(args[i])
			self.writeVar(f.args[i])
			if self.dialect == DIALECT_3:
				# Add type
				self.write(':')
				self.writeType(f.args[i].data_type)
			
			# Default arguments
			if (f.args[i].data_value != None):
				self.write('=')
				self.writeValue(f.args[i].data_value)
			
		self.write(')')
		
		if (f.id.data_type != None) and (self.dialect == DIALECT_3):
			self.write(':')
			self.writeType(f.id.data_type)
		
		self.write(':\n')
		
		#self.writeNamespace(f.namespace, indent+1)
		self.writeBlock(f.block, indent+1)
		
		# Extra blank line after functions
		self.writeIndent(indent)
		self.write('\n')
	
	def writeModule(self, m, indent=0):
		m.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeComment('### Module "' + m.name + '"')
		for im in m.imports:
			#self.write('import ')
			self.write('from ')
			self.write(str(im))
			self.write(' import *')
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.writeNamespace(m.namespace, indent)
		
		self.writeComment('### Classes...')
		for typ in m.classes:
			self.writeClass(typ, indent)
		
		self.writeComment('### Funcs...')
		for func in m.funcs:
			self.writeFunc(func, indent)
		
		self.writeComment('### Root Block (main function):')
		if (m.block):
			self.writeBlock(m.block, indent)
		
	def writeClass(self, c, indent=0):
		c.destination = self.streamOut.size	# Record offset in output stream
		#self.write('# Class "' + t.id.name + '"\n')
		self.writeIndent(indent)
		self.write('class ')
		self.write(c.id.name)
		self.write(':\n')
		
		if (c.namespace):
			#self.writeIndent(indent+1)
			#self.write('### Class namespace...\n')
			self.writeNamespace(c.namespace, indent+1)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.writeFunc(func, indent+1)
		
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		
		# Extra blank line after classes
		self.writeIndent(indent)
		self.write('\n')
	
	def writeBlock(self, b, indent=0):
		#self.write('# Block "' + b.name + '"\n')
		b.destination = self.streamOut.size	# Record offset in output stream
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.writeIndent(indent)
				#self.write('### Block namespace...\n')
				self.writeNamespace(b.namespace, indent)
		
		i = 0
		for instr in b.instrs:
			if (instr.control) or (instr.call):
				i += 1
			
			if (instr.control) or (instr.call) or (instr.comment):
				self.writeIndent(indent)
				if not self.writeInstr(instr, indent): self.write('\n')
		
		if (i == 0):
			# Empty blocks should at least have "pass" in them
			self.writeIndent(indent)
			self.write('pass\n')
		
		#self.write('# End-of-Block "' + b.name + '"\n')
		
	def writeInstr(self, i, indent):
		#put(' writing instruction: ' + str(i))
		i.destination = self.streamOut.size	# Record offset in output stream
		
		if (i.comment):
			self.writeComment(i.comment)
			self.writeIndent(indent)
			
		if (i.control):
			return self.writeControl(i.control, indent)
			
		if (i.call):
			self.writeCall(i.call)
			return False
		
		#self.write('pass')
		return False
		
	def writeControl(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0):
					self.writeIndent(indent)
					self.write('el')	#elif
				self.write('if (')
				
				self.writeExpression(c.exprs[j])
				self.write('):\n')
				self.writeBlock(c.blocks[j], indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.writeIndent(indent)
				self.write('else:\n')
				self.writeBlock(c.blocks[j], indent+1)
			return True
		elif (c.controlType == C_FOR):
			self.write('for ')
			self.writeExpression(c.exprs[0])
			self.write(' in ')
			self.writeExpression(c.exprs[1])
			self.write(':\n')
			self.writeBlock(c.blocks[0], indent+1)
			return True
		elif (c.controlType == C_WHILE):
			self.write('while ')
			self.writeExpression(c.exprs[0])
			self.write(':\n')
			self.writeBlock(c.blocks[0], indent+1)
			return True
		elif (c.controlType == C_RETURN):
			self.write('return')
			if (len(c.exprs) > 0):
				self.write(' ')
				self.writeExpression(c.exprs[0])
			#self.write('\n')
			return False
		elif (c.controlType == C_BREAK):
			self.write('break')
		elif (c.controlType == C_CONTINUE):
			self.write('continue')
		elif (c.controlType == C_RAISE):
			self.write('raise ')
			self.writeExpression(c.exprs[0])
			return False
		else:
			self.write('#CONTROL "' + str(c.controlType) + '"\n')
		
	def writeCall(self, c, level=0):
		# Returns True if it was written out as a block (else: inline). This is used for formatting and indentation
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.writeVar(c.args[0].var)
			self.writeExpression(c.args[0], level)
			self.write(' = ')
			self.writeExpression(c.args[1], level)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.writeExpression(c.args[0], level)
			self.write('[')
			self.writeExpressionList(c.args, 1, level)
			self.write(']')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('[')
			self.writeExpressionList(c.args, 0, level)
			self.write(']')
			
		elif i == I_DICT_CONSTRUCTOR.name:
			self.write('{')
			i = 0
			while (i < len(c.args)):
				if (i > 0): self.write(',\t')
				self.writeExpression(c.args[i], level=level)
				i += 1
				self.write(': ')
				self.writeExpression(c.args[i], level=level)
				i += 1
			self.write('}')
			
		elif i == I_OBJECT_CALL.name:
			#self.write('# ' + str(i) + ' c=' + str(c) + '\n')
			
			self.writeExpression(c.args[0], 0)
			self.write('(')
			self.writeExpressionList(c.args, 1, 0)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.writeExpression(c.args[0], 0)
			self.write('.')
			self.writeExpression(c.args[1], 0)
		
		elif any(i in p for p in PAT_INFIX):
			self.writeExpression(c.args[0], level)	# level-1
			
			self.write(' ' + i + ' ')
			
			self.writeExpression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			self.write(i)
			self.write('(')
			
			#self.writeExpressionList(c.args, 0, level)	# Works if not using named arguments
			
			# Check for named arguments
			for i in xrange(len(c.args)):
				if (i > 0): self.write(', ')
				#@var e HAULExpression
				e = c.args[i]
				
				if ((e.call) and (e.call.id.name == '=')):
					# named argument!
					put_debug('Named argument in call')
					self.write(e.call.args[0].var.name)
					self.write('=')
					self.writeExpression(e.call.args[1])
					
				else:
					# Normal argument
					self.writeExpression(e, level=level)
			
			self.write(')')
			
	def writeExpressionList(self, es, start, level):
		i = 0
		for i in xrange(len(es)-start):
			if (i > 0): self.write(', ')
			self.writeExpression(es[start+i], level=level)
	
	def writeExpression(self, e, level=0):
		
		if (e.value): self.writeValue(e.value)
		if (e.var): self.writeVar(e.var)
		if (e.call):
			if (level > 0): self.write('(')
			self.writeCall(e.call, level+1)
			if (level > 0): self.write(')')
		
		# For debugging: Show returnType of that expression in curly brackets
		if ADD_TYPE_HINTS: self.write('{' + str(e.returnType) + '}')
		
		
	def writeValue(self, v):
		#if (type(v.data) == str):	#@TODO: Use v.type to determine it!
		if (v.type == T_STRING):
			s = str(v.data)
			s = s.replace('\\', '\\\\')
			s = s.replace('\'', '\\\'')
			s = s.replace('\r', '\\r')
			s = s.replace('\n', '\\n')
			self.write("'" + s + "'")
		else:
			self.write(str(v))	#.data
		
	
	def writeType(self, t):
		if (t == T_BOOLEAN): self.write('bool')
		elif (t == T_INTEGER): self.write('int')
		elif (t == T_FLOAT): self.write('float')
		elif (t == T_STRING): self.write('str')
		elif (t == T_OBJECT): self.write('obj')
		elif (t == T_NOTHING): self.write('void')
		elif (t == T_UNKNOWN): self.write('?')
		else:
			self.write(str(t))
	
	def writeVar(self, v):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


