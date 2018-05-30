#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

from haul.haul import *

class HAULWriter_json(HAULWriter):
	"Writes JSON representation"
	def __init__(self, streamOut):
		HAULWriter.__init__(self, streamOut)
		self.defaultExtension = 'json'
		self.writeComment('Translated from HAUL to JSON on ' + str(datetime.datetime.now()))
		
	def writeComment(self, t):
		"Add a comment to the file - NOT for JSON!"
		#self.streamOut.put('// ' + t + '\n')
		put('NOT adding comment to file: "' + t + '"')
		
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
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
			self.writeIndent(indent+1)
			cb(item, indent+1)
			i += 1
		
		self.write('\n')
		self.writeIndent(indent)
		self.write(']')
	
	def writeVar(self, v, indent=0):
		#self.write('"' + v.id.name + '"')
		self.write(v.name)
	
	def writeNamespace(self, ns, indent=0):
		self.write('{\n')
		
		#self.write('\t/* ' + str(ns) + ' */\n')
		
		i = 0
		for id in ns.ids:
			if (i > 0):
				self.write(',')
				self.write('\n')
			
			#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data))
			self.writeIndent(indent+1)
			self.write(id.name)
			self.write(': {')
			self.write('kind: "' + str(id.kind) + '", ')
			self.write('data_type: "' + str(id.data_type) + '", ')
			self.write('data_value: "' + str(id.data_value) + '"')
			self.write('}')
			i += 1
		if (i > 0): self.write('\n')
		self.writeIndent(indent)
		self.write('}')
	
	def writeFunc(self, f, indent=0):
		self.write('{' + '\n')
		
		self.writeIndent(indent+1)
		#self.write('"id": "' + f.id.name + '",' + '\n')
		self.write('"id": ')
		self.writeId(f.id)
		self.write(',' + '\n')
		
		if (not f.id.data_type == None):
			self.writeIndent(indent+1)
			self.write('"type": "' + f.id.data_type + '",' + '\n')
		
		if (f.namespace and len(f.namespace.ids) > 0):
			self.writeIndent(indent+1)
			self.write('"namespace": ')
			self.writeNamespace(f.namespace, indent+1)
			self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"args": ')
		self.writeArray(f.args, self.writeVar, indent+1)
		self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"block": ')
		if (f.block):
			self.writeBlock(f.block, indent+1)
		else:
			self.write('null')
		self.write('\n')
		
		self.writeIndent(indent)
		self.write('}')
		
	def writeModule(self, m, indent=0):
		self.write('{' + '\n')
		#self.write('\t' + '//Module "' + m.id.name + '"\n')
		
		if (m.namespace and len(m.namespace.ids) > 0):
			self.writeIndent(indent+1)
			self.write('"namespace": ')
			self.writeNamespace(m.namespace, indent+1)
			self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"imports": [')
		i = 0
		for im in m.imports:
			if (i > 0): self.write(', ')
			self.write('"' + str(im) + '"')
			i += 1
		self.write('],' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"classes": ')
		self.writeArray(m.classes, self.writeClass, indent+1)
		self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"funcs": ')
		self.writeArray(m.funcs, self.writeFunc, indent+1)
		self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"block": ')
		if (m.block):
			self.writeBlock(m.block, indent+1)
		else:
			self.write('null')
		self.write('\n')
		
		self.writeIndent(indent)
		self.write('}' + '\n')
		
	def writeClass(self, c, indent=0):
		#self.write('# Type "' + t.id.name + '"')
		self.write('{' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"id": ')
		self.writeId(c.id)
		self.write(',' + '\n')
		#@TODO: Variables
		#@TODO: Initializer?
		
		if (c.namespace and len(c.namespace.ids) > 0):
			self.writeIndent(indent+1)
			self.write('"namespace": ')
			self.writeNamespace(c.namespace, indent+1)
			self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"funcs": ')
		self.writeArray(c.funcs, self.writeFunc, indent+1)
		self.write('\n')
		
		self.writeIndent(indent)
		self.write('}')
		
	def writeBlock(self, b, indent=0):
		# Just write instructions
		self.write('{' + '\n')
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				self.writeIndent(indent+1)
				self.write('"namespace": ')
				self.writeNamespace(b.namespace, indent+1)
				self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"instrs": ')
		self.writeArray(b.instrs, self.writeInstr, indent+1)
		
		self.write('\n')
		self.writeIndent(indent)
		self.write('}')
		
	def writeInstr(self, i, indent):
		self.write('{' + '\n')
		
		self.writeIndent(indent+1)
		
		if (i.control):
			self.write('"control": ')
			self.writeControl(i.control, indent+1)
		if (i.call):
			self.write('"call": ')
			self.writeCall(i.call, indent+1)
		
		self.write('\n')
		self.writeIndent(indent)
		self.write('}')
		
	def writeControl(self, c, indent=0):
		self.write('{' + '\n')
		
		self.writeIndent(indent+1)
		#self.write('"id": "' + c.id.name + '"')
		self.write('"controlType": ')
		self.write(c.controlType)
		self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"exprs": ')
		self.writeArray(c.exprs, self.writeExpression, indent+1)
		self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"blocks": ')
		self.writeArray(c.blocks, self.writeBlock, indent+1)
		self.write('\n')
		
		
		self.writeIndent(indent)
		self.write('}')
		
	def writeCall(self, c, indent=0):
		self.write('{' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"id": ')
		self.writeId(c.id)
		self.write(',' + '\n')
		
		self.writeIndent(indent+1)
		self.write('"args": ')
		self.writeArray(c.args, self.writeExpression, indent+1)
		self.write('\n')
		
		self.writeIndent(indent)
		self.write('}')
		
	def writeExpression(self, e, indent=0):
		#self.write('{' + '\n')
		self.write('{')
		#self.writeIndent(indent+1)
		
		if (e.value):
			self.write('"value": ')
			self.writeValue(e.value, indent+1)
		if (e.var):
			self.write('"var": ')
			self.writeVar(e.var, indent+1)
		if (e.call):
			self.write('"call": ')
			self.writeCall(e.call, indent+1)
			self.write('\n')
			self.writeIndent(indent)
		#self.write('\n')
		#self.writeIndent(indent)
		self.write('}')
		
	def writeValue(self, v, indent=0):
		if (type(v.data) == str):
			self.write("'" + v.data + "'")	#@FIXME: This lacks propper escaping!
		else:
			self.write(str(v))	#.data


