#!/bin/python3
#from __test_micropython_grammar import *
#from __test_micropython_lexer import *
from __test_micropython_parser import *

def put(t:str):
	print(t)

def dump(pn:mp_parse_node_t, indent:int=0):
	
	#r = 'pn:\n'
	r = DUMP_INDENT*indent
	
	if pn is None:
		r += 'pn=None\n'
	elif not isinstance(pn, mp_parse_node_t):
		r += 'pn=VALUE: %s (%s)\n' % (str(pn), str(type(pn)))
	#elif MP_PARSE_NODE_IS_NULL(pn) and (i == num_nodes-1):
	#	r += 'pn=NULL = END\n' % (DUMP_INDENT * (indent+1))
	#	#continue	# Do not dump trailing NULLs
	elif MP_PARSE_NODE_IS_STRUCT(pn):
		#r += 'root=%s' % pn.dump()
		kind = pn.kind_num_nodes & 0xff
		
		# Parse known rules
		if kind == RULE_import_from:
			r += 'IMPORT %s.%s\n' % (pn.nodes[0].id_value, str(pn.nodes[1]))
			return r
		elif kind == RULE_term:
			r += 'TERM(' + (', '.join([str(pnn) for pnn in pn.nodes])) + ')\n'
			return r
			
		elif kind == RULE_expr_stmt:
			
			if MP_PARSE_NODE_IS_STRUCT(pn.nodes[0]) and (pn.nodes[0].kind_num_nodes & 0xff == RULE_atom_expr_normal):
				# Call!
				r += 'CALL '
				#assert(pn.nodes[0].nodes[1].kind_num_nodes & 0xff == RULE_trailer_paren)
				if (pn.nodes[0].nodes[1].kind_num_nodes & 0xff == RULE_trailer_paren):
					r += pn.nodes[0].nodes[0].id_value
					r += '('
					r += ', '.join([ dump(pnn, 0).strip() for pnn in pn.nodes[0].nodes[1].nodes ])
					r += ')\n'
				else:
					r += 'UNKNOWN EXPRESSION:' + dump(pn.nodes[0], indent+1)	#indent+1)
				
			else:
				# Set
				r += 'SET '
				r += '<'
				#r += pn.nodes[0].id_value
				r += str(pn.nodes[0])
				#r += dump(pn.nodes[0])
				r += '> := <'
				r += dump(pn.nodes[1], 0).strip()	#indent+1)
				r += '>\n'
			
			return r
			
			#pass
		
		
		r += 'pn=%s {\t// line %d\n' % (
			rule_name_table[kind] if kind < len(rule_name_table) else '0x%02X'%kind,
			pn.source_line
		)
		num_nodes = pn.kind_num_nodes >> 8
		#for pnn in pn.nodes:
		for i,pnn in enumerate(pn.nodes[:num_nodes]):
			#r += '%s%s\n' % (DUMP_INDENT * (indent+1), str(pnn))
			r += dump(pnn, indent+1)
		r += '%s}\n' % (DUMP_INDENT * indent)
	else:
		# Unknown mp_parse_node_t
		r += 'pn=%s\n' % str(pn)
	return r


if __name__ == '__main__':
	#filename = '__test_micropython_lexer.py'
	filename = '__test_micropython_parser.py'
	#filename = 'micropython_minimal/test.py'
	
	put('Loading "%s"...' % filename)
	with open(filename, 'r') as h: code = h.read()
	if code[-1] == '\x04': code = code[:-1]
	#filename = 'test_input'
	#code = 'a=1'
	
	put('Setting up reader and lexer...')
	reader = mp_reader_t(code)
	lex = mp_lexer_new(src_name=filename, reader=reader)
	
	put('Parsing...')
	t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_FILE_INPUT)
	#t:mp_parse_tree_t = mp_parse(lex, MP_PARSE_SINGLE_INPUT)
	put('Result Tree:')
	#put(str(t))
	put(dump(t.root))
	
	put('EOF')
