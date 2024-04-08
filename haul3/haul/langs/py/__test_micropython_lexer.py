#!/bin/python3
#"""
#	Translation of MicroPython's "py/lexer.h/c" to Python
#	
#	2024-04-05 Bernhard "HotKey" Slawik
#"""
### Glue code
def put(t):
	print(t)

MICROPY_ALLOC_LEXER_INDENT_INIT = 8	#@FIXME: ?
MICROPY_ALLOC_LEXEL_INDENT_INC = 1	#@FIXME: ?

MP_LEXER_EOF = chr(0x1a)	# = MP_READER_EOF
MP_LEXER_VERBOSE = False

def MP_ARRAY_SIZE(a):	return len(a)
def CUR_CHAR(lex):	return lex.chr0

def strcmp(s, t):
	for i in range(len(s)):
		c1 = ord(s[i])
		if i >= len(t): return 1	#+i
		c2 = ord(t[i])
		if c1 > c2: return 1	#+i
		elif c1 < c2: return -1	#-i
	if len(t) > len(s): return -1	#-i
	return 0

#print(strcmp('aaXaa', 'aaYaa'))


# Define some types
size_t = int
unichar = str
byte = str
char = str
qstr = str
vstr_t = str
mp_int_t = int
mp_token_kind_t = int


# Define a dummy reader
class mp_reader_t:
	def __init__(self, data):
		self.data = data
		self.ofs = 0
	def readbyte(self, data):
		if self.ofs >= len(self.data):
			return MP_LEXER_EOF
		
		r = self.data[self.ofs]
		self.ofs += 1
		return r
	def __repr__(self):
		return 'byte %d / %d' % (self.ofs, len(self.data))

def unichar_isspace(c):
	return c in [' ', '\t']

def unichar_isalpha(c):
	return c in  [
		'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
		'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
	]
def unichar_isdigit(c):
	return c in  ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def unichar_isxdigit(c):
	return c.lower() in  ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

def unichar_xdigit_value(c):
	return ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'].index(c.lower())

### lexer.h
# lexer.h -- simple tokeniser for MicroPython
#
# Uses (byte) length instead of null termination.
# Tokens are the same - UTF-8 with (byte) length.
#

# mp_token_kind_t
#typedef enum _mp_token_kind_t {
MP_TOKEN_END = 0

MP_TOKEN_INVALID = 1
MP_TOKEN_DEDENT_MISMATCH = 2
MP_TOKEN_LONELY_STRING_OPEN = 3
#if MICROPY_PY_FSTRINGS
MP_TOKEN_MALFORMED_FSTRING = 4
MP_TOKEN_FSTRING_RAW = 5
#endif

MP_TOKEN_NEWLINE = 6
MP_TOKEN_INDENT = 7
MP_TOKEN_DEDENT = 8

MP_TOKEN_NAME = 9
MP_TOKEN_INTEGER = 10
MP_TOKEN_FLOAT_OR_IMAG = 11
MP_TOKEN_STRING = 12
MP_TOKEN_BYTES = 13

MP_TOKEN_ELLIPSIS = 14

MP_TOKEN_KW_FALSE = 15
MP_TOKEN_KW_NONE = 16
MP_TOKEN_KW_TRUE = 17
MP_TOKEN_KW___DEBUG__ = 18
MP_TOKEN_KW_AND = 19
MP_TOKEN_KW_AS = 20
MP_TOKEN_KW_ASSERT = 21
#if MICROPY_PY_ASYNC_AWAIT
MP_TOKEN_KW_ASYNC = 22
MP_TOKEN_KW_AWAIT = 23
#endif
MP_TOKEN_KW_BREAK = 24
MP_TOKEN_KW_CLASS = 25
MP_TOKEN_KW_CONTINUE = 26
MP_TOKEN_KW_DEF = 27
MP_TOKEN_KW_DEL = 28
MP_TOKEN_KW_ELIF = 29
MP_TOKEN_KW_ELSE = 30
MP_TOKEN_KW_EXCEPT = 31
MP_TOKEN_KW_FINALLY = 32
MP_TOKEN_KW_FOR = 33
MP_TOKEN_KW_FROM = 34
MP_TOKEN_KW_GLOBAL = 35
MP_TOKEN_KW_IF = 36
MP_TOKEN_KW_IMPORT = 37
MP_TOKEN_KW_IN = 38
MP_TOKEN_KW_IS = 39
MP_TOKEN_KW_LAMBDA = 40
MP_TOKEN_KW_NONLOCAL = 41
MP_TOKEN_KW_NOT = 42
MP_TOKEN_KW_OR = 43
MP_TOKEN_KW_PASS = 44
MP_TOKEN_KW_RAISE = 45
MP_TOKEN_KW_RETURN = 46
MP_TOKEN_KW_TRY = 47
MP_TOKEN_KW_WHILE = 48
MP_TOKEN_KW_WITH = 49
MP_TOKEN_KW_YIELD = 50

MP_TOKEN_OP_ASSIGN = 51
MP_TOKEN_OP_TILDE = 52

# Order of these 6 matches corresponding mp_binary_op_t operator
MP_TOKEN_OP_LESS = 53
MP_TOKEN_OP_MORE = 54
MP_TOKEN_OP_DBL_EQUAL = 55
MP_TOKEN_OP_LESS_EQUAL = 56
MP_TOKEN_OP_MORE_EQUAL = 57
MP_TOKEN_OP_NOT_EQUAL = 58

# Order of these 13 matches corresponding mp_binary_op_t operator
MP_TOKEN_OP_PIPE = 59
MP_TOKEN_OP_CARET = 60
MP_TOKEN_OP_AMPERSAND = 61
MP_TOKEN_OP_DBL_LESS = 62
MP_TOKEN_OP_DBL_MORE = 63
MP_TOKEN_OP_PLUS = 64
MP_TOKEN_OP_MINUS = 65
MP_TOKEN_OP_STAR = 66
MP_TOKEN_OP_AT = 67
MP_TOKEN_OP_DBL_SLASH = 68
MP_TOKEN_OP_SLASH = 69
MP_TOKEN_OP_PERCENT = 70
MP_TOKEN_OP_DBL_STAR = 71

# Order of these 13 matches corresponding mp_binary_op_t operator
MP_TOKEN_DEL_PIPE_EQUAL = 72
MP_TOKEN_DEL_CARET_EQUAL = 73
MP_TOKEN_DEL_AMPERSAND_EQUAL = 74
MP_TOKEN_DEL_DBL_LESS_EQUAL = 75
MP_TOKEN_DEL_DBL_MORE_EQUAL = 76
MP_TOKEN_DEL_PLUS_EQUAL = 77
MP_TOKEN_DEL_MINUS_EQUAL = 78
MP_TOKEN_DEL_STAR_EQUAL = 79
MP_TOKEN_DEL_AT_EQUAL = 80
MP_TOKEN_DEL_DBL_SLASH_EQUAL = 81
MP_TOKEN_DEL_SLASH_EQUAL = 82
MP_TOKEN_DEL_PERCENT_EQUAL = 83
MP_TOKEN_DEL_DBL_STAR_EQUAL = 84

