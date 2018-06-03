#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.js.writer_js import *

import json

def put(txt):
	print('HAULBuilder_webos:\t' + str(txt))


class HAULBuilder_webos(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='js', platform='webos')
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_js, dialect=DIALECT_WRAP_MAIN))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		startPath = os.getcwd()
		
		libs_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'webos', 'libs'))
		res_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'webos', 'res'))
		
		
		js_filename = name + '.js'
		js_filename_full = os.path.join(self.staging_path, js_filename)
		
		
		#VM_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'vm')
		#QEMU_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'qemu')
		
		#palm_sdk_path = 'Z:\\Apps\\_code\\HP_webOS'
		palm_sdk_path = self.get_path('PALM_SDK_PATH', os.path.abspath(os.path.join(self.tools_path, 'palm-sdk')))
		
		
		put('Translating sources to JavaScript...')
		self.translate_project(output_path=self.staging_path)
		
		if not os.path.isfile(js_filename_full):
			raise HAULBuildError('Main JavaScript file "{}" was not created!'.format(js_filename_full))
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
		app_package = 'wtf.haul'	#'de.bernhardslawik.haul'
		app_id = app_package + '.' + name
		
		appInfo = {
			'id': app_id,
			'version': '0.0.1',
			'vendor': 'Bernhard Slawik',
			'type': 'web',
			'main': 'index.html',
			'title': name,
			'icon': 'icon_64x64.png'
		}
		
		app_info_json = json.dumps(appInfo, indent=4)
		write_file(self.staging_path + '/appinfo.json', app_info_json)
		
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
		ipk_filename = appInfo['id'] + '_' + appInfo['version'] + '_all.ipk'
		ipk_filename_full = os.path.abspath(os.path.join(self.output_path, ipk_filename))
		
		put('Packaging using "palm-package"...')
		r = self.command('palm-package "%s" --outdir="%s"' % (self.staging_path, self.output_path))
		
		if not os.path.isfile(ipk_filename_full):
			put(r)
			raise HAULBuildError('Packaged IPK file "{}" was not created!'.format(ipk_filename_full))
			return False
		
		
		
		# Test
		if (self.project.run_test == True):
			put('Test: Installing using "palm-install"')
			self.command('palm-install "%s"' % (ipk_filename_full))
			
			put('Test: Launching using "palm-launch"')
			self.command('palm-launch %s' % (app_id))
		
		put('Done.')
		return True
		
