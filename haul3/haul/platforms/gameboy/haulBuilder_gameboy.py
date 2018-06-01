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


#HAULBUILDER_GAMEBOY_DIR = os.path.dirname(__file__)
#GBDK_DIR = os.path.abspath(os.path.join(HAULBUILDER_GAMEBOY_DIR, 'gbdk'))
#GAMEBOY_LIB_DIR = os.path.abspath(os.path.join(HAULBUILDER_GAMEBOY_DIR, 'lib'))
#EMU_DIR = os.path.abspath(os.path.join(HAULBUILDER_GAMEBOY_DIR, 'emu'))


class HAULBuilder_gameboy(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='c', platform='gameboy')
	
	def build(self, source_path, source_filename, output_path, staging_path, data_path, resources=None, perform_test_run=False):
		
		HAULBuilder.build(self, source_path=source_path, source_filename=source_filename, output_path=output_path, staging_path=staging_path, data_path=data_path, resources=resources, perform_test_run=perform_test_run)
		
		
		startPath = os.getcwd()
		
		#@TODO: Use module.imports!
		libs = ['hio']	#['sys', 'hio']
		
		tools_path = os.path.join(data_path, '..', 'tools')
		libs_path = os.path.join(data_path, 'platforms', 'gameboy', 'libs')
		gbdk_path = os.path.join(tools_path, 'platforms', 'gameboy', 'gbdk')
		bgb_path = os.path.join(tools_path, 'platforms', 'gameboy', 'bgb')
		
		name = name_by_filename(source_filename)
		cFilename = name + '.c'
		cFilenameStaging = os.path.abspath(os.path.join(staging_path, cFilename))
		
		oFilename = name + '.o'
		oFilenameStaging = os.path.abspath(os.path.join(staging_path, oFilename))
		
		gbFilename = name + '.gb'
		gbFilenameStaging = os.path.abspath(os.path.join(staging_path, gbFilename))
		
		self.rm_if_exists(oFilenameStaging)
		self.rm_if_exists(gbFilenameStaging)
		
		
		
		put('Translating source...')
		m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=cFilenameStaging, DestWriterClass=HAULWriter_c, dialect=DIALECT_GBDK)
		
		if not os.path.isfile(cFilenameStaging):
			put('Main C file "%s" was not created! Aborting.' % (cFilenameStaging))
			return False
		
		
		#self.copy(os.path.join(libs_path, 'hio.h'), os.path.join(staging_path, 'hio.h'))
		
		# Prepare environment
		my_env = os.environ.copy()
		
		#my_env['GBDKDIR'] = os.path.join(GBDK_DIR, '')	# Note the trailing slash! It is important or else GBDK will screw things up!
		
		#@FIXME: For some reason this must be relative or else the GB compilation fails with "...gameboy.re not found"
		my_env['GBDKDIR'] = './tools/platforms/gameboy/gbdk/'	# Note the trailing slash! It is important or else GBDK will screw things up!
		
		# Compilation
		put('Compiling using GBDK...')
		
		cmd = os.path.join(gbdk_path, 'bin', 'lcc')
		cmd += ' -Wa-l'
		cmd += ' -Wl-m'
		cmd += ' -Wl-j'
		cmd += ' -DUSE_SFR_FOR_REG'
		cmd += ' -I"%s"' % (libs_path)
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
		cmd = os.path.join(gbdk_path, 'bin', 'lcc')
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
		self.copy(gbFilenameStaging, os.path.join(output_path, gbFilename))
		
		
		# Test
		if perform_test_run:
			put('Launching BGB emulator...')
			
			cmd = '"%s"' % os.path.join(bgb_path, 'bgb.exe')
			cmd += ' "%s"' % (gbFilenameStaging)
			
			r = self.command(cmd)
		
		put('Done.')
		
		
