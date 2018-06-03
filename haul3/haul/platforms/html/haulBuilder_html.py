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

class HAULBuilder_html(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='html', lang='js')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_js, dialect=DIALECT_WRAP_MAIN))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		html_filename = self.project.name + '.html'
		html_filename_full = os.path.abspath(os.path.join(self.output_path, html_filename))
		
		#single_file = False
		
		#if (single_file):
		put('Translating to JavaScript...')
		#self.translate_project(output_path=self.staging_path, dest_extension='js')
		
		#stream_out = FileWriter(html_filename
		self.translate_project()
		
		#@TODO: Copy native libs to output_path!
		
		put('Creating single HTML file...')
		#@TODO: Merge native libs into HTML if specified
		
		#@TODO: Get this HTML from a dta file in haul3/data/platforms/html/index.html
		
		
		html = '''<!DOCTYPE html>
<html>
<head>
<title>''' + self.project.name + '''</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

<style type="text/css">
#hioOut {
	font-family: monospace;
	background-color: #000000;
	color: #f0f0f0;
	
	display: block;
	width: 100%;
	min-height: 20em;
}
</style>
<script type="text/javascript">
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

// Translated source goes here:
'''
		
		# Insert source(s)
		for s in self.project.sources:
			html = html + self.type(s.dest_filename)
		
		html = html + '''
// End of translated code

</script>
</head>
<body>
	<h1>''' + self.project.name + '''</h1>
	<div id="hioOut"></div>
	<input type="text" id="hioIn" /><button onclick="hioIn_enter();">OK</button>
	<small>HAUL3</small>
</body>
</html>
'''
		self.touch(html_filename_full, html)
		
		
		# Test
		if self.project.run_test:
		
			put('Test: Launching...')
			cmd = BROWSER_CMD
			cmd += ' file://%s' % (html_filename_full)
			r = self.command(cmd)
			put(r)
		
		
		put('Done.')
		
