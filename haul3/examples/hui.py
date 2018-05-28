# HAUL UI glue

# Load the real file, overwriting this module instance (same name!)
#import imp
#hui = imp.load_source('hio', '../haul/langs/py/lib/hui.py')

def put(txt):
	print(str(txt))

class HUI_Action:
	def __init__(self, name, handler=None):
		self.name = name
		self.handler = handler
		#self.immediate = False	# e.g. trigger via hardware keys
		#self.
		#self.rare
	def execute(self, ctx):
		self.handler(ctx)

class HUI_Content:
	def __init__(self, name):
		self.name = name
		#self.mime
		#self.data
		pass

class HUI_Status:
	def __init__(self):
		self.text = ''
		self.busy = False
		self.progress = 0
		self.length = 0

class HUI_Context:
	def __init__(self, name):
		self.name = name
		self.parent = None
		self.actions = dict()
		self.contents = []
		self.status = None
		self.invalid = False
	
	def new_context(self, ctx):
		ctx.parent = self
		return ctx
	
	def add_action(self, action):
		#self.actions.append(action)
		self.actions[action.name] = action
		self.invalidate()
		return action
	
	def execute_action(self, action_name):
		self.actions[action_name].execute(self)
	
	def add_content(self, content):
		self.contents.append(content)
		return content
	
	def leave(self):
		pass
	
	def invalidate(self):
		self.invalid = True
	
	def refresh(self):
		if not self.invalid: return
		# Refresh stuff
		put(self.name)
		put('=' * (len(self.name)))	# Underline
		
		put('')
		put('Contents:')
		for content in self.contents:
			#action = self.actions[action_name]
			put('\t* ' + content.name)
		
		put('')
		put('Actions:')
		for action_name in self.actions:
			action = self.actions[action_name]
			put('\t* ' + action.name)
		
		put('')
		put('Status:')
		put('\t' + str(self.status))
		
		put('')
		
		self.invalid = False

class HUI:
	def __init__(self):
		self.root = Context(name='root')
		self.path = [self.root]
	
	def start(self, ctx):
		ctx = self.root.new_context(ctx)
		self.path.append(ctx)
		return ctx
	
	def back(self):
		ctx = self.path.pop()
		return ctx
	

hui = HUI()
