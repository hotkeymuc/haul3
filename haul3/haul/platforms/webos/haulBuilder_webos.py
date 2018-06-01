#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.js.haulWriter_js import *

import json

def put(txt):
	print('HAULBuilder_webos:\t' + str(txt))


PALM_SDK_DIR = 'Z:\\Apps\\_code\\HP_webOS'
#HAULBUILDER_WEBOS_DIR = os.path.dirname(__file__)
#VM_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'vm')
#QEMU_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'qemu')

class HAULBuilder_webos(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='js', platform='webos')
	
	def build(self, source_path, source_filename, output_path, staging_path, data_path, resources=None, perform_test_run=False):
		
		HAULBuilder.build(self, source_path=source_path, source_filename=source_filename, output_path=output_path, staging_path=staging_path, data_path=data_path, resources=resources, perform_test_run=perform_test_run)
		
		
		startPath = os.getcwd()
		
		#@TODO: Use module.imports!
		libs = ['hio']	#['sys', 'hio']
		
		tools_path = os.path.join(data_path, '..', 'tools')
		libs_path = os.path.join(data_path, 'platforms', 'webos', 'libs')
		res_path = os.path.join(data_path, 'platforms', 'webos', 'res')
		#gbdk_path = os.path.join(tools_path, 'platforms', 'gameboy', 'gbdk')
		#bgb_path = os.path.join(tools_path, 'platforms', 'gameboy', 'bgb')
		
		
		#@TODO: Use module.imports!
		libs = ['hio']	#['sys', 'hio']
		
		name = name_by_filename(source_filename)
		jsFilename = name + '.js'
		jsFilenameFull = os.path.join(staging_path, jsFilename)
		
		
		put('Translating source...')
		m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=jsFilenameFull, DestWriterClass=HAULWriter_js, dialect=DIALECT_WRAP_MAIN)
		
		
		if not os.path.isfile(jsFilenameFull):
			put('Main JavaScript file "%s" was not created! Aborting.' % (jsFilenameFull))
			return False
		
		#@FIXME: We need to create a matching Assistant!
		"""
function MainAssistant(argFromPusher) {
	this.args = argFromPusher;
}

MainAssistant.prototype = {
	setup: function() {
		//Ares.setupSceneAssistant(this);
	},
	cleanup: function() {
		//Ares.cleanupSceneAssistant(this);
	},
	activate: function() {
		//this.controller.get("photoView").mojo.centerUrlProvided(this.photo.photoUrl);
		main();
	}
};
		"""
		
		
		put('Staging webOS app...')
		appNamespace = 'wtf.haul'	#'de.bernhardslawik.haul'
		appId = appNamespace + '.' + name
		
		appInfo = {
			'id': appId,
			'version': '0.0.1',
			'vendor': 'Bernhard Slawik',
			'type': 'web',
			'main': 'index.html',
			'title': name,
			'icon': 'icon_64x64.png'
		}
		
		appInfo_json = json.dumps(appInfo, indent=4)
		writeFile(staging_path + '/appinfo.json', appInfo_json)
		
		self.copy(os.path.join(res_path, 'icon_64x64.png'), os.path.join(staging_path, 'icon_64x64.png'))
		self.copy(os.path.join(res_path, 'index.html'), os.path.join(staging_path, 'index.html'))
		self.copy(os.path.join(res_path, 'style.css'), os.path.join(staging_path, 'style.css'))
		
		
		put('Gathering sources...')
		sources = []
		for l in libs:
			#self.copy('haul/langs/js/lib/' + l + '.js', staging_path + '/' + l + '.js')
			self.copy(os.path.join(libs_path, l + '.js'), os.path.join(staging_path, l + '.js'))
			sources.append({
				'source': l + '.js'
			})
		
		
		assistants = ['stage-assistant', 'app-assistant']
		for l in assistants:
			self.copy(os.path.join(res_path, l + '.js'), os.path.join(staging_path, l + '.js'))
			sources.append({
				'source': l + '.js'
			})
		
		
		sources.append({
			'scenes': 'main',
			'source': name + '.js'
		})
		
		#sources_json = str(sources)
		sources_json = json.dumps(sources, indent=4)
		writeFile(staging_path + '/sources.json', sources_json)
		
		
		# Package
		ipkFilename = appInfo['id'] + '_' + appInfo['version'] + '_all.ipk'
		ipkFilenameFull = os.path.abspath(os.path.join(output_path, ipkFilename))
		
		put('Packaging using "palm-package"...')
		r = self.command('palm-package "%s" --outdir="%s"' % (staging_path, output_path))
		
		if not os.path.isfile(ipkFilenameFull):
			put(r)
			put('Packaged IPK file "%s" was not created! Aborting.' % (ipkFilenameFull))
			return False
		
		
		
		# Test
		if perform_test_run:
			put('Test: Installing using "palm-install"')
			self.command('palm-install "%s"' % (ipkFilenameFull))
			
			put('Test: Launching using "palm-launch"')
			self.command('palm-launch %s' % (appId))
		
		put('Done.')
		
		
