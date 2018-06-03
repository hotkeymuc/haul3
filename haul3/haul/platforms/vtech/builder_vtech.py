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


class HAULBuilder_vtech(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='vtech', lang='c')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_c, dialect=DIALECT_Z88DK))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		vgl_model = '2000'
		
		#@TODO: Allow other Z88DK targets!
		#@Actually, turn this into builder_z80!
		z88dk_target = 'vgl'
		z88dk_subtype = vgl_model + '_rom_autostart'
		mess_sys = 'gl' + vgl_model
		
		
		#z88dk_path = os.path.abspath('Z:/Data/_code/_cWorkspace/z88dk.git')
		z88dk_path = self.get_path('Z88DK_PATH', os.path.abspath(os.path.join(self.tools_path, 'platforms', 'z80', 'z88dk')))
		put('Using Z88DK in "{}"'.format(z88dk_path))
		
		z88dk_lib_path = os.path.abspath(z88dk_path + '/lib')
		
		libs_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'vtech', 'libs'))
		start_path = os.getcwd()
		
		c_filename = name + '.c'
		c_filename_full = os.path.abspath(os.path.join(self.staging_path, c_filename))
		
		bin_name = name + '_z80_' + z88dk_target + z88dk_subtype
		bin_filename = bin_name + '.bin'
		bin_filename_full = os.path.abspath(os.path.join(self.staging_path, bin_filename))
		
		self.rm_if_exists(bin_filename_full)
		
		
		#put('Copying essentials...')
		#essentials = ['vtech']
		
		put('Copying libraries...')
		for s in self.project.libs:
			self.copy(os.path.join(libs_path, s.name + '.h'), os.path.join(self.staging_path, s.name + '.h'))
		
		
		put('Translating sources to C...')
		#m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=oplFilenameFull, DestWriterClass=HAULWriter_opl, dialect=DIALECT_OPL3)
		m = self.translate_project(output_path=self.staging_path)
		
		
		if not os.path.isfile(c_filename_full):
			raise HAULBuildError('Main C file "{}" was not created!'.format(c_filename_full))
			return False
		
		
		# Compilation
		put('Compiling using Z88DK...')
		
		# Set environment
		my_env = os.environ.copy()
		my_env['PATH'] = os.environ['PATH'] + ';' + os.path.join(z88dk_path, 'bin')
		# Normally these files reside inside the z88dk, but we canhijack them and use our minimal local version
		my_env['OZFILES'] = z88dk_lib_path
		my_env['ZCCCFG'] = os.path.abspath(z88dk_lib_path + '/config')
		
		
		### Using SDCC compiler (can not handle inline #asm/#endasm in C!)
		#SET ZCCCMD=zcc +vgl -vn -clib=sdcc_iy -SO3 --max-allocs-per-node200000 %PROGNAME%.c -o %PROGNAME% -create-app
		#SET ZCCCMD=zcc +vgl -v -clib=sdcc_iy -SO3 --max-allocs-per-node200000 %PROGNAME%.c -o %PROGNAME% -create-app
		
		### Using SCCZ80 compiler
		#SET ZCCCMD=zcc +vgl -vn -clib=new %VGLOPTS% %SRCPATH%%PROGNAME%.c -o %PROGNAME% -create-app
		
		cmd = os.path.join(z88dk_path, 'bin', 'zcc')
		cmd = 'zcc'
		cmd += ' +' + z88dk_target
		cmd += ' -vn'
		cmd += ' -clib=new'
		cmd += ' -subtype=' + z88dk_subtype
		
		#cmd += ' -I' + os.path.abspath(libs_path)
		#cmd += ' -I' + os.path.abspath(os.path.join(z88dk_path, 'include'))
		
		#cmd += ' -lm'
		#cmd += ' -l' + 'gen_math'
		#cmd += ' -l' + 'zx80_clib'
		#cmd += ' -lndos'
		#cmd += ' -l' + 'z88_clib'
		#cmd += ' -l' + 'z88_math'
		
		cmd += ' ' + c_filename
		cmd += ' -o ' + bin_name
		cmd += ' -create-app'
		
		
		self.chdir(self.staging_path)	# Change to staging dir (some configs are created during build)
		r = self.command(cmd, env=my_env)
		self.chdir(start_path)	# Change back
		
		#@TODO: IF ERRORLEVEL 1 GOTO:ERROR
		
		if not os.path.isfile(bin_filename_full):
			put(r)
			raise HAULBuildError('BIN file "{}" was not created!'.format(bin_filename_full))
			return False
		
		
		put('Copying bin file "%s" to output directory...' % (bin_filename))
		self.copy(bin_filename_full, os.path.join(self.output_path, bin_filename))
		
		
		# Test
		if (self.project.run_test == True):
			
			#mess_path = 'Z:\\Apps\\_emu\\MESSUI-0.181'
			mess_path = self.get_path('MESS_PATH', os.path.abspath(os.path.join(self.tools_path, 'mess')))
			
			#mess_rom_path = 'Z:\\Apps\\_emu\\_roms'
			mess_rom_path = self.get_path('MESS_ROM_PATH', os.path.abspath(os.path.join(self.data_path, 'mess_roms')))
			
			put('Launching MESS emulator...')
			
			#"%MESSPATH%\mess.exe" -rompath "%ROMPATH%" %EMUSYS% -cart "%PROGNAME%.bin" -window -nomax -nofilter -sleep -volume -10 -skip_gameinfo -speed 2.00
			
			cmd = '"%s"' % os.path.join(mess_path, 'mess.exe')
			cmd += ' -rompath "%s"' % (mess_rom_path)
			cmd += ' %s' % (mess_sys)
			cmd += ' -cart "%s"' % (os.path.abspath(os.path.join(self.output_path, bin_filename)))
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
			self.chdir(start_path)	# Change back
			
			#@TODO: Delete the config file that MESS is creating (CFG)
		
		put('Done.')
		return True
		