MP_TOKEN_DEL_PAREN_OPEN = 85
MP_TOKEN_DEL_PAREN_CLOSE = 86
MP_TOKEN_DEL_BRACKET_OPEN = 87
MP_TOKEN_DEL_BRACKET_CLOSE = 88
MP_TOKEN_DEL_BRACE_OPEN = 89
MP_TOKEN_DEL_BRACE_CLOSE = 90
MP_TOKEN_DEL_COMMA = 91
MP_TOKEN_DEL_COLON = 92
MP_TOKEN_DEL_PERIOD = 93
MP_TOKEN_DEL_SEMICOLON = 94
MP_TOKEN_DEL_EQUAL = 95
MP_TOKEN_DEL_MINUS_MORE = 95
# } mp_token_kind_t

# Token names for debugging
mp_token_kind_names = [
	'MP_TOKEN_END',	#0
	'MP_TOKEN_INVALID',	#1
	'MP_TOKEN_DEDENT_MISMATCH',	#2
	'MP_TOKEN_LONELY_STRING_OPEN',	#3
	#if MICROPY_PY_FSTRINGS
	'MP_TOKEN_MALFORMED_FSTRING',	#4
	'MP_TOKEN_FSTRING_RAW',	#5
	#endif
	'MP_TOKEN_NEWLINE',	#6
	'MP_TOKEN_INDENT',	#7
	'MP_TOKEN_DEDENT',	#8
	'MP_TOKEN_NAME',	#9
	'MP_TOKEN_INTEGER',	#10
	'MP_TOKEN_FLOAT_OR_IMAG',	#11
	'MP_TOKEN_STRING',	#12
	'MP_TOKEN_BYTES',	#13
	'MP_TOKEN_ELLIPSIS',	#14
	'MP_TOKEN_KW_FALSE',	#15
	'MP_TOKEN_KW_NONE',	#16
	'MP_TOKEN_KW_TRUE',	#17
	'MP_TOKEN_KW___DEBUG__',	#18
	'MP_TOKEN_KW_AND',	#19
	'MP_TOKEN_KW_AS',	#20
	'MP_TOKEN_KW_ASSERT',	#21
	#if MICROPY_PY_ASYNC_AWAIT
	'MP_TOKEN_KW_ASYNC',	#22
	'MP_TOKEN_KW_AWAIT',	#23
	#endif
	'MP_TOKEN_KW_BREAK',	#24
	'MP_TOKEN_KW_CLASS',	#25
	'MP_TOKEN_KW_CONTINUE',	#26
	'MP_TOKEN_KW_DEF',	#27
	'MP_TOKEN_KW_DEL',	#28
	'MP_TOKEN_KW_ELIF',	#29
	'MP_TOKEN_KW_ELSE',	#30
	'MP_TOKEN_KW_EXCEPT',	#31
	'MP_TOKEN_KW_FINALLY',	#32
	'MP_TOKEN_KW_FOR',	#33
	'MP_TOKEN_KW_FROM',	#34
	'MP_TOKEN_KW_GLOBAL',	#35
	'MP_TOKEN_KW_IF',	#36
	'MP_TOKEN_KW_IMPORT',	#37
	'MP_TOKEN_KW_IN',	#38
	'MP_TOKEN_KW_IS',	#39
	'MP_TOKEN_KW_LAMBDA',	#40
	'MP_TOKEN_KW_NONLOCAL',	#41
	'MP_TOKEN_KW_NOT',	#42
	'MP_TOKEN_KW_OR',	#43
	'MP_TOKEN_KW_PASS',	#44
	'MP_TOKEN_KW_RAISE',	#45
	'MP_TOKEN_KW_RETURN',	#46
	'MP_TOKEN_KW_TRY',	#47
	'MP_TOKEN_KW_WHILE',	#48
	'MP_TOKEN_KW_WITH',	#49
	'MP_TOKEN_KW_YIELD',	#50
	'MP_TOKEN_OP_ASSIGN',	#51
	'MP_TOKEN_OP_TILDE',	#52
	# Order of these 6 matches corresponding 'MP_binary_op_t operator
	'MP_TOKEN_OP_LESS',	#53
	'MP_TOKEN_OP_MORE',	#54
	'MP_TOKEN_OP_DBL_EQUAL',	#55
	'MP_TOKEN_OP_LESS_EQUAL',	#56
	'MP_TOKEN_OP_MORE_EQUAL',	#57
	'MP_TOKEN_OP_NOT_EQUAL',	#58
	# Order of these 13 matches corresponding 'MP_binary_op_t operator
	'MP_TOKEN_OP_PIPE',	#59
	'MP_TOKEN_OP_CARET',	#60
	'MP_TOKEN_OP_AMPERSAND',	#61
	'MP_TOKEN_OP_DBL_LESS',	#62
	'MP_TOKEN_OP_DBL_MORE',	#63
	'MP_TOKEN_OP_PLUS',	#64
	'MP_TOKEN_OP_MINUS',	#65
	'MP_TOKEN_OP_STAR',	#66
	'MP_TOKEN_OP_AT',	#67
	'MP_TOKEN_OP_DBL_SLASH',	#68
	'MP_TOKEN_OP_SLASH',	#69
	'MP_TOKEN_OP_PERCENT',	#70
	'MP_TOKEN_OP_DBL_STAR',	#71
	# Order of these 13 matches corresponding 'MP_binary_op_t operator
	'MP_TOKEN_DEL_PIPE_EQUAL',	#72
	'MP_TOKEN_DEL_CARET_EQUAL',	#73
	'MP_TOKEN_DEL_AMPERSAND_EQUAL',	#74
	'MP_TOKEN_DEL_DBL_LESS_EQUAL',	#75
	'MP_TOKEN_DEL_DBL_MORE_EQUAL',	#76
	'MP_TOKEN_DEL_PLUS_EQUAL',	#77
	'MP_TOKEN_DEL_MINUS_EQUAL',	#78
	'MP_TOKEN_DEL_STAR_EQUAL',	#79
	'MP_TOKEN_DEL_AT_EQUAL',	#80
	'MP_TOKEN_DEL_DBL_SLASH_EQUAL',	#81
	'MP_TOKEN_DEL_SLASH_EQUAL',	#82
	'MP_TOKEN_DEL_PERCENT_EQUAL',	#83
	'MP_TOKEN_DEL_DBL_STAR_EQUAL',	#84
	'MP_TOKEN_DEL_PAREN_OPEN',	#85
	'MP_TOKEN_DEL_PAREN_CLOSE',	#86
	'MP_TOKEN_DEL_BRACKET_OPEN',	#87
	'MP_TOKEN_DEL_BRACKET_CLOSE',	#88
	'MP_TOKEN_DEL_BRACE_OPEN',	#89
	'MP_TOKEN_DEL_BRACE_CLOSE',	#90
	'MP_TOKEN_DEL_COMMA',	#91
	'MP_TOKEN_DEL_COLON',	#92
	'MP_TOKEN_DEL_PERIOD',	#93
	'MP_TOKEN_DEL_SEMICOLON',	#94
	'MP_TOKEN_DEL_EQUAL',	#95
	'MP_TOKEN_DEL_MINUS_MORE',	#95
]

