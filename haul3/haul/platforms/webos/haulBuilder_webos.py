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
HAULBUILDER_WEBOS_DIR = os.path.dirname(__file__)
#VM_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'vm')
#QEMU_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'qemu')

class HAULBuilder_webos(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='js', platform='webos')
	
	def build(self, inputFilename, sourcePath, stagingPath, outputPath, resources=None, perform_test_run=False):
		
		put('Starting build...')
		HAULBuilder.build(self, inputFilename, outputPath)
		
		put('Cleaning staging path...')
		self.clean(stagingPath)
		
		#@TODO: Use module.imports!
		libs = ['hio']	#['sys', 'hio']
		
		name = nameByFilename(inputFilename)
		jsFilename = name + '.js'
		jsFilenameFull = os.path.join(stagingPath, jsFilename)
		
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(sourcePath, inputFilename), SourceReaderClass=HAULReader_py, destFilename=jsFilenameFull, DestWriterClass=HAULWriter_js, dialect=DIALECT_WRAP_MAIN)
		
		if not os.path.isfile(jsFilenameFull):
			put('Main JavaScript file "%s" was not created! Aborting.' % (jsFilenameFull))
			return False
		
		
		
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
		writeFile(stagingPath + '/appinfo.json', appInfo_json)
		
		self.copy(HAULBUILDER_WEBOS_DIR + '/res/icon_64x64.png', stagingPath + '/icon_64x64.png')
		self.copy(HAULBUILDER_WEBOS_DIR + '/res/index.html', stagingPath + '/index.html')
		self.copy(HAULBUILDER_WEBOS_DIR + '/res/style.css', stagingPath + '/style.css')
		
		
		put('Gathering sources...')
		sources = []
		for l in libs:
			#self.copy('haul/langs/js/lib/' + l + '.js', stagingPath + '/' + l + '.js')
			self.copy(HAULBUILDER_WEBOS_DIR + '/lib/' + l + '.js', stagingPath + '/' + l + '.js')
			sources.append({
				'source': l + '.js'
			})
		
		
		assistants = ['stage-assistant', 'app-assistant']
		for l in assistants:
			self.copy(HAULBUILDER_WEBOS_DIR + '/res/' + l + '.js', stagingPath + '/' + l + '.js')
			sources.append({
				'source': l + '.js'
			})
		
		
		sources.append({
			'scenes': 'main',
			'source': name + '.js'
		})
		
		#sources_json = str(sources)
		sources_json = json.dumps(sources, indent=4)
		writeFile(stagingPath + '/sources.json', sources_json)
		
		
		# Package
		ipkFilename = appInfo['id'] + '_' + appInfo['version'] + '_all.ipk'
		ipkFilenameFull = os.path.abspath(os.path.join(outputPath, ipkFilename))
		
		put('Packaging using "palm-package"...')
		r = self.command('palm-package "%s" --outdir="%s"' % (stagingPath, outputPath))
		
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
		
		
