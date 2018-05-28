# HUI Protocol for creating UIs through a network connection

def put(txt):
	print('huip.py:\t' + str(txt))

def hexdump(data):
	COLS = 8
	r = ''
	r1 = ''
	r2 = ''
	l = len(data)
	for i in xrange(l):
		v = data[i]
		
		if ((i % COLS) == 0):
			r += '\t' + ('%04X' % i) + ': '
		r += '%02X ' % v
		
		if (v >= 32) and (v < 128):
			r2 += chr(v)
		else:
			r2 += '.'
		
		if ((i % COLS) == (COLS-1)) or (i == l-1):
			for j in xrange(COLS-1 - (i % COLS)):
				r1 += '   '	# Pad missing bytes
			r += r1 + '|' + r2 + '\n'
			r1 = ''
			r2 = ''
		
	return r


# List of commands in HUIP
HUIP_COMMAND_PUT = 1
HUIP_COMMAND_BEEP = 2
HUIP_COMMAND_ADD_ACTION = 3
HUIP_COMMAND_ADD_INPUT = 4

HUIP_EVENT_ACTION = 10
HUIP_EVENT_INPUT = 11

HUIP_TYPE_BOOL = 0
HUIP_TYPE_UINT8 = 1
HUIP_TYPE_UINT16 = 2
HUIP_TYPE_UINT32 = 4
HUIP_TYPE_STRING = 5


class HUIP_Encoder:
	"HUIP byte stream encoder"
	def __init__(self):
		self.on_packet = None
		self.buffer = []
	
	### Packet encapsulation / transport
	def packet_begin(self):
		#put('---- Packet ----')
		self.buffer = []
	def packet_byte(self, b):
		#put('0x%02x' % b)
		self.buffer.append(b)
	def packet_end(self):
		#put('---- End ----')
		if (self.on_packet != None): self.on_packet(self.buffer)
		self.buffer = []
	
	### Encoding of primitive values
	def encode_uint8(self, b):
		self.packet_byte(b)
	def encode_uint16(self, w):
		self.encode_uint8(w >> 8)
		self.encode_uint8(w & 0xff)
	def encode_uint32(self, d):
		self.encode_uint16(d >> 16)
		self.encode_uint16(d & 0x0000ffff)
	def encode_string(self, s):
		l = len(s)
		self.encode_uint16(l)
		for b in s:
			self.encode_uint8(ord(b))
	def encode_bool(self, b):
		self.encode_uint8(1 if b == True else 0)
	def encode_type(self, type):
		self.encode_uint8(type)
	def encode_value(self, type, value):
		#self.encode_type(type)
		if (type == HUIP_TYPE_BOOL):
			self.encode_bool(value)
		elif (type == HUIP_TYPE_UINT8):
			self.encode_uint8(value)
		elif (type == HUIP_TYPE_UINT16):
			self.encode_uint16(value)
		elif (type == HUIP_TYPE_UINT32):
			self.encode_uint32(value)
		elif (type == HUIP_TYPE_STRING):
			self.encode_string(value)
		else:
			raise Exception('Unknown type %s' % (str(type)))
		
	def encode_command(self, cmd):
		self.encode_uint8(cmd)
	def encode_id(self, id):
		self.encode_string(str(id))	#@FIXME: Use an uid number?
	
	### Actual functions to call
	def command_put(self, text):
		self.packet_begin()
		self.encode_command(HUIP_COMMAND_PUT)
		self.encode_string(text)
		self.packet_end()
	
	def command_beep(self):
		self.packet_begin()
		self.encode_command(HUIP_COMMAND_BEEP)
		self.packet_end()
	
	def command_add_action(self, action_id):
		self.packet_begin()
		self.encode_command(HUIP_COMMAND_ADD_ACTION)
		self.encode_string(action_id)
		self.packet_end()
	
	def command_add_input(self, input_id, type, default_value):
		self.packet_begin()
		self.encode_command(HUIP_COMMAND_ADD_INPUT)
		self.encode_id(input_id)
		self.encode_type(type)
		self.encode_value(type, default_value)
		self.packet_end()
	
	### Response from client
	def event_action(self, action_id):
		self.packet_begin()
		self.encode_command(HUIP_EVENT_ACTION)
		self.encode_id(action_id)
		self.packet_end()
	
	def event_input(self, input_id, type, value):
		self.packet_begin()
		self.encode_command(HUIP_EVENT_INPUT)
		self.encode_id(input_id)
		self.encode_type(type)
		self.encode_value(type, value)
		self.packet_end()
	


