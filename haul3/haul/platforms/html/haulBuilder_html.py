#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.js.haulWriter_js import *

import json

def put(txt):
	print('HAULBuilder_html:\t' + str(txt))


HAULBUILDER_HTML_DIR = os.path.dirname(__file__)
BROWSER_CMD = 'cmd /c start'	# Invoke OS browser

#@TODO: Get this HTML from a dta file in haul3/data/platforms/html/index.html
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
<title>{0}</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<style type="text/css"></style>
{2}
<script type="text/javascript">
{3}

// Translated source goes here:
{1}
// End of translated code
</script>
</head>
<body>
	<h1>{0}</h1>
	<div id="hioOut"></div>
	<input type="text" id="hioIn" /><button onclick="hioIn_enter();">OK</button>
	<small>HAUL3</small>
</body>
</html>
'''

JS_GLUE = '''
var hio = {
	_putElement: null,
	_fetchElement: null,
	
	init: function(e) {
		this._putElement = document.getElementById("hioOut");
		this._fetchElement = document.getElementById("hioIn");
		
		main();
	},
	put: function(txt) {
		this._putElement.innerText += txt + '\\n';
	},
	put_direct: function(txt) {
		this._putElement.innerText += txt;
	},
	shout: function(txt) {
		alert(txt);
	},
	fetch: function() {
		//var txt = this._fetchElement.value;
		//this._fetchElement.value = '';
		txt = prompt('hio.fetch');
		return txt;
	}
};
async function _main_async() {
	// Call main, but be async, so we can have a proper fetch from stdin
	main();
}
function put(txt) {
	hio.put(txt);
}
function put_direct(txt) {
	hio.put_direct(txt);
}
function shout(txt) {
	alert(txt);
}
/*
function fetch() {
	return prompt('hio.fetch');
}
*/
var _fetchResolve = null;
function fetch() {
	var txt = prompt('hio.fetch');
	//let txt = await fetch_wait();
	return txt;
}
function fetch_wait() {
	return new Promise((resolve, reject) => {
		_fetchResolve = resolve;
		resolve(prompt('fetch_wait'));
	});
}
function hioIn_enter() {
	var txt = hio._fetchElement.value;
	hio._fetchElement.value = '';
	if (_fetchResolve !== null) {
		_fetchResolve(txt);
		_fetchResolve = null;
	}
}
function int_str(i) {
	return ('' + i);
}

window.onload = function(e) {
	hio.init(e);
};
'''

class HAULBuilder_html(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='html', lang='js')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_js, dialect=DIALECT_WRAP_MAIN))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		html_filename = self.project.name + '.html'
		html_filename_full = os.path.abspath(os.path.join(self.output_path, html_filename))
		
		libs_data_path = self.data_path + '/platforms/html/libs'
		
		single_file = True
		
		if (single_file == True):
			# All-in-one self-contained HTML file
			
			stream_js = StringWriter()
			
			put('Creating single HTML file...')
			
			put('Merging native libs...')
			#js_lib = JS_GLUE
			headers = ''
			
			js_lib = ''
			for s in self.project.libs:
				lib_filename_data = libs_data_path + '/' + s.name + '.js'
				js_lib = js_lib + '// ' + s.name + '\n'
				js_lib = js_lib + self.type(lib_filename_data)
				js_lib = js_lib + '\n'
			
			put('Translating sources to JavaScript...')
			self.translate_project(stream_out_single=stream_js)
			
			js_source = stream_js.r
			
			# Insert into template
			#@TODO: Get this template HTML from a dta file in haul3/data/platforms/html/index.html
			html = HTML_TEMPLATE.format(self.project.name, js_source, headers, js_lib)
			
			# Write
			self.touch(html_filename_full, html)
		
		else:
			# Individual files
			
			put('Translating sources to JavaScript...')
			self.translate_project(output_path=self.output_path, dest_extension='js')
			
			# Copy native libs to output_path
			js_lib = ''
			headers = ''
			for s in self.project.libs:
				lib_filename_data = libs_data_path + '/' + s.name + '.js'
				self.copy(lib_filename_data, self.output_path + '/' + s.name + '.js')
				headers = headers + '\n<script type="text/javascript" src="' + s.name + '.js"></script>'
			
			for s in self.project.sources:
				headers = headers + '\n<script type="text/javascript" src="' + s.name + '.js"></script>'
			
			put('Creating main HTML file...')
			js_source = 'main();'
			
			# Insert into template
			#@TODO: Get this template HTML from a dta file in haul3/data/platforms/html/index.html
			html = HTML_TEMPLATE.format(self.project.name, js_source, headers, js_lib)
			
			# Write
			self.touch(html_filename_full, html)
		
		# Run test
		if self.project.run_test:
		
			put('Test: Launching...')
			cmd = BROWSER_CMD
			cmd += ' file://%s' % (html_filename_full)
			r = self.command(cmd)
			put(r)
		
		
		put('Done.')
		
