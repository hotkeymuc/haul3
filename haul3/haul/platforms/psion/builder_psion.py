#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Builder for PSION (CM/XP)

* translates to OPL (using Basic language)
* compiles in VM using PSION DevKit for DOS
* emulates using ORG2BETA for DOS
"""

from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.opl.writer_opl import *




class HAULBuilder_psion(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='psion', lang='opl')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_opl, dialect=DIALECT_OPL3))
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		data_libs_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'psion', 'libs'))
		vm_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'psion', 'vm'))
		qemu_path = self.get_path('QEMU_PATH', os.path.abspath(os.path.join(self.tools_path, 'qemu')))
		
		
		#@FIXME: Bootable packs can be created using BLDPACK. But for some reason it then does not include all binaries!
		#@FIXME: When disabling bootable, I use MAKEPACK which seems to handle multiple files easily, but can not handle BIN files needed for bootable.
		bootable = not True	# Make it auto-run by including a BOOT.BIN and renaming the main proc BOOT
		lcd_lines = 2	# 2 for CM/XP, 4 for LZ etc.
		
		
		
		name8 = self.name_to_8(name).upper()
		opl_filename = name8 + '.OPL'
		#ob3Filename = name8 + '.ob3'
		opl_filename_full = os.path.abspath(os.path.join(self.staging_path, opl_filename))
		opk_filename = name8 + '.OPK'
		
		
		put('Preparing path names...')
		for s in self.project.sources:
			s.dest_filename = self.staging_path + '/' + self.name_to_8(s.name).upper() + '.OPL'
		for s in self.project.libs:
			s.dest_filename = self.staging_path + '/' + self.name_to_8(s.name).upper() + '.OPL'
		
		put('Copying libraries...')
		for s in self.project.libs:
			self.copy(os.path.join(data_libs_path, s.name + '.opl'), os.path.join(self.staging_path, self.name_to_8(s.name).upper() + '.OPL'))
		
		
		put('Translating sources to OPL3...')
		#m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=opl_filename_full, DestWriterClass=HAULWriter_opl, dialect=DIALECT_OPL3)
		m = self.translate_project(output_path=self.staging_path)
		
		
		### Split main module into separate files
		func_libs = []
		# OPL3 (XP/CM) does not support multiple procs in one file.
		for f in m.funcs:
			#put(str(f.id.name) + ':	' + str(f))
			# Select module name
			func_name = f.id.name
			func_name8 = func_name[0:8].upper()
			#@TODO: Ensure that this name is unique! Or just give random name (lame)
			
			func_filename = func_name8 + '.OPL'
			func_filename_full = os.path.abspath(os.path.join(self.staging_path, func_filename))
			
			streamOut = StringWriter()
			writer = HAULWriter_opl(streamOut, dialect=DIALECT_OPL3)
			m = writer.write_function(f)	# That's where the magic happens!
			
			put('Writing function "%s" to "%s"...' % (f.id.name, func_filename_full))
			write_file(func_filename_full, streamOut.r)
			self.copy(func_filename_full, func_filename_full+'.bak')	# Backup (compiler deletes it?!)
			
			# Add to compile files
			func_libs.append(func_filename)
		
		
		"""
		### For testing: Create a (valid) dummy OPL file
		NL = chr(0)	#'\r\n'
		if bootable:
			oplDummySource = 'BOOT:' + NL	# Must be called "BOOT" to be called by BOOT.BIN on start-up
		else:
			oplDummySource = name8 + ':' + NL
		
		oplDummySource += 'PRINT"Hello from HAUL"' + NL
		oplDummySource += 'BEEP 250,440' + NL
		oplDummySource += 'PAUSE 40' + NL
		self.touch(opl_filename_full, oplDummySource)
		"""
		
		# Check if translation worked
		if not os.path.isfile(opl_filename_full):
			raise HAULBuildError('Main OPL file "%s" was not created!'.format(opl_filename_full))
			return False
			
		
		self.copy(opl_filename_full, opl_filename_full + '.bak')	# Backup main file for testing (source file gets deleted somehow...)
		
		
		put('Preparing VM automation...')
		disk_sys = os.path.join(vm_path, 'sys_msdos622.disk')
		disk_compiler = os.path.join(vm_path, 'app_devkit.disk')
		disk_empty = os.path.join(vm_path, 'empty.disk')
		disk_temp = os.path.abspath(os.path.join(self.staging_path, 'tmp.disk'))
		
		# Create/clear temp scratch disk
		self.copy(disk_empty, disk_temp)
		build_log_file = os.path.abspath(os.path.join(self.staging_path, 'build.log'))
		#self.touch(build_log_file, '# Build log')
		self.rm_if_exists(build_log_file)
		self.rm_if_exists(os.path.abspath(os.path.join(self.staging_path, opk_filename)))
		
		
		DOS_SYS_DIR = 'C:'
		DOS_COMPILER_DRIVE = 'D'
		DOS_COMPILER_DIR = DOS_COMPILER_DRIVE + ':'
		DOS_STAGING_DIR = 'F:'
		DOS_TEMP_DRIVE = 'E'
		DOS_TEMP_DIR = DOS_TEMP_DRIVE + ':'
		DOS_LOG_FILE = DOS_TEMP_DIR + '\\build.log'	#DOS_LOG_FILE = DOS_STAGING_DIR + '\\build.log'
		
		DEVKIT_PATH = DOS_COMPILER_DIR + '\\DEVKIT'
		
		CRLF = '\r\n'
		
		# Startup prolog...
		autoexec = 'ECHO.' + CRLF
		
		autoexec += 'SMARTDRV /C /X' + CRLF
		
		autoexec = 'CLS' + CRLF
		autoexec += 'SET TEMP=E:' + CRLF
		autoexec += 'ECHO haulBuilder_psion' + CRLF
		autoexec += 'ECHO.' + CRLF
		
		# Compile...
		autoexec += ':COMPILE' + CRLF
		autoexec += 'ECHO ----------------------------------------' + CRLF
		#autoexec += 'ECHO Staging dir:' + CRLF
		#autoexec += 'DIR ' + DOS_STAGING_DIR + ' /B' + CRLF
		
		autoexec += 'ECHO Staging...' + CRLF
		#autoexec += 'COPY ' + DOS_STAGING_DIR + '\*.opl ' + DOS_TEMP_DIR + CRLF
		DOS_IN_FILE = DOS_TEMP_DIR + '\\' + opl_filename
		DOS_OUT_FILE = DOS_TEMP_DIR + '\\' + opk_filename
		
		
		autoexec += 'ECHO Build log >' + DOS_LOG_FILE + CRLF
		
		autoexec += DOS_COMPILER_DRIVE + ':' + CRLF
		autoexec += 'CD ' + DEVKIT_PATH + CRLF
		
		autoexec += DOS_TEMP_DRIVE + ':' + CRLF
		autoexec += 'CD ' + DOS_TEMP_DIR + CRLF
		
		
		### List all source files
		#oplFiles = []
		source_list_filename = DOS_TEMP_DIR + '\\' + name8 + '.lst'
		
		
		"""
		autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + opl_filename + ' ' + DOS_TEMP_DIR + CRLF
		#oplFiles.append(DOS_TEMP_DIR + '\\' + opl_filename)
		autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\' + opl_filename + '>' + source_list_filename + CRLF
		
		for l in libs:
			autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + l + '.OPL ' + DOS_TEMP_DIR + CRLF
			#oplFiles.append(DOS_TEMP_DIR + '\\' + l + '.OPL')
			autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\' + l + '.OPL>>' + source_list_filename + CRLF
		"""
		
		autoexec += 'COPY NUL ' + source_list_filename + CRLF
		for s in self.project.sources:
			n = self.name_to_8(s.name).upper() + '.OPL'
			autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + n + ' ' + DOS_TEMP_DIR + CRLF
			#oplFiles.append(DOS_TEMP_DIR + '\\' + n)
			autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\' + n + '>>' + source_list_filename + CRLF
		for s in self.project.libs:
			n = self.name_to_8(s.name).upper() + '.OPL'
			autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + n + ' ' + DOS_TEMP_DIR + CRLF
			#oplFiles.append(DOS_TEMP_DIR + '\\' + n)
			autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\' + n + '>>' + source_list_filename + CRLF
		
		for n in func_libs:
			autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + n + ' ' + DOS_TEMP_DIR + CRLF
			#oplFiles.append(DOS_TEMP_DIR + '\\' + n)
			autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\' + n + '>>' + source_list_filename + CRLF
		
		if bootable:
			# Add BOOT procedure that calls the main file
			autoexec += 'ECHO BOOT:>' + DOS_TEMP_DIR + '\\BOOT.OPL' + CRLF
			autoexec += 'ECHO ' + name8 + ':>>' + DOS_TEMP_DIR + '\\BOOT.OPL' + CRLF
			autoexec += 'ECHO GET>>' + DOS_TEMP_DIR + '\\BOOT.OPL' + CRLF
			
			#oplFiles.append(DOS_TEMP_DIR + '\\BOOT.OPL')
			autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\BOOT.OPL>>' + source_list_filename + CRLF
		
		
		#autoexec += 'ECHO ---------- All sources ----------' + CRLF
		#autoexec += 'TYPE ' + source_list_filename + CRLF
		#autoexec += 'ECHO --------------------' + CRLF
		
		### Compile
		OPLTRAN_CMD = DEVKIT_PATH + '\\OPLTRAN @' + source_list_filename
		OPLTRAN_CMD += ' -t'	# Include source and object
		if lcd_lines == 2:
			# Two-line LCD driver
			OPLTRAN_CMD += ' -x'
		
		autoexec += 'ECHO Executing "' + OPLTRAN_CMD + '"...' + CRLF
		autoexec += 'ECHO ' + OPLTRAN_CMD + ' >>' + DOS_LOG_FILE + CRLF
		autoexec += OPLTRAN_CMD + ' >>' + DOS_LOG_FILE + CRLF
		autoexec += 'TYPE ' + DOS_LOG_FILE + CRLF
		
		#@TODO: Check for compilation errors
		autoexec += 'IF ERRORLEVEL 1 GOTO ERROR' + CRLF
		
		### Create pack list (.bld file that tells which records to put in the OPK file)
		bld_name = name8
		bld_filename = bld_name+'.bld'
		
		# Header line
		pakSize = 16	# in kB, either 8 or 16
		#l = '%s %d NOCOPY NOWRITE' % (bld_name, pakSize)
		l = '%s %d' % (bld_name, pakSize)
		autoexec += 'ECHO ' + l + '>' + bld_filename + CRLF
		
		
		if bootable:
			# Add boot binary to pak
			autoexec += 'COPY ' + DEVKIT_PATH + '\\BOOT.BIN' + ' ' + DOS_TEMP_DIR + CRLF
			l = 'BOOT BIN'
			#l += '  !Boot file'
			autoexec += 'ECHO ' + l + '>>' + bld_filename + CRLF
		
		
		# Lib files preceed the main file
		for s in self.project.libs:
			l = self.name_to_8(s.name).upper()
			#while len(l) < 8: l += ' '
			l += ' OB3'
			#l = l + ' OB3 ' + l
			#@FIXME: They must be renamed according to their returnType, e.g. FOO%
			#l += ' ' + func_name8 + typeIndicator
			#l += ' ' + l.upper() + '  !Function/Lib'
			#l += '  !Function/Lib'
			autoexec += 'ECHO ' + l + '>>' + bld_filename + CRLF
		
		
		# main OB3 file
		l = name8
		#while len(l) < 8: l += ' '
		l += ' OB3'
		#l += '  !Main module'
		#if bootable: l += ' BOOT  !Boot file'	# Rename it "BOOT" to be called by BOOT.BIN
		autoexec += 'ECHO ' + l + '>>' + bld_filename + CRLF
		
		
		if bootable:
			l = 'BOOT OB3'
			#l += '  !Boot file'
			#l = 'BOOT OPL  !Boot file'	#@FIXME: This lets BLDPACK crash/hang
			autoexec += 'ECHO ' + l + '>>' + bld_filename + CRLF
		
		# Empty line
		#autoexec += 'ECHO>>' + bld_filename + CRLF
		
		
		### Build pack
		if bootable:
			# Using BLDPACK
			BLD_CMD = DEVKIT_PATH + '\\BLDPACK @' + bld_name + ' -map'
		else:
			# Using MAKEPACK (does not support BIN files, but is good)
			BLD_CMD = DEVKIT_PATH + '\\MAKEPACK ' + bld_filename
		
		autoexec += 'ECHO Executing "' + BLD_CMD + '"...' + CRLF
		autoexec += 'ECHO ' + BLD_CMD + ' >>' + DOS_LOG_FILE + CRLF
		autoexec += BLD_CMD + ' >>' + DOS_LOG_FILE + CRLF
		
		
		autoexec += 'TYPE ' + DOS_LOG_FILE + CRLF
		autoexec += 'ECHO ----------------------------------------' + CRLF
		autoexec += 'ECHO ---------------------------------------- >>' + DOS_LOG_FILE + CRLF
		
		
		autoexec += 'ECHO Publishing...' + CRLF
		#autoexec += 'SMARTDRV /C /X' + CRLF
		#autoexec += 'COPY /B ' + DOS_OUT_FILE + ' ' + DOS_STAGING_DIR + CRLF
		#autoexec += 'COPY /B ' + DOS_LOG_FILE + ' ' + DOS_STAGING_DIR + CRLF
		autoexec += 'COPY /B ' + DOS_TEMP_DIR + '\*.* ' + DOS_STAGING_DIR + CRLF
		autoexec += 'ECHO ----------------------------------------' + CRLF
		
		
		if (self.project.run_test == True):
			# Test result
			
			autoexec += 'CLS' + CRLF
			autoexec += 'ECHO Testing "' + DOS_OUT_FILE + '"...' + CRLF
			autoexec += 'ECHO ----------------------------------------' + CRLF
			
			autoexec += DOS_TEMP_DRIVE + ':' + CRLF
			autoexec += 'CD ' + DOS_TEMP_DIR + CRLF
			
			
			# Call ORG2BETA.EXE emulator
			autoexec += 'COPY ' + DEVKIT_PATH + '\\PSION.INI .' + CRLF
			#autoexec += 'COPY ' + DEVKIT_PATH + '\\*.DAT .' + CRLF
			autoexec += 'COPY ' + DEVKIT_PATH + '\\24-CM.DAT .' + CRLF
			autoexec += 'RENAME ' + DOS_OUT_FILE + ' PAK_B.OPK' + CRLF
			
			if bootable:
				put('Procedure "' + name8 + '" should start automatically on boot.')
				put('However, BLDPACK seems to have issues on bootable packs with multiple procedures. If you encounter problems: use bootable=False when building to force MAKEPACK')
			else:
				put('You have to manually RUN procedure "B:' + name8 + '"')
			put('Press F10, ESC to quit the emulator')
			autoexec += DEVKIT_PATH + '\\ORG2BETA' + CRLF
			
			"""
			# Call ORG2.EXE emulator
			autoexec += DEVKIT_PATH + '\\ORG2' + CRLF
			"""
		
		autoexec += 'GOTO SHUTDOWN' + CRLF
		
		# Error handler in autoexec
		autoexec += ':ERROR' + CRLF
		autoexec += 'ECHO An error has occured! Stopping build.' + CRLF
		autoexec += 'PAUSE' + CRLF
		autoexec += 'GOTO SHUTDOWN' + CRLF
		
		
		# Shutdown epilogue...
		autoexec += ':SHUTDOWN' + CRLF
		autoexec += 'ECHO.' + CRLF
		autoexec += 'CHOICE /C:YN /T:Y,2 /N "Shut down? [Y/N]"' + CRLF
		autoexec += 'IF ERRORLEVEL 2 GOTO NOSHUTDOWN' + CRLF
		autoexec += 'GOTO:DOSHUTDOWN' + CRLF
		
		autoexec += ':DOSHUTDOWN' + CRLF
		autoexec += 'ECHO Shutting down...' + CRLF
		autoexec += 'SMARTDRV /C/X' + CRLF
		autoexec += 'SHUTDOWN S' + CRLF
		
		autoexec += ':NOSHUTDOWN' + CRLF
		autoexec += 'ECHO Not shutting down. Use "SHUTDOWN S" to shut down manually.' + CRLF
		autoexec += 'GOTO:EOF' + CRLF
		autoexec += ':EOF' + CRLF
		
		
		self.touch(os.path.abspath(os.path.join(self.staging_path, 'AUTOEXEC.BAT')), autoexec)
		
		
		put('Compiling using QEMU on MS-DOS 6.22 and PSION Developer Kit...')
		
		### Call QEMU...
		#put('VM_DIR="%s"' % (VM_DIR))
		cmd = os.path.join(qemu_path, 'qemu-system-i386')
		cmd += ' -m 64 -L . -k de'
		cmd += ' -boot c'
		cmd += ' -hda "' + disk_sys + '"'	# C:
		cmd += ' -hdb "' + disk_compiler + '"'	# D:
		cmd += ' -hdc "' + disk_temp + '"'	# E:
		cmd += ' -hdd "fat:rw:/' + os.path.abspath(self.staging_path) + '"'	# F:
		cmd += ' -soundhw pcspk'
		
		
		r = self.command(cmd)
		put('Returned "' + str(r) + '"')
		
		if (self.exists(build_log_file)):
			buildLog = self.type(build_log_file)
			put('Build log: "' + buildLog + '"')
		else:
			put('No build log was created. Oh-oh!')
		
		# Check if successfull
		if (self.exists(self.staging_path + '/' + opk_filename)):
			put('Compilation seems successfull.')
			put('Copying to build directory...')
			self.copy(self.staging_path + '/' + opk_filename, self.output_path + '/' + opk_filename)
		
		else:
			raise HAULBuildError('Build seems to have failed, since there is no output file "{}".'.format(self.staging_path + '/' + opk_filename))
			return False
		
		put('Done.')
		return True
		
