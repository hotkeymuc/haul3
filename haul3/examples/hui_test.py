from hui import *

def put(txt):
	print('hui_test.py:\t' + str(txt))
	

ctx = hui.start(Context(name='hui_test'))
ctx.add_action(Action(name='Run'))

#hui.refresh()
ctx.refresh()


"""
#@TODO: Example: E-Mail Client
controls = [list, view]
actions = [new, delete[selected], mark[selected]]
content = text/mail

#@TODO: Example: Chat Client
controls = [contact, chatlog, text]
actions = [send[text] ]
content = string

#@TODO: Example: Web Browser
controls = [view]
actions = [goTo, back, reload]
content = file/html

#@TODO: Example: File Browser
controls = [list]
actions = [new, search, edit[selected], execute[selected], copy[selected], rename[selected]]
content = file

#@TODO: Example: Text editor
controls = [area]
actions = [new, open, save]
content = file, string

#@TODO: Example: Phone
controls = [number]
actions = [dial, search]
content = contact

#@TODO: Example: Calculator
controls = [equation]
actions = [evaluate, symbol]
content = string

#@TODO: Example: Camera
controls = [video]
actions = [captureStill, captureVideo, settings]
content = image
"""
"""
# Example: Text editor
context = hui.context()
#context.set_content(hui.content(name='text'))
#content_text = hui.content(name='text', )
action_new = hui.action('new')
action_new.on_execute = handle_action_new
context.add_action(action_new)

action_open = hui.action('open')
action_open.on_execute = handle_action_open
context.add_action(action_open)

action_save = hui.action('save')
action_save.on_execute = handle_action_save
context.add_action(action_save)
"""
