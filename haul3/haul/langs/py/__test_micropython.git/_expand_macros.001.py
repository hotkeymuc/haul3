#!/bin/python3
"""
C-Macro-Expander
================

This script parses .c/.h files and expands the #define macros.
It even takes care of dynamic/recursive #defines.

It does, however, NOT expand "if/else/endif" statements, as I might want to use them down the line.

It is mainly used for my own passion project "HAUL":
I want to use MicroPython's Python language parser and translate it to Python itself.


2024-04-01 Bernhard "HotKey" Slawik
"""

import os	# for checking file existence
import re	# For quickly searching for qualifiers/full words

MAX_STRING_LENGTH = 2000	# Throw exception if string gets too big
MAX_DEFINE_REAPPLY = 3	# Max. recursion depth of define resolution
SHOW_CODE_WHILE_PROCESSING = False
STRIP_BLOCK_COMMENTS = True	# Strip all block comments
STRIP_LINE_COMMENTS = True	# Strip away comments at end of lines
KEEP_SIMPLE_DEFINES = True	# Keep simple define statements (without arguments) as-is, so they can be turned into constants for better readability
AUTO_ENUM = True	# Automatically assign integer values to enums

def put(t):
	print(t)

# Specify file mapping for "#include" statement. All files which are not found are just ignored.
PATH_TRANSLATE = {
	#'py/': ''
	'py/grammar.h': './grammar.h'
}
def translate_path(p):
	for s,t in PATH_TRANSLATE.items():
		if p.startswith(s):
			p = t + p[len(s):]
	return p

def count_whitespace(t):
	# Count indents
	TAB_SIZE = 4
	indent = 0
	i = 0
	while t[i] in [' ', '\t']:
		if t[i] == '\t': indent += TAB_SIZE
		else: indent += 1
		i += 1
	return indent


def reduce_whitespace(t):
	r = t.strip().replace('\t', ' ')
	while '  ' in r: r = r.replace('  ', ' ')
	return r

WORD_CHARS = [
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
	'_'
]

def contains_word(t, src):
	"""Search for the given src word, but only in full words."""
	#@FIXME: Use RegExp!
	"""
	in_word = False
	for c in t:
		if c in WORD_CHARS:
			if not in_word:
				in_word = True
				word = ''
			word += c
		else:
			if in_word:
				if word == src: return True
				in_word = False
	if in_word:
		if word == src: return True
	return False
	"""
	return src in re.split('\W', t)

def replace_word(t, src, repl):
	"""Replace the given src word with repl, but only in full words."""
	#@FIXME: Use RegExp!
	r = ''
	in_word = False
	for c in t:
		if c in WORD_CHARS:
			if not in_word:
				in_word = True
				word = ''
			word += c
		else:
			if in_word:
				if word == src: word = repl
				r += word
				in_word = False
			r += c
	if in_word:
		if word == src: word = repl
		r += word
	return r

#put('"%s"' % replace_word('This-is---a test for the replacer, for everyone,for the people and fortune.', 'for', 'FOUR'))
#put('"%s"' % replace_word('1_for 1', 'for', 'FOUR'))



