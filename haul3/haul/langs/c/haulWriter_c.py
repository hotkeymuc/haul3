#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

TODO:


"""

import datetime
import copy

from haul.haul import *

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
//### Arduino glue code (pre) from haulWriter_c. Should go to platforms/arduino
#define print(t)	Serial.println(t)
#define str(i)	i

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
	
	def __init__(self, streamOut, dialect=DIALECT_C):
		HAULWriter.__init__(self, streamOut)
		self.defaultExtension = 'c'
		self.write_comment('Translated from HAUL3 to C on ' + str(datetime.datetime.now()) )
		
		self.dialect = dialect
		
	
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def write_comment(self, t):
		"Add a comment to the file"
		self.streamOut.put('// ' + t + '\n')
		
	def writeNamespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.writeIndent(indent)
			self.write('/**\n')
			
			self.writeIndent(indent)
			self.write(' * Namespace "' + str(ns) + '":\n')
			
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				self.writeIndent(indent)
				self.write(' * @' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) + '\n')
			
			self.writeIndent(indent)
			self.write(' */\n')
		
	def write_function(self, f, indent=0, parentClassName=None):
		f.destination = self.streamOut.size	# Record offset in output stream
		###self.writeNamespace(f.namespace, indent)
		
		name = f.id.name
		if (not parentClassName == None):
			if (name == A_INIT):
				name = parentClassName
			else:
				if name == '__repr__': name = 'toString'
				name = parentClassName + '.' + name
		
		self.writeIndent(indent)
		
		if (self.dialect == DIALECT_Z88DK) and (f.id.data_type == None):
			# Z88DK: Do not add "void" in front of methods
			pass
		else:
			self.writeType(f.id.data_type)	# Return type
			self.write(' ')
		
		self.write(name)	# Name
		self.write('(')
		j = 0
		for i in xrange(len(f.args)):
			if (i == 0) and (not parentClassName == None):
				# skip first "self"
				continue
				
			if (j > 0): self.write(', ')
			#self.writeExpression(args[i])
			
			self.writeType(f.args[i].data_type)
			self.write(' ')
			self.writeVar(f.args[i])
			j += 1
		self.write(') {\n')
		
		#self.writeNamespace(f.namespace, indent+1)
		self.write_block(f.block, indent+1)
		
		self.writeIndent(indent)
		self.write('}\n')
		
	def write_module(self, m, indent=0):
		m.destination = self.streamOut.size	# Record offset in output stream
		self.write_comment('### Begin of Module "' + m.name + '"')
		
		#self.write('### Module namespace...\n')
		self.writeNamespace(m.namespace, indent)
		
		if self.dialect == DIALECT_ARDUINO:
			self.write(GLUE_ARDUINO_PRE);
		
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
					self.write('.c"\n')
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
			self.write('void main_internal() {\n')
		elif self.dialect == DIALECT_Z88DK:
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
		elif self.dialect == DIALECT_ARDUINO:
			self.write('}\n')
			self.write(GLUE_ARDUINO_POST);
		elif self.dialect == DIALECT_Z88DK:
			self.write('}\n')
			#self.write(GLUE_Z88DK_POST);
		else:
			self.writeIndent(1)
			self.write('return 0;\n')
			self.write('}\n')
		
		
		self.write('\n')
		self.write_comment('### End of Module')
		
	
	def write_class(self, c, indent=0):
		c.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeIndent(indent)
		self.write_comment('# Class "' + c.id.name + '"')
		
		
		# Because we will mess up the namespace
		nsOld = c.namespace
		c.namespace = copy.copy(nsOld)
		
		if (c.namespace):
			# Fix self --> this
			selfId = c.namespace.get_id(name=A_SELF, kind=K_VARIABLE)
			if not selfId == None:
				selfId.name = 'this'
			
			#self.writeIndent(indent+1)
			#self.write('### Class namespace...\n')
			self.writeNamespace(c.namespace, indent+0)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.write_function(func, indent+0, parentClassName=c.id.name)
		
		# Restore sanity
		c.namespace = nsOld
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		
	def write_block(self, b, indent=0):
		b.destination = self.streamOut.size	# Record offset in output stream
		
		#self.write_comment("# Block \"" + b.name + "\"")
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.writeIndent(indent)
				#self.write('### Block namespace...\n')
				###self.writeNamespace(b.namespace, indent)
				
				# Pre-define vars
				for id in b.namespace.ids:
					#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
					if (id.kind == K_VARIABLE):
						self.writeIndent(indent)
						self.writeType(id.data_type)
						self.write(' ')
						self.write(str(id.name) + ';\n')
		
		for instr in b.instrs:
			self.writeIndent(indent)
			self.writeInstr(instr, indent)
			#self.write(';')
			self.write('\n')
			
	def writeInstr(self, i, indent):
		i.destination = self.streamOut.size	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.comment):
			self.write_comment(i.comment)
			self.writeIndent(indent)
			
		if (i.control): self.writeControl(i.control, indent)
		if (i.call):
			self.writeCall(i.call)
			self.write(';')
		
	def writeControl(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('else ')
				self.write('if (')
				
				self.writeExpression(c.exprs[j])
				self.write(') {\n')
				self.write_block(c.blocks[j], indent+1)
				self.writeIndent(indent)
				self.write('}')
				if (j < len(c.blocks)):
					self.write(' ')
				else:
					self.write('\n')
				j += 1
			
			if (j < len(c.blocks)):
				self.writeIndent(indent)
				self.write('else {\n')
				self.write_block(c.blocks[j], indent+1)
				self.writeIndent(indent)
				self.write('}\n')
		
		elif (c.controlType == C_FOR):
			self.write('for (')
			self.writeExpression(c.exprs[0])
			
			#self.write(' in ')
			#self.writeExpression(c.exprs[1])
			if (len(c.exprs) < 2):
				put('TOO LESS FOR EXPRESSIONS!')
				self.write_comment('Too less expressions: ')
				self.writeExpressionList(c.exprs)
			
			elif ((c.exprs[1].call != None) and (c.exprs[1].call.id.name == 'xrange')):
				self.write(' = 0; ')
				self.writeExpression(c.exprs[0])
				self.write(' < ')
				self.writeExpression(c.exprs[1].call.args[0])
				self.write('; ')
				self.writeExpression(c.exprs[0])
				self.write('++')
			else:
				put('UNHANDLED FOR CONSTRUCT: ' + str(c.exprs))
				#self.write_comment('Unhandled kind of for-loop construct: ')
				#self.write(str(c.exprs))
				self.write(' in ')
				self.writeExpression(c.exprs[1])
			
			
			self.write(') {\n')
			self.write_block(c.blocks[0], indent+1)
			self.writeIndent(indent)
			self.write('}\n')
		elif (c.controlType == C_WHILE):
			self.write('while (')
			self.writeExpression(c.exprs[0])
			self.write(') {\n')
			self.write_block(c.blocks[0], indent+1)
			self.writeIndent(indent)
			self.write('}\n')
		elif (c.controlType == C_RETURN):
			self.write('return')
			if (len(c.exprs) > 0):
				self.write(' ')
				self.writeExpression(c.exprs[0])
			self.write(';')
		elif (c.controlType == C_BREAK):
			self.write('break;')
		elif (c.controlType == C_CONTINUE):
			self.write('continue;')
		elif (c.controlType == C_RAISE):
			self.write('raise ')
			self.writeExpression(c.exprs[0])
			self.write(';')
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
			self.writeExpression(c.args[0], 0)
			self.write('(')
			self.writeExpressionList(c.args, 1, 0)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.writeExpression(c.args[0], 0)
			self.write('.')
			self.writeExpression(c.args[1], 0)
		
		elif (i in INFIX_KEYS):
			
			#@TODO: Check type of both expressions, maybe chose a different function! e.g. str_compare
			if ((i == '==') and ((c.args[0].returnType == T_STRING) or (c.args[1].returnType == T_STRING))):
				self.write('str_compare(')
				self.writeExpressionList(c.args, 0, level)	# level-1
				self.write(')')
			elif ((i == '!=') and ((c.args[0].returnType == T_STRING) or (c.args[1].returnType == T_STRING))):
				self.write('str_compare(')
				self.writeExpressionList(c.args, 0, level)	# level-1
				self.write(') == 0')
			else:
				self.writeExpression(c.args[0], level)	# level-1
				
				#if (i in HAULWriter_py.INFIX):
				#	self.write(' ' + HAULWriter_py.INFIX[i] + ' ')
				#else:
				self.write(' ' + INFIX_TRANS[i] + ' ')
				
				self.writeExpression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			
			# Check if it is a constructor call
			ns = c.id.namespace
			iid = ns.find_id(i)
			if (iid.kind == K_TYPE):
				# If ns.find_id returns kind=K_FUNCTION it is a standard call, if it is K_TYPE it is an instantiation (call of constructor)!
				self.write('new ')
			
			self.write(i)
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
			s = v.data
			s = s.replace('"', '\\"')
			self.write('"' + s + '"')	#@TODO: Escaping!
		else:
			self.write(str(v))	#.data
			
	def writeVar(self, v, isClass=False):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')
	def writeType(self, t):
		#@TODO: "None" -> void
		if (t == T_BOOLEAN): self.write('bool')
		elif (t == T_INTEGER): self.write('int')
		elif (t == T_FLOAT): self.write('float')
		elif (t == T_STRING): self.write('char *')
		else:
			self.write(str(t))

