#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.c.writer_c import *

import json

def put(txt):
	print('HAULBuilder_vtech:\t' + str(txt))


Z88DK_VGL_MODEL = '4000'
MESS_DIR = 'Z:\\Apps\\_emu\\MESSUI-0.181'
MESS_ROM_DIR = 'Z:\\Apps\\_emu\\_roms'
#MESS_SYS = 'gl1000'
#MESS_SYS = 'gl2000'
MESS_SYS = 'gl4000'
#MESS_SYS = 'gl4004'

class HAULBuilder_vtech(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='vtech', lang='c')
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_c, dialect=DIALECT_Z88DK))
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		tools_path = os.path.abspath(os.path.join(self.data_path, '..', 'tools'))
		
		#z88dk_path = os.path.abspath(os.path.join(tools_path, 'platforms', 'z80', 'z88dk'))
		#z88dk_lib_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'vtech', 'lib'))
		
		z88dk_path = os.path.abspath('Z:/Data/_code/_cWorkspace/z88dk.git')
		z88dk_lib_path = os.path.abspath(z88dk_path + '/lib')
		
		
		vm_path = os.path.join(self.data_path, 'platforms', 'vtech', 'vm')
		#mess_path = os.path.join(tools_path, 'mess')
		mess_path = MESS_DIR
		libs_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'vtech', 'libs'))
		
		startPath = os.getcwd()
		
		cFilename = name + '.c'
		cFilenameStaging = os.path.abspath(os.path.join(self.staging_path, cFilename))
		
		binName = name + '_z80_vtech'
		binFilename = binName + '.bin'
		binFilenameStaging = os.path.abspath(os.path.join(self.staging_path, binFilename))
		
		
		self.rm_if_exists(binFilenameStaging)
		
		put('Copying essentials...')
		essentials = ['vtech', ]
		
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
		my_env['PATH'] = os.environ['PATH'] + ';' + os.path.join(z88dk_path, 'bin')
		# Normally these files reside inside the z88dk, but we hijack them and use our minimal local version
		my_env['OZFILES'] = z88dk_lib_path
		my_env['ZCCCFG'] = os.path.abspath(z88dk_lib_path + '/config')
		
		
		### Use SDCC compiler (can not handle inline #asm/#endasm in C!)
		#SET ZCCCMD=zcc +vgl -vn -clib=sdcc_iy -SO3 --max-allocs-per-node200000 %PROGNAME%.c -o %PROGNAME% -create-app
		#SET ZCCCMD=zcc +vgl -v -clib=sdcc_iy -SO3 --max-allocs-per-node200000 %PROGNAME%.c -o %PROGNAME% -create-app
		
		### Use SCCZ80 compiler
		#SET ZCCCMD=zcc +vgl -vn -clib=new %VGLOPTS% %SRCPATH%%PROGNAME%.c -o %PROGNAME% -create-app
		
		cmd = os.path.join(z88dk_path, 'bin', 'zcc')
		cmd = 'zcc'
		cmd += ' +vgl'
		cmd += ' -vn'
		cmd += ' -clib=new'
		cmd += ' -subtype=' + Z88DK_VGL_MODEL + '_rom_autostart'
		
		#cmd += ' -I' + os.path.abspath(libs_path)
		#cmd += ' -I' + os.path.abspath(os.path.join(z88dk_path, 'include'))
		
		#cmd += ' -lm'
		#cmd += ' -l' + 'gen_math'
		#cmd += ' -l' + 'zx80_clib'
		#cmd += ' -lndos'
		#cmd += ' -l' + 'z88_clib'
		#cmd += ' -l' + 'z88_math'
		
		cmd += ' ' + cFilename
		cmd += ' -o ' + binName
		cmd += ' -create-app'
		
		
		self.chdir(self.staging_path)	# Change to staging dir (some configs are created during build)
		r = self.command(cmd, env=my_env)
		self.chdir(startPath)	# Change back
		
		#@TODO: IF ERRORLEVEL 1 GOTO:ERROR
		
		
		if not os.path.isfile(binFilenameStaging):
			put(r)
			put('BIN file "%s" was not created! Aborting.' % (binFilenameStaging))
			return False
		
		
		put('Copying bin file "%s" to output directory...' % (binFilename))
		self.copy(binFilenameStaging, os.path.join(self.output_path, binFilename))
		
		
		# Test
		if (self.project.run_test == True):
			put('Launching MESS emulator...')
			
			#"%MESSPATH%\mess.exe" -rompath "%ROMPATH%" %EMUSYS% -cart "%PROGNAME%.bin" -window -nomax -nofilter -sleep -volume -10 -skip_gameinfo -speed 2.00
			
			cmd = '"%s"' % os.path.join(MESS_DIR, 'mess.exe')
			cmd += ' -rompath "%s"' % (MESS_ROM_DIR)
			cmd += ' %s' % (MESS_SYS)
			cmd += ' -cart "%s"' % (os.path.abspath(os.path.join(self.output_path, binFilename)))
			cmd += ' -window'
			cmd += ' -nomax'
			cmd += ' -nofilter'
			cmd += ' -sleep'
			cmd += ' -volume -20'
			cmd += ' -skip_gameinfo'
			cmd += ' -speed 2.00'
			#cmd += ' -debug'	# Attach debug console and STEP
			
			self.chdir(self.staging_path)	# Change to staging dir (MESS creates some messy files wherever it is called)
			r = self.command(cmd)
			self.chdir(startPath)	# Change back
			
			#@TODO: Delete the config file that MESS is creating (CFG)
		
		put('Done.')
		
		