class MacroExpander:
	def __init__(self):
		self.defines = {}
	
	
	def process_file(self, filename, is_include=False):
		lines = []
		put('Processing %sfile "%s"...' % ('include ' if is_include else '', filename))
		inside_comment = False
		inside_comment_later = False
		
		for line_num,line in enumerate(open(filename, 'r')):
			if SHOW_CODE_WHILE_PROCESSING:
				#put('%d:	%s' % (line_num+1, line))
				if not is_include:	# Only show code for main file (includes will repeat!)
					put('%d:	%s' % (line_num+1, line.strip()))
			
			# Count indents
			indent = count_whitespace(line)
			# ...and remove it for processing
			r = reduce_whitespace(line)
			
			# Handle Comments
			if '/*' in r:
				if STRIP_BLOCK_COMMENTS:
					r = r[:r.index('/*')]
				inside_comment_later = True
			if '*/' in r:
				if STRIP_BLOCK_COMMENTS:
					r = r[r.index('*/')+2:]
				inside_comment_later = False
				inside_comment = False
			if '//' in r:
				if STRIP_LINE_COMMENTS:
					r = r[:r.index('//')].strip()	# Skip line comments
				
			if inside_comment:
				if STRIP_BLOCK_COMMENTS:
					r = ''
				#continue
			
			# Expansion/includes can lead to multiple lines
			#r = self.process_line(r)
			lines2 = self.process_line(r)
			
			# Dump
			#put('%d:	%-80s	->	"%s"' % (line_num+1, line.strip(), r))
			
			for r in lines2:
				#if r.strip() != '':
				#put('%d:	%s' % (line_num+1, r))
				lines.append((' '*indent) + r)
			
			if inside_comment_later:
				inside_comment = True
				inside_comment_later = False
		
		#return '\n'.join(lines)
		return lines
	
	def process_line(self, t):
		"""Process one line"""
		r = t
		lines = []	# Be able to return multiple lines
		
		# Handle defines
		if r.startswith('#define'):
			# Declare a define
			r = r[len('#define '):]
			def_name = None
			
			if '(' in r and ' ' in r and r.index('(') < r.index(' '):
				#put('Define with params!')
				def_name = r[:r.index('(')]
				def_args= [ arg.strip() for arg in r[r.index('(')+1:r.index(')')].split(',') ]
				def_rep = r[r.index(')')+1:].strip()
				r = ''	# Do not output anything
			elif ' ' in r:
				# Regular define
				def_name = r[:r.index(' ')]
				def_args = None
				def_rep = r[r.index(' ')+1:]
				# Check if it is "simple" (e.g. a decimal or hex number, optionally in brackets
				#if KEEP_SIMPLE_DEFINES and re.match(r'^\(?\s*(0x)?\d+\s*\)?$', def_rep.strip()):
				if KEEP_SIMPLE_DEFINES and re.match(r'^\(?\s*(0x)?[0-9a-fA-F]+\s*\)?$', def_rep.strip()):
					# Do not create a define, but keep the original line
					r = t	# +  '	// Kept as define, because KEEP_SIMPLE_DEFINES'
					def_name = None
			else:
				# Empty define
				def_name = r
				def_args = None
				def_rep = ''
				r = ''	# Do not output anything
			
			if def_name is not None:
				#put('New define: name="%s", args=%s, replace with "%s"' % (def_name, str(def_args), def_rep))
				def_id = '%04X_%s'%(len(def_name), def_name)
				self.defines[def_id] = (def_name, def_args, def_rep)
		
		elif r.startswith('#undef'):
			# Undefine
			r = r[len('#undef '):]
			def_name = r
			def_id = '%04X_%s'%(len(def_name), def_name)
			if def_id in self.defines:
				del self.defines[def_id]
			else:
				put('Undefining non-existent define "%s"' % def_name)
			r = ''
		
		elif r.startswith('#ifdef'):
			#r = r[len('#ifdef '):]
			#@FIXME: Handle a "stack" of if/ifdef
			pass
		elif r.startswith('#ifndef'):
			#r = r[len('#ifndef '):]
			#@FIXME: Handle a "stack" of if/ifdef
			pass
		elif r.startswith('#else'):
			#r = r[len('#else '):]
			#@FIXME: Handle a "stack" of if/ifdef
			pass
		elif r.startswith('#endif'):
			#@FIXME: Handle a "stack" of if/ifdef
			pass
		else:
			# Apply defines
			"""
			r_old = None
			timeout = MAX_DEFINE_REAPPLY
			while r != r_old:
				r_old = r
				r = self.apply_defines(r)
				if len(r) > MAX_STRING_LENGTH:
					raise Exception('String too long: "%s"' % r)
				timeout -= 1
				if timeout < 10:
					put('Potential circular expansion from "%s" to "%s"' % (r_old, r))
				if timeout < 0:
					raise Exception('Circular expansion in line "%s"' % r)
			"""
			r_old = None
			for i in range(MAX_DEFINE_REAPPLY):
				r_old = r
				r = self.apply_defines(r)
				if r == r_old: break
			if i >= MAX_DEFINE_REAPPLY:
				put('Max recursion depth (MAX_DEFINE_REAPPLY=%d) reached!' % MAX_DEFINE_REAPPLY)
			
		
		# Handle includes
		if r.startswith('#include'):
			f = r[len('#include '):]
			if f.startswith('<'):
				# Skip system includes
				put('Skipping system include file %s' % f)
				r = ''
				pass
			else:
				f2 = translate_path(f[1:-1])
				if not os.path.isfile(f2):
					put('Include file %s -> "%s" was NOT FOUND!' % (f, f2))
					r = ''
				else:
					# Merge into this file
					lines.extend( self.process_file(f2, is_include=True))
					#r = '\n'.join(self.process_file(f2, is_include=True))
					r = ''
			pass
		
		
		# Convert single line to lines
		#if lines is None:
		#	lines = [ r ]
		if r.strip() != '':
			lines.append(r)
		
		return lines
	
	def apply_defines(self, t):
		if len(t) == 0: return t
		
		r = t
		timeout = 10000	# To prevent endless recursions
		expanding = True
		
		defs_sorted = list(reversed(sorted(self.defines.items())))
		
		#put('Processing "%s"...' % r)
		#while expanding:
		if True:
			expanding = False
			
			#for def_id, def_v in self.defines.items():
			for def_id, def_v in defs_sorted:	# Longest first!
				def_name, def_args, def_rep = def_v
				
				#if not def_name in r:
				if not contains_word(r, def_name):
					continue
				
				#put('Define "%s" matches: "%s"' % (def_name, r))
				timeout -= 1
				if timeout < 0:
					raise Exception('Define expansion did not terminate while applying define "%s" on line "%s"' % (def_name, r))
					sys.exit(1)
				
				if def_args is None:
					# Do simple replace (no args)
					r = r.replace(def_name, def_rep)
				else:
					# Define has args!
					#put('Applying define-args for "%s" in line "%s"...' % (def_name, r))
					p = r.index(def_name)
					pre = r[:p]
					
					# Find closing bracket
					p += len(def_name)
					p2 = p
					b = 0
					while p2 < len(r):
						c = r[p2]
						if c == '(': b += 1
						if c == ')': b -= 1
						if b <= 0: break
						p2 += 1
					post = r[p2+1:]
					arg_t = r[p+1:p2]
					#put('[%s]' % arg_t)
					
					arg_t = self.apply_defines(arg_t)	# Arguments must also be processed (recursively)
					
					#put('Expanding "%s" into pre=[%s] t=[%s] post=[%s] and processing with def_rep=[%s]' % (r, pre, t, post, def_rep))
					
					arg_vals = [ v.strip() for v in arg_t.split(',') ]	# Extract arguments (comma-separated)
					
					t = def_rep
					for a_i, a_name in enumerate(def_args):
						if a_name == '...': 
							t = t.replace('__VA_ARGS__', ', '.join(arg_vals[a_i:]))
							continue
						if a_i >= len(arg_vals):
							raise Exception('Macro %s requires %d arguments %s, but only %d given %s in: "%s"' % (def_name, len(def_args), str(def_args), len(arg_vals), str(arg_vals), r))
							continue
						v = arg_vals[a_i]
						t = t.replace('##%s'%a_name, v)
						t = t.replace('#%s'%a_name, '"%s"'%v)
						
						"""
						if t.startswith(a_name): t = v+t[len(a_name):]
						#if t == a_name: t = v
						#if t.startswith(a_name+','): t = v+t[len(a_name):]
						#if t.startswith(a_name+' '): t = v+t[len(a_name):]
						#if t.startswith(a_name+'\t'): t = v+t[len(a_name):]
						
						t = t.replace(' %s '%a_name, ' '+v+' ')
						t = t.replace(' %s,'%a_name, ' '+v+',')
						t = t.replace(',%s '%a_name, ','+v+' ')
						t = t.replace(',%s,'%a_name, ','+v+',')
						t = t.replace(' %s)'%a_name, ' '+v+')')
						t = t.replace(',%s)'%a_name, ','+v+')')
						t = t.replace('(%s '%a_name, '('+v+' ')
						t = t.replace('(%s,'%a_name, '('+v+',')
						"""
						t = replace_word(t, a_name, v)
					r = pre + t + post
				
				#put('Define "%s" result: "%s"' % (def_name, r))
				if len(r) > MAX_STRING_LENGTH:
					raise Exception('String got too long while expanding (MAX_STRING_LENGTH): "%s"' % r)
				#expanding = True
				#break	 # Need to restart with big defines again
				
		# while expanding
		return r
	

