# HAUL Platform Capabilities

PLATFORM = 'Unknown'

# User interface capabilities
TEXT_OUT = True	# Can text be communicated to the user?
TEXT_OUT_WIDTH = 20	# Length of one text line
TEXT_OUT_HEIGHT = 4	# Number of lines to display at once
TEXT_IN = True	# Can the user input text?
TEXT_IN_EDIT = False	# Can Text be input "in bulk", i.e. multiple lines etc.

UI_LIST = False	# Can lists be displayed?
UI_MENU = False	# Is there a concept of "menus"?
#UI_GRID = False	# Is it possible for users to edit grids? (like spread sheets)
#UI_IMAGE = False	# Can images be displayed?
#UI_CARDS = False	# Is there a concept of multiple "cards"? (like windows or tabs)

GFX_PIXELS = False	# Is there some sort of 2-dimensional canvas to draw on?
GFX_PIXELS_WIDTH = 320	# Number of horizontal pixels
GFX_PIXELS_HEIGHT = 240
GFX_PIXELS_BITS = 24	# How many bits are there per pixel?
GFX_PHYSICAL_SIZE_X = 80	# Horizontal size in millimeters
GFX_PHYSICAL_SIZE_Y = 60	# Vertical size in millimeters
GFX_VECTORS = False	# Is there some sort way for vector output? (Oscilloscope, 3d printer, plotter etc.)

# Navigation capabilities (UI)
NAV_TWOWAY = False	# Is there some sort of "up/down" or "left/right"?
NAV_DIRECTIONAL = False	# Is there a 4-way navigation?
NAV_CONTINUOUS = False	# Is there continuous control? (e.g. mouse)
NAV_ABSOLUTE = False	# Is there absolute control? (e.g. touch screen)
NAV_OK = True	# Is there an "affirmative" input?
NAV_BACK = False	# Is there a dedicated "back" button?
NAV_STOP = False	# Is there a dedicated "stop" button?
NAV_MENU = False	# Is there a "menu" (or "secondary") button? (e.g. right mouse button, menu key, ...)

# Communication capabilities
COM_SERIAL = False	# Is there a way of transmitting serial data?
COM_SOCKET = False	# Is there a concept of end-to-end sockets?

# Audio capabilities
AUDIO_SYNTH = True	# Can the platform produce an audible signal?
AUDIO_SYNTH_PITCH = False	# Can the platform influence the frequency of the beep?
AUDIO_SYNTH_LENGTH = False	# Can the length of the beep be influenced?
AUDIO_SYNTH_AMPLITUDE = False	# Can the amplitude be changed?
AUDIO_SYNTH_CHANNELS = 1	# How many tones can be synthesized at once?
AUDIO_PCM = False	# Can the platform reproduce PCM coded signals?
AUDIO_PCM_SAMPLE_RATE = 44100	# What is the maximum sample rate?
