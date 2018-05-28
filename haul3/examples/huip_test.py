from huip import *

def put(txt):
	print('huip_test.py:\t' + str(txt))
	

def test(context):
	put('Test was called')
	context.put('Test was called')




# A test client (i.e. a renderer/terminal of some sorts)
class Test_Client(HUIP_Client):
	
	def handle_put(self, text):
		# Output basic text to the console/user
		print('Client_test:\t"%s"' % str(text))
	
	def handle_beep(self):
		# Emit a sound
		print('BEEP! goes the client_test')
	
	def handle_add_action(self, action_id):
		# App allows a new action
		print('New allowed action: action_id="%s"' % (str(action_id)))
	
	def handle_add_input(self, input_id, type, default_value):
		print('New input requested: "%s", type=%d, default_value=%s' % (input_id, type, default_value))
		
		# Perform input from stdin
		value = raw_input(input_id + ' [' + str(default_value) + ']: ')
		#print(str(input_id) + ' [' + str(default_value) + ']:')
		#value = '1234567'
		
		if (value == ''): value = default_value
		
		if (type == HUIP_TYPE_BOOL):		value = True if (value.lower() in ['1', 'true', 'y', 'yes']) else False
		elif (type == HUIP_TYPE_UINT8):	value = int(value)
		elif (type == HUIP_TYPE_UINT16):	value = int(value)
		elif (type == HUIP_TYPE_UINT32):	value = int(value)
		elif (type == HUIP_TYPE_STRING):	value = str(value)
		
		# Trigger input event
		self.event_input(input_id, type, value)

"""
# Protocol encoder test
test_client = Test_Client()

encoder = HUIP_Encoder()

def encoder_on_packet(data):
	put('Encoder generated packet: ' + str(data))
	put('Passing it on to the client...')
	test_client.decoder.handle_packet(data)

encoder.on_packet = encoder_on_packet
encoder.command_put('Hello world!')
encoder.command_beep()

# Simulate the user invoking an action
test_client.command_action('test')

# Generate invalid packet: encoder.packet_begin(); encoder.encode_uint8(HUIP_COMMAND_PUT); encoder.packet_end()
"""

### A test app
import time
import thread
class Test_App(HUIP_App):
	def __init__(self):
		HUIP_App.__init__(self)
		pass
	
	#def handle_action(self, id):
	#	print('Test_App:\tUser has triggered an action: id=' + str(id))
	
	def start(self, session):
		#self.main()	# Run direct
		thread.start_new_thread(self.main, (session,))	# Run in separate thread
	
	def main(self, session):
		# Basic output
		self.put('Loading Test_App...')
		
		# UI
		self.add_action(action_id='test2', on_execute=self.test2)
		self.add_input(input_id='some_text', type=HUIP_TYPE_STRING, default_value='Some text', on_enter=lambda input_id, type, value: self.handle_some_text(value))
		
		self.put('Test_App is ready.')
		
		# Delays
		for i in xrange(3):
			self.put('Test_App says: ' + str(1+i))
			time.sleep(1)
		
		# End.
		self.put('End of Test_App')
	
	def test2(self):
		self.put('You have successfully triggered action "test2" inside Test_App')
	
	def handle_some_text(self, text):
		self.put('Thank you for entering "%s" in Test_App' % (text))


test_app = Test_App()
test_client = Test_Client()

session = HUIP_Session(app=test_app, client=test_client)
session.start()

# simulate user interaction
time.sleep(.99)
action_id = 'test2'
test_client.event_action(action_id)
test_client.event_action(action_id)
test_client.event_action(action_id)
test_client.event_action(action_id)

input_id = 'some_text'
test_client.event_input(input_id, HUIP_TYPE_STRING, 'hello there!')


time.sleep(5)