class HUIP_Decoder:
	"HUIP byte stream decoder"
	
	def __init__(self):
		self.buffer = []
		self.ofs = 0
		self.len = 0
		
		self.on_command_put = None
		self.on_command_beep = None
		
		self.on_command_add_action = None
		self.on_command_add_input = None
		
		self.on_event_action = None
		self.on_event_input = None
	
	### Transport
	def decode_packet(self, data):
		self.buffer = data
		self.ofs = 0
		self.len = len(data)
		
		self.parse_packet()
	
	def get_byte(self):
		if (self.ofs >= self.len):
			raise Exception('Out of data')
		
		#@FIXME: Do a ring buffer
		b = self.buffer[self.ofs]
		self.ofs += 1
		return b
	
	def parse_packet(self):
		cmd = self.decode_command()
		
		# Do the actual packet decoding
		if (cmd == HUIP_COMMAND_PUT):
			s = self.decode_string()
			if (self.on_command_put != None): self.on_command_put(s)
		elif (cmd == HUIP_COMMAND_BEEP):
			if (self.on_command_beep != None): self.on_command_beep()
		
		elif (cmd == HUIP_COMMAND_ADD_ACTION):
			action_id = self.decode_id()
			if (self.on_command_add_action != None): self.on_command_add_action(action_id)
		elif (cmd == HUIP_COMMAND_ADD_INPUT):
			input_id = self.decode_id()
			type = self.decode_type()
			default_value = self.decode_value(type)
			if (self.on_command_add_input != None): self.on_command_add_input(input_id, type, default_value)
		
		elif (cmd == HUIP_EVENT_ACTION):
			action_id = self.decode_id()
			if (self.on_event_action != None): self.on_event_action(action_id)
		elif (cmd == HUIP_EVENT_INPUT):
			input_id = self.decode_id()
			type = self.decode_type()
			value = self.decode_value(type)
			if (self.on_event_input != None): self.on_event_input(input_id, type, value)
		
		else:
			raise Exception('Unknown command 0x%02X in packet:\n%s' % (cmd, hexdump(self.buffer)))
	
	### Decoding of primitives
	def decode_uint8(self):
		return self.get_byte()
	def decode_uint16(self):
		return (self.decode_uint8() << 8) + self.decode_uint8()
	def decode_uint32(self):
		return (self.decode_uint16() << 16) + self.decode_uint16()
	def decode_string(self):
		l = self.decode_uint16()
		s = ''
		for i in xrange(l):
			s += chr(self.decode_uint8())
		return s
	def decode_bool(self):
		v = self.decode_uint8()
		if (v == 0):
			return False
		return True
	def decode_type(self):
		return self.decode_uint8()
	def decode_value(self, type):
		#type = self.decode_type()
		if (type == HUIP_TYPE_BOOL): return self.decode_bool()
		if (type == HUIP_TYPE_UINT8): return self.decode_uint8()
		if (type == HUIP_TYPE_UINT16): return self.decode_uint16()
		if (type == HUIP_TYPE_UINT32): return self.decode_uint32()
		if (type == HUIP_TYPE_STRING): return self.decode_string()
		else:
			raise Exception('Unknown value type %d' % (type))
		
	def decode_command(self):
		return self.decode_uint8()
	def decode_id(self):
		return self.decode_string()	#@FIXME: Use uid of some sorts!