# this data structure is exposed for efficiency
# public members are: source_name, tok_line, tok_column, tok_kind, vstr

class mp_lexer_t:
	
	source_name:str = None	# name of source
	reader = None #<mp_reader_t>	# stream source
	
	chr0:unichar = 0
	chr1:unichar = 0
	chr2:unichar = 0	# current cached characters from source
	
	#if MICROPY_PY_FSTRINGS
	chr0_saved: unichar = 0
	chr1_saved:unichar = 0
	chr2_saved:unichar = 0	# current cached characters from alt source
	#endif
	
	line:size_t = 0	# current source line
	column:size_t = 0	# current source column
	
	emit_dent:mp_int_t = 0	# non-zero when there are INDENT/DEDENT tokens to emit
	nested_bracket_level:mp_int_t = 0	# >0 when there are nested brackets over multiple lines
	
	alloc_indent_level:size_t = 0
	num_indent_level:size_t = 0
	indent_level = []
	
	tok_line:size_t = 0	# token source line
	tok_column:size_t = 0	# token source column
	tok_kind = 0	# token kind
	vstr:vstr_t = None	# token data
	
	#if MICROPY_PY_FSTRINGS
	fstring_args:vstr_t = None	# extracted arguments to pass to .format()
	fstring_args_idx:size_t = 0	# how many bytes of fstring_args have been read
	#endif
	
	def __repr__(self):
		#return str(self.__dict__)
		#return '%s: %s' % (mp_token_kind_names[self.tok_kind], str(self.__dict__))
		#return '%d: %s	"%s"		%s' % (self.tok_line, mp_token_kind_names[self.tok_kind], self.vstr, str(self.__dict__))
		clean = lambda t: '\\n' if t == '\n' else '\\r' if t == '\r' else '\\t' if t == '\t' else t
		#return 'Line %d, Col %d: "%s" + "%s%s%s", tok=%s (%d)' % (self.tok_line, self.tok_column, clean(self.vstr), clean(self.chr0), clean(self.chr1), clean(self.chr2), mp_token_kind_names[self.tok_kind], self.tok_kind)
		return 'Line %d, Col %d: "%s" (%d) = %s (%d)' % (self.tok_line, self.tok_column, clean(self.vstr), len(self.vstr), mp_token_kind_names[self.tok_kind], self.tok_kind)

#} mp_lexer_t


### lexer.c

#define TAB_SIZE (8)
TAB_SIZE = 4	#8

# TODO seems that CPython allows NULL byte in the input stream
# don't know if that's intentional or not, but we don't allow it

#define MP_LEXER_EOF ((unichar)MP_READER_EOF)
#define CUR_CHAR(lex) ((lex)->chr0)

def is_end(lex:mp_lexer_t) -> bool:
	return lex.chr0 == MP_LEXER_EOF

def is_physical_newline(lex:mp_lexer_t) -> bool:
	return lex.chr0 == '\n'

def is_char(lex:mp_lexer_t, c:byte) -> bool:
	return lex.chr0 == c

def is_char_or(lex:mp_lexer_t, c1:byte, c2:byte) -> bool:
	return (lex.chr0 == c1) or (lex.chr0 == c2)

def is_char_or3(lex:mp_lexer_t, c1:byte, c2:byte, c3:byte) -> bool:
	return lex.chr0 == c1 or lex.chr0 == c2 or lex.chr0 == c3

#if MICROPY_PY_FSTRINGS
def is_char_or4(lex:mp_lexer_t, c1:byte, c2:byte, c3:byte, c4:byte) -> bool:
	return lex.chr0 == c1 or lex.chr0 == c2 or lex.chr0 == c3 or lex.chr0 == c4
#endif

def is_char_following(lex:mp_lexer_t, c:byte) -> bool:
	return lex.chr1 == c

def is_char_following_or(lex:mp_lexer_t, c1:byte, c2:byte) -> bool:
	return lex.chr1 == c1 or lex.chr1 == c2

def is_char_following_following_or(lex:mp_lexer_t, c1:byte, c2:byte) -> bool:
	return lex.chr2 == c1 or lex.chr2 == c2

def is_char_and(lex:mp_lexer_t, c1:byte, c2:byte) -> bool:
	return lex.chr0 == c1 and lex.chr1 == c2

def is_whitespace(lex:mp_lexer_t) -> bool:
	return unichar_isspace(lex.chr0)

def is_letter(lex:mp_lexer_t) -> bool:
	return unichar_isalpha(lex.chr0)

def is_digit(lex:mp_lexer_t) -> bool:
	return unichar_isdigit(lex.chr0)

def is_following_digit(lex:mp_lexer_t) -> bool:
	return unichar_isdigit(lex.chr1)

def is_following_base_char(lex:mp_lexer_t) -> bool:
	#chr1:unichar = lex.chr1 | 0x20
	#chr1:unichar = lex.chr1 if lex.chr1 != '\x00' else ' '
	chr1:unichar = lex.chr1 if ord(lex.chr1) > 0 else ' '
	return chr1 == 'b' or chr1 == 'o' or chr1 == 'x'

def is_following_odigit(lex:mp_lexer_t) -> bool:
	return lex.chr1 >= '0' and lex.chr1 <= '7'

def is_string_or_bytes(lex:mp_lexer_t) -> bool:
	return is_char_or(lex, '\'', '\"')\
		or (is_char_or4(lex, 'r', 'u', 'b', 'f') and is_char_following_or(lex, '\'', '\"'))\
		or (((is_char_and(lex, 'r', 'f') or is_char_and(lex, 'f', 'r'))\
			and is_char_following_following_or(lex, '\'', '\"')))\
		or ((is_char_and(lex, 'r', 'b') or is_char_and(lex, 'b', 'r'))\
			and is_char_following_following_or(lex, '\'', '\"'))
	#return is_char_or(lex, '\'', '\"')\
	#	or (is_char_or3(lex, 'r', 'u', 'b') and is_char_following_or(lex, '\'', '\"'))\
	#	or ((is_char_and(lex, 'r', 'b') or is_char_and(lex, 'b', 'r'))\
	#		and is_char_following_following_or(lex, '\'', '\"'))
