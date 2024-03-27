"""
ShadowRunner for HAUL3

This is shadowRunner3 - the resurrection of the VM idea introduced in "shadowRunner1"
For platforms that are too finicky to compile directly (now) we produce a byte code and implement a platform-specific VM
The VM itself is, again, coded in HAUL3 so it CAN be cross-compiled for the "easy" platforms OR implemented natively on that platform (which is easier for e.g. Z80 ASM).

2017-01-25
"""

import strings

#@fun put
#@arg txt String
def put(txt):
	print('vm:\t' + str(txt))

### Configuration
#@var VM_VALUE_SIZE byte
#@var VM_MEM_SIZE int
#@var VM_STACK_SIZE int
VM_VALUE_SIZE = 2	# Size in bytes
VM_MEM_SIZE = 128	#64	#1024 * 1
VM_STACK_SIZE = 8

### Value modes
# Value modes 0,1,2,7 do not need further data
#@var VM_VALUE_MODES Dict
VM_VALUE_MODES = {
	0x00: '0',
	0x01: '1',
	0x02: 'A',	# value in Accumulator
	0x03: 'D',	# Direct value
	0x04: 'M',	# Memory address
	0x05: 'N',	# Named item (e.g. variable)
	0x06: 'R',	# Memory address relative to A
	0x07: 'S',	# (top-most) Stack value
}

"""
### Create the long version of the value mode list
#@fun _vm_list_value_modes String
def _vm_list_value_modes():
	#@var r String
	r2 = '\n### VM_VALUE_MODES (auto-generated)\n'
	r = ''
	for value_mode_num in sorted(VM_VALUE_MODES):
		r2 = r2 + '#@const VM_VALUE_MODE_' + VM_VALUE_MODES[value_mode_num] + ' byte ' + ('%d' % (value_mode_num)) + '\n'
		r = r + 'VM_VALUE_MODE_' + VM_VALUE_MODES[value_mode_num] + '\t= 0x' + ('%02x' % (value_mode_num)) + '\n'
	return r2 + '\n' + r
put(_vm_list_value_modes()); sys.exit()
"""

### VM_VALUE_MODES (auto-generated)
#@const VM_VALUE_MODE_0 byte 0
#@const VM_VALUE_MODE_1 byte 1
#@const VM_VALUE_MODE_A byte 2
#@const VM_VALUE_MODE_D byte 3
#@const VM_VALUE_MODE_M byte 4
#@const VM_VALUE_MODE_N byte 5
#@const VM_VALUE_MODE_R byte 6
#@const VM_VALUE_MODE_S byte 7
VM_VALUE_MODE_0	= 0x00
VM_VALUE_MODE_1	= 0x01
VM_VALUE_MODE_A	= 0x02
VM_VALUE_MODE_D	= 0x03
VM_VALUE_MODE_M	= 0x04
VM_VALUE_MODE_N	= 0x05
VM_VALUE_MODE_R	= 0x06
VM_VALUE_MODE_S	= 0x07


### Mapping of opcodes
#@var VM_OPCODES Dict
VM_OPCODES = {
	0x00: 'NOP',
	
	0x10: 'LOAD_',	# Set accumulator to _
	0x18: 'LOAD_IP',	# Load InstructionPointer into accumulator
	0x19: 'LOAD_SP',	# Load StackPointer into accumulator
	
	0x20: 'ADD_',	# Add _ to accumulator
	0x28: 'SUB_',	# Subtract value from accumulator
	
	0x30: 'MUL_',	# Multiply accumulator by _
	0x38: 'DIV_',	# Divide accumulator by _
	
	0x40: 'SHL_',	# Shift left by _
	0x48: 'SHR_',	# Shift right by _
	
	0x50: 'AND_',	# AND accumulator with _
	0x58: 'OR_',	# OR accumulator with _
	0x60: 'XOR_',	# XOR accumulator with _
	
	0x70: 'PUSH_',	# Push _
	0x80: 'POP_',	# Pop into accumulator item #; e.g. POP_1 = Pop the second-last argument into accumulator (keeping the top-most value, which is e.g. the return address)
	
	0x90: 'JUMP_',	# Jump to _
	0xa0: 'CALL_',	# Push PC+1+VALUE_SIZE onto stack and jump to _
	0xa8: 'HOOK_',	# Push PC+1+VALUE_SIZE onto stack and jump to system function _
	0xb0: 'RET',	# Pop the return address and jump there
	
	0xc0: 'IF_IS_',	# If accumulator == _
	0xc8: 'IF_NOT_',	# If accumulator != _
	0xd0: 'IF_LT_',	# If accumulator < _
	0xd8: 'IF_GT_',	# If accumulator > _
	
	0xe0: 'COMMENT',
	0xf0: 'HALT',
	0xff: 'NOP_FF'	# Intentionally left blank.
}

