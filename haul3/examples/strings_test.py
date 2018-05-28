import strings

#@var a String

a = 'Hello world!'
print(a)


### Option 1: Use native String, call library functions externally:
#@var b1 String
b1 = strings.sub(a,6,11)
print(b1)

### Option 2: Wrap it inside an object (which has the same name as the import):
#@var b2 strings
b2 = strings.new(a)
b2 = b2.sub(6,11)
print(b2)

# EOF