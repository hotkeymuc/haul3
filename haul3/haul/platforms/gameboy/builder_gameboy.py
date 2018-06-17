#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.c.writer_c import *

import json

def put(txt):
	print('HAULBuilder_gameboy:\t' + str(txt))


class HAULBuilder_gameboy(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='gameboy', lang='c')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_c, dialect=DIALECT_GBDK))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		
		start_path = os.getcwd()
		
		
		gbdk_path = os.path.abspath(self.get_path('GBDK_PATH', os.path.join(self.tools_path, 'platforms', 'gameboy', 'gbdk')))
		
		libs_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'gameboy', 'libs'))
		
		c_filename = name + '.c'
		c_filename_full = os.path.abspath(os.path.join(self.staging_path, c_filename))
		
		o_filename = name + '.o'
		o_filename_full = os.path.abspath(os.path.join(self.staging_path, o_filename))
		
		gb_filename = name + '.gb'
		gb_filename_full = os.path.abspath(os.path.join(self.staging_path, gb_filename))
		
		self.rm_if_exists(o_filename_full)
		self.rm_if_exists(gb_filename_full)
		
		put('Preparing path names...')
		for s in self.project.sources:
			s.dest_filename = self.staging_path + '/' + (s.name.split('.')[-1]) + '.c'
		
		put('Translating source...')
		#m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=c_filename_full, DestWriterClass=HAULWriter_c, dialect=DIALECT_GBDK)
		self.translate_project(output_path=self.staging_path)
		
		if not os.path.isfile(c_filename_full):
			raise HAULBuildError('Main C file "{}" was not created!'.format(c_filename_full))
			return False
		
		
		#self.copy(os.path.join(libs_path, 'hio.h'), os.path.join(self.staging_path, 'hio.h'))
		# Using libraries via command line argument
		#put('Copying libraries...')
		#for s in self.project.libs:
		#	self.copy(libs_path + '/' + s.name + '.h', self.staging_path + '/' + s.name + '.h')
		
		
		# Prepare environment
		my_env = os.environ.copy()
		
		#my_env['GBDKDIR'] = os.path.join(GBDK_DIR, '')	# Note the trailing slash! It is important or else GBDK will screw things up!
		
		#@FIXME: For some reason this must be relative or else the GB compilation fails with "...gameboy.re not found"
		#my_env['GBDKDIR'] = './tools/platforms/gameboy/gbdk/'	# Note the trailing slash! It is important or else GBDK will screw things up!
		#my_env['GBDKDIR'] = gbdk_path.replace('\\', '/') + '/'	# Note the trailing slash! It is important or else GBDK will screw things up!
		my_env['GBDKDIR'] = os.path.join(gbdk_path, '')	# Note the trailing slash! It is important or else GBDK will screw things up!
		
		my_env['TEMP'] = os.path.abspath(self.staging_path)
		my_env['TMP'] = os.path.abspath(self.staging_path)
		
		
		# Compilation
		put('Compiling using GBDK...')
		
		cmd = os.path.join(gbdk_path, 'bin', 'lcc')
		cmd += ' -Wa-l'
		cmd += ' -Wl-m'
		cmd += ' -Wl-j'
		
		cmd += ' -DUSE_SFR_FOR_REG'
		cmd += ' -I"{}"'.format(os.path.join(gbdk_path, 'include'))
		cmd += ' -I"{}"'.format(libs_path)
		cmd += ' -c'
		cmd += ' -v'
		cmd += ' -o "%s"' % (o_filename_full)
		cmd += ' "%s"' % (c_filename_full)
		
		#self.chdir(stagingPath)	# Change to staging dir (some configs are created during build)
		r = self.command(cmd, env=my_env)
		#self.chdir(start_path)	# Change back
		
		if not os.path.isfile(o_filename_full):
			put(r)
			raise HAULBuildError('O file "{}" was not created!'.format(o_filename_full))
			return False
		
		
		#@TODO: Add libs!
		
		put('Compiling GB using GBDK...')
		cmd = os.path.abspath(os.path.join(gbdk_path, 'bin', 'lcc'))
		cmd += ' -Wa-l'
		cmd += ' -Wl-m'
		cmd += ' -Wl-j'
		cmd += ' -DUSE_SFR_FOR_REG'
		#cmd += ' -I"%s"' % (GAMEBOY_LIB_DIR)
		cmd += ' -o "%s"' % (gb_filename_full)
		#cmd += ' -o %s' % (gb_filename)
		cmd += ' "%s"' % (o_filename_full)
		
		#self.chdir(stagingPath)
		r = self.command(cmd, env=my_env)
		#self.chdir(start_path)	# Change back
		
		if not os.path.isfile(gb_filename_full):
			put(r)
			raise HAULBuildError('GB file "{}" was not created!'.format(gb_filename_full))
			return False
		
		
		put('Copying GB file "%s" to output directory...' % (gb_filename))
		self.copy(gb_filename_full, os.path.join(self.output_path, gb_filename))
		
		
		# Test
		if (self.project.run_test == True):
			bgb_path = self.get_path('BGB_PATH', os.path.join(self.tools_path, 'platforms', 'gameboy', 'bgb'))
			
			put('Launching BGB emulator...')
			
			cmd = '"%s"' % os.path.join(bgb_path, 'bgb.exe')
			cmd += ' "%s"' % (gb_filename_full)
			
			r = self.command(cmd)
		
		put('Done.')
		return True
		
