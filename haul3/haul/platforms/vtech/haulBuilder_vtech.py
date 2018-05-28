#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.c.haulWriter_c import *

import json

def put(txt):
	print('HAULBuilder_vtech:\t' + str(txt))


HAULBUILDER_VTECH_DIR = os.path.dirname(__file__)
Z88DK_DIR = os.path.abspath(os.path.join(HAULBUILDER_VTECH_DIR, 'z88dk'))
VTECH_LIB_DIR = os.path.abspath(os.path.join(HAULBUILDER_VTECH_DIR, 'lib'))
LIB_DIR = os.path.abspath(os.path.join(HAULBUILDER_VTECH_DIR, 'lib2'))

MESS_DIR = 'Z:\\Apps\\_emu\\MESSUI-0.181'
MESS_ROM_DIR = 'Z:\\Apps\\_emu\\_roms'
#MESS_SYS = 'gl1000'
#MESS_SYS = 'gl2000'
#MESS_SYS = 'gl4000'
MESS_SYS = 'gl4004'

class HAULBuilder_vtech(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='c', platform='vtech')
	
	def build(self, inputFilename, sourcePath, stagingPath, outputPath, resources=None, perform_test_run=False):
		
		put('Starting build...')
		HAULBuilder.build(self, inputFilename, outputPath)
		
		
		put('Cleaning staging path...')
		self.clean(stagingPath)
		
		startPath = os.getcwd()
		
		#@TODO: Use module.imports!
		libs = ['hio']	#['sys', 'hio']
		
		name = nameByFilename(inputFilename)
		cFilename = name + '.c'
		cFilenameStaging = os.path.abspath(os.path.join(stagingPath, cFilename))
		
		binFilename = name + '_z80_vtech.bin'
		binFilenameStaging = os.path.abspath(os.path.join(stagingPath, binFilename))
		
		
		self.rm_if_exists(binFilenameStaging)
		
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(sourcePath, inputFilename), SourceReaderClass=HAULReader_py, destFilename=cFilenameStaging, DestWriterClass=HAULWriter_c, dialect=DIALECT_Z88DK)
		
		if not os.path.isfile(cFilenameStaging):
			put('Main C file "%s" was not created! Aborting.' % (cFilenameStaging))
			return False
		
		
		#appInfo_json = json.dumps(appInfo, indent=4)
		#writeFile(stagingPath + '/appinfo.json', appInfo_json)
		
		"""
		put('Gathering sources...')
		sources = []
		for l in libs:
			#self.copy('haul/langs/js/lib/' + l + '.js', stagingPath + '/' + l + '.js')
			self.copy(HAULBUILDER_WEBOS_DIR + '/lib/' + l + '.js', stagingPath + '/' + l + '.js')
			sources.append({
				'source': l + '.js'
			})
		"""
		
		# Compilation
		put('Compiling using Z88DK...')
		
		# Set environment
		
		my_env = os.environ.copy()
		my_env['PATH'] = os.environ['PATH'] + ';' + os.path.join(Z88DK_DIR, 'BIN')
		# Normally these files reside inside the z88dk, but we hijack them and use our minimal local version
		#my_env['OZFILES'] = os.join(Z88DK_DIR, 'LIB')
		#my_env['ZCCCFG'] = os.join(Z88DK_DIR, 'LIB', 'CONFIG')
		my_env['OZFILES'] = VTECH_LIB_DIR
		my_env['ZCCCFG'] = os.path.join(VTECH_LIB_DIR, 'config')
		
		"""
		cmd = os.path.join(Z88DK_DIR, 'bin', 'sccz80')	# Floating point (dstore/dload): https://www.z88dk.org/forum/viewtopic.php?pid=12763
		cmd += ' -//'
		cmd += ' -v'
		cmd += ' -zorg=' + os.path.join(Z88DK_DIR, 'bin')
		cmd += ' -I' + LIB_DIR
		cmd += ' -I' + os.path.join(Z88DK_DIR, 'include')
		cmd += ' ' + os.path.join(stagingPath, cFilename)
		"""
		
		cmd = os.path.join(Z88DK_DIR, 'bin', 'zcc')
		cmd += ' +vtech'
		#cmd += ' +z80'
		cmd += ' -subtype=rom_autostart'
		#cmd += ' -v'
		#cmd += ' -vn'
		cmd += ' -I' + LIB_DIR
		cmd += ' -I' + os.path.join(Z88DK_DIR, 'include')
		
		#cmd += ' -lm'
		#cmd += ' -l' + 'gen_math'
		#cmd += ' -l' + 'zx80_clib'
		#cmd += ' -lndos'
		#cmd += ' -l' + 'z88_clib'
		#cmd += ' -l' + 'z88_math'
		
		cmd += ' -o' + binFilenameStaging
		cmd += ' ' + cFilenameStaging
		
		
		self.chdir(stagingPath)	# Change to staging dir (some configs are created during build)
		r = self.command(cmd, env=my_env)
		self.chdir(startPath)	# Change back
		
		
		if not os.path.isfile(binFilenameStaging):
			put(r)
			put('BIN file "%s" was not created! Aborting.' % (binFilenameStaging))
			return False
		
		
		put('Copying bin file "%s" to output directory...' % (binFilename))
		self.copy(binFilenameStaging, os.path.join(outputPath, binFilename))
		
		
		# Test
		if perform_test_run:
			put('Launching MESS emulator...')
			
			cmd = '"%s"' % os.path.join(MESS_DIR, 'mess.exe')
			cmd += ' -rompath "%s"' % (MESS_ROM_DIR)
			cmd += ' %s' % (MESS_SYS)
			cmd += ' -cart "%s"' % (os.path.abspath(os.path.join(stagingPath, binFilename)))
			cmd += ' -window'
			cmd += ' -sleep'
			#cmd += ' -debug'	# Attach debug console and STEP
			
			self.chdir(stagingPath)	# Change to staging dir (MESS creates some messy files wherever it is called)
			r = self.command(cmd)
			self.chdir(startPath)	# Change back
			
			#@TODO: Delete the config file that MESS is creating (CFG)
		
		put('Done.')
		
		
