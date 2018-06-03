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
	
	def __init__(self, stream_out, dialect=DIALECT_TURBO):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'pas'
		self.write_comment('Translated from HAUL3 to Pascal on ' + str(datetime.datetime.now()) )
		
		self.dialect = dialect
		# Pascal uses name of function to return values
		self.last_function_name = 'RESULT'
		
	def write_comment(self, t):
		"Add a comment to the file"
		#self.stream_out.put('(* ' + t + ' *)\n')
		self.stream_out.put('{ ' + t + ' }\n')
		
	def write_indent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def write_namespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			
			# Search "real" variables
			vs = 0
			for id in ns.ids:
				if (id.kind == 'var'):
					vs += 1
			
			if (vs > 0):
				self.write_indent(indent)
				self.write('Var');
				self.write('\n');
				
				#self.write('\t');
				#self.write_comment('Namespace "' + str(ns) + '"')
				
				for id in ns.ids:
					#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
					#self.write('#@' + str(id.kind) + ' ' + str(id.name) + ': ' + str(id.data_type) + '\n')
					if (id.kind == 'var'):
						
						self.write_indent(indent+1)
						self.write(str(id.name))
						self.write(': ')
						self.write_type(id.data_type)
						if (id.data_value != None):
							self.write(' = ')
							self.write(str(id.data_value))
						self.write(';\n')
			#self.write('\n')
		
	def write_function(self, f, indent=0, writeBody=True):
		f.destination = self.stream_out.size	# Record offset in output stream
		#self.write_namespace(f.namespace, indent)
		
		self.write_indent(indent)
		
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
			#self.write_expression(args[i])
			self.write_var(f.args[i])
			
			self.write(':')
			#id = f.namespace.getId(f.args[i].name)
			id = f.namespace.find_id(f.args[i].name)
			if (id == None):
				self.write_comment('UnknownType')
			else:
				self.write_type(id.data_type)
		self.write(')')
		
		if (f.id.data_type == None):
			pass
		else:
			self.write(':')
			self.write_type(f.id.data_type);
		self.write(';\n')
		
		if (writeBody == True):
			#self.write_namespace(f.namespace, indent+1)
			self.write_block(f.block, indent)
			self.write(';\n')
			self.write('\n')
		
		
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.size	# Record offset in output stream
		self.write_comment('### Module "' + m.name + '"')
		
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
		
		
		self.write_comment('### Module namespace...')
		self.write_namespace(m.namespace, indent)
		
		self.write_comment('### Classes...')
		#@TODO: first "Interface", then "Implementation"
		for typ in m.classes:
			self.write_class(typ, indent)
		
		self.write_comment('### Funcs...')
		for func in m.funcs:
			self.write_function(func, indent)
		
		self.write_comment('### Root Block (main function):')
		if (m.block):
			self.write_block(m.block, indent)
			self.write('.')
		
	def write_class(self, c, indent=0):
		c.destination = self.stream_out.size	# Record offset in output stream
		#self.write('# Class "' + t.id.name + '"\n')
		self.write_indent(indent)
		self.write('Type ')
		self.write(c.id.name)
		self.write(' = Object\n')
		
		if (c.namespace):
			#self.write_indent(indent+1)
			#self.write('### Class namespace...\n')
			self.write_namespace(c.namespace, indent+1)
		
		# Methods (only signature!)
		for func in c.funcs:
			self.write_function(func, indent+1, writeBody=False)
		
		self.write('End;\n')
		
		self.write_comment('Implementation of "' + c.id.name + '"')
		# Implementation
		#@TODO: Initializer?
		for func in c.funcs:
			self.write_function(func, indent)
		
		self.write_comment('End-of-Class "' + c.id.name + '"');
		self.write('\n')
		
	def write_block(self, b, indent=0):
		b.destination = self.stream_out.size	# Record offset in output stream
		#self.write("# Block \"" + b.name + "\"\n")
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.write_indent(indent)
				#self.write('### Block namespace...\n')
				self.write_namespace(b.namespace, indent)
				self.write_indent(indent)
		
		self.write('Begin\n')
		for instr in b.instrs:
			self.write_instruction(instr, indent+1)
		self.write_indent(indent)
		self.write('End');
		
	def write_instruction(self, i, indent):
		i.destination = self.stream_out.size	# Record offset in output stream
		#put(' writing instruction: ' + str(i))
		if (i.control):
			self.write_indent(indent)
			self.write_control(i.control, indent)
			self.write(';\n')
		if (i.call):
			self.write_indent(indent)
			self.write_call(i.call)
			self.write(';\n')
		
	
	def write_control(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write(' Else ')	#elif
				self.write('If (')
				
				self.write_expression(c.exprs[j])
				self.write(') Then ')
				self.write_block(c.blocks[j], indent)
				j += 1
			
			if (j < len(c.blocks)):
				self.write_indent(indent)
				self.write('Else ')
				self.write_block(c.blocks[j], indent)
		
		elif (c.controlType == C_FOR):
			self.write('For ')
			self.write_expression(c.exprs[0])
			self.write(' in ')
			self.write_expression(c.exprs[1])
			self.write(' Do ')
			self.write_block(c.blocks[0], indent)
			
		elif (c.controlType == C_WHILE):
			self.write('While ')
			self.write_expression(c.exprs[0])
			self.write(' Do ')
			self.write_block(c.blocks[0], indent)
			
		elif (c.controlType == C_RETURN):
			#self.write('Result {function name here!} := ')
			if (len(c.exprs) == 1):
				self.write(self.last_function_name + ' := ')
				self.write_expression(c.exprs[0])
				self.write(';\n')
				self.write_indent(indent)
			
			self.write('{ RETURN }')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def write_call(self, c, level=0):
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.write_var(c.args[0].var)
			self.write_expression(c.args[0], level)
			self.write(' := ')
			self.write_expression(c.args[1], level)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.write_expression(c.args[0], level)
			self.write('[')
			self.write_expression_list(c.args, 1, level)
			self.write(']')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('[')
			self.write_expression_list(c.args, 0, level)
			self.write(']')
			
		elif i == I_OBJECT_CALL.name:
			self.write_expression(c.args[0], level)
			if (len(c.args) == 1):
				# No arguments: Leave the empty brackets away
				pass
			else:
				self.write('(')
				self.write_expression_list(c.args, 1, level)
				self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.write_expression(c.args[0], level)
			self.write('.')
			self.write_expression(c.args[1], level)
		
		elif any(i in p for p in PAT_INFIX):
			self.write_expression(c.args[0], level)	# level-1
			
			#@TODO: Use look-up for infix translation
			if (i == '=='): i = '='
			elif (i == '!='): i = '<>'
			
			self.write(' ' + i + ' ')
			
			self.write_expression(c.args[1], level)	# level-1
		
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
				self.write_expression_list(c.args, 0, level)
				self.write(')')
				
			
	def write_expression_list(self, es, start, level):
		i = 0
		for i in xrange(len(es)-start):
			if (i > 0): self.write(', ')
			self.write_expression(es[start+i], level=level)
	
	def write_expression(self, e, level=0):
		if (e.value): self.write_value(e.value)
		if (e.var): self.write_var(e.var)
		if (e.call):
			if (level > 0): self.write('(')
			self.write_call(e.call, level+1)
			if (level > 0): self.write(')')
			
	def write_value(self, v):
		if (v.type == T_STRING):
			#@TODO: Escaping!
			t = v.data_str
			t = t.replace('\\', '\\\\')
			t = t.replace('"', '\\"')
			t = t.replace('\r', '\\r')
			t = t.replace('\n', '\\n')
			t = t.replace('\'', '\\\'')
			self.write("'" + t + "'")
		elif (v.type == T_BOOLEAN):
			if (v.data_bool): self.write('true')
			else: self.write('false')
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_float))
		else:
			self.write('[type=' + str(v.type) + ']')
			
		
	def write_type(self, v):
		if (v == T_INTEGER):	self.write('Integer')
		elif (v == T_BOOLEAN):	self.write('Boolean')
		elif (v == T_FLOAT):	self.write('Real')	#'Single'
		elif (v == T_STRING):	self.write('String')
		elif (v == T_CLASS):	self.write('Pointer')
		else:
			self.write(str(v)+'???')
	
	def write_var(self, v):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