if __name__ == '__main__':
	
	me = MacroExpander()
	
	# Test recursive macros
	#t = me.process_line('#define foo bar')
	#t = me.process_line('#define extra(v) EXTRA_##v')
	#t = me.process_line('#define baz(n, m, ...) [BAZ##m_##n __VA_ARGS__]')
	#t = me.process_line('I like foo at the baz(A, B, C, D).')
	
	filename_input = 'parse.c'
	filename_output = '%s.c.EXPANDED-NOCOMMENTS.txt' % filename_input
	
	
	# Do it!
	lines = me.process_file(filename_input)
	
	put('-' * 80)
	
	# Post-processing: Fix indents, auto-enumerate enums
	put('Post-processing...')
	level = 0
	in_enum = False
	enum_index = 0
	for i in range(len(lines)):	# We need to alter it while iterating, that's why we go by index
		l = lines[i]
		indent = count_whitespace(l)
		
		#put('indent=%d	level=%d' % (indent, level))
		l = l.strip()
		if l.startswith('}'): level -= 1
		
		# Auto-enumerate enums
		if AUTO_ENUM:
			if contains_word(l, 'enum') and l.endswith('{'):
				in_enum = True
				enum_index = 0
			elif in_enum and not l.startswith('#'):
				if l.startswith('}'):
					in_enum = False
				else:
					l += '	// enum_index=%d'%enum_index
					enum_index += 1
		
		# Re-apply indent
		lines[i] = '%s%s' % ('\t' * level, l)
		
		if l.endswith('{'): level += 1
		
	# Write output
	if filename_output is not None:
		put('-' * 80)
		put('Writing output file "%s"...' % filename_output)
		with open(filename_output, 'w') as h:
			h.write('\n'.join(lines))
	
	put('-' * 80)
	put('\n'.join(lines))