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
		HAULBuilder.__init__(self, lang='js', platform='html')
	
	def build(self, source_path, source_filename, output_path, staging_path, data_path, resources=None, perform_test_run=False):
		
		HAULBuilder.build(self, source_path=source_path, source_filename=source_filename, output_path=output_path, staging_path=staging_path, data_path=data_path, resources=resources, perform_test_run=perform_test_run)
		
		name = name_by_filename(source_filename)
		
		jsFilename = name + '.js'
		jsFilenameFull = os.path.join(staging_path, jsFilename)
		
		htmlFilename = name + '.html'
		htmlFilenameFull = os.path.abspath(os.path.join(output_path, htmlFilename))
		
		
		put('Cleaning staging paths...')
		self.clean(staging_path)
		
		#@TODO: Use module.imports!
		libs = ['hio']	#['sys', 'hio']
		
		
		put('Translating source...')
		m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=jsFilenameFull, DestWriterClass=HAULWriter_js, dialect=DIALECT_WRAP_MAIN)
		
		if not os.path.isfile(jsFilenameFull):
			put('Main JavaScript file "%s" was not created! Aborting.' % (jsFilenameFull))
			return False
		
		
		
		html = '''<!DOCTYPE html>
<html>
<head>
<title>HAUL for HTML</title>
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
''' + self.type(jsFilenameFull) + '''
// End of translated code

</script>
</head>
<body>
	<h1>HAUL for HTML</h1>
	<div id="hioOut"></div>
	<input type="text" id="hioIn" /><button onclick="hioIn_enter();">OK</button>
</body>
</html>
'''
		self.touch(htmlFilenameFull, html)
		
		
		# Test
		if perform_test_run:
		
			put('Test: Launching...')
			cmd = BROWSER_CMD
			cmd += ' file://%s' % (htmlFilenameFull)
			r = self.command(cmd)
			put(r)
		
		
		put('Done.')
		