class HUIP_Client:
	"A client presents the actual user interface of an app to the user"
	def __init__(self):
		self.encoder = HUIP_Encoder()
		
		self.decoder = HUIP_Decoder()
		self.decoder.on_command_put = self.handle_put
		self.decoder.on_command_beep = self.handle_beep
		self.decoder.on_command_add_action = self.handle_add_action
		self.decoder.on_command_add_input = self.handle_add_input
	
	### Actual implementations of common ui functions
	def handle_put(self, text):
		# Output basic text to the console/user
		pass
	
	def handle_beep(self):
		# Emit a sound
		pass
	
	def handle_add_action(self, action_id):
		# Allow a new action
		pass
	def handle_add_input(self, input_id, type, default_value):
		# Add interface to enter that input
		pass
	
	### Client responses to the app (e.g. events)
	def event_action(self, action_id):
		# Trigger an action
		self.encoder.event_action(action_id)
	def event_input(self, input_id, type, value):
		# Entered a value
		self.encoder.event_input(input_id, type, value)


class HUIP_App:
	"An app handles the program logic which is interfaced by a client"
	def __init__(self):
		
		# Invoking commands requires an encoder
		self.encoder = HUIP_Encoder()
		
		# Getting responses from the user requires a decoder
		self.decoder = HUIP_Decoder()
		self.decoder.on_event_action = self.handle_event_action
		self.decoder.on_event_input = self.handle_event_input
		
		# UI
		self.actions = {}
		self.inputs = {}
	
	def start(self, session):
		pass
	
	### Actual functions to be called by the app
	def put(self, text):
		"Show text on client"
		self.encoder.command_put(text)
	
	def beep(self):
		"Make client beep"
		self.encoder.command_beep()
	
	### UI (called by app to make client display stuff)
	def add_action(self, action_id, on_execute):
		"Introduce that action to the user"
		# Store callback
		self.actions[action_id] = on_execute
		# Push to client
		self.encoder.command_add_action(action_id)
	
	#@TODO: min, max, options=array, is_mandatory
	def add_input(self, input_id, type, default_value, on_enter):
		"Introduce that action to the user"
		# Store callback
		self.inputs[input_id] = on_enter
		# Push to client
		self.encoder.command_add_input(input_id, type, default_value)
	
	### Responses from client (events the user did and our app should respond to)
	def handle_event_action(self, action_id):
		"Perform the given action"
		if (action_id in self.actions):
			handler = self.actions[action_id]
			# Actually call it
			handler()
		else:
			raise Exception('Action "%s" not known by app' % (str(action_id)))
	
	def handle_event_input(self, input_id, type, value):
		"Respond to given input"
		if (input_id in self.inputs):
			handler = self.inputs[input_id]
			# Actually call it
			handler(input_id, type, value)
		else:
			raise Exception('Input "%s" not known by app' % (str(input_id)))
	


from threading import Lock

class HUIP_Session:
	"A session connects a client to an app"
	def __init__(self, app, client):
		self.app = app
		self.app.encoder.on_packet = self.app_on_packet
		self.app_lock = Lock()
		
		self.client = client
		self.client.encoder.on_packet = self.client_on_packet
		self.client_lock = Lock()
		
		#self.start()
	
	def start(self):
		self.app.start(self)
	
	def app_on_packet(self, data):
		"Send packets from the app to the client (e.g. ui commands)"
		put('app --> client: %i bytes\n%s' %(len(data), hexdump(data)))
		self.client_lock.acquire()
		self.client.decoder.decode_packet(data)
		self.client_lock.release()
	
	def client_on_packet(self, data):
		"Send packets from the client to the app (e.g. events)"
		put('app <-- client: %i bytes\n%s' %(len(data), hexdump(data)))
		self.app_lock.acquire()
		self.app.decoder.decode_packet(data)
		self.app_lock.release()
