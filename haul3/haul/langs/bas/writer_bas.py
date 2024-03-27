#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

from haul.core import *

def put(t):
	print('HAULWriter_bas:\t' + str(t))


PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '||', '^'
	'>', '<', '==', '>=', '<=',
]

DIALECT_GW = 0
DIALECT_MS = 1

class HAULWriter_bas(HAULWriter):
	"Writes Basic code"
	
	def __init__(self, stream_out, dialect=DIALECT_GW):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'bas'
		
		#self.write_comment('Translated from HAUL3 to BASIC on ' + str(datetime.datetime.now()) )
		
		self.dialect = dialect
		
		# Add line numbers?
		self.line_numbering = False
		self.current_line = 10
		# Have "real" functions (or only GOSUB?)
		self.functions = True
		
		if self.dialect == DIALECT_MS:
			self.line_numbering = True
			self.functions = False
		
	
	def write_nl(self):
		self.write('\n')
		self.current_line = self.current_line + 10
		if self.line_numbering == True:
			self.write(str(self.current_line) + ' ')
	
	def write_comment(self, t):
		"Add a comment to the file"
		self.write('\'' + t)
		self.write_nl()
		#self.stream_out.put('REM ' + t + '\n')
		#self.stream_out.put('REM ' + t + '\n')
		
	def write_indent(self, num):
		r = ''
		for i in range(num):
			r += '\t'
		self.write(r)
		
	def write_namespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.write_indent(indent)
			self.write_comment('Namespace "' + str(ns) + '"')
			
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data))
				if (id.name == 'res'): continue	# Do not (re-)declare result
				if (id.kind == 'var'):
					self.write_indent(indent)
					#self.write('#@' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data) + '\n')
					#self.write('DIM ' + str(id.name))
					self.write('DIM ' + str(id.name))
					self.write('	\' AS ')
					self.write_type(id.data_type)
					self.write_nl()
		
	def write_function(self, f, indent=0):
		f.destination = self.stream_out.ofs	# Record offset in output stream
		
		#@TODO: Resollve GOSUB <f.id>
		f.line_number = self.current_line
		f.id.user = self.current_line
		
		#self.write_namespace(f.namespace, indent)
		self.write_indent(indent)
		
		if (self.functions):
			self.write('FUNCTION ')
			self.write(f.id.name)
			
			if (len(f.args) > 0):
				self.write('(')
				for i in range(len(f.args)):
					if (i > 0): self.write(', ')
					#self.write_expression(args[i])
					self.write_var(f.args[i])
					"""
					# QBasic:
					id = f.namespace.findId(f.args[i].name)
					if (id == None):
						#self.write_comment('UnknownType')
						pass
					else:
						self.write(' AS ')
						self.write_type(id.data)
					"""
				self.write(')')
		else:
			# No support for "real" functions
			self.write('\'Function ' + f.id.name)
			
		self.write_nl()
		
		#if self.dialect == DIALECT_OPL:
		#	self.write_namespace(f.namespace, indent+1)
		self.write_block(f.block, indent+1)
		
		if (self.functions):
			self.write('END FUNCTION')
		else:
			self.write('RETURN \'End of ' + f.id.name)
		self.write_nl()
		
		#@TODO: Resolve GOSUB <end of f.id>
		
		self.write_indent(indent)
		self.write_nl()
		
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.ofs	# Record offset in output stream
		if self.line_numbering == True:
			# Initial line
			self.write(str(self.current_line) + ' ')
		
		self.write_comment('### Module "' + m.name + '"')
		self.write_comment('Translated from HAUL3 to BASIC on ' + str(datetime.datetime.now()) )
		
		for im in m.imports:
			"""
			self.write('\'INCLUDE ')
			self.write(str(im))
			self.write_nl()
			"""
			
			#self.write('LOADM "' + str(im) + '"\n')	# Not compatible with old OPL, gives error
			
		#self.write('### Module namespace...\n')
		self.write_namespace(m.namespace, indent)
		
		self.write_comment('### Root Block (main function):')
		if (m.block):
			self.write_block(m.block, indent)
			# Terminate main block
			self.write('END')
			self.write_nl()
		
		#@FIXME: Old OPL needs to have each PROC in its own file. Newer OPL can have "PROC xxx:" in source
		### OPL seems to need the procs at the bottom (after main proc)
		self.write_comment('### Classes...')
		for typ in m.classes:
			self.write_class(typ, indent)
		
		self.write_comment('### Funcs...')
		for func in m.funcs:
			self.write_function(func, indent)
		
		# Fill last line
		if self.line_numbering == True:
			self.write('REM End of module\n')
		
	
	def write_class(self, c, indent=0):
		c.destination = self.stream_out.ofs	# Record offset in output stream
		
		#self.write_comment('# Class "' + c.id.name + '"\n')
		self.write_indent(indent)
		self.write('class ')
		self.write(c.id.name)
		self.write(':')
		self.write_nl()
		
		if (c.namespace):
			self.write_namespace(c.namespace, indent+1)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.write_function(func, indent+1)
		
	def write_block(self, b, indent=0):
		b.destination = self.stream_out.ofs	# Record offset in output stream
		
		#@TODO: Resolve GOSUB <b.id>
		b.line_number = self.current_line
		
		#self.write_comment("# Block \"" + b.name + "\"\n")
		for instr in b.instrs:
			if (instr.control) or (instr.call):
				self.write_indent(indent)
				self.write_instruction(instr, indent)
				
			if (instr.comment):
				self.write('\'')
				self.write(instr.comment)
				
			self.write_nl()
		
		#@TODO: Resolve GOSUB <end of b.id>
		
	def write_instruction(self, i, indent):
		i.destination = self.stream_out.ofs	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.control):
			self.write_control(i.control, indent)
		if (i.call):
			self.write_call(i.call)
		
	def write_control(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0):
					self.write_indent(indent)
					self.write('ELSE ')	# "ELSEIF" in OPL
				self.write('IF ')
				
				self.write_expression(c.exprs[j])
				#self.write(')')
				self.write(' THEN')
				self.write_nl()
				self.write_block(c.blocks[j], indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.write_indent(indent)
				self.write('ELSE')
				self.write_nl()
				self.write_block(c.blocks[j], indent+1)
			
			self.write_indent(indent)
			self.write('END IF')
			self.write_nl()
		
		elif (c.controlType == C_FOR):
			self.write('FOR ')
			self.write_expression(c.exprs[0])
			self.write(' in ')
			self.write_expression(c.exprs[1])
			self.write_nl()
			self.write_block(c.blocks[0], indent+1)
			
			self.write('NEXT ')
			self.write_expression(c.exprs[0])
			
		elif (c.controlType == C_RETURN):
			if (self.functions == True):
				self.write('RETURN ')
				self.write_expression(c.exprs[0])
			else:
				self.resolve_expressions(c.exprs, 0, 0)
				self.write('R = ')
				self.write_expression_list(c.exprs, 0, 0)
				self.write_nl()
				self.write_indent(indent)
				self.write('RETURN')
				
				
			#self.write_nl()
		else:
			self.write_comment('CONTROL "' + str(c.controlType) + '"')
			self.write_nl()
		
	def write_call(self, c, level=0):
		i = c.id.name
		
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.write_var(c.args[0].var)
			self.resolve_expressions(c.args, 1, level)
			
			self.write_expression(c.args[0], level)
			self.write(' = ')
			self.write_expression_list(c.args, 1, level)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.resolve_expressions(c.args, 1, level)
			self.write_expression(c.args[0], level)
			self.write('(')
			self.write_expression_list(c.args, 1, level)
			self.write(')')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			#@FIXME: Write it out...
			self.resolve_expressions(c.args, 0, level)
			self.write('(')
			self.write_expression_list(c.args, 0, level)
			self.write(')')
			
		elif i == I_OBJECT_CALL.name:
			#@FIXME: Not trivially supported in GW
			self.resolve_expressions(c.args, 1, level)
			self.write_expression(c.args[0], level)
			self.write('(')
			self.write_expression_list(c.args, 1, level)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.resolve_expressions(c.args, 1, level)
			self.write_expression(c.args[0], level)
			self.write('.')
			self.write_expression_list(c.args, 1, level)
		
		elif any(i in p for p in PAT_INFIX):
			self.resolve_expressions(c.args, 0, level)
			
			self.write_expression(c.args[0], level)	# level-1
			
			self.write(' ' + i + ' ')
			
			self.write_expression_list(c.args, 1, level)	# level-1
		
		else:
			# Write a standard call
			
			# Internals
			is_internal = False
			if i == I_PRINT.name:
				i = 'PRINT'
				is_internal = True
			elif (i == I_STR.name):
				i = 'STR$'
				is_internal = True
			
			
			if (self.functions == True) or (is_internal == True):
				self.resolve_expressions(c.args, 0, level)
				
				#if (level == 0): #self.write('CALL ')
				self.write(i)
				
				if (len(c.args) > 0):
					self.write('(')
					self.write_expression_list(c.args, 0, level)
					self.write(')')
				
			else:
				# No "real" function, so convert it to a GOSUB
				self.write_comment('Call function ' + str(i))
				
				# Prepare function arguments
				f = c.id.data_function
				j = 0
				for j in range(len(f.args)):
					# Set the function arguments (variabes) directly
					fa = f.args[j]
					a = c.args[j]
					
					# Create a virtua HAULCall to set that var
					c2 = HAULCall(I_VAR_SET)
					e2 = HAULExpression()
					e2.var = fa
					c2.args.append(e2)
					c2.args.append(a)
					self.write_call(c2)
					self.write_nl()
					j = j + 1
					
				self.write('GOSUB ??? \'' + i + '')
				
				self.write_nl()
			
		
	def resolve_expressions(self, es, start, level=0):
		if self.functions == True: return
		
		i = 0
		for i in range(len(es)-start):
			e = es[start+i]
			if (e.call != None) and (not e.call.id.name in PAT_INFIX):
				self.write_comment('Resolve GOSUB call to ' + e.call.id.name)
				
				self.write_expression(e, 0)
				
				self.write_resolved_variable(i, e.call.id.data_type)
				self.write(' = ')
				self.write('R')
				#self.write_type(e.call.id.data_type)
				self.write_nl()
			
		
	def write_resolved_variable(self, i, typ):
		self.write('A')
		self.write(str(i))
		self.write_type(typ)
	
	def write_expression_list(self, es, start, level):
		i = 0
		for i in range(len(es)-start):
			e = es[start+i]
			if (i > 0): self.write(', ')
			
			if (self.functions == False) and (e.call != None) and (not e.call.id.name in PAT_INFIX):
				self.write_resolved_variable(i, e.call.id.data_type)
				
			else:
				self.write_expression(e, level=level)
			
			
	
	def write_expression(self, e, level=0):
		if (e.value): self.write_value(e.value)
		if (e.var): self.write_var(e.var)
		if (e.call):
			if (level > 0): self.write('(')
			self.write_call(e.call, level+1)
			if (level > 0): self.write(')')
			
	def write_value(self, v):
		if (v.type == T_STRING):
			t = v.data_str
			t = t.replace('\r', '"+CHR$(13)+"')
			t = t.replace('\n', '"+CHR$(10)+"')
			t = t.replace('"', '"+CHR$(34)+"')
			self.write('"' + t + '"')
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_float))
		elif (v.type == T_BOOLEAN):
			if (v.data_bool == True):
				self.write('TRUE')
			else:
				self.write('FALSE')
		else:
			self.write('[type=' + v.type + '?]')
	
	def write_type(self, v):
		if (v == T_INTEGER):	self.write('%')
		elif (v == T_FLOAT):	pass	# self.write('#')
		elif (v == T_STRING):	self.write('$')
		#else:
		#	self.write(str(v))
			
		
	def write_var(self, v):
		self.write(v.name)
		
		# Add type identifier
		#self.write('[' + v.parentNamespace.name + ':' + v.name + ']')
		#id = v.parentNamespace.findId(v)
		self.write_type(v.data_type)


