# This is HIO test

#import hio
#hio.put('Hello World! (module ns)')
#hio.put_direct('Enter your name:')
#name = hio.get()
#hio.put('You entered: "' + name + '"')


from hio import *
put('Hello World! (imported local ns)')


put_direct('Enter your name:')
name = get()
put('You entered: "' + name + '"')