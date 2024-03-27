#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
from haul.core import *

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
	'in'
]
#'+=', '-='

class HAULWriter_py(HAULWriter):
	"Writes Python code"
	
	def __init__(self, stream_out, dialect=DIALECT_2):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'py'
		self.dialect = dialect
		self.write_comment('Translated from HAUL3 to Python on ' + str(datetime.datetime.now()))
		
	def write_comment(self, t):
		"Add a comment to the file"
		self.stream_out.put('# ' + t + '\n')
		
	def write_indent(self, num):
		r = ''
		for i in range(num):
			r += '\t'
		self.write(r)
		
	def write_namespace(self, ns, indent=0):
		# Delimiter (must match readAnnotation())
		d = ' '
		
		if (ns and len(ns.ids) > 0):
			#self.write_indent(indent)
			#self.write_comment('Namespace "' + str(ns) + '"')
			
			for id in sorted(ns.ids):
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type) + '\n')
				
				#@TODO: lang.py.lang_py.L_PY_SELF
				if (id.name == 'self'): continue
				if (id.name == '__init__'): continue
				
				# Skip functions here, add the annotations later when they get declared (due to tempNs parsing)
				if (id.kind == K_FUNCTION): continue
				
				# Skip "foreign" entries
				if (id.namespace != ns): continue
				
				self.write_indent(indent)
				self.write('#@' + str(id.kind) + d + str(id.name))
				if (id.data_type != None):
					#self.write('\t' + str(id.data_type))
					self.write(d)
					self.write_type(id.data_type)
					
					if (id.data_value != None):
						#self.write('\t' + str(id.data_value))
						self.write(d)
						if (id.data_value): self.write_value(id.data_value)
					
				self.write('\n')
			
			# Extra blank line after namespaces
			self.write_indent(indent)
			self.write('\n')
			
		
	def write_function(self, f, indent=0):
		f.destination = self.stream_out.ofs	# Record offset in output stream
		
		#self.write_namespace(f.namespace, indent)
		
		# Write function annotation
		d = ' '
		self.write_indent(indent)
		self.write('#@fun' + d + str(f.id.name))
		#if ((f.id.data_type != None) and (f.id.data_type != T_NOTHING)):
		if ((f.returnType != None) and (f.returnType != T_NOTHING)):
			self.write(d)
			#self.write_type(f.id.data_type)
			self.write_type(f.returnType)
		self.write('\n')
		
		#@var a HAULId
		for a in f.args:
			
			if (a.name == 'self'): continue
			
			self.write_indent(indent)
			self.write('#@arg' + d + str(a.name))
			if ((a.data_type != None) and (a.data_type != T_NOTHING)):
				self.write(d)
				self.write_type(a.data_type)
				if ((a.data_value != None) and (a.data_value.type != T_UNKNOWN)):
					self.write(d)
					self.write_value(a.data_value)
			
			self.write('\n')
		# End of manual function annotation
		
		self.write_indent(indent)
		self.write('def ')
		self.write(f.id.name)
		self.write('(')
		for i in range(len(f.args)):
			if (i > 0): self.write(', ')
			#self.write_expression(args[i])
			self.write_var(f.args[i])
			if self.dialect == DIALECT_3:
				# Add type
				self.write(':')
				self.write_type(f.args[i].data_type)
			
			# Default arguments
			if (f.args[i].data_value != None):
				self.write('=')
				self.write_value(f.args[i].data_value)
			
		self.write(')')
		
		if (f.id.data_type != None) and (self.dialect == DIALECT_3):
			self.write(':')
			self.write_type(f.id.data_type)
		
		self.write(':\n')
		
		# Depends on "BLOCKS_HAVE_LOCAL_NAMESPACE" - variables might be stored here (False) o in the block (True)
		self.write_namespace(f.namespace, indent+1)
		
		self.write_block(f.block, indent+1)
		
		# Extra blank line after functions
		self.write_indent(indent)
		self.write('\n')
	
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.ofs	# Record offset in output stream
		
		self.write_comment('### Module "' + m.name + '"')
		for im in m.imports:
			#self.write('import ')
			self.write('from ')
			self.write(str(im))
			self.write(' import *')
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.write_namespace(m.namespace, indent)
		
		self.write_comment('### Classes...')
		for typ in m.classes:
			self.write_class(typ, indent)
		
		self.write_comment('### Funcs...')
		for func in m.funcs:
			self.write_function(func, indent)
		
		self.write_comment('### Root Block (main function):')
		if (m.block):
			self.write_block(m.block, indent)
		
	def write_class(self, c, indent=0):
		c.destination = self.stream_out.ofs	# Record offset in output stream
		#self.write('# Class "' + t.id.name + '"\n')
		self.write_indent(indent)
		self.write('class ')
		self.write(c.id.name)
		
		if ((c.inherits != None) and (len(c.inherits) > 0)):
			self.write('(')
			i = 0
			for inh_name in c.inherits:
				if (i > 0): self.write(', ')
				self.write(inh_name)
				i = i + 1
			self.write(')')
		
		self.write(':\n')
		
		if (c.namespace):
			#self.write_indent(indent+1)
			#self.write('### Class namespace...\n')
			self.write_namespace(c.namespace, indent+1)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.write_function(func, indent+1)
		
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		
		# Extra blank line after classes
		self.write_indent(indent)
		self.write('\n')
	
	def write_block(self, b, indent=0):
		#self.write('# Block "' + b.name + '"\n')
		b.destination = self.stream_out.ofs	# Record offset in output stream
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.write_indent(indent)
				#self.write('### Block namespace...\n')
				self.write_namespace(b.namespace, indent)
		
		i = 0
		for instr in b.instrs:
			if (instr.control) or (instr.call):
				i += 1
			
			if (instr.control) or (instr.call) or (instr.comment):
				self.write_indent(indent)
				if not self.write_instruction(instr, indent): self.write('\n')
		
		if (i == 0):
			# Empty blocks should at least have "pass" in them
			self.write_indent(indent)
			self.write('pass\n')
		
		#self.write('# End-of-Block "' + b.name + '"\n')
		
	def write_instruction(self, i, indent):
		#put(' writing instruction: ' + str(i))
		i.destination = self.stream_out.ofs	# Record offset in output stream
		
		if (i.comment):
			self.write_comment(i.comment)
			self.write_indent(indent)
			
		if (i.control):
			return self.write_control(i.control, indent)
			
		if (i.call):
			self.write_call(i.call)
			return False
		
		#self.write('pass')
		return False
		
	def write_control(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0):
					self.write_indent(indent)
					self.write('el')	#elif
				self.write('if (')
				
				self.write_expression(c.exprs[j])
				self.write('):\n')
				self.write_block(c.blocks[j], indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.write_indent(indent)
				self.write('else:\n')
				self.write_block(c.blocks[j], indent+1)
			
			# Add blank line at end of if/elif/else
			self.write_indent(indent)
			self.write('\n')
			
			return True
		elif (c.controlType == C_FOR):
			self.write('for ')
			self.write_expression(c.exprs[0])
			self.write(' in ')
			self.write_expression(c.exprs[1])
			self.write(':\n')
			self.write_block(c.blocks[0], indent+1)
			return True
		elif (c.controlType == C_WHILE):
			self.write('while ')
			self.write_expression(c.exprs[0])
			self.write(':\n')
			self.write_block(c.blocks[0], indent+1)
			return True
		elif (c.controlType == C_RETURN):
			self.write('return')
			if (len(c.exprs) > 0):
				self.write(' ')
				self.write_expression(c.exprs[0])
			#self.write('\n')
			return False
		elif (c.controlType == C_BREAK):
			self.write('break')
		elif (c.controlType == C_CONTINUE):
			self.write('continue')
		elif (c.controlType == C_RAISE):
			self.write('raise ')
			self.write_expression(c.exprs[0])
			return False
		else:
			self.write('#CONTROL "' + str(c.controlType) + '"\n')
		
	def write_call(self, c, level=0):
		# Returns True if it was written out as a block (else: inline). This is used for formatting and indentation
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.write_var(c.args[0].var)
			self.write_expression(c.args[0], level)
			self.write(' = ')
			self.write_expression(c.args[1], level)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.write_expression(c.args[0], level)
			self.write('[')
			self.write_expression_list(c.args, 1, level)
			self.write(']')
			
		elif i == I_ARRAY_SLICE.name:
			self.write_expression(c.args[0], level)
			self.write('[')
			self.write_expression(c.args[1], level)
			self.write(':')
			self.write_expression(c.args[2], level)
			self.write(']')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('[')
			self.write_expression_list(c.args, 0, level)
			self.write(']')
			
		elif i == I_DICT_CONSTRUCTOR.name:
			self.write('{')
			i = 0
			while (i < len(c.args)):
				if (i > 0): self.write(',\t')
				self.write_expression(c.args[i], level=level)
				i += 1
				self.write(': ')
				self.write_expression(c.args[i], level=level)
				i += 1
			self.write('}')
			
		elif i == I_OBJECT_CALL.name:
			#self.write('# ' + str(i) + ' c=' + str(c) + '\n')
			
			self.write_expression(c.args[0], 0)
			self.write('(')
			self.write_expression_list(c.args, 1, 0)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.write_expression(c.args[0], 0)
			self.write('.')
			self.write_expression(c.args[1], 0)
		
		elif any(i in p for p in PAT_INFIX):
			
			self.write_expression(c.args[0], level)	# level-1
			
			j = 1
			while (j < len(c.args)):
				self.write(' ' + i + ' ')
				self.write_expression(c.args[j], level)	# level-1
				j += 1
		
		else:
			# Write a standard call
			
			
			if i == I_PRINT.name:
				i = 'print'
			if i == I_STR.name:
				i = 'str'
			
			
			self.write(i)
			self.write('(')
			
			#self.write_expression_list(c.args, 0, level)	# Works if not using named arguments
			
			# Check for named arguments
			for i in range(len(c.args)):
				if (i > 0): self.write(', ')
				#@var e HAULExpression
				e = c.args[i]
				
				if ((e.call) and (e.call.id.name == '=')):
					# named argument!
					put_debug('Named argument in call')
					self.write(e.call.args[0].var.name)
					self.write('=')
					self.write_expression(e.call.args[1])
					
				else:
					# Normal argument
					self.write_expression(e, level=level)
			
			self.write(')')
			
	def write_expression_list(self, es, start, level):
		i = 0
		for i in range(len(es)-start):
			if (i > 0): self.write(', ')
			self.write_expression(es[start+i], level=level)
	
	def write_expression(self, e, level=0):
		
		if (e.value): self.write_value(e.value)
		if (e.var): self.write_var(e.var)
		if (e.call):
			if (level > 0): self.write('(')
			self.write_call(e.call, level+1)
			if (level > 0): self.write(')')
		
		# For debugging: Show returnType of that expression in curly brackets
		if ADD_TYPE_HINTS: self.write('{' + str(e.returnType) + '}')
		
		
	def write_value(self, v):
		#if (type(v.data) == str):	#@TODO: Use v.type to determine it!
		if (v.type == T_STRING):
			s = str(v.data_str)
			s = s.replace('\\', '\\\\')
			s = s.replace('\'', '\\\'')
			s = s.replace('\r', '\\r')
			s = s.replace('\n', '\\n')
			self.write("'" + s + "'")
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_int))
		elif (v.type == T_BOOLEAN):
			if (v.data_bool == True): self.write('True')
			else: self.write('False')
		elif (v.type == T_NOTHING):
			self.write('None')
		elif (v.type == None):
			# This should not happen!
			put('Value has no type!')
			self.write('[type=None]')
		else:
			put('Unknown value type: ' + str(v.type))
			self.write(str(v))	#.data
		
	
	def write_type(self, t):
		if (t == T_BOOLEAN): self.write('bool')
		elif (t == T_INTEGER): self.write('int')
		elif (t == T_FLOAT): self.write('float')
		elif (t == T_STRING): self.write('str')
		elif (t == T_OBJECT): self.write('obj')
		elif (t == T_NOTHING): self.write('void')
		elif (t == T_UNKNOWN): self.write('[type=UNKNOWN]')
		else:
			# Class name assumed
			self.write(str(t))
	
	def write_var(self, v):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


