#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

TODO:


"""

import datetime
import copy

from haul.core import *

def put(t):
	print('HAULWriter_c:\t' + str(t))


INFIX_TRANS = {
	'and':	'&&',
	'or':	'||',
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


DIALECT_C = 0
DIALECT_ARDUINO = 1
DIALECT_Z88DK = 2
DIALECT_GBDK = 3



GLUE_ARDUINO_PRE = '''
//### Arduino glue code (pre) from writer_c
'''

GLUE_ARDUINO_POST = '''
//### Arduino glue code (post)
void setup() {
	Serial.begin(9600);
	_main();
}

void loop() {
}
'''



class HAULWriter_c(HAULWriter):
	"Writes C code"
	
	# Translation of (internal) infix representation to language functions
	
	def __init__(self, stream_out, dialect=DIALECT_C):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'c'
		self.write_comment('Translated from HAUL3 to C on ' + str(datetime.datetime.now()) )
		
		self.dialect = dialect
		
	
	def write_indent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def write_comment(self, t):
		"Add a comment to the file"
		if ('\n' in t):
			self.stream_out.put('/* ' + t + ' */\n')
		else:
			self.stream_out.put('// ' + t + '\n')
		
	def write_namespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.write_indent(indent)
			self.write('/**\n')
			
			self.write_indent(indent)
			self.write(' * Namespace "' + str(ns) + '":\n')
			
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				self.write_indent(indent)
				self.write(' * @' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) + '\n')
			
			self.write_indent(indent)
			self.write(' */\n')
		
	def write_function(self, f, indent=0, parentClassName=None):
		f.destination = self.stream_out.ofs	# Record offset in output stream
		###self.write_namespace(f.namespace, indent)
		
		name = f.id.name
		if (not parentClassName == None):
			if (name == A_INIT):
				name = parentClassName
			else:
				if name == '__repr__': name = 'toString'
				name = parentClassName + '.' + name
		
		self.write_indent(indent)
		
		if (self.dialect == DIALECT_Z88DK) and (f.id.data_type == None):
			# Z88DK: Do not add "void" in front of methods
			pass
		else:
			self.write_type(f.id.data_type)	# Return type
			self.write(' ')
		
		self.write(name)	# Name
		self.write('(')
		j = 0
		for i in xrange(len(f.args)):
			if (i == 0) and (not parentClassName == None):
				# skip first "self"
				continue
				
			if (j > 0): self.write(', ')
			#self.write_expression(args[i])
			
			self.write_type(f.args[i].data_type)
			self.write(' ')
			self.write_var(f.args[i])
			j += 1
		self.write(') {\n')
		
		#self.write_namespace(f.namespace, indent+1)
		self.write_block(f.block, indent+1)
		
		self.write_indent(indent)
		self.write('}\n')
		
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.ofs	# Record offset in output stream
		self.write_comment('### Begin of Module "' + m.name + '"')
		
		#self.write('### Module namespace...\n')
		self.write_namespace(m.namespace, indent)
		
		if self.dialect == DIALECT_ARDUINO:
			self.write(GLUE_ARDUINO_PRE);
		elif self.dialect == DIALECT_Z88DK:
			self.write('#define VGL\n')
			self.write('#include <stdio.h>\n')
		elif self.dialect == DIALECT_GBDK:
			self.write('#include <gb/gb.h>\n')
			self.write('#include <gb/font.h>\n')
			self.write('#include <gb/console.h>\n')
			self.write('#include <gb/drawing.h>\n')
			self.write('#include <stdio.h>\n')
			pass
		
		if (len(m.imports) > 0):
			self.write('\n')
			self.write_comment('### Imports...')
			
			for im in m.imports:
				if self.dialect == DIALECT_GBDK:
					self.write('#include "')
					self.write(str(im))
					self.write('.h"\n')
				elif self.dialect == DIALECT_ARDUINO:
					self.write('#include "')
					self.write(str(im))
					#self.write('.c"\n')
					self.write('.h"\n')
					
				elif self.dialect == DIALECT_Z88DK:
					self.write('#include "')
					self.write(str(im))
					self.write('.h"\n')
				else:
					self.write('#include <')
					self.write(str(im))
					self.write('.c>\n')
			
			self.write('\n')
		
		
		if (len(m.classes) > 0):
			self.write('\n')
			self.write_comment('### Classes...')
			for typ in m.classes:
				self.write_class(typ, indent)
				self.write('\n')
		
		if (len(m.funcs) > 0):
			self.write('\n')
			self.write_comment('### Functions...')
			for func in m.funcs:
				self.write_function(func, indent)
				self.write('\n')
		
		self.write('\n')
		self.write_comment('### Root Block (main function)...')
		if self.dialect == DIALECT_GBDK:
			self.write('void main_internal(void) {\n')
		elif self.dialect == DIALECT_Z88DK:
			#self.write('void main(void) {\n')
			self.write('main() {\n')
		elif self.dialect == DIALECT_ARDUINO:
			#self.write('int main() {\n')
			self.write('void _main() {\n')
		else:
			self.write('int main() {\n')
		
		if (m.block):
			self.write_block(m.block, indent+1)
		
		
		if self.dialect == DIALECT_GBDK:
			self.write('}\n')
			self.write('\n')
			self.write('font_t print_font;\n')
			self.write('void main(void) {\n')
			self.write('	font_init();\n')
			self.write('	print_font = font_load(font_ibm);\n')
			self.write('	font_set(print_font);\n')
			self.write('	main_internal();\n')
			self.write('}\n')
		
		elif self.dialect == DIALECT_ARDUINO:
			self.write('}\n')
			self.write(GLUE_ARDUINO_POST);
		elif self.dialect == DIALECT_Z88DK:
			self.write('while(1){} // Break in end\n')
			self.write('}\n')
			#self.write(GLUE_Z88DK_POST);
		else:
			self.write_indent(1)
			self.write('return 0;\n')
			self.write('}\n')
		
		
		self.write('\n')
		self.write_comment('### End of Module')
		
	
	def write_class(self, c, indent=0):
		c.destination = self.stream_out.ofs	# Record offset in output stream
		
		self.write_indent(indent)
		self.write_comment('# Class "' + c.id.name + '"')
		
		
		# Because we will mess up the namespace
		nsOld = c.namespace
		c.namespace = copy.copy(nsOld)
		
		if (c.namespace):
			# Fix self --> this
			selfId = c.namespace.get_id(name=A_SELF, kind=K_VARIABLE)
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
		b.destination = self.stream_out.ofs	# Record offset in output stream
		
		#self.write_comment("# Block \"" + b.name + "\"")
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.write_indent(indent)
				#self.write('### Block namespace...\n')
				###self.write_namespace(b.namespace, indent)
				
				# Pre-define vars
				for id in b.namespace.ids:
					#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
					if (id.kind == K_VARIABLE):
						self.write_indent(indent)
						self.write_type(id.data_type)
						self.write(' ')
						self.write(str(id.name) + ';\n')
		
		for instr in b.instrs:
			self.write_indent(indent)
			self.write_instruction(instr, indent)
			#self.write(';')
			self.write('\n')
			
	def write_instruction(self, i, indent):
		i.destination = self.stream_out.ofs	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.comment):
			self.write_comment(i.comment)
			self.write_indent(indent)
			
		if (i.control): self.write_control(i.control, indent)
		if (i.call):
			self.write_call(i.call)
			self.write(';')
		
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
			
			#self.write(' in ')
			#self.write_expression(c.exprs[1])
			if (len(c.exprs) < 2):
				put('TOO LESS FOR EXPRESSIONS!')
				self.write_comment('Too less expressions: ')
				self.write_expression_list(c.exprs)
			
			elif ((c.exprs[1].call != None) and (c.exprs[1].call.id.name == 'xrange')):
				self.write(' = 0; ')
				self.write_expression(c.exprs[0])
				self.write(' < ')
				self.write_expression(c.exprs[1].call.args[0])
				self.write('; ')
				self.write_expression(c.exprs[0])
				self.write('++')
			else:
				put('UNHANDLED FOR CONSTRUCT: ' + str(c.exprs))
				#self.write_comment('Unhandled kind of for-loop construct: ')
				#self.write(str(c.exprs))
				self.write(' in ')
				self.write_expression(c.exprs[1])
			
			
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
			self.write('raise ')
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
			
			#@TODO: Check type of both expressions, maybe chose a different function! e.g. str_compare
			if ((i == '==') and ((c.args[0].returnType == T_STRING) or (c.args[1].returnType == T_STRING))):
				self.write('str_compare(')
				self.write_expression_list(c.args, 0, level)	# level-1
				self.write(')')
			elif ((i == '!=') and ((c.args[0].returnType == T_STRING) or (c.args[1].returnType == T_STRING))):
				self.write('str_compare(')
				self.write_expression_list(c.args, 0, level)	# level-1
				self.write(') == 0')
			else:
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
			if (iid.kind == K_TYPE):
				# If ns.find_id returns kind=K_FUNCTION it is a standard call, if it is K_TYPE it is an instantiation (call of constructor)!
				self.write('new ')
			
			
			# Internals
			if i == I_PRINT.name:
				if self.dialect == DIALECT_ARDUINO:
					i = 'Serial.println'
				else:
					i = 'printf'
			if i == I_STR.name:
				i = 'itoa'
			
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
			#@TODO: Escaping!
			t = v.data_str
			t = t.replace('\\', '\\\\')
			t = t.replace('"', '\\"')
			t = t.replace('\r', '\\r')
			t = t.replace('\n', '\\n')
			#t = t.replace('\'', '\\\'')
			self.write('"' + t + '"')
		elif (v.type == T_BOOLEAN):
			if (v.data_bool): self.write('true')
			else: self.write('false')
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_float))
		else:
			self.write('[type=' + str(v.type) + ']')
		
	def write_var(self, v, isClass=False):
		#@TODO: Filter out internal ids, like I_BOOL_TRUE, I_BOOL_FALSE
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')
	def write_type(self, t):
		#@TODO: "None" -> void
		if (t == T_BOOLEAN): self.write('bool')
		elif (t == T_INTEGER): self.write('int')
		elif (t == T_FLOAT): self.write('float')
		elif (t == T_STRING): self.write('char *')
		else:
			self.write(str(t))

