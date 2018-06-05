# This is HIO test

from hio import *

#init()
put('Hello World! (via hio)')

put_('Enter your name:')
name = fetch()
put_('You entered: "')
put(name)
put_('"')

