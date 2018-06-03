#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

TODO:
	* None --> undefined
	* provide:
		print(...) --> console.log
		str(...) --> ...toString()
	* check environment:
		Browser
		nodejs
		JScript
		
	* self --> this is currently handled by manipulating the name space. That's kind of uncool.

"""

import datetime
import copy

from haul.haul import *

def put(t):
	print('HAULWriter_js:\t' + str(t))


INFIX_TRANS = {
	'and':	'&&',
	'or':	'||',
	'not':	'!',
	'&':	'&',
	'|':	'|',
	'^':	'^',
	'%':	'%',
	'+':	'+',
	'-':	'-',
	'*':	'*',
	'/':	'/',
	'<':	'<',
	'>':	'>',
	'<=':	'<=',
	'>=':	'>=',
	'==':	'==',
	'!=':	'!=',
	'<<':	'<<',
	'>>':	'>>',
}
INFIX_KEYS = INFIX_TRANS.keys()


DIALECT_NORMAL = 0
DIALECT_WRAP_MAIN = 1

class HAULWriter_js(HAULWriter):
	"Writes JavaScript code"
	
	# Translation of (internal) infix representation to language functions
	
	def __init__(self, stream_out, dialect=DIALECT_NORMAL):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'js'
		self.dialect = dialect
		self.write_comment('Translated from HAUL3 to JavaScript on ' + str(datetime.datetime.now()) )
		
	def write_comment(self, t):
		"Add a comment to the file"
		self.stream_out.put('// ' + t + '\n')
		
	def write_indent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def write_namespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.write_indent(indent)
			self.write('// Namespace "' + str(ns) + '"\n')
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				self.write_indent(indent)
				self.write('//@' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) + '\n')
				
				if (id.name == 'this'):
					continue
				
				# Introduce variable (with const value)
				if (id.kind == K_VARIABLE):
					self.write_indent(indent)
					self.write('var ' + str(id.name))
					if (id.data_value != None):
						self.write(' = ')
						self.write_value(id.data_value)
					self.write(';\n')
		
	def write_function(self, f, indent=0, parentClassName=None):
		f.destination = self.stream_out.size	# Record offset in output stream
		
		# No need to declare arguments
		#self.write_namespace(f.namespace, indent)	# Namespace outside function
		self.write_comment('Namespace skipped (function args)')
		
		name = f.id.name
		if (not parentClassName == None):
			if (name == A_INIT):
				name = parentClassName
			else:
				if name == '__repr__': name = 'toString'
				name = parentClassName + '.prototype.' + name
		
		self.write_indent(indent)
		self.write('var ')
		self.write(name)
		self.write(' = function(')
		j = 0
		for i in xrange(len(f.args)):
			if (i == 0) and (not parentClassName == None):
				# skip first "self"
				continue
				
			if (j > 0): self.write(', ')
			#self.write_expression(args[i])
			self.write_var(f.args[i])
			j += 1
		self.write(') {\n')
		
		#self.write_namespace(f.namespace, indent+1)	# Namespace inside function
		self.write_block(f.block, indent+1)
		
		self.write_indent(indent)
		self.write('};\n')
		
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.size	# Record offset in output stream
		
		self.write('//### Module "' + m.name + '"\n')
		for im in m.imports:
			self.write('//import ')
			self.write(str(im))
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.write_namespace(m.namespace, indent)
		
		self.write('//### Classes...\n')
		for typ in m.classes:
			self.write_class(typ, indent)
		
		self.write('//### Funcs...\n')
		for func in m.funcs:
			self.write_function(func, indent)
		
		self.write('//### Root Block (main function):\n')
		if (self.dialect == DIALECT_WRAP_MAIN):
			self.write('function main() {\n');
			if (m.block):
				self.write_block(m.block, indent+1)
			self.write('}\n');
		else:
			if (m.block):
				self.write_block(m.block, indent)
		
		
	
	def write_class(self, c, indent=0):
		c.destination = self.stream_out.size	# Record offset in output stream
		
		self.write_indent(indent)
		self.write('//# Class "' + c.id.name + '"\n')
		
		
		# Because we will mess up the namespace
		nsOld = c.namespace
		c.namespace = copy.copy(nsOld)
		
		if (c.namespace):
			# Fix self --> this
			selfId = c.namespace.get_id(A_SELF, kind=K_VARIABLE)
			if not selfId == None:
				selfId.name = 'this'
			
			#self.write_indent(indent+1)
			#self.write('### Class namespace...\n')
			self.write_namespace(c.namespace, indent+0)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.write_function(func, indent+0, parentClassName=c.id.name)
		
		# Restore sanity
		c.namespace = nsOld
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		
	def write_block(self, b, indent=0):
		b.destination = self.stream_out.size	# Record offset in output stream
		#self.write("# Block \"" + b.name + "\"\n")
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.write_indent(indent)
				#self.write('### Block namespace...\n')
				self.write_namespace(b.namespace, indent)
		
		for instr in b.instrs:
			#self.write_indent(indent)
			self.write_instruction(instr, indent)
			#self.write(';')
			#self.write('\n')
			
	def write_instruction(self, i, indent):
		i.destination = self.stream_out.size	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.comment):
			self.write_indent(indent)
			self.write_comment(i.comment)
			
		if (i.control):
			self.write_indent(indent)
			self.write_control(i.control, indent)
			self.write('\n')
		if (i.call):
			self.write_indent(indent)
			self.write_call(i.call)
			self.write(';\n')
		
	def write_control(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('else ')
				self.write('if (')
				
				self.write_expression(c.exprs[j])
				self.write(') {\n')
				self.write_block(c.blocks[j], indent+1)
				self.write_indent(indent)
				self.write('}')
				if (j < len(c.blocks)):
					self.write(' ')
				else:
					self.write('\n')
				j += 1
			
			if (j < len(c.blocks)):
				self.write_indent(indent)
				self.write('else {\n')
				self.write_block(c.blocks[j], indent+1)
				self.write_indent(indent)
				self.write('}\n')
		
		elif (c.controlType == C_FOR):
			self.write('for (')
			self.write_expression(c.exprs[0])
			
			self.write(' in ')
			self.write_expression(c.exprs[1])
			"""
			#@FIXME: Dirty hack to handle xrange (only simplest case)
			if (c.exprs[1].call.id.name == 'xrange'):
				self.write(' = 0; ')
				self.write_expression(c.exprs[0])
				self.write(' < ')
				self.write_expression(c.exprs[1].call.args[0])
				self.write('; ')
				self.write_expression(c.exprs[0])
				self.write('++')
			"""
			
			self.write(') {\n')
			self.write_block(c.blocks[0], indent+1)
			self.write_indent(indent)
			self.write('}\n')
		elif (c.controlType == C_WHILE):
			self.write('while (')
			self.write_expression(c.exprs[0])
			self.write(') {\n')
			self.write_block(c.blocks[0], indent+1)
			self.write_indent(indent)
			self.write('}\n')
		elif (c.controlType == C_RETURN):
			self.write('return')
			if (len(c.exprs) > 0):
				self.write(' ')
				self.write_expression(c.exprs[0])
			self.write(';')
		elif (c.controlType == C_BREAK):
			self.write('break;')
		elif (c.controlType == C_CONTINUE):
			self.write('continue;')
		elif (c.controlType == C_RAISE):
			self.write('throw ')
			self.write_expression(c.exprs[0])
			self.write(';')
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
			self.write(' = ')
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
			self.write_expression(c.args[0], 0)
			self.write('(')
			self.write_expression_list(c.args, 1, 0)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.write_expression(c.args[0], 0)
			self.write('.')
			self.write_expression(c.args[1], 0)
		
		elif (i in INFIX_KEYS):
			self.write_expression(c.args[0], level)	# level-1
			
			#if (i in HAULWriter_py.INFIX):
			#	self.write(' ' + HAULWriter_py.INFIX[i] + ' ')
			#else:
			self.write(' ' + INFIX_TRANS[i] + ' ')
			
			self.write_expression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			
			# Check if it is a constructor call
			ns = c.id.namespace
			iid = ns.find_id(i)
			if (iid.kind == K_CLASS):
				# If ns.findId returns kind=K_FUNCTION it is a standard call, if it is K_CLASS it is an instantiation (call of constructor)!
				self.write('new ')
			
			self.write(i)
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
			self.write("'" + v.data_str + "'")	#@TODO: Escaping!
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_float))
		elif (v.type == T_BOOLEAN):
			if (v.data.data_bool == True):
				self.write('true')
			else:
				self.write('false')
		else:
			self.write('[type=' + v.type + '?]')
			
	def write_var(self, v, isClass=False):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


