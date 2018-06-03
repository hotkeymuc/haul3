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
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_js, dialect=DIALECT_WRAP_MAIN))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		startPath = os.getcwd()
		
		tools_path = os.path.join(self.data_path, '..', 'tools')
		libs_path = os.path.join(self.data_path, 'platforms', 'webos', 'libs')
		res_path = os.path.join(self.data_path, 'platforms', 'webos', 'res')
		#gbdk_path = os.path.join(tools_path, 'platforms', 'gameboy', 'gbdk')
		#bgb_path = os.path.join(tools_path, 'platforms', 'gameboy', 'bgb')
		
		
		jsFilename = name + '.js'
		jsFilenameFull = os.path.join(self.staging_path, jsFilename)
		
		
		put('Translating sources to JavaScript...')
		self.translate_project(output_path=self.staging_path)
		
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
		write_file(self.staging_path + '/appinfo.json', appInfo_json)
		
		self.copy(os.path.join(res_path, 'icon_64x64.png'), os.path.join(self.staging_path, 'icon_64x64.png'))
		self.copy(os.path.join(res_path, 'index.html'), os.path.join(self.staging_path, 'index.html'))
		self.copy(os.path.join(res_path, 'style.css'), os.path.join(self.staging_path, 'style.css'))
		
		
		put('Gathering sources...')
		sources = []
		for s in self.project.libs:
			l = s.name
			
			#self.copy('haul/langs/js/lib/' + l + '.js', staging_path + '/' + l + '.js')
			self.copy(os.path.join(libs_path, l + '.js'), os.path.join(self.staging_path, l + '.js'))
			sources.append({
				'source': l + '.js'
			})
		
		
		assistants = ['stage-assistant', 'app-assistant']
		for l in assistants:
			self.copy(os.path.join(res_path, l + '.js'), os.path.join(self.staging_path, l + '.js'))
			sources.append({
				'source': l + '.js'
			})
		
		
		#@FIXME: Only the main source file has a main scene!
		for s in self.project.sources:
			sources.append({
				'scenes': 'main',
				'source': s.name + '.js'
			})
		
		#sources_json = str(sources)
		sources_json = json.dumps(sources, indent=4)
		write_file(self.staging_path + '/sources.json', sources_json)
		
		
		# Package
		ipkFilename = appInfo['id'] + '_' + appInfo['version'] + '_all.ipk'
		ipkFilenameFull = os.path.abspath(os.path.join(self.output_path, ipkFilename))
		
		put('Packaging using "palm-package"...')
		r = self.command('palm-package "%s" --outdir="%s"' % (self.staging_path, self.output_path))
		
		if not os.path.isfile(ipkFilenameFull):
			put(r)
			put('Packaged IPK file "%s" was not created! Aborting.' % (ipkFilenameFull))
			return False
		
		
		
		# Test
		if (self.project.run_test == True):
			put('Test: Installing using "palm-install"')
			self.command('palm-install "%s"' % (ipkFilenameFull))
			
			put('Test: Launching using "palm-launch"')
			self.command('palm-launch %s' % (appId))
		
		put('Done.')
		
		
