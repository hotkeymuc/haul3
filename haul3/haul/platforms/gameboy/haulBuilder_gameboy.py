#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.c.haulWriter_c import *

import json

def put(txt):
	print('HAULBuilder_gameboy:\t' + str(txt))


HAULBUILDER_GAMEBOY_DIR = os.path.dirname(__file__)
GBDK_DIR = os.path.abspath(os.path.join(HAULBUILDER_GAMEBOY_DIR, 'gbdk'))
GAMEBOY_LIB_DIR = os.path.abspath(os.path.join(HAULBUILDER_GAMEBOY_DIR, 'lib'))
EMU_DIR = os.path.abspath(os.path.join(HAULBUILDER_GAMEBOY_DIR, 'emu'))


class HAULBuilder_gameboy(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='c', platform='gameboy')
	
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
		
		oFilename = name + '.o'
		oFilenameStaging = os.path.abspath(os.path.join(stagingPath, oFilename))
		
		gbFilename = name + '.gb'
		gbFilenameStaging = os.path.abspath(os.path.join(stagingPath, gbFilename))
		
		self.rm_if_exists(oFilenameStaging)
		self.rm_if_exists(gbFilenameStaging)
		
		
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(sourcePath, inputFilename), SourceReaderClass=HAULReader_py, destFilename=cFilenameStaging, DestWriterClass=HAULWriter_c, dialect=DIALECT_GBDK)
		
		if not os.path.isfile(cFilenameStaging):
			put('Main C file "%s" was not created! Aborting.' % (cFilenameStaging))
			return False
		
		
		#self.copy(os.path.join(GAMEBOY_LIB_DIR, 'hio.h'), os.path.join(stagingPath, 'hio.h'))
		
		# Prepare environment
		my_env = os.environ.copy()
		
		#my_env['GBDKDIR'] = os.path.join(GBDK_DIR, '')	# Note the trailing slash! It is important or else GBDK will screw things up!
		
		#@FIXME: For some reason this must be relative or else the GB compilation fails with "...gameboy.re not found"
		my_env['GBDKDIR'] = './haul/platforms/gameboy/gbdk/'	# Note the trailing slash! It is important or else GBDK will screw things up!
		
		# Compilation
		put('Compiling using GBDK...')
		
		cmd = os.path.join(GBDK_DIR, 'bin', 'lcc')
		cmd += ' -Wa-l'
		cmd += ' -Wl-m'
		cmd += ' -Wl-j'
		cmd += ' -DUSE_SFR_FOR_REG'
		cmd += ' -I"%s"' % (GAMEBOY_LIB_DIR)
		cmd += ' -c'
		cmd += ' -o "%s"' % (oFilenameStaging)
		cmd += ' "%s"' % (cFilenameStaging)
		
		#self.chdir(stagingPath)	# Change to staging dir (some configs are created during build)
		r = self.command(cmd, env=my_env)
		#self.chdir(startPath)	# Change back
		
		if not os.path.isfile(oFilenameStaging):
			put(r)
			put('O file "%s" was not created! Aborting.' % (oFilenameStaging))
			return False
		
		
		put('Compiling GB using GBDK...')
		cmd = os.path.join(GBDK_DIR, 'bin', 'lcc')
		cmd += ' -Wa-l'
		cmd += ' -Wl-m'
		cmd += ' -Wl-j'
		cmd += ' -DUSE_SFR_FOR_REG'
		#cmd += ' -I"%s"' % (GAMEBOY_LIB_DIR)
		cmd += ' -o "%s"' % (gbFilenameStaging)
		#cmd += ' -o %s' % (gbFilename)
		cmd += ' "%s"' % (oFilenameStaging)
		
		#self.chdir(stagingPath)
		r = self.command(cmd, env=my_env)
		#self.chdir(startPath)	# Change back
		
		if not os.path.isfile(gbFilenameStaging):
			put(r)
			put('GB file "%s" was not created! Aborting.' % (gbFilenameStaging))
			return False
		
		
		
		put('Copying GB file "%s" to output directory...' % (gbFilename))
		self.copy(gbFilenameStaging, os.path.join(outputPath, gbFilename))
		
		
		# Test
		if perform_test_run:
			put('Launching BGB emulator...')
			
			cmd = '"%s"' % os.path.join(EMU_DIR, 'bgb.exe')
			cmd += ' "%s"' % (gbFilenameStaging)
			
			r = self.command(cmd)
		
		put('Done.')
		
		