"""
### Create the long version of the opcode list
def _vm_list_opcodes():
	r2 = '\n### VM_OPCODES (auto-generated)\n'
	r = ''
	for op_num in sorted(VM_OPCODES):
		r2 = r2 + '#@const VM_OP_' + VM_OPCODES[op_num] + ' byte ' + ('%d' % (op_num)) + '\n'
		r = r + 'VM_OP_' + VM_OPCODES[op_num] + '\t= 0x' + ('%02x' % (op_num)) + '\n'
	return r2 + '\n' + r
put(_vm_list_opcodes()); sys.exit()
"""

### VM_OPCODES (auto-generated)
#@const VM_OP_NOP byte 0
#@const VM_OP_LOAD_ byte 16
#@const VM_OP_LOAD_IP byte 24
#@const VM_OP_LOAD_SP byte 25
#@const VM_OP_ADD_ byte 32
#@const VM_OP_SUB_ byte 40
#@const VM_OP_MUL_ byte 48
#@const VM_OP_DIV_ byte 56
#@const VM_OP_SHL_ byte 64
#@const VM_OP_SHR_ byte 72
#@const VM_OP_AND_ byte 80
#@const VM_OP_OR_ byte 88
#@const VM_OP_XOR_ byte 96
#@const VM_OP_PUSH_ byte 112
#@const VM_OP_POP_ byte 128
#@const VM_OP_JUMP_ byte 144
#@const VM_OP_CALL_ byte 160
#@const VM_OP_HOOK_ byte 168
#@const VM_OP_RET byte 176
#@const VM_OP_IF_IS_ byte 192
#@const VM_OP_IF_NOT_ byte 200
#@const VM_OP_IF_LT_ byte 208
#@const VM_OP_IF_GT_ byte 216
#@const VM_OP_COMMENT byte 224
#@const VM_OP_HALT byte 240
#@const VM_OP_NOP_FF byte 255
VM_OP_NOP	= 0x00
VM_OP_LOAD_	= 0x10
VM_OP_LOAD_IP	= 0x18
VM_OP_LOAD_SP	= 0x19
VM_OP_ADD_	= 0x20
VM_OP_SUB_	= 0x28
VM_OP_MUL_	= 0x30
VM_OP_DIV_	= 0x38
VM_OP_SHL_	= 0x40
VM_OP_SHR_	= 0x48
VM_OP_AND_	= 0x50
VM_OP_OR_	= 0x58
VM_OP_XOR_	= 0x60
VM_OP_PUSH_	= 0x70
VM_OP_POP_	= 0x80
VM_OP_JUMP_	= 0x90
VM_OP_CALL_	= 0xa0
VM_OP_HOOK_	= 0xa8
VM_OP_RET	= 0xb0
VM_OP_IF_IS_	= 0xc0
VM_OP_IF_NOT_	= 0xc8
VM_OP_IF_LT_	= 0xd0
VM_OP_IF_GT_	= 0xd8
VM_OP_COMMENT	= 0xe0
VM_OP_HALT	= 0xf0
VM_OP_NOP_FF	= 0xff


### Sys hooks
#@const VM_HOOK_PUT_S byte 0
#@const VM_HOOK_PUT_A byte 1
VM_HOOK_PUT_S	= 0x00
VM_HOOK_PUT_A	= 0x01


