'''
Based on parseExpression.py
(C)opyright 2011-2012 Bernhard -HotKey- Slawik, http://www.bernhardslawik.de

This is some kind of general-purpose parser. A really simple one. But I like simple things.

'''
from bootstrap_lib import *
from src.htk.py.lib import *
from bootstrap_tokenizer import *

#from bootstrap_htk_php import *
#platformOut = 'php'

# Since this is the bootstrap you need a dedicated "bootstrap_htk_xxx.py" for the FIRST compilation.
# After that you may compile to any platform you wish.
from bootstrap_htk_py import *
platforms = ['py', 'js']
platformOut = 'py'

filename = 'auto'
#filename = 'test'
#filename = 'htk/common/tokenizer'
#filename = 'htk/common/parser_blocks'
#filename = 'htk/py/htk_py'
#filename = 'htk/php/htk_php'
pathSrc = 'src'
pathBuild = 'build'
filenameIn = pathSrc + '/' + filename + '.hal'
filenameOut = pathBuild + '/' + filename + '.' + platformOut

filenamesRes = [
	"/auto.hal",
	#"/test.hal",
	"/res/test.txt",
	
	"/htk/common/lib.hal",
	"/htk/common/tokenizer.hal",
	"/htk/common/htk.hal",
	
	"/htk/py/htk_py.hal",
	"/htk/py/lib.py",
	
	"/htk/js/htk_js.hal",
	"/htk/js/lib.js"
]

'''
from Tkinter import *

root = Tk()
def popup(txt):
	#w = Label(root, text=txt)
	#w.pack()
	text = Text(root)
	text.insert(END, txt)
	text.pack(side=LEFT)
	#root.mainloop()

class App:
	def __init__(self, master):
		frame = Frame(master)
		frame.pack()

		self.button = Button(frame, text="Quit", fg="red", command=frame.quit)
		self.button.pack(side=LEFT)

		self.butTranslate = Button(frame, text="Translate", command=self.actionTranslate)
		self.butTranslate.pack(side=LEFT)
		
		self.textInput = Text(root, yscrollcommand=self.actionScroll)
		#self.textInput.tag_config("myTag", background="yellow", foreground="red")
		self.textInput.insert(END, input)   #, "myTag")
		self.textInput.pack(side=LEFT)
		
		self.textOutput = Text(root)
		self.textOutput.pack(side=RIGHT)
		
	def actionScroll(self, up, down):
		#put(str(a1) + " " + str(a2))
		self.textOutput.yview(MOVETO, up)
		pass
	def actionTranslate(self):
		code = translate(self.textInput.get(1.0, END))
		self.textOutput.delete(1.0, END)
		self.textOutput.insert(END, code);
app = App(root)

'''

def myExportTokens(tokens):
	#global $stateNames;
	r = ''
	for token in tokens:
		if (len(r) > 0): r = r + CR
		r = r + stateNames[token.state] if ((token.state > 0) and (token.state < len(stateNames))) else 'UNKNOWN_TOKEN('+str(token.state) + ')'
		r = r + '   '
		r = r + '"' + str(token.data) + '"'
	return r
#


def translate(streamIn, streamOut, translator):
	#put('================= HAL Input =======================')
	#input = file_getAll(filenameIn)
	#put(input)
	#popup(input)
	
	tokenizer = Tokenizer(streamIn)
	#translator = Translator_py()
	translator.translate(tokenizer, streamOut)
	
	'''
	put('================= Tokenizer... =======================')
	parser = Parser_Blocks()
	parser.parse(streamIn)
	put('================= Parser... =======================')
	tokens = parser.getAsList()
	#put(myExportTokens(tokens))
	#popup(myExportTokens(tokens))
	put('================== Translator... ======================')
	#translator = Translator_PHP()
	translator = Translator_py()
	translator.translate(streamOut, tokens)
	#put(code)
	#popup(code)
	'''
	put('========================================')
	put('finished.')
	#return code


#@todo: Use Packager_PHP!

## Copy runtime shared files
#streamOut = stream_file_write(filenameOut)
#put('bootstrap: Adding platform specific library resource...')
#streamIn = stream_file_read('src/htk/' + platformOut + '/lib.' + platformOut)
#streamOut.putAll(streamIn.getAll())
#streamIn.close()



### Package
streamOut = stream_file_write(filenameOut)

if (platformOut == 'py'):
	translator = Translator_py()
elif (platformOut == 'js'):
	translator = Translator_js()

### Libraries...
put('bootstrap: Adding platform specific library resource...')
streamIn = stream_file_read(pathSrc + '/htk/' + platformOut + '/lib.' + platformOut)
streamOut.putAll(streamIn)
streamIn.close()

put('bootstrap: Translating and adding platform independent helper functions...')
streamIn = stream_file_read(pathSrc + '/htk/common/lib.hal')
translate(streamIn, streamOut, translator)
streamIn.close()

### Resources
put('bootstrap: Adding resources...')
ress = resources()
for filenameRes in filenamesRes:
	res = resource(filenameRes, stream_file_read(pathSrc + filenameRes))
	ress.add(res)
streamOut.putString('#############################################################' + CR)
streamOut.putString('# Resources' + CR)
streamOut.putString('#############################################################' + CR)
#ress.dump_py(streamOut)



### Just-in-time compiler...
put('bootstrap: Translating and adding tokenizer for run-time loading...');
streamIn = stream_file_read(pathSrc + '/htk/common/tokenizer.hal');
translate(streamIn, streamOut, translator)
streamIn.close()

put('bootstrap: Translating and adding htk prototype for run-time loading...');
streamIn = stream_file_read(pathSrc + '/htk/common/htk.hal');
translate(streamIn, streamOut, translator)
streamIn.close()

#put('bootstrap: Translating and adding target htk for run-time loading...')
#streamIn = stream_file_read(pathSrc + '/htk/' + platformOut + '/htk_' + platformOut + '.hal')
#translate(streamIn, streamOut, translator)
#streamIn.close()
for platform in platforms:
	put('bootstrap: Translating and adding htk (' + platform + ') for run-time loading...')
	streamIn = stream_file_read(pathSrc + '/htk/' + platform + '/htk_' + platform + '.hal')
	translate(streamIn, streamOut, translator)
	streamIn.close()

### Main executable
put('bootstrap: Translating and adding the main file "' + filenameIn + '"...')
streamIn = stream_file_read(filenameIn)
translate(streamIn, streamOut, translator)
streamIn.close()

put('bootstrap: Closing...')
streamOut.close()

put('bootstrap: "' + filenameOut + '" finished.')
