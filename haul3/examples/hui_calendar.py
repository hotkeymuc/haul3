from hui import *

def put(txt):
	print('calendar.py:\t' + str(txt))
	

### Context
cal = hui.start(Context(name='calendar'))



### Content
selected_time_content = Content(name='selected_time')
#selected_time_content.default_value = today
cal.add_content(selected_time_content)

events_content = Content(name='events')
#events_content.view = all_events, from=selected_time, to=...
cal.add_content(events_content)


### Actions
def create_event_handler(ctx):
	put('create_event_handler was called')
create_event_action = Action(name='create_event', handler=create_event_handler)
cal.add_action(create_event_action)


### Play around
#hui.refresh()
cal.refresh()

cal.execute_action('create_event')