class Memory:
	
	#@var size int
	#@var data byte []
	
	#@fun __init__
	#@arg size int
	def __init__(self, size):
		self.size = size
		#self.data = bytearray([0] * self.size)
		
		#@var i int
		#self.data = []	#bytearray([0] * self.size)
		#for i in range(self.size): self.data.append(0x00)
		#self.data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,	0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,	0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,	0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		self.data = [ 0 ] * size
		
	
	#@fun peek byte
	#@arg address int
	def peek(self, address):
		#if (address >= self.size):
		#	put('Peek past end of memory (%04X)' % (address))
		return self.data[address]
	
	#@fun poke
	#@arg address int
	#@arg value byte
	def poke(self, address, value):
		#if (address >= self.size):
		#	put('Poke past end of memory (%04X)' % (address))
		#	return
		self.data[address] = value
	
	#@fun write_to_file
	#@arg filename String
	#@arg size int 0
	def write_to_file(self, filename, size):
		"""
		#@var h int
		if (size < 0):
			size = self.size
		h = open(filename, 'wb'):
		h.write(self.data[0:size])
		h.close()
		"""
		put('Disabled for HAUL translation')


class VM:
	
	#@var a int
	#@var mem Memory
	#@var ip int
	#@var ip_next int
	#@var stack Memory
	#@var sp int
	#@var running bool
	#@var named_offset int
	
	#@fun __init__
	def __init__(self):
		self.a = 0
		
		self.mem = Memory(VM_MEM_SIZE)
		self.ip = 0
		self.ip_next = 0
		
		# It is also possible to have stack and heap in the same memory location!
		# self.stack = self.mem; self.sp = VM_MEM_SIZE - VM_STACK_SIZE * VM_VALUE_SIZE
		self.stack = Memory(VM_STACK_SIZE)
		self.sp = 0
		
		self.running = False
		
		self.named_offset = 0x0000	# Where variables start
	
	#@fun push
	#@arg value2 int
	def push(self, value2):
		self.stack.poke(self.sp, value2 >> 8)
		self.sp = self.sp + 1
		self.stack.poke(self.sp, value2 & 0xff)
		self.sp = self.sp + 1
	
	#@fun pop int
	def pop(self):
		# Hard-coded for VALUE_SIZE==2
		#@var r int
		self.sp = self.sp - 1
		r = self.stack.peek(self.sp)
		self.sp = self.sp - 1
		r = r + (self.stack.peek(self.sp) << 8)
		return r
	
	#@fun pop_multi int
	#@arg i byte
	def pop_multi(self, i):
		#@var r int
		#@var spi int
		self.sp = self.sp - 2
		spi = self.sp - i*2
		r = (self.stack.peek(spi) << 8) + self.stack.peek(spi+1)
		while spi < self.sp:
			self.stack.poke(spi, self.stack.peek(spi+2))
			spi = spi + 1
		return r
	
	#@fun peek byte
	#@arg address int
	def peek(self, address):
		return self.mem.peek(address)
	
	#@fun poke
	#@arg address int
	#@arg value byte
	def poke(self, address, value):
		#if (address >= VM_MEM_SIZE):
		#	put('MEM OOB!')
		#	return
		self.mem.poke(address, value)
	
	#@fun get_value int
	def get_value(self):
		#@var r int
		r = self.mem.peek(self.ip_next) << 8
		self.ip_next = self.ip_next + 1
		r = r + self.mem.peek(self.ip_next)
		self.ip_next = self.ip_next + 1
		return r
	
	#@fun get_value_signed int
	def get_value_signed(self):
		#@var v int
		v = self.get_value()
		if (v >= 0x8000):
			return (v - 0x10000)
			
		
		return v
	
	#@fun peek_value int
	#@arg address int
	def peek_value(self, address):
		#return (self.mem.peek(address) << 8) + self.mem.peek(address)
		return (self.mem.peek(address) * 256) + self.mem.peek(address)
	
	#@fun halt
	def halt(self):
		put('HALT!')
		self.running = False
	
	#@fun error
	#@arg msg String
	def error(self, msg):
		#@var r String
		#r = ('VM error: "%s" at %04X' % (msg, self.ip))
		r = ('VM error: "' + msg + '" at ' + str(self.ip))
		self.running = False
		raise Exception(r)
	
	#@fun hook
	#@arg index int
	def hook(self, index):
		#put('Sys hook %04X' % (index))
		put('Sys hook ' + str(index))
		#@var value int
		#@var c byte
		#@var r String
		
		if (index == VM_HOOK_PUT_S):
			# Output string whose address is in stack
			value = self.pop()
			r = ''
			c = 0xff
			while (c != 0):
				c = self.peek(value)
				if (c != 0):
					r = r + chr(c)
					value = value + 1
				#
			put(r)
			return
		
		if (index == VM_HOOK_PUT_A):
			put('A=%04X' % (self.a))
			return
		
		self.error('Sys hook 0x%04X is not implemented!' % (index))
		
	
	#@fun step_over
	def step_over(self):
		#@var op byte
		#@var value_mode byte
		### Fetch instruction
		op = self.peek(self.ip_next)
		
		self.ip_next = self.ip_next + 1	# Step over this instruction
		
		if (op == VM_OP_COMMENT):
			while (self.peek(self.ip_next) != 0):
				self.ip_next = self.ip_next + 1	# Step over this instruction
			return
		
		# Check if this instruction has arguments we also need to skip
		value_mode = op & 0x07	# lowest bits
		#if (value_mode in [VM_VALUE_MODE_D, VM_VALUE_MODE_M, VM_VALUE_MODE_N, VM_VALUE_MODE_R]):
		if ((value_mode == VM_VALUE_MODE_D) or (value_mode == VM_VALUE_MODE_M) or (value_mode == VM_VALUE_MODE_N) or (value_mode == VM_VALUE_MODE_R)):
			# These value modes use additional data
			self.ip_next = self.ip_next + VM_VALUE_SIZE
			
		
		return
	
	#@fun step
	def step(self):
		# Do one instruction cycle
		
		#@var op byte
		#@var r String
		
		### Fetch instruction
		self.ip = self.ip_next
		op = self.peek(self.ip)
		self.ip_next = self.ip + 1
		
		#put('A=%04X	IP=%04X	SP=%04X	OP=%02X %s' % (self.a, self.ip, self.sp, op, VM_OPCODES[op]))
		#put('>\t%04X\t%02X	%s' % (self.ip, op, VM_OPCODES[op & 0xf8]))
		r = ('>\t%04X' % (self.ip))
		r = r + ('\t%02X' % (op))
		r = r + ('\t%s' % (VM_OPCODES[op & 0xf8]))
		put(r)
		
		### Handle op codes that do not need any addressing
		
		if (op == VM_OP_NOP):
			return
		if (op == VM_OP_LOAD_IP):
			self.a = self.ip
			return
		if (op == VM_OP_LOAD_SP):
			self.a = self.sp
			return
		if (op == VM_OP_RET):
			self.ip_next = self.pop()	# This looks sleek!
			return
		if (op == VM_OP_COMMENT):
			"""
			### Skip until zero-character
			while self.peek(self.ip_next) != 0:
				self.ip_next = self.ip_next + 1
			self.ip_next = self.ip_next + 1
			return
			"""
			### Output until zero character
			#@var comment String
			#@var c byte
			comment = ''
			c = 255
			while (c != 0):
				c = self.peek(self.ip_next)
				if (c != 0):
					comment = comment + chr(c)
					self.ip_next = self.ip_next + 1
				
			put('Comment: "' + comment + '"')
			self.ip_next = self.ip_next + 1
			return
		
		if (op == VM_OP_HALT):
			self.halt()
			return
		
		if (op == VM_OP_NOP_FF):
			return
		
		#@TODO: Speed improvement: Handle some op codes directly without loading their constant value (e.g. ADD_1, POP_0, ...). This speeds up some common cases!
		
		
		### Now determine the value mode
		#@var value_mode byte
		#@var op_base byte
		#@var value int
		
		value_mode = op & 0x07	# lowest bits
		op_base = op & 0xf8	# keep the rest
		#put('>\t%04X\t%02X %s%s' % (self.ip, op, VM_OPCODES[op & 0xf8], VM_VALUE_MODES[value_mode]))
		#put('\t\t\t%s%s' % (VM_OPCODES[op & 0xf8], VM_VALUE_MODES[value_mode]))
		r = ('\t\t\t%s' % (VM_OPCODES[op & 0xf8]))
		r = r + ('%s' % (VM_VALUE_MODES[value_mode]))
		put(r)
		
		### Handle value mode, i.e. get the value for the operation
		if (value_mode == VM_VALUE_MODE_0):	value = 0
		elif (value_mode == VM_VALUE_MODE_1):	value = 1
		elif (value_mode == VM_VALUE_MODE_D):	value = self.get_value()
		elif (value_mode == VM_VALUE_MODE_A):	value = self.a
		elif (value_mode == VM_VALUE_MODE_M):	value = self.peek_value(self.get_value())
		elif (value_mode == VM_VALUE_MODE_N):	value = self.peek_value(self.named_offset + self.get_value())	# named value
		elif (value_mode == VM_VALUE_MODE_R):	value = self.peek_value(self.a + self.get_value_signed())
		elif (value_mode == VM_VALUE_MODE_S):	value = self.pop()
		
		### Now that we have the value: Do something with it!
		
		if (op_base == VM_OP_LOAD_):	self.a = value
		elif (op_base == VM_OP_ADD_):	self.a = self.a + value
		elif (op_base == VM_OP_SUB_):	self.a = self.a - value
		elif (op_base == VM_OP_MUL_):	self.a = self.a * value
		elif (op_base == VM_OP_DIV_):	self.a = self.a / value
		elif (op_base == VM_OP_SHL_):	self.a = self.a << value
		elif (op_base == VM_OP_SHR_):	self.a = self.a >> value
		elif (op_base == VM_OP_AND_):	self.a = self.a & value
		elif (op_base == VM_OP_OR_):	self.a = self.a | value
		elif (op_base == VM_OP_XOR_):	self.a = (self.a ^ value)
		elif (op_base == VM_OP_PUSH_):
			self.push(value)
		elif (op_base == VM_OP_POP_):
			self.a = self.pop_multi(value)
		
		elif (op_base == VM_OP_JUMP_):
			self.ip_next = value
		elif (op_base == VM_OP_CALL_):
			self.push(self.ip_next)
			self.ip_next = value
		elif (op_base == VM_OP_HOOK_):
			self.hook(value)
		elif (op_base == VM_OP_IF_IS_):
			if not (self.a == value): self.step_over()
		elif (op_base == VM_OP_IF_NOT_):
			if not (self.a != value): self.step_over()
		elif (op_base == VM_OP_IF_LT_):
			if not (self.a < value): self.step_over()
		elif (op_base == VM_OP_IF_GT_):
			if not (self.a > value): self.step_over()
		
		
		#else:
		#	#self.error('Unknown opcode %02X' % (op))
		
		#return
	
	#@fun run
	def run(self):
		self.running = True
		while (self.running):
			self.step()
		return
	
	#@fun assemble int
	#@arg op byte
	#@arg value int
	def assemble(self, op, value=(0-1)):
		#@var value_mode byte
		#@var op_base byte
		#@var r String
		value_mode = op & 0x07
		op_base = op & 0xf8
		r = ('%04X\t' % (self.ip))
		r = r + ('%02X' % (op))
		r = r + ('\t%s' % (VM_OPCODES[op_base]))
		r = r + ('%s' % (VM_VALUE_MODES[value_mode]))
		
		self.poke(self.ip, op)
		self.ip = self.ip + 1
		
		if (value >= 0):
			r = r + ('\t%04X' % (value))
			self.poke(self.ip, value >> 8)
			self.ip = self.ip + 1
			self.poke(self.ip, value & 0xff)
			self.ip = self.ip + 1
		put(r)
		return self.ip
	
	#@fun compile_arg
	#@arg text String
	#@arg value int
	def compile_arg(self, text, value):
		# Compile and assemble one instruction into mem
		#@var text2 String
		#@var op int
		#@var op_num int
		#@var op_name String
		#@var op_name_len int
		#@var op_best_len int
		#@var op_rest String
		#@var value_mode_num int
		
		#text2 = text.upper()
		text2 = text
		
		op = 0-1
		op_best_len = 0
		### Find the longest opcode name that fits
		for op_num in VM_OPCODES:
			op_name = VM_OPCODES[op_num]
			op_name_len = strings.length(op_name)
			if (op_name_len > op_best_len):
				#if (text2[0:op_name_len] == op_name):
				#if (text2.startswith(op_name)):
				if (strings.startsWith(text2, op_name)):
					op = op_num
					op_best_len = op_name_len
				
			
		
		#op_rest = text2[op_best_len:]
		op_rest = strings.rest(text2, op_best_len)
		if (op < 0):
			self.error('Unknown opcode in "%s"' % (text))
		#put('Best fit for "%s" is "%s" (%02X). Rest is "%s"' % (text, VM_OPCODES[op], op, op_rest))
		
		for value_mode_num in VM_VALUE_MODES:
			if (op_rest == VM_VALUE_MODES[value_mode_num]):
				op = op + value_mode_num
				break
		
		return self.assemble(op, value)
	
	
	#@fun compile
	#@arg text String
	def compile(self, text):
		return self.compile_arg(text, 0-1)
	
	#@fun text
	#@arg text String
	def text(self, text):
		#@var c String
		# Add a zero-terminated string
		for c in text:
			self.poke(self.ip, ord(c))
			self.ip = self.ip + 1
		self.poke(self.ip, 0)
		self.ip = self.ip + 1
		return self.ip
	
	#@fun __repr__ String
	def __repr__(self):
		#@var r String
		#@var op byte
		r = 'VM status\t'
		#r = r + 'regs: A=%04X	IP=%04X/%04X	SP=%04X/%04X' % (self.a, self.ip, VM_MEM_SIZE, self.sp, VM_STACK_SIZE)
		r = r + 'regs: A=%04X' % (self.a)
		r = r + '	IP=%04X' % (self.ip)
		r = r + '/%04X' % (VM_MEM_SIZE)
		r = r + '	SP=%04X' % (self.sp)
		r = r + '/%04X' % (VM_STACK_SIZE)
		
		r = r + '\t'
		op = self.peek(self.ip)
		r = r + 'OP=%02X' % (op)
		#if (op in VM_OPCODES):
		r = r + ' (%s)' % (VM_OPCODES[op])
		#else: r = r + ' (unknown op)'
		
		return r
	


