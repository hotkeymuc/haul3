#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

from haul.core import *

class HAULWriter_json(HAULWriter):
	"Writes JSON representation"
	def __init__(self, stream_out):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'json'
		self.write_comment('Translated from HAUL to JSON on ' + str(datetime.datetime.now()))
		
	def write_comment(self, t):
		"Add a comment to the file - NOT for JSON!"
		#self.stream_out.put('// ' + t + '\n')
		put('NOT adding comment to file: "' + t + '"')
		
	def write_indent(self, num):
		r = ''
		for i in range(num):
			r += '\t'
		self.write(r)
	
	def writeId(self, id):
		#self.write('"' + id.name + '"')
		self.write('"' + str(id.namespace) + ':' + id.name + '"')
	
	def writeArray(self, arr, cb, indent=0):
		if (len(arr) == 0):
			self.write('[]')
			return
			
		self.write('[' + '\n')
		
		i = 0
		for item in arr:
			if (i > 0): self.write(',' + '\n')
			self.write_indent(indent+1)
			cb(item, indent+1)
			i += 1
		
		self.write('\n')
		self.write_indent(indent)
		self.write(']')
	
	def write_var(self, v, indent=0):
		#self.write('"' + v.id.name + '"')
		self.write(v.name)
	
	def write_namespace(self, ns, indent=0):
		self.write('{\n')
		
		#self.write('\t/* ' + str(ns) + ' */\n')
		
		i = 0
		for id in ns.ids:
			if (i > 0):
				self.write(',')
				self.write('\n')
			
			#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data))
			self.write_indent(indent+1)
			self.write(id.name)
			self.write(': {')
			self.write('kind: "' + str(id.kind) + '", ')
			self.write('data_type: "' + str(id.data_type) + '", ')
			self.write('data_value: "' + str(id.data_value) + '"')
			self.write('}')
			i += 1
		if (i > 0): self.write('\n')
		self.write_indent(indent)
		self.write('}')
	
	def write_function(self, f, indent=0):
		self.write('{' + '\n')
		
		self.write_indent(indent+1)
		#self.write('"id": "' + f.id.name + '",' + '\n')
		self.write('"id": ')
		self.writeId(f.id)
		self.write(',' + '\n')
		
		if (not f.id.data_type == None):
			self.write_indent(indent+1)
			self.write('"type": "' + f.id.data_type + '",' + '\n')
		
		if (f.namespace and len(f.namespace.ids) > 0):
			self.write_indent(indent+1)
			self.write('"namespace": ')
			self.write_namespace(f.namespace, indent+1)
			self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"args": ')
		self.writeArray(f.args, self.write_var, indent+1)
		self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"block": ')
		if (f.block):
			self.write_block(f.block, indent+1)
		else:
			self.write('null')
		self.write('\n')
		
		self.write_indent(indent)
		self.write('}')
		
	def write_module(self, m, indent=0):
		self.write('{' + '\n')
		#self.write('\t' + '//Module "' + m.id.name + '"\n')
		
		if (m.namespace and len(m.namespace.ids) > 0):
			self.write_indent(indent+1)
			self.write('"namespace": ')
			self.write_namespace(m.namespace, indent+1)
			self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"imports": [')
		i = 0
		for im in m.imports:
			if (i > 0): self.write(', ')
			self.write('"' + str(im) + '"')
			i += 1
		self.write('],' + '\n')
		
		self.write_indent(indent+1)
		self.write('"classes": ')
		self.writeArray(m.classes, self.write_class, indent+1)
		self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"funcs": ')
		self.writeArray(m.funcs, self.write_function, indent+1)
		self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"block": ')
		if (m.block):
			self.write_block(m.block, indent+1)
		else:
			self.write('null')
		self.write('\n')
		
		self.write_indent(indent)
		self.write('}' + '\n')
		
	def write_class(self, c, indent=0):
		#self.write('# Type "' + t.id.name + '"')
		self.write('{' + '\n')
		
		self.write_indent(indent+1)
		self.write('"id": ')
		self.writeId(c.id)
		self.write(',' + '\n')
		#@TODO: Variables
		#@TODO: Initializer?
		
		if (c.namespace and len(c.namespace.ids) > 0):
			self.write_indent(indent+1)
			self.write('"namespace": ')
			self.write_namespace(c.namespace, indent+1)
			self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"funcs": ')
		self.writeArray(c.funcs, self.write_function, indent+1)
		self.write('\n')
		
		self.write_indent(indent)
		self.write('}')
		
	def write_block(self, b, indent=0):
		# Just write instructions
		self.write('{' + '\n')
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				self.write_indent(indent+1)
				self.write('"namespace": ')
				self.write_namespace(b.namespace, indent+1)
				self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"instrs": ')
		self.writeArray(b.instrs, self.write_instruction, indent+1)
		
		self.write('\n')
		self.write_indent(indent)
		self.write('}')
		
	def write_instruction(self, i, indent):
		self.write('{' + '\n')
		
		self.write_indent(indent+1)
		
		if (i.control):
			self.write('"control": ')
			self.write_control(i.control, indent+1)
		if (i.call):
			self.write('"call": ')
			self.write_call(i.call, indent+1)
		
		self.write('\n')
		self.write_indent(indent)
		self.write('}')
		
	def write_control(self, c, indent=0):
		self.write('{' + '\n')
		
		self.write_indent(indent+1)
		#self.write('"id": "' + c.id.name + '"')
		self.write('"controlType": ')
		self.write(c.controlType)
		self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"exprs": ')
		self.writeArray(c.exprs, self.write_expression, indent+1)
		self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"blocks": ')
		self.writeArray(c.blocks, self.write_block, indent+1)
		self.write('\n')
		
		
		self.write_indent(indent)
		self.write('}')
		
	def write_call(self, c, indent=0):
		self.write('{' + '\n')
		
		self.write_indent(indent+1)
		self.write('"id": ')
		self.writeId(c.id)
		self.write(',' + '\n')
		
		self.write_indent(indent+1)
		self.write('"args": ')
		self.writeArray(c.args, self.write_expression, indent+1)
		self.write('\n')
		
		self.write_indent(indent)
		self.write('}')
		
	def write_expression(self, e, indent=0):
		#self.write('{' + '\n')
		self.write('{')
		#self.write_indent(indent+1)
		
		if (e.value):
			self.write('"value": ')
			self.write_value(e.value, indent+1)
		if (e.var):
			self.write('"var": ')
			self.write_var(e.var, indent+1)
		if (e.call):
			self.write('"call": ')
			self.write_call(e.call, indent+1)
			self.write('\n')
			self.write_indent(indent)
		#self.write('\n')
		#self.write_indent(indent)
		self.write('}')
		
	def write_value(self, v, indent):
		if (v.type == T_STRING):
			self.write('"' + v.data_str.replace('"', '\\"') + '"')	#@TODO: Escaping!
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_float))
		elif (v.type == T_BOOLEAN):
			if (v.data_bool == True):
				self.write('true')
			else:
				self.write('false')
		else:
			#self.write('[type=' + v.type + '?]')
			self.write('undefined')
	


