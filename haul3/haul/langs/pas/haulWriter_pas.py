#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@TODO:
	* Add compiler switches:
		$N+
	* Pascal functions return using the function name as a variable, e.g. "myfunc:=1;"
	* Pascal does not support overloading, so we need functions for each variable type, e.g. str_int(), str_float(), ...
	* Pascal has the reserved word "Str(int, str);" - so it must be called differently in HAUL3 conversion!
	* integer-div is "div", e.g. "a := 7 div 3;"
	
"""

import datetime

from haul.haul import *

def put(t):
	print('HAULWriter_pas:\t' + str(t))


PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '||', '^'
	'>', '<', '==', '!=', '>=', '<=',
]


DIALECT_TURBO = 0
DIALECT_PP = 1

class HAULWriter_pas(HAULWriter):
	"Writes Pascal code"
	
	def __init__(self, streamOut, dialect=DIALECT_TURBO):
		HAULWriter.__init__(self, streamOut)
		self.defaultExtension = 'pas'
		self.writeComment('Translated from HAUL3 to Pascal on ' + str(datetime.datetime.now()) )
		
		self.dialect = dialect
		# Pascal uses name of function to return values
		self.last_function_name = 'RESULT'
		
	def writeComment(self, t):
		"Add a comment to the file"
		#self.streamOut.put('(* ' + t + ' *)\n')
		self.streamOut.put('{ ' + t + ' }\n')
		
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def writeNamespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			
			# Search "real" variables
			vs = 0
			for id in ns.ids:
				if (id.kind == 'var'):
					vs += 1
			
			if (vs > 0):
				self.writeIndent(indent)
				self.write('Var');
				self.write('\n');
				
				#self.write('\t');
				#self.writeComment('Namespace "' + str(ns) + '"')
				
				for id in ns.ids:
					#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
					#self.write('#@' + str(id.kind) + ' ' + str(id.name) + ': ' + str(id.data_type) + '\n')
					if (id.kind == 'var'):
						
						self.writeIndent(indent+1)
						self.write(str(id.name))
						self.write(': ')
						self.writeType(id.data_type)
						if (id.data_value != None):
							self.write(' = ')
							self.write(str(id.data_value))
						self.write(';\n')
			#self.write('\n')
		
	def writeFunc(self, f, indent=0, writeBody=True):
		f.destination = self.streamOut.size	# Record offset in output stream
		#self.writeNamespace(f.namespace, indent)
		
		self.writeIndent(indent)
		
		#if (self.dialect == DIALECT_TURBO) and (f.id.data_type == None):
		if (f.id.data_type == None):
			self.write('Procedure ')
		else:
			self.write('Function ')
		
		self.write(f.id.name)
		self.last_function_name = f.id.name
		self.write('(')
		for i in xrange(len(f.args)):
			if (i > 0): self.write('; ')
			#self.writeExpression(args[i])
			self.writeVar(f.args[i])
			
			self.write(':')
			#id = f.namespace.getId(f.args[i].name)
			id = f.namespace.find_id(f.args[i].name)
			if (id == None):
				self.writeComment('UnknownType')
			else:
				self.writeType(id.data_type)
		self.write(')')
		
		if (f.id.data_type == None):
			pass
		else:
			self.write(':')
			self.writeType(f.id.data_type);
		self.write(';\n')
		
		if (writeBody == True):
			#self.writeNamespace(f.namespace, indent+1)
			self.writeBlock(f.block, indent)
			self.write(';\n')
			self.write('\n')
		
		
	def writeModule(self, m, indent=0):
		m.destination = self.streamOut.size	# Record offset in output stream
		self.writeComment('### Module "' + m.name + '"')
		
		#@TODO: program or unit?
		self.write('Program ' + m.name + ';\n');
		
		if self.dialect == DIALECT_TURBO:
			# Use 8087 mode (floats)
			self.write('{$N+} { Use floats }\n');
			#self.write('{$R-} { Disable range checks }\n');
		elif self.dialect == DIALECT_PP:
			#self.write('{$appl ' + m.name + '}\n');
			self.write('{$appl HAUL}\n');
			#self.write('{$I PalmAPI.pas }\n');
			pass
		
		if (len(m.imports) > 0):
			if self.dialect == DIALECT_TURBO:
				self.write('Uses ')
				i = 0
				for im in m.imports:
					if (i > 0): self.write(', ')
					self.write(str(im))
					i += 1
				self.write(';\n')
			elif self.dialect == DIALECT_PP:
				for im in m.imports:
					self.write('{$I ' + str(im) + '.pas}\n');
		
		
		self.writeComment('### Module namespace...')
		self.writeNamespace(m.namespace, indent)
		
		self.writeComment('### Classes...')
		#@TODO: first "Interface", then "Implementation"
		for typ in m.classes:
			self.writeClass(typ, indent)
		
		self.writeComment('### Funcs...')
		for func in m.funcs:
			self.writeFunc(func, indent)
		
		self.writeComment('### Root Block (main function):')
		if (m.block):
			self.writeBlock(m.block, indent)
			self.write('.')
		
	def writeClass(self, c, indent=0):
		c.destination = self.streamOut.size	# Record offset in output stream
		#self.write('# Class "' + t.id.name + '"\n')
		self.writeIndent(indent)
		self.write('Type ')
		self.write(c.id.name)
		self.write(' = Object\n')
		
		if (c.namespace):
			#self.writeIndent(indent+1)
			#self.write('### Class namespace...\n')
			self.writeNamespace(c.namespace, indent+1)
		
		# Methods (only signature!)
		for func in c.funcs:
			self.writeFunc(func, indent+1, writeBody=False)
		
		self.write('End;\n')
		
		self.writeComment('Implementation of "' + c.id.name + '"')
		# Implementation
		#@TODO: Initializer?
		for func in c.funcs:
			self.writeFunc(func, indent)
		
		self.writeComment('End-of-Class "' + c.id.name + '"');
		self.write('\n')
		
	def writeBlock(self, b, indent=0):
		b.destination = self.streamOut.size	# Record offset in output stream
		#self.write("# Block \"" + b.name + "\"\n")
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.writeIndent(indent)
				#self.write('### Block namespace...\n')
				self.writeNamespace(b.namespace, indent)
				self.writeIndent(indent)
		
		self.write('Begin\n')
		for instr in b.instrs:
			self.writeInstr(instr, indent+1)
		self.writeIndent(indent)
		self.write('End');
		
	def writeInstr(self, i, indent):
		i.destination = self.streamOut.size	# Record offset in output stream
		#put(' writing instruction: ' + str(i))
		if (i.control):
			self.writeIndent(indent)
			self.writeControl(i.control, indent)
			self.write(';\n')
		if (i.call):
			self.writeIndent(indent)
			self.writeCall(i.call)
			self.write(';\n')
		
	
	def writeControl(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write(' Else ')	#elif
				self.write('If (')
				
				self.writeExpression(c.exprs[j])
				self.write(') Then ')
				self.writeBlock(c.blocks[j], indent)
				j += 1
			
			if (j < len(c.blocks)):
				self.writeIndent(indent)
				self.write('Else ')
				self.writeBlock(c.blocks[j], indent)
		
		elif (c.controlType == C_FOR):
			self.write('For ')
			self.writeExpression(c.exprs[0])
			self.write(' in ')
			self.writeExpression(c.exprs[1])
			self.write(' Do ')
			self.writeBlock(c.blocks[0], indent)
			
		elif (c.controlType == C_WHILE):
			self.write('While ')
			self.writeExpression(c.exprs[0])
			self.write(' Do ')
			self.writeBlock(c.blocks[0], indent)
			
		elif (c.controlType == C_RETURN):
			#self.write('Result {function name here!} := ')
			if (len(c.exprs) == 1):
				self.write(self.last_function_name + ' := ')
				self.writeExpression(c.exprs[0])
				self.write(';\n')
				self.writeIndent(indent)
			
			self.write('{ RETURN }')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def writeCall(self, c, level=0):
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.writeVar(c.args[0].var)
			self.writeExpression(c.args[0], level)
			self.write(' := ')
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
			
		elif i == I_OBJECT_CALL.name:
			self.writeExpression(c.args[0], level)
			if (len(c.args) == 1):
				# No arguments: Leave the empty brackets away
				pass
			else:
				self.write('(')
				self.writeExpressionList(c.args, 1, level)
				self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.writeExpression(c.args[0], level)
			self.write('.')
			self.writeExpression(c.args[1], level)
		
		elif any(i in p for p in PAT_INFIX):
			self.writeExpression(c.args[0], level)	# level-1
			
			#@TODO: Use look-up for infix translation
			if (i == '=='): i = '='
			elif (i == '!='): i = '<>'
			
			self.write(' ' + i + ' ')
			
			self.writeExpression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			
			# Check if it is a constructor call
			ns = c.id.namespace
			iid = ns.find_id(i)
			if (iid.kind == K_CLASS):
				# This is actually a call to a constructor
				self.write(i)
				self.write('.Create')
			else:
				# Just a function call
				self.write(i)
			
			if (len(c.args) == 0):
				# No arguments: Leave the empty brackets away
				pass
			else:
				self.write('(')
				self.writeExpressionList(c.args, 0, level)
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
			
	def writeValue(self, v):
		if (type(v.data) == str):
			self.write("'" + v.data + "'")	#@TODO: Escaping!
		else:
			self.write(str(v))	#.data
		
	def writeType(self, v):
		if (v == T_INTEGER):	self.write('Integer')
		elif (v == T_BOOLEAN):	self.write('Boolean')
		elif (v == T_FLOAT):	self.write('Real')	#'Single'
		elif (v == T_STRING):	self.write('String')
		elif (v == T_CLASS):	self.write('Pointer')
		else:
			self.write(str(v)+'???')
	
	def writeVar(self, v):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