#@var vm VM

"""
#@fun test_stack1
def test_stack1():
	#@var c int
	vm.stack[0] = '0'
	vm.stack[1] = '1'
	vm.stack[2] = '2'
	vm.stack[3] = '3'
	vm.stack[4] = '4'
	vm.stack[5] = '5'
	put(vm.stack)
	
	vm.push1('A')
	vm.push1('B')
	vm.push1('C')
	vm.push1('D')
	put(vm.stack)
	
	
	#c = vm.pop1()
	c = vm.pop_multi1(1)
	put(chr(c))
	put(vm.stack)
	
	c = vm.pop1()
	put(chr(c))
	put(vm.stack)

#@fun test_stack2
def test_stack2():
	#@var c int
	vm.push(0x4141)
	vm.push(0x4242)
	vm.push(0x4343)
	vm.push(0x4444)
	put(vm.stack)
	
	#c = vm.pop2()
	c = vm.pop_multi2(2)
	put(chr(c & 0xff))
	
	put(vm.stack)
	
"""

#@fun test_hello_world
def test_hello_world():
	#@var hello_offset int
	### Add a comment (it will be skipped) - We will use its data!
	hello_offset = vm.compile('COMMENT')
	vm.text('Hello world!')
	
	# Call PUT with address of string
	vm.compile_arg('PUSH_D', hello_offset)
	#vm.compile('HOOK_0')
	vm.compile_arg('HOOK_D', VM_HOOK_PUT_S)
	#vm.compile('HALT')
	


put('Lets go shadow running...')


vm = VM()

test_hello_world()
#vm.mem.write_to_file('vm_test_hello.srb', size=vm.ip)


#vm.assemble(VM_OP_NOP)
#vm.compile('add_0')

vm.compile('COMMENT'); vm.text('Accumulator test: ')
vm.compile('LOAD_0')
#vm.compile('HOOK_0')
vm.compile('ADD_1')
#vm.compile('HOOK_0')
#vm.compile_arg('ADD_D', 3)
#vm.compile('ADD_1')
#vm.compile('HOOK_0')
vm.compile('IF_IS_0'); vm.compile('COMMENT'); vm.text('it is ZERO.')
vm.compile('IF_IS_1'); vm.compile('COMMENT'); vm.text('it is ONE.')

vm.compile('HALT')
#vm.mem.write_to_file('vm_test.srb', size=vm.ip)


vm.mem.poke(VM_MEM_SIZE-1, VM_OP_HALT) # Stop and end of memory


put(vm)

put('----------------------------------------')	#put('-' * 80)
vm.run()
put('----------------------------------------')	#put('-' * 80)
put(vm)

