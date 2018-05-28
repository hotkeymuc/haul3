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

JAVA_GLUE_CODE_PRE = '''
//### Java glue code (pre)
'''

JAVA_GLUE_CODE_POST = '''//### Java glue code (post)'''


class HAULWriter_java(HAULWriter):
	"Writes Java code"
	
	# Translation of (internal) infix representation to language functions
	
	def __init__(self, streamOut):
		HAULWriter.__init__(self, streamOut)
		self.defaultExtension = 'java'
		self.writeComment('Translated from HAUL3 to Java on ' + str(datetime.datetime.now()) )
		
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def writeComment(self, t):
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
		
	def writeFunc(self, f, indent=0, parentClassName=None):
		f.destination = self.streamOut.size	# Record offset in output stream
		
		###self.writeNamespace(f.namespace, indent)
		
		name = f.id.name
		if (not parentClassName == None):
			if (name == A_INIT):
				name = parentClassName
			else:
				if name == '__repr__': name = 'toString'
				#name = parentClassName + '.' + name
		
		self.writeIndent(indent)
		
		if (parentClassName == None):
			self.write('static ')
		
		if (f.id.name != A_INIT):	# Java initializers have no return value
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
		self.writeBlock(f.block, indent+1)
		
		self.writeIndent(indent)
		self.write('}\n')
		
	def writeModule(self, m, indent=0, package='wtf.haul'):
		m.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeComment('### Begin of Module "' + m.name + '"')
		
		self.write('//package ' + str(m.namespace) + '\n')
		
		self.write('package ')
		self.write(package)
		self.write(';\n')
		
		
		#self.write('### Module namespace...\n')
		self.writeNamespace(m.namespace, indent)
		
		self.write(JAVA_GLUE_CODE_PRE)
		
		if (len(m.imports) > 0):
			self.write('\n')
			self.writeComment('### Imports...')
			for im in m.imports:
				self.write('// import ')
				self.write(str(im))
				self.write(';\n')
			self.write('\n')
		
		
		if (len(m.classes) > 0):
			self.write('\n')
			self.writeComment('### Classes...')
			for typ in m.classes:
				self.writeClass(typ, indent)
				self.write('\n')
		
		self.write('\n')
		self.writeComment('### Root Block (main function)...')
		
		# Wrap all functions into a class
		self.writeIndent(indent)
		self.write('public class ')
		#self.write(m.name.capitalize())
		self.write(m.name)
		self.write(' implements IMain')
		self.write(' {\n')
		
		self.writeIndent(indent+1)
		self.write('public static void main(String[] args) {\n')
		self.writeIndent(indent+2)
		self.write('new ')
		self.write(m.name)
		self.write('()._main();\n')
		self.writeIndent(indent+1)
		self.write('}\n')
		
		
		if (len(m.funcs) > 0):
			#self.write('\n')
			self.writeIndent(indent+1)
			self.writeComment('### Functions...')
			for func in m.funcs:
				self.writeFunc(func, indent+1, parentClassName=None)
				#self.write('\n')
		
		
		self.writeIndent(indent+1)
		#self.write('public static void main(String[] args) {\n')
		self.write('public void _main() {\n')
		
		if (m.block):
			self.writeBlock(m.block, indent+2)
		
		self.writeIndent(indent+1)
		self.write('}\n')
		
		self.writeIndent(indent)
		self.write('}\n')
		
		self.write(JAVA_GLUE_CODE_POST)
		#self.write('\n')
		
		self.writeComment('### End of Module')
		
	
	def writeClass(self, c, indent=0):
		c.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeIndent(indent)
		self.writeComment('# Class "' + c.id.name + '"')
		
		self.writeIndent(indent)
		self.write('class ' + c.id.name + ' {\n')
		
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
			self.writeNamespace(c.namespace, indent+1)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.writeFunc(func, indent+1, parentClassName=c.id.name)
		
		# Restore sanity
		c.namespace = nsOld
		
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		self.writeIndent(indent)
		self.write('}\n')
		
	def writeBlock(self, b, indent=0):
		b.destination = self.streamOut.size	# Record offset in output stream
		
		#self.writeComment("# Block \"" + b.name + "\"")
		
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
			self.writeComment(i.comment)
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
				self.writeBlock(c.blocks[j], indent+1)
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
				self.writeBlock(c.blocks[j], indent+1)
				self.writeIndent(indent)
				self.write('}\n')
		
		elif (c.controlType == C_FOR):
			self.write('for (')
			self.writeExpression(c.exprs[0])
			
			self.write(' in ')
			self.writeExpression(c.exprs[1])
			"""
			#@FIXME: Dirty hack to handle xrange (only simplest case)
			
			if (c.exprs[1].call.id.name == 'xrange'):
				self.write(' = 0; ')
				self.writeExpression(c.exprs[0])
				self.write(' < ')
				self.writeExpression(c.exprs[1].call.args[0])
				self.write('; ')
				self.writeExpression(c.exprs[0])
				self.write('++')
			"""
			
			self.write(') {\n')
			self.writeBlock(c.blocks[0], indent+1)
			self.writeIndent(indent)
			self.write('}\n')
		elif (c.controlType == C_WHILE):
			self.write('while (')
			self.writeExpression(c.exprs[0])
			self.write(') {\n')
			self.writeBlock(c.blocks[0], indent+1)
			self.writeIndent(indent)
			self.write('}')
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
			self.write('throw ')
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
			if ((c.args[0].returnType == T_STRING) or (c.args[1].returnType == T_STRING)):
				isStr = True
			else:
				isStr = False
			
			if (isStr) and (i == '=='):
				self.writeExpression(c.args[0], level)	# level-1
				self.write('.equals(')
				self.writeExpression(c.args[1], level)	# level-1
				self.write(')')
			elif (isStr) and (i == '!='):
				self.write('!')
				self.writeExpression(c.args[0], level)	# level-1
				self.write('.equals(')
				self.writeExpression(c.args[1], level)	# level-1
				self.write(')')
			else:
				self.writeExpression(c.args[0], level)	# level-1
				self.write(' ' + INFIX_TRANS[i] + ' ')
				self.writeExpression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			
			# Check if it is a constructor call
			ns = c.id.namespace
			iid = ns.find_id(i)
			if (iid.kind == K_CLASS):
				# If ns.findId returns kind=K_FUNCTION it is a standard call, if it is K_CLASS it is an instantiation (call of constructor)!
				self.write('new ')
			
			#@FIXME: Check for library calls (This could also be done in the HAULReader)
			if i in ['put', 'fetch', 'shout', 'put_direct']:
				self.write('hio.')	# Add HIO prefix
			elif (i == 'int_str'):
				i = 'Integer.toString'
			
			
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
			#@TODO: Escaping!
			t = v.data
			t = t.replace('\\', '\\\\')
			t = t.replace('"', '\\"')
			t = t.replace('\r', '\\r')
			t = t.replace('\n', '\\n')
			t = t.replace('\'', '\\\'')
			self.write('"' + t + '"')
		else:
			self.write(str(v))	#.data
			
	def writeVar(self, v, isClass=False):
		#@FIXME: Translation! V_TRUE or something
		#if (v.data == '#true'): self.write('true')
		#elif (v.data == '#false'): self.write('false')
		#else:
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')
	def writeType(self, t):
		
		if (t == T_INTEGER): t = 'int'
		elif (t == T_STRING): t = 'String'
		elif (t == T_BOOLEAN): t = 'Boolean'
		elif (t == T_NOTHING): t = 'void'
		elif (t == None): t = 'void'
		self.write(str(t))