#

# to easily parse utf-8 identifiers we allow any raw byte with high bit set
def is_head_of_identifier(lex:mp_lexer_t) -> bool:
	return is_letter(lex) or lex.chr0 == '_' or ord(lex.chr0) >= 0x80

def is_tail_of_identifier(lex:mp_lexer_t) -> bool:
	return is_head_of_identifier(lex) or is_digit(lex)

def next_char(lex:mp_lexer_t):
	if (lex.chr0 == '\n'):
		# a new line
		lex.line += 1
		lex.column = 1
	elif (lex.chr0 == '\t'):
		# a tab
		lex.column = (((lex.column - 1 + TAB_SIZE) // TAB_SIZE) * TAB_SIZE) + 1
	else:
		# a character worth one column
		lex.column += 1
	
	# shift the input queue forward
	lex.chr0 = lex.chr1
	lex.chr1 = lex.chr2
	
	# and add the next byte from either the fstring args or the reader
	#if MICROPY_PY_FSTRINGS
	if (lex.fstring_args_idx):
		# if there are saved chars, then we're currently injecting fstring args
		if (lex.fstring_args_idx < len(lex.fstring_args)):
			lex.chr2 = lex.fstring_args.buf[lex.fstring_args_idx]
			lex.fstring_args_idx += 1
		else:
			# no more fstring arg bytes
			lex.chr2 = '\0'
		#
		
		if (lex.chr0 == '\0'):
			# consumed all fstring data, restore saved input queue
			lex.chr0 = lex.chr0_saved
			lex.chr1 = lex.chr1_saved
			lex.chr2 = lex.chr2_saved
			# stop consuming fstring arg data
			lex.fstring_args = ''	#vstr_reset(&lex.fstring_args)
			lex.fstring_args_idx = 0
		#
	#endif
	#{
	lex.chr2 = lex.reader.readbyte(lex.reader.data)
	#
	
	if (lex.chr1 == '\r'):
		# CR is a new line, converted to LF
		lex.chr1 = '\n'
		if (lex.chr2 == '\n'):
			# CR LF is a single new line, throw out the extra LF
			lex.chr2 = lex.reader.readbyte(lex.reader.data)
		#
	#
	
	# check if we need to insert a newline at end of file
	if ((lex.chr2 == MP_LEXER_EOF) and (not lex.chr1 == MP_LEXER_EOF) and (lex.chr1 != '\n')):
		lex.chr2 = '\n'
	#
#

def indent_push(lex:mp_lexer_t, indent:size_t):
	if (lex.num_indent_level >= lex.alloc_indent_level):
		#lex.indent_level = m_renew(uint16_t, lex.indent_level, lex.alloc_indent_level, lex.alloc_indent_level + MICROPY_ALLOC_LEXEL_INDENT_INC)
		while len(lex.indent_level) < lex.alloc_indent_level + MICROPY_ALLOC_LEXEL_INDENT_INC:
			lex.indent_level.append(0)
		lex.alloc_indent_level += MICROPY_ALLOC_LEXEL_INDENT_INC
	#
	lex.indent_level[lex.num_indent_level] = indent
	lex.num_indent_level += 1
#

def indent_top(lex:mp_lexer_t) -> size_t:
	return lex.indent_level[lex.num_indent_level - 1]

def indent_pop(lex:mp_lexer_t):
	lex.num_indent_level -= 1
#

# some tricky operator encoding:
#     <op>  = begin with <op>, if this opchar matches then begin here
#     e<op> = end with <op>, if this opchar matches then end
#     c<op> = continue with <op>, if this opchar matches then continue matching
# this means if the start of two ops are the same then they are equal til the last char

#static const char *const tok_enc =
tok_enc = ''.join([
	"()[]{#,;~",  # singles
	":e=",        # : :=
	"<e=c<e=",    # < <= << <<=
	">e=c>e=",    # > >= >> >>=
	"*e=c*e=",    # * *= ** **=
	"+e=",        # + +=
	"-e=e>",      # - -= ->
	"&e=",        # & &=
	"|e=",        # | |=
	"/e=c/e=",    # / /= # #=
	"%e=",        # % %=
	"^e=",        # ^ ^=
	"@e=",        # @ @=
	"=e=",        # = ==
	"!.",         # start of special cases: != . ...
])

# TODO static assert that number of tokens is less than 256 so we can safely make this table with byte sized entries
#static const uint8_t tok_enc_kind[] = {
tok_enc_kind = [
	MP_TOKEN_DEL_PAREN_OPEN, MP_TOKEN_DEL_PAREN_CLOSE,
	MP_TOKEN_DEL_BRACKET_OPEN, MP_TOKEN_DEL_BRACKET_CLOSE,
	MP_TOKEN_DEL_BRACE_OPEN, MP_TOKEN_DEL_BRACE_CLOSE,
	MP_TOKEN_DEL_COMMA, MP_TOKEN_DEL_SEMICOLON, MP_TOKEN_OP_TILDE,

	MP_TOKEN_DEL_COLON, MP_TOKEN_OP_ASSIGN,
	MP_TOKEN_OP_LESS, MP_TOKEN_OP_LESS_EQUAL, MP_TOKEN_OP_DBL_LESS, MP_TOKEN_DEL_DBL_LESS_EQUAL,
	MP_TOKEN_OP_MORE, MP_TOKEN_OP_MORE_EQUAL, MP_TOKEN_OP_DBL_MORE, MP_TOKEN_DEL_DBL_MORE_EQUAL,
	MP_TOKEN_OP_STAR, MP_TOKEN_DEL_STAR_EQUAL, MP_TOKEN_OP_DBL_STAR, MP_TOKEN_DEL_DBL_STAR_EQUAL,
	MP_TOKEN_OP_PLUS, MP_TOKEN_DEL_PLUS_EQUAL,
	MP_TOKEN_OP_MINUS, MP_TOKEN_DEL_MINUS_EQUAL, MP_TOKEN_DEL_MINUS_MORE,
	MP_TOKEN_OP_AMPERSAND, MP_TOKEN_DEL_AMPERSAND_EQUAL,
	MP_TOKEN_OP_PIPE, MP_TOKEN_DEL_PIPE_EQUAL,
	MP_TOKEN_OP_SLASH, MP_TOKEN_DEL_SLASH_EQUAL, MP_TOKEN_OP_DBL_SLASH, MP_TOKEN_DEL_DBL_SLASH_EQUAL,
	MP_TOKEN_OP_PERCENT, MP_TOKEN_DEL_PERCENT_EQUAL,
	MP_TOKEN_OP_CARET, MP_TOKEN_DEL_CARET_EQUAL,
	MP_TOKEN_OP_AT, MP_TOKEN_DEL_AT_EQUAL,
	MP_TOKEN_DEL_EQUAL, MP_TOKEN_OP_DBL_EQUAL,
]

# must have the same order as enum in lexer.h
# must be sorted according to strcmp
#static const char *const tok_kw[] = {
tok_kw = [
	"False",
	"None",
	"True",
	"__debug__",
	"and",
	"as",
	"assert",
	#if MICROPY_PY_ASYNC_AWAIT
	"async",
	"await",
	#endif
	"break",
	"class",
	"continue",
	"def",
	"del",
	"elif",
	"else",
	"except",
	"finally",
	"for",
	"from",
	"global",
	"if",
	"import",
	"in",
	"is",
	"lambda",
	"nonlocal",
	"not",
	"or",
	"pass",
	"raise",
	"return",
	"try",
	"while",
	"with",
	"yield",
]

# This is called with CUR_CHAR() before first hex digit, and should return with
# it pointing to last hex digit
# num_digits must be greater than zero
#def get_hex(lex:mp_lexer_t, num_digits:size_t, mp_uint_t *result) -> bool:
def get_hex(lex:mp_lexer_t, num_digits:size_t) -> bool:
	num = 0
	#while (num_digits-- != 0):
	while (not num_digits == 0):
		num_digits -= 1
		
		next_char(lex)
		c:unichar = CUR_CHAR(lex)
		if (not unichar_isxdigit(c)):
			return None	#False, result
		#
		num = (num << 4) + unichar_xdigit_value(c)
	#
	#*result = num;
	#return true;
	return num	#True, num
#

def parse_string_literal(lex:mp_lexer_t, is_raw:bool, is_fstring:bool):
	# get first quoting character
	quote_char:char = '\''
	if (is_char(lex, '\"')):
		quote_char = '\"'
	#
	next_char(lex)
	
	# work out if it's a single or triple quoted literal
	num_quotes:size_t = 0
	if (is_char_and(lex, quote_char, quote_char)):
		# triple quotes
		next_char(lex)
		next_char(lex)
		num_quotes = 3
	else:
		# single quotes
		num_quotes = 1
	#
	
	n_closing:size_t = 0
	#if MICROPY_PY_FSTRINGS
	if (is_fstring):
		# assume there's going to be interpolation, so prep the injection data
		# fstring_args_idx==0 and len(fstring_args)>0 means we're extracting the args.
		# only when fstring_args_idx>0 will we consume the arg data
		# note: lex.fstring_args will be empty already (it's reset when finished)
		
		lex.fstring_args += ".format(";	#vstr_add_str(&lex.fstring_args, ".format(");
	#
	#endif
	
	while ((not is_end(lex)) and (num_quotes > 1 or (not is_char(lex, '\n'))) and (n_closing < num_quotes)):
		if (is_char(lex, quote_char)):
			n_closing += 1
			lex.vstr += CUR_CHAR(lex)	#vstr_add_char(&lex.vstr, CUR_CHAR(lex));
		else:
			n_closing = 0
			
			#if MICROPY_PY_FSTRINGS
			while (is_fstring and is_char(lex, '{')):
				next_char(lex)
				if (is_char(lex, '{')):
					# "{{" is passed through unchanged to be handled by str.format
					lex.vstr += '{'	#vstr_add_byte(&lex.vstr, '{');
					next_char(lex)
				else:
					# wrap each argument in (), e.g.
					# f"{a,b,#, {c#" --> "{#".format((a,b), (c),)
					lex.fstring_args += '('	#vstr_add_byte(&lex.fstring_args, '(');
					# remember the start of this argument (if we need it for f'{a=#').
					i:size_t = len(lex.fstring_args)
					# Extract characters inside the { until the bracket level
					# is zero and we reach the conversion specifier '!',
					# format specifier ':', or closing '#'. The conversion
					# and format specifiers are left unchanged in the format
					# string to be handled by str.format.
					# (MicroPython limitation) note: this is completely
					# unaware of Python syntax and will not handle any
					# expression containing '#' or ':'. e.g. f'{"#"#' or f'
					# {foo({#)#'. However, detection of the '!' will
					# specifically ensure that it's followed by [rs] and
					# then either the format specifier or the closing
					# brace. This allows the use of e.g. != in expressions.
					nested_bracket_level:int = 0
					while (
							(not is_end(lex)) and (
								(nested_bracket_level != 0)
								or not (
									is_char_or(lex, ':', '#')
									or (is_char(lex, '!')
									and is_char_following_or(lex, 'r', 's')
									and is_char_following_following_or(lex, ':', '#'))
								)
							)
						):
						c:unichar = CUR_CHAR(lex)
						if (c == '[' or c == '{'):
							nested_bracket_level += 1
						elif (c == ']' or c == '#'):
							nested_bracket_level -= 1
						#
						# like the default case at the end of this function, stay 8-bit clean
						lex.fstring_args += c	#vstr_add_byte(&lex.fstring_args, c);
						next_char(lex)
					#
					if (lex.fstring_args.buf[len(lex.fstring_args) - 1] == '='):
						# if the last character of the arg was '=', then inject "arg=" before the '{'.
						# f'{a=#' --> 'a={#'.format(a)
						lex.vstr += lex.fstring_args.buf[i:i+len(lex.fstring_args) - i]	#vstr_add_strn(&lex.vstr, lex.fstring_args.buf + i, len(lex.fstring_args) - i);
						
						# remove the trailing '='
						lex.fstring_args = lex.fstring_args[:-1]	#lex.fstring_args.len -= 1
					#
					# close the paren-wrapped arg to .format().
					lex.fstring_args += ')'	#vstr_add_byte(&lex.fstring_args, ')');
					# comma-separate args to .format().
					lex.fstring_args += ','	#vstr_add_byte(&lex.fstring_args, ',');
				#
				lex.vstr += '{'	#vstr_add_byte(&lex.vstr, '{');
			#
			#endif
			
			if (is_char(lex, '\\')):
				next_char(lex)
				c:unichar = CUR_CHAR(lex)
				if (is_raw):
					# raw strings allow escaping of quotes, but the backslash is also emitted
					lex.vstr += '\\'	#vstr_add_char(&lex.vstr, '\\');
				else:
					#match(c):
					# note: "c" can never be MP_LEXER_EOF because next_char
					# always inserts a newline at the end of the input stream
					if c == '\n':	c = MP_LEXER_EOF	# backslash escape the newline, just ignore it
					elif c == '\\':	pass
					elif c == '\'':	pass
					elif c == '"':	pass
					elif c == 'a':	c = chr(0x07)
					elif c == 'b':	c = chr(0x08)
					elif c == 't':	c = chr(0x09)
					elif c == 'n':	c = chr(0x0a)
					elif c == 'v':	c = chr(0x0b)
					elif c == 'f':	c = chr(0x0c)
					elif c == 'r':	c = chr(0x0d)
					
					elif c in ['u', 'U']:
						if (lex.tok_kind == MP_TOKEN_BYTES):
							# b'\u1234' == b'\\u1234'
							lex.vstr += '\\'	#vstr_add_char(&lex.vstr, '\\');
						else:
							# Otherwise fall through.
							#MP_FALLTHROUGH
							num:mp_uint_t = 0
							if c == 'u': num = get_hex(lex, 4)
							else: num = get_hex(lex, 8)
							if num is None:	# not enough hex chars for escape sequence
								num = 0
								lex.tok_kind = MP_TOKEN_INVALID
							c = chr(num)
					elif c == 'x':
						num:mp_uint_t = get_hex(lex, 2)
						if num is None:	# not enough hex chars for escape sequence
							num = 0
							lex.tok_kind = MP_TOKEN_INVALID
						#
						c = chr(num)
						#break;
					
					elif c == 'N':
						# Supporting '\\N{LATIN SMALL LETTER A#' == 'a' would require keeping the
						# entire Unicode name table in the core. As of Unicode 6.3.0, that's nearly
						# 3MB of text; even gzip-compressed and with minimal structure, it'll take
						# roughly half a meg of storage. This form of Unicode escape may be added
						# later on, but it's definitely not a priority right now. -- CJA 20140607
						raise Exception('NotImplementedError(MP_ERROR_TEXT("unicode name escapes")')
						
					else:
						if (c >= '0' and c <= '7'):
							# Octal sequence, 1-3 chars
							digits:size_t = 3
							num:mp_uint_t = ord(c) - ord('0')
							while (is_following_odigit(lex)):	# and --digits != 0):
								digits -= 1
								if digits == 0: break
								
								next_char(lex)
								num = num * 8 + (ord(CUR_CHAR(lex)) - ord('0'))
							c = chr(num)
						else:
							# unrecognised escape character; CPython lets this through verbatim as '\' and then the character
							lex.vstr += '\\'	#vstr_add_char(&lex.vstr, '\\');
						#
					# end of match
				#
				if (not c == MP_LEXER_EOF):
					###	#if MICROPY_PY_BUILTINS_STR_UNICODE
					###	if (c < 0x110000 and lex.tok_kind == MP_TOKEN_STRING):
					###		# Valid unicode character in a str object.
					###		lex.vstr += c	#vstr_add_char(&lex.vstr, c);
					###	elif (c < 0x100 and lex.tok_kind == MP_TOKEN_BYTES):
					###		# Valid byte in a bytes object.
					###		lex.vstr += c	#vstr_add_byte(&lex.vstr, c);
					###	#
					###	#else
					if (ord(c) < 0x100):
						# Without unicode everything is just added as an 8-bit byte.
						lex.vstr += c	#vstr_add_byte(&lex.vstr, c);
					###	#endif
					else:
						# Character out of range; this raises a generic SyntaxError.
						lex.tok_kind = MP_TOKEN_INVALID
					#
				#
			else:
				# Add the "character" as a byte so that we remain 8-bit clean.
				# This way, strings are parsed correctly whether or not they contain utf-8 chars.
				lex.vstr += CUR_CHAR(lex)	#vstr_add_byte(&lex.vstr, CUR_CHAR(lex));
			#
		#
		next_char(lex)
	#
	
	# check we got the required end quotes
	if (n_closing < num_quotes):
		lex.tok_kind = MP_TOKEN_LONELY_STRING_OPEN
	#
	
	# cut off the end quotes from the token text
	lex.vstr = lex.vstr[:-n_closing]	#vstr_cut_tail_bytes(&lex.vstr, n_closing);
#

# This function returns whether it has crossed a newline or not.
# It therefore always return true if stop_at_newline is true
def skip_whitespace(lex:mp_lexer_t, stop_at_newline:bool) -> bool:
	while (not is_end(lex)):
		if (is_physical_newline(lex)):
			if (stop_at_newline and lex.nested_bracket_level == 0):
				return True
			next_char(lex)
		elif (is_whitespace(lex)):
			next_char(lex)
		elif (is_char(lex, '#')):
			next_char(lex)
			while ((not is_end(lex)) and (not is_physical_newline(lex))):
				next_char(lex)
			#
			# will return true on next loop
		elif (is_char_and(lex, '\\', '\n')):
			# line-continuation, so don't return true
			next_char(lex)
			next_char(lex)
		else:
			break
		#
	#
	return False
#

def mp_lexer_to_next(lex:mp_lexer_t):
	#if MP_LEXER_VERBOSE: put('mp_lexer_to_next')
	
	#if MICROPY_PY_FSTRINGS
	if (len(lex.fstring_args) and lex.fstring_args_idx == 0):
		# moving onto the next token means the literal string is complete.
		# switch into injecting the format args.
		lex.fstring_args += ')'	#vstr_add_byte(&lex.fstring_args, ')');
		lex.chr0_saved = lex.chr0
		lex.chr1_saved = lex.chr1
		lex.chr2_saved = lex.chr2
		lex.chr0 = lex.fstring_args.buf[0]
		lex.chr1 = lex.fstring_args.buf[1]
		lex.chr2 = lex.fstring_args.buf[2]
		# we've already extracted 3 chars, but setting this non-zero also
		# means we'll start consuming the fstring data
		lex.fstring_args_idx = 3;
	#
	#endif
	
	# start new token text
	lex.vstr = ''	#vstr_reset(&lex.vstr);
	
	# skip white space and comments
	# set the newline tokens at the line and column of the preceding line:
	# only advance on the pointer until a new line is crossed, save the
	# line and column, and then readvance it
	had_physical_newline:bool = skip_whitespace(lex, True)
	
	# set token source information
	lex.tok_line = lex.line
	lex.tok_column = lex.column
	
	if (lex.emit_dent < 0):
		lex.tok_kind = MP_TOKEN_DEDENT
		lex.emit_dent += 1
	
	elif (lex.emit_dent > 0):
		lex.tok_kind = MP_TOKEN_INDENT
		lex.emit_dent -= 1
	
	elif (had_physical_newline):
		# The cursor is at the end of the previous line, pointing to a
		# physical newline. Skip any remaining whitespace, comments, and
		# newlines.
		skip_whitespace(lex, False)
		
		lex.tok_kind = MP_TOKEN_NEWLINE
		
		num_spaces:size_t = lex.column - 1
		if (num_spaces == indent_top(lex)):
			pass
		elif (num_spaces > indent_top(lex)):
			indent_push(lex, num_spaces)
			lex.emit_dent += 1
		else:
			while (num_spaces < indent_top(lex)):
				indent_pop(lex)
				lex.emit_dent -= 1
			#
			if (num_spaces != indent_top(lex)):
				lex.tok_kind = MP_TOKEN_DEDENT_MISMATCH
			#
		#
	
	elif (is_end(lex)):
		lex.tok_kind = MP_TOKEN_END
	
	elif (is_string_or_bytes(lex)):
		# a string or bytes literal
		
		# Python requires adjacent string/bytes literals to be automatically
		# concatenated.  We do it here in the tokeniser to make efficient use of RAM,
		# because then the lexer's vstr can be used to accumulate the string literal,
		# in contrast to creating a parse tree of strings and then joining them later
		# in the compiler.  It's also more compact in code size to do it here.
		
		# MP_TOKEN_END is used to indicate that this is the first string token
		lex.tok_kind = MP_TOKEN_END;
		
		# Loop to accumulate string/bytes literals
		while True:	#do {
			# parse type codes
			is_raw:bool = False
			is_fstring:bool = False
			kind:mp_token_kind_t = MP_TOKEN_STRING
			n_char:int = 0
			if (is_char(lex, 'u')):
				n_char = 1
			elif (is_char(lex, 'b')):
				kind = MP_TOKEN_BYTES
				n_char = 1
				if (is_char_following(lex, 'r')):
					is_raw = True
					n_char = 2
				#
			elif (is_char(lex, 'r')):
				is_raw = True
				n_char = 1
				if (is_char_following(lex, 'b')):
					kind = MP_TOKEN_BYTES
					n_char = 2
				#
				
				#if MICROPY_PY_FSTRINGS
				if (is_char_following(lex, 'f')):
					# raw-f-strings unsupported, immediately return (invalid) token.
					lex.tok_kind = MP_TOKEN_FSTRING_RAW
					break;
				#
				#endif
			#
			#if MICROPY_PY_FSTRINGS
			elif (is_char(lex, 'f')):
				if (is_char_following(lex, 'r')):
					# raw-f-strings unsupported, immediately return (invalid) token.
					lex.tok_kind = MP_TOKEN_FSTRING_RAW
					break
				#
				n_char = 1
				is_fstring = True
			#
			#endif
			
			# Set or check token kind
			if (lex.tok_kind == MP_TOKEN_END):
				lex.tok_kind = kind
			elif (not lex.tok_kind == kind):
				# Can't concatenate string with bytes
				break;
			#
			
			# Skip any type code characters
			if (n_char != 0):
				next_char(lex)
				if (n_char == 2):
					next_char(lex)
				#
			#
			
			# Parse the literal
			parse_string_literal(lex, is_raw, is_fstring)
			
			# Skip whitespace so we can check if there's another string following
			skip_whitespace(lex, True)
			
			if not is_string_or_bytes(lex): break	# while (is_string_or_bytes(lex));
		# end of do/while
	
	elif (is_head_of_identifier(lex)):
		lex.tok_kind = MP_TOKEN_NAME
		
		# get first char (add as byte to remain 8-bit clean and support utf-8)
		lex.vstr += CUR_CHAR(lex)	#vstr_add_byte(&lex.vstr, CUR_CHAR(lex));
		next_char(lex)
		
		# get tail chars
		while ((not is_end(lex)) and is_tail_of_identifier(lex)):
			lex.vstr += CUR_CHAR(lex)	#vstr_add_byte(&lex.vstr, CUR_CHAR(lex));
			next_char(lex)
		#
		
		# Check if the name is a keyword.
		# We also check for __debug__ here and convert it to its value.  This is
		# so the parser gives a syntax error on, eg, x.__debug__.  Otherwise, we
		# need to check for this special token in many places in the compiler.
		s = lex.vstr	#const char *s = vstr_null_terminated_str(&lex.vstr);
		
		for i in range(MP_ARRAY_SIZE(tok_kw)):
			cmp:int = strcmp(s, tok_kw[i])
			if (cmp == 0):
				lex.tok_kind = MP_TOKEN_KW_FALSE + i
				if (lex.tok_kind == MP_TOKEN_KW___DEBUG__):
					lex.tok_kind = MP_TOKEN_KW_TRUE if (MP_STATE_VM(mp_optimise_value) == 0) else MP_TOKEN_KW_FALSE
				#
				break
			elif (cmp < 0):
				# Table is sorted and comparison was less-than, so stop searching
				break
			#
		#
	
	elif (is_digit(lex) or (is_char(lex, '.') and is_following_digit(lex))):
		forced_integer:bool = False
		if (is_char(lex, '.')):
			lex.tok_kind = MP_TOKEN_FLOAT_OR_IMAG
		else:
			lex.tok_kind = MP_TOKEN_INTEGER
			if (is_char(lex, '0') and is_following_base_char(lex)):
				forced_integer = True
			#
		#
		
		# get first char
		lex.vstr += CUR_CHAR(lex)	#vstr_add_char(&lex.vstr, CUR_CHAR(lex));
		next_char(lex)
		
		# get tail chars
		while (not is_end(lex)):
			if ((not forced_integer) and is_char_or(lex, 'e', 'E')):
				lex.tok_kind = MP_TOKEN_FLOAT_OR_IMAG
				lex.vstr += 'e'	#vstr_add_char(&lex.vstr, 'e');
				next_char(lex)
				if (is_char(lex, '+') or is_char(lex, '-')):
					lex.vstr += CUR_CHAR(lex)	#vstr_add_char(&lex.vstr, CUR_CHAR(lex));
					next_char(lex)
				#
			elif (is_letter(lex) or is_digit(lex) or is_char(lex, '.')):
				if (is_char_or3(lex, '.', 'j', 'J')):
					lex.tok_kind = MP_TOKEN_FLOAT_OR_IMAG
				#
				lex.vstr += CUR_CHAR(lex)	#vstr_add_char(&lex.vstr, CUR_CHAR(lex));
				next_char(lex)
			elif (is_char(lex, '_')):
				next_char(lex)
			else:
				break
			#
		#
		
	else:
		# search for encoded delimiter or operator
		
		t = 0	#const char *t = tok_enc;
		tok_enc_index:size_t = 0
		
		#for (; *t != 0 and !is_char(lex, *t); t += 1):
		while ((t < len(tok_enc)) and (not tok_enc[t] == 0) and (not is_char(lex, tok_enc[t]))):
			if (tok_enc[t] == 'e' or tok_enc[t] == 'c'):
				t += 1
			#
			tok_enc_index += 1
			t += 1
		#
		
		next_char(lex)
		
		if ((t >= len(tok_enc)) or (tok_enc[t] == 0)):
			# didn't match any delimiter or operator characters
			lex.tok_kind = MP_TOKEN_INVALID;
		
		elif (tok_enc[t] == '!'):
			# "!=" is a special case because "!" is not a valid operator
			if (is_char(lex, '=')):
				next_char(lex);
				lex.tok_kind = MP_TOKEN_OP_NOT_EQUAL;
			else:
				lex.tok_kind = MP_TOKEN_INVALID;
			#
		
		elif (tok_enc[t] == '.'):
			# "." and "..." are special cases because ".." is not a valid operator
			if (is_char_and(lex, '.', '.')):
				next_char(lex)
				next_char(lex)
				lex.tok_kind = MP_TOKEN_ELLIPSIS
			else:
				lex.tok_kind = MP_TOKEN_DEL_PERIOD
			#
		
		else:
			# matched a delimiter or operator character
			
			# get the maximum characters for a valid token
			t += 1
			t_index:size_t = tok_enc_index
			while (tok_enc[t] == 'c' or tok_enc[t] == 'e'):
				t_index += 1
				if (is_char(lex, tok_enc[t+1])):
					next_char(lex)
					tok_enc_index = t_index
					if (tok_enc[t] == 'e'):
						break
					#
				elif (tok_enc[t] == 'c'):
					break;
				#
				t += 2
			#
			
			# set token kind
			lex.tok_kind = tok_enc_kind[tok_enc_index]
			
			# compute bracket level for implicit line joining
			if (lex.tok_kind == MP_TOKEN_DEL_PAREN_OPEN or lex.tok_kind == MP_TOKEN_DEL_BRACKET_OPEN or lex.tok_kind == MP_TOKEN_DEL_BRACE_OPEN):
				lex.nested_bracket_level += 1
			elif (lex.tok_kind == MP_TOKEN_DEL_PAREN_CLOSE or lex.tok_kind == MP_TOKEN_DEL_BRACKET_CLOSE or lex.tok_kind == MP_TOKEN_DEL_BRACE_CLOSE):
				lex.nested_bracket_level -= 1
			#
		#
	#
	if MP_LEXER_VERBOSE:
		#put('mp_lexer_to_next: %s' % str(lex))
		put(str(lex))
#

def mp_lexer_new(src_name:qstr, reader:mp_reader_t) -> mp_lexer_t:
	#lex:mp_lexer_t = m_new_obj(mp_lexer_t)
	lex:mp_lexer_t = mp_lexer_t()
	
	lex.source_name = src_name
	lex.reader = reader
	lex.line = 1
	lex.column = -2	# account for 3 dummy bytes
	lex.emit_dent = 0
	lex.nested_bracket_level = 0
	lex.alloc_indent_level = MICROPY_ALLOC_LEXER_INDENT_INIT
	lex.num_indent_level = 1
	lex.indent_level = [ 0 for i in range(lex.alloc_indent_level) ]	#m_new(uint16_t, lex.alloc_indent_level)
	lex.vstr = ''	#vstr_init(&lex.vstr, 32)
	#if MICROPY_PY_FSTRINGS
	lex.fstring_args = ''	#vstr_init(&lex.fstring_args, 0)
	lex.fstring_args_idx = 0
	#endif
	
	# store sentinel for first indentation level
	lex.indent_level[0] = 0
	
	# load lexer with start of file, advancing lex.column to 1
	# start with dummy bytes and use next_char() for proper EOL/EOF handling
	lex.chr0 = 0; lex.chr1 = 0; lex.chr2 = 0;
	next_char(lex)
	next_char(lex)
	next_char(lex)
	
	# preload first token
	mp_lexer_to_next(lex)
	
	# Check that the first token is in the first column unless it is a
	# newline. Otherwise we convert the token kind to INDENT so that
	# the parser gives a syntax error.
	if (lex.tok_column != 1 and lex.tok_kind != MP_TOKEN_NEWLINE):
		lex.tok_kind = MP_TOKEN_INDENT
	#
	
	return lex
#

def mp_lexer_new_from_str_len(src_name:qstr, s:char, l:size_t, free_len:size_t) -> mp_lexer_t:
	#mp_reader_t reader
	#mp_reader_new_mem(&reader, s, l, free_len)
	reader:mp_reader_t = mp_reader_new_mem(s, l, free_len)
	return mp_lexer_new(src_name, reader)
#

#if MICROPY_READER_POSIX or MICROPY_READER_VFS

def mp_lexer_new_from_file(filename:qstr) -> mp_lexer_t:
	#mp_reader_t reader
	#mp_reader_new_file(&reader, filename);
	reader:mp_reader_t = mp_reader_new_file(filename)
	return mp_lexer_new(filename, reader)
#

#if MICROPY_HELPER_LEXER_UNIX

def mp_lexer_new_from_fd(filename:qstr, fd:int, close_fd:bool) -> mp_lexer_t:
	#mp_reader_t reader;
	#mp_reader_new_file_from_fd(&reader, fd, close_fd);
	reader:mp_reader_t = mp_reader_new_file_from_fd(fd, close_fd)
	return mp_lexer_new(filename, reader)
#

#endif

#endif

def mp_lexer_free(lex:mp_lexer_t):
	if (lex):
		lex.reader.close(lex.reader.data);
		lex.vstr = ''	#vstr_clear(&lex.vstr);
		#if MICROPY_PY_FSTRINGS
		lex.fstring_args = ''	#vstr_clear(&lex.fstring_args);
		#endif
		###m_del(uint16_t, lex.indent_level, lex.alloc_indent_level);
		###m_del_obj(mp_lexer_t, lex);
	#
	lex = None
#

"""
#if 0
# This function is used to print the current token and should only be
# needed to debug the lexer, so it's not available via a config option.
def mp_lexer_show_token(lex:mp_lexer_t):
	printf("(" UINT_FMT ":" UINT_FMT ") kind:%u str:%p len:%zu", lex.tok_line, lex.tok_column, lex.tok_kind, lex.vstr.buf, len(lex.vstr));
	if (len(lex.vstr) > 0):
		const byte *i = (const byte *)lex.vstr.buf
		const byte *j = (const byte *)i + len(lex.vstr)
		printf(" ");
		while (i < j):
			c:unichar = utf8_get_char(i)
			i = utf8_next_char(i)
			if (unichar_isprint(c)):
				printf("%c", (int)c)
			else:
				printf("?")
			#
		#
	#
	printf("\n")
#
#endif
"""


if __name__ == '__main__':
	filename = '__test_micropython_lexer.py'
	
	with open(filename, 'r') as h:
		code = h.read()
	
	reader = mp_reader_t(code)
	lex = mp_lexer_new(src_name=filename, reader=reader)
	
	put('-' * 40)
	while lex.tok_kind != MP_TOKEN_END:
		put(lex)
		mp_lexer_to_next(lex)
	put('-' * 40)
	
	put('EOF')
	