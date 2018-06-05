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
	
	def __init__(self, stream_out):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'java'
		self.write_comment('Translated from HAUL3 to Java on ' + str(datetime.datetime.now()) )
		
	def write_indent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def write_comment(self, t):
		"Add a comment to the file"
		if ('\n' in t):
			self.stream_out.put('/* ' + t + '*/\n')
		else:
			self.stream_out.put('// ' + t + '\n')
		
	def write_namespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			#self.write_indent(indent)
			#self.write('/**\n')
			
			#self.write_indent(indent)
			#self.write(' * Namespace "' + str(ns) + '":\n')
			
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				#self.write_indent(indent)
				#self.write(' * @' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) + '\n')
				
				if (id.kind == K_VARIABLE):
					self.write_indent(indent)
					self.write_type(id.data_type)
					self.write(' ')
					self.write(id.name)
					
					if (id.data_value != None):
						self.write(' = ')
						self.write_value(id.data_value)
					self.write(';\n')
			
			#self.write_indent(indent)
			#self.write(' */\n')
		
	def write_function(self, f, indent=0, parentClassName=None):
		f.destination = self.stream_out.ofs	# Record offset in output stream
		
		###self.write_namespace(f.namespace, indent)
		
		name = f.id.name
		if (not parentClassName == None):
			if (name == A_INIT):
				name = parentClassName
			else:
				if name == '__repr__': name = 'toString'
				#name = parentClassName + '.' + name
		
		self.write_indent(indent)
		
		if (parentClassName == None):
			self.write('static ')
		
		if (f.id.name != A_INIT):	# Java initializers have no return value
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
			self.write_var(f.args[i], namespace=f.namespace)
			j += 1
		self.write(') {\n')
		
		if (BLOCKS_HAVE_LOCAL_NAMESPACE == False):
			# In this case, function arguments AND local variables share the same namespace
			# This will lead to Java errors (variable X is already defined in method)
			self.write_namespace(f.namespace, indent+1)
		
		self.write_block(f.block, indent+1, namespace=f.namespace)
		
		self.write_indent(indent)
		self.write('}\n')
		
	def write_module(self, m, indent=0, package='wtf.haul'):
		m.destination = self.stream_out.ofs	# Record offset in output stream
		
		self.write_comment('### Begin of Module "' + m.name + '"')
		
		self.write('//package ' + str(m.namespace) + '\n')
		
		self.write('package ')
		self.write(package)
		self.write(';\n')
		
		
		#self.write('### Module namespace...\n')
		#self.write_namespace(m.namespace, indent)
		
		self.write(JAVA_GLUE_CODE_PRE)
		
		if (len(m.imports) > 0):
			self.write('\n')
			self.write_comment('### Imports...')
			for im in m.imports:
				self.write('// import ')
				self.write(str(im))
				self.write(';\n')
			self.write('\n')
		
		
		if (len(m.classes) > 0):
			self.write('\n')
			self.write_comment('### Classes...')
			for typ in m.classes:
				self.write_class(typ, indent)
				self.write('\n')
		
		self.write('\n')
		self.write_comment('### Root Block (main function)...')
		
		# Wrap all functions into a class
		self.write_indent(indent)
		self.write('public class ')
		#self.write(m.name.capitalize())
		self.write(m.name)
		#self.write(' implements IMain')	# Requires interface IMain
		self.write(' {\n')
		
		self.write_indent(indent+1)
		self.write('public static void main(String[] args) {\n')
		self.write_indent(indent+2)
		self.write('new ')
		self.write(m.name)
		self.write('()._main();\n')
		self.write_indent(indent+1)
		self.write('}\n')
		
		
		if (len(m.funcs) > 0):
			#self.write('\n')
			self.write_indent(indent+1)
			self.write_comment('### Functions...')
			for func in m.funcs:
				self.write_function(func, indent+1, parentClassName=None)
				#self.write('\n')
		
		
		self.write_indent(indent+1)
		#self.write('public static void main(String[] args) {\n')
		self.write('public void _main() {\n')
		
		if (m.block):
			self.write_block(m.block, indent+2, namespace=m.namespace)
		
		self.write_indent(indent+1)
		self.write('}\n')
		
		self.write_indent(indent)
		self.write('}\n')
		
		self.write(JAVA_GLUE_CODE_POST)
		#self.write('\n')
		
		self.write_comment('### End of Module')
		
	
	def write_class(self, c, indent=0):
		c.destination = self.stream_out.ofs	# Record offset in output stream
		
		self.write_indent(indent)
		self.write_comment('# Class "' + c.id.name + '"')
		
		self.write_indent(indent)
		self.write('class ' + c.id.name + ' {\n')
		
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
			self.write_namespace(c.namespace, indent+1)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.write_function(func, indent+1, parentClassName=c.id.name)
		
		# Restore sanity
		c.namespace = nsOld
		
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		self.write_indent(indent)
		self.write('}\n')
		
	def write_block(self, b, indent=0, namespace=None):
		b.destination = self.stream_out.ofs	# Record offset in output stream
		
		#self.write_comment("# Block \"" + b.name + "\"")
		ns = namespace
		if (BLOCKS_HAVE_LOCAL_NAMESPACE == True):
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.write_indent(indent)
				#self.write('### Block namespace...\n')
				self.write_namespace(b.namespace, indent)
				
				"""
				# Pre-define vars
				for id in b.namespace.ids:
					#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
					if (id.kind == K_VARIABLE):
						self.write_indent(indent)
						self.write_type(id.data_type)
						self.write(' ')
						self.write(str(id.name) + ';\n')
				"""
				ns = b.namespace
		
		for instr in b.instrs:
			self.write_indent(indent)
			self.write_instruction(instr, indent, namespace=ns)
			#self.write(';')
			self.write('\n')
			
	def write_instruction(self, i, indent, namespace):
		i.destination = self.stream_out.ofs	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.comment):
			self.write_comment(i.comment)
			self.write_indent(indent)
			
		if (i.control): self.write_control(i.control, indent, namespace=namespace)
		if (i.call):
			self.write_call(i.call, namespace=namespace)
			self.write(';')
		
	def write_control(self, c, indent=0, namespace=None):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('else ')
				self.write('if (')
				
				self.write_expression(c.exprs[j], namespace=namespace)
				self.write(') {\n')
				self.write_block(c.blocks[j], indent+1, namespace=namespace)
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
				self.write_block(c.blocks[j], indent+1, namespace=namespace)
				self.write_indent(indent)
				self.write('}\n')
		
		elif (c.controlType == C_FOR):
			self.write('for (')
			self.write_expression(c.exprs[0], namespace=namespace)
			
			self.write(' in ')
			self.write_expression(c.exprs[1], namespace=namespace)
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
			self.write_block(c.blocks[0], indent+1, namespace=namespace)
			self.write_indent(indent)
			self.write('}\n')
		elif (c.controlType == C_WHILE):
			self.write('while (')
			self.write_expression(c.exprs[0], namespace=namespace)
			self.write(') {\n')
			self.write_block(c.blocks[0], indent+1, namespace=namespace)
			self.write_indent(indent)
			self.write('}')
		elif (c.controlType == C_RETURN):
			self.write('return')
			if (len(c.exprs) > 0):
				self.write(' ')
				self.write_expression(c.exprs[0], namespace=namespace)
			self.write(';')
		elif (c.controlType == C_BREAK):
			self.write('break;')
		elif (c.controlType == C_CONTINUE):
			self.write('continue;')
		elif (c.controlType == C_RAISE):
			self.write('throw ')
			self.write_expression(c.exprs[0], namespace=namespace)
			self.write(';')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def write_call(self, c, level=0, namespace=None):
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.write_var(c.args[0].var)
			self.write_expression(c.args[0], level, namespace=namespace)
			self.write(' = ')
			self.write_expression(c.args[1], level, namespace=namespace)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.write_expression(c.args[0], level, namespace=namespace)
			self.write('[')
			self.write_expression_list(c.args, 1, level, namespace=namespace)
			self.write(']')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('[')
			self.write_expression_list(c.args, 0, level, namespace=namespace)
			self.write(']')
			
		elif i == I_DICT_CONSTRUCTOR.name:
			self.write('{')
			i = 0
			while (i < len(c.args)):
				if (i > 0): self.write(',\t')
				self.write_expression(c.args[i], level=level, namespace=namespace)
				i += 1
				self.write(': ')
				self.write_expression(c.args[i], level=level, namespace=namespace)
				i += 1
			self.write('}')
			
		elif i == I_OBJECT_CALL.name:
			self.write_expression(c.args[0], 0, namespace=namespace)
			self.write('(')
			self.write_expression_list(c.args, 1, 0, namespace=namespace)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.write_expression(c.args[0], 0, namespace=namespace)
			self.write('.')
			self.write_expression(c.args[1], 0, namespace=namespace)
		
		elif (i in INFIX_KEYS):
			
			#@TODO: Check type of both expressions, maybe chose a different function! e.g. str_compare
			if ((c.args[0].returnType == T_STRING) or (c.args[1].returnType == T_STRING)):
				isStr = True
			else:
				isStr = False
			
			if (isStr) and (i == '=='):
				self.write_expression(c.args[0], level, namespace=namespace)	# level-1
				self.write('.equals(')
				self.write_expression(c.args[1], level, namespace=namespace)	# level-1
				self.write(')')
			elif (isStr) and (i == '!='):
				self.write('!')
				self.write_expression(c.args[0], level, namespace=namespace)	# level-1
				self.write('.equals(')
				self.write_expression(c.args[1], level, namespace=namespace)	# level-1
				self.write(')')
			else:
				self.write_expression(c.args[0], level, namespace=namespace)	# level-1
				self.write(' ' + INFIX_TRANS[i] + ' ')
				self.write_expression(c.args[1], level, namespace=namespace)	# level-1
		
		else:
			# Write a standard call
			
			# Check if it is a constructor call
			ns = c.id.namespace
			iid = ns.find_id(i)
			if (iid.kind == K_CLASS):
				# If ns.findId returns kind=K_FUNCTION it is a standard call, if it is K_CLASS it is an instantiation (call of constructor)!
				self.write('new ')
			
			#@FIXME: Check for library calls (This could also be done in the HAULReader)
			# We can see the namespace this call goes to and the current local namespace
			# If the call goes to a different module, we need to add a prefix!
			#put('Need to see if call is external: ' + str(i) + ' (' + str(iid.namespace) + ') VS ' + str(namespace))
			#put('...it is child of ' + str(iid.namespace.parent))
			#if (iid.namespace.has_child
			
			
			# Internals
			if i == I_PRINT.name:
				i = 'System.out.println'
			if i == I_STR.name:
				i = 'Integer.toString'
			if i in ['put', 'fetch', 'shout', 'put_']:
				i = 'hio.' + i
			
			
			self.write(i)
			self.write('(')
			self.write_expression_list(c.args, 0, level, namespace=namespace)
			self.write(')')
			
	def write_expression_list(self, es, start, level, namespace=None):
		i = 0
		for i in xrange(len(es)-start):
			if (i > 0): self.write(', ')
			self.write_expression(es[start+i], level=level, namespace=namespace)
	
	def write_expression(self, e, level=0, namespace=None):
		if (e.value): self.write_value(e.value)
		if (e.var): self.write_var(e.var, namespace=namespace)
		if (e.call):
			if (level > 0): self.write('(')
			self.write_call(e.call, level+1, namespace=namespace)
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
			
	def write_var(self, v, isClass=False, namespace=None):
		# Write out known values
		if (v == I_BOOL_TRUE): self.write_value(v.data_value)
		elif (v == I_BOOL_FALSE): self.write_value(v.data_value)
		elif (v == I_NOTHING): self.write_value(v.data_value)
		else:
			self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')
	def write_type(self, t):
		
		if (t == T_INTEGER): t = 'int'
		elif (t == T_STRING): t = 'String'
		elif (t == T_BOOLEAN): t = 'Boolean'
		elif (t == T_NOTHING): t = 'void'
		elif (t == None): t = 'void'
		self.write(str(t))

