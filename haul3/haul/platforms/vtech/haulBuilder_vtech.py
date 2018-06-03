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


MESS_DIR = 'Z:\\Apps\\_emu\\MESSUI-0.181'
MESS_ROM_DIR = 'Z:\\Apps\\_emu\\_roms'
#MESS_SYS = 'gl1000'
#MESS_SYS = 'gl2000'
#MESS_SYS = 'gl4000'
MESS_SYS = 'gl4004'

class HAULBuilder_vtech(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='vtech', lang='c')
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_c, dialect=DIALECT_Z88DK))
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		z88dk_lib_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'vtech', 'lib'))
		vm_path = os.path.join(self.data_path, 'platforms', 'vtech', 'vm')
		tools_path = os.path.abspath(os.path.join(self.data_path, '..', 'tools'))
		#mess_path = os.path.join(tools_path, 'mess')
		mess_path = MESS_DIR
		z88dk_path = os.path.abspath(os.path.join(tools_path, 'platforms', 'z80', 'z88dk'))
		libs_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'vtech', 'libs'))
		
		startPath = os.getcwd()
		
		cFilename = name + '.c'
		cFilenameStaging = os.path.abspath(os.path.join(self.staging_path, cFilename))
		
		binFilename = name + '_z80_vtech.bin'
		binFilenameStaging = os.path.abspath(os.path.join(self.staging_path, binFilename))
		
		
		self.rm_if_exists(binFilenameStaging)
		
		put('Copying libraries...')
		for s in self.project.libs:
			self.copy(os.path.join(libs_path, s.name + '.h'), os.path.join(self.staging_path, s.name + '.h'))
		
		
		put('Translating sources to C...')
		#m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=oplFilenameFull, DestWriterClass=HAULWriter_opl, dialect=DIALECT_OPL3)
		m = self.translate_project(output_path=self.staging_path)
		
		
		if not os.path.isfile(cFilenameStaging):
			put('Main C file "%s" was not created! Aborting.' % (cFilenameStaging))
			return False
		
		
		# Compilation
		put('Compiling using Z88DK...')
		
		# Set environment
		
		my_env = os.environ.copy()
		my_env['PATH'] = os.environ['PATH'] + ';' + os.path.join(z88dk_path, 'BIN')
		# Normally these files reside inside the z88dk, but we hijack them and use our minimal local version
		#my_env['OZFILES'] = os.join(z88dk_path, 'LIB')
		#my_env['ZCCCFG'] = os.join(z88dk_path, 'LIB', 'CONFIG')
		my_env['OZFILES'] = z88dk_lib_path
		my_env['ZCCCFG'] = os.path.join(z88dk_lib_path, 'config')
		
		"""
		cmd = os.path.join(z88dk_path, 'bin', 'sccz80')	# Floating point (dstore/dload): https://www.z88dk.org/forum/viewtopic.php?pid=12763
		cmd += ' -//'
		cmd += ' -v'
		cmd += ' -zorg=' + os.path.join(z88dk_path, 'bin')
		cmd += ' -I' + libs_path
		cmd += ' -I' + os.path.join(z88dk_path, 'include')
		cmd += ' ' + os.path.join(staging_path, cFilename)
		"""
		
		cmd = os.path.join(z88dk_path, 'bin', 'zcc')
		cmd += ' +vtech'
		#cmd += ' +z80'
		cmd += ' -subtype=rom_autostart'
		#cmd += ' -v'
		#cmd += ' -vn'
		cmd += ' -I' + os.path.abspath(libs_path)
		cmd += ' -I' + os.path.abspath(os.path.join(z88dk_path, 'include'))
		
		#cmd += ' -lm'
		#cmd += ' -l' + 'gen_math'
		#cmd += ' -l' + 'zx80_clib'
		#cmd += ' -lndos'
		#cmd += ' -l' + 'z88_clib'
		#cmd += ' -l' + 'z88_math'
		
		cmd += ' -o' + binFilenameStaging
		cmd += ' ' + cFilenameStaging
		
		
		self.chdir(self.staging_path)	# Change to staging dir (some configs are created during build)
		r = self.command(cmd, env=my_env)
		self.chdir(startPath)	# Change back
		
		
		if not os.path.isfile(binFilenameStaging):
			put(r)
			put('BIN file "%s" was not created! Aborting.' % (binFilenameStaging))
			return False
		
		
		put('Copying bin file "%s" to output directory...' % (binFilename))
		self.copy(binFilenameStaging, os.path.join(self.output_path, binFilename))
		
		
		# Test
		if (self.project.run_test == True):
			put('Launching MESS emulator...')
			
			cmd = '"%s"' % os.path.join(MESS_DIR, 'mess.exe')
			cmd += ' -rompath "%s"' % (MESS_ROM_DIR)
			cmd += ' %s' % (MESS_SYS)
			cmd += ' -cart "%s"' % (os.path.abspath(os.path.join(self.staging_path, binFilename)))
			cmd += ' -window'
			cmd += ' -sleep'
			#cmd += ' -debug'	# Attach debug console and STEP
			
			self.chdir(self.staging_path)	# Change to staging dir (MESS creates some messy files wherever it is called)
			r = self.command(cmd)
			self.chdir(self.startPath)	# Change back
			
			#@TODO: Delete the config file that MESS is creating (CFG)
		
		put('Done.')
		
		
