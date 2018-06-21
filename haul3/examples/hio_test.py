# This is HIO test

import hio
hio.put('Hello World! (via hio)')
hio.put_('Enter your name:')
name = hio.fetch()
hio.put_('You entered: "')
hio.put(name)
hio.put_('"')


#from hio import *
#init()
#put('Hello World! (via hio)')
#put_('Enter your name:')
#name = fetch()
#put_('You entered: "')
#put(name)
#put_('"')

