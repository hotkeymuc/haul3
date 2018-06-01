#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Builder for PSION (CM/XP)

* translates to OPL (using Basic language)
* compiles in VM using PSION DevKit for DOS
* emulates using ORG2BETA for DOS
"""

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.opl.haulWriter_opl import *




class HAULBuilder_psion(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='opl', platform='psion')
	
	def build(self, source_path, source_filename, output_path, staging_path, data_path, resources=None, perform_test_run=False):
		
		HAULBuilder.build(self, source_path=source_path, source_filename=source_filename, output_path=output_path, staging_path=staging_path, data_path=data_path, resources=resources, perform_test_run=perform_test_run)
		
		libs_path = os.path.join(data_path, 'platforms', 'psion', 'libs')
		vm_path = os.path.join(data_path, 'platforms', 'psion', 'vm')
		tools_path = os.path.join(data_path, '..', 'tools')
		qemu_path = os.path.join(tools_path, 'qemu')
		
		
		
		#@FIXME: Bootable packs can be created using BLDPACK. But for some reason it then does not include all binaries!
		#@FIXME: When disabling bootable, I use MAKEPACK which seems to handle multiple files easily, but can not handle BIN files needed for bootable.
		bootable = not True	# Make it auto-run by including a BOOT.BIN and renaming the main proc BOOT
		lcd_lines = 2	# 2 for CM/XP, 4 for LZ etc.
		
		
		name = name_by_filename(source_filename)
		staging_path = os.path.realpath(staging_path)
		
		name8 = name[0:8].upper()
		oplFilename = name8 + '.OPL'
		#ob3Filename = name8 + '.ob3'
		outputFilename = name8 + '.OPK'
		oplFilenameFull = os.path.join(staging_path, oplFilename)
		
		put('Staging to "%s"...' % (staging_path))
		
		
		put('Cleaning staging path...')
		self.clean(staging_path)
		
		
		put('Copying libraries...')
		#self.copy('haul/platforms/dos/lib/hio.pas', staging_path + '/hio.pas')
		
		libs = []
		"""
		#@TODO: Use module.imports!
		libs = ['sys', 'hio']
		for l in libs:
			self.copy('haul/platforms/psion/lib/' + l + '.opl', staging_path + '/' + l + '.opl')
		"""
		
		put('Translating source...')
		m = self.translate(name=name, source_filename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, dest_filename=oplFilenameFull, DestWriterClass=HAULWriter_opl, dialect=DIALECT_OPL3)
		
		
		### Split module into separate files
		# OPL3 (XP/CM) does not support multiple procs in one file.
		for f in m.funcs:
			#put(str(f.id.name) + ':	' + str(f))
			# Select module name
			funcName = f.id.name
			funcName8 = funcName[0:8].upper()
			#@TODO: Ensure that this name is unique! Or just give random name (lame)
			
			funcFilename = funcName8 + '.OPL'
			funcFilenameFull = os.path.join(staging_path, funcFilename)
			
			streamOut = StringWriter()
			writer = HAULWriter_opl(streamOut, dialect=DIALECT_OPL3)
			m = writer.writeFunc(f)	# That's where the magic happens!
			
			put('Writing function "%s" to "%s"...' % (f.id.name, funcFilenameFull))
			writeFile(funcFilenameFull, streamOut.r)
			self.copy(funcFilenameFull, funcFilenameFull+'.bak')	# Backup (compiler deletes it?!)
			
			# Add to compile files
			libs.append(funcName8)
		
		
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
		self.touch(oplFilenameFull, oplDummySource)
		"""
		
		# Check if translation worked
		if not os.path.isfile(oplFilenameFull):
			put('Main OPL file "%s" was not created! Aborting.' % (oplFilenameFull))
			return False
			
		
		self.copy(oplFilenameFull, oplFilenameFull+'.bak')	# Backup main file for testing (source file gets deleted somehow...)
		
		
		put('Preparing VM automation...')
		disk_sys = os.path.join(vm_path, 'sys_msdos622.disk')
		disk_compiler = os.path.join(vm_path, 'app_devkit.disk')
		disk_empty = os.path.join(vm_path, 'empty.disk')
		disk_temp = os.path.join(staging_path, 'tmp.disk')
		
		# Create/clear temp scratch disk
		self.copy(disk_empty, disk_temp)
		buildlogFile = os.path.join(staging_path, 'build.log')
		#self.touch(buildlogFile, '# Build log')
		self.rm_if_exists(buildlogFile)
		self.rm_if_exists(os.path.join(staging_path, outputFilename))
		
		
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
		DOS_IN_FILE = DOS_TEMP_DIR + '\\' + oplFilename
		DOS_OUT_FILE = DOS_TEMP_DIR + '\\' + outputFilename
		
		
		autoexec += 'ECHO Build log >' + DOS_LOG_FILE + CRLF
		
		autoexec += DOS_COMPILER_DRIVE + ':' + CRLF
		autoexec += 'CD ' + DEVKIT_PATH + CRLF
		
		autoexec += DOS_TEMP_DRIVE + ':' + CRLF
		autoexec += 'CD ' + DOS_TEMP_DIR + CRLF
		
		
		### List all source files
		#oplFiles = []
		sourceListFilename = DOS_TEMP_DIR + '\\' + name8 + '.lst'
		
		
		autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + oplFilename + ' ' + DOS_TEMP_DIR + CRLF
		#oplFiles.append(DOS_TEMP_DIR + '\\' + oplFilename)
		autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\' + oplFilename + '>' + sourceListFilename + CRLF
		
		for l in libs:
			autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + l + '.OPL ' + DOS_TEMP_DIR + CRLF
			#oplFiles.append(DOS_TEMP_DIR + '\\' + l + '.OPL')
			autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\' + l + '.OPL>>' + sourceListFilename + CRLF
		
		if bootable:
			# Add BOOT procedure that calls the main file
			autoexec += 'ECHO BOOT:>' + DOS_TEMP_DIR + '\\BOOT.OPL' + CRLF
			autoexec += 'ECHO ' + name8 + ':>>' + DOS_TEMP_DIR + '\\BOOT.OPL' + CRLF
			autoexec += 'ECHO GET>>' + DOS_TEMP_DIR + '\\BOOT.OPL' + CRLF
			
			#oplFiles.append(DOS_TEMP_DIR + '\\BOOT.OPL')
			autoexec += 'ECHO ' + DOS_TEMP_DIR + '\\BOOT.OPL>>' + sourceListFilename + CRLF
		
		### Compile
		OPLTRAN_CMD = DEVKIT_PATH + '\\OPLTRAN @' + sourceListFilename
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
		bldName = name8
		bldFilename = bldName+'.bld'
		
		# Header line
		pakSize = 16	# in kB, either 8 or 16
		#l = '%s %d NOCOPY NOWRITE' % (bldName, pakSize)
		l = '%s %d' % (bldName, pakSize)
		autoexec += 'ECHO ' + l + '>' + bldFilename + CRLF
		
		
		if bootable:
			# Add boot binary to pak
			autoexec += 'COPY ' + DEVKIT_PATH + '\\BOOT.BIN' + ' ' + DOS_TEMP_DIR + CRLF
			l = 'BOOT BIN'
			#l += '  !Boot file'
			autoexec += 'ECHO ' + l + '>>' + bldFilename + CRLF
		
		
		# Lib files preceed the main file
		for l in libs:
			#while len(l) < 8: l += ' '
			l += ' OB3'
			#l = l + ' OB3 ' + l
			#@FIXME: They must be renamed according to their returnType, e.g. FOO%
			#l += ' ' + funcName8 + typeIndicator
			#l += ' ' + l.upper() + '  !Function/Lib'
			#l += '  !Function/Lib'
			autoexec += 'ECHO ' + l + '>>' + bldFilename + CRLF
		
		
		# main OB3 file
		l = name8
		#while len(l) < 8: l += ' '
		l += ' OB3'
		#l += '  !Main module'
		#if bootable: l += ' BOOT  !Boot file'	# Rename it "BOOT" to be called by BOOT.BIN
		autoexec += 'ECHO ' + l + '>>' + bldFilename + CRLF
		
		
		if bootable:
			l = 'BOOT OB3'
			#l += '  !Boot file'
			#l = 'BOOT OPL  !Boot file'	#@FIXME: This lets BLDPACK crash/hang
			autoexec += 'ECHO ' + l + '>>' + bldFilename + CRLF
		
		# Empty line
		#autoexec += 'ECHO>>' + bldFilename + CRLF
		
		
		### Build pack
		if bootable:
			# Using BLDPACK
			BLD_CMD = DEVKIT_PATH + '\\BLDPACK @' + bldName + ' -map'
		else:
			# Using MAKEPACK (does not support BIN files, but is good)
			BLD_CMD = DEVKIT_PATH + '\\MAKEPACK ' + bldFilename
		
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
		
		
		if perform_test_run:
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
		
		
		self.touch(os.path.join(staging_path, 'AUTOEXEC.BAT'), autoexec)
		
		
		put('Compiling using QEMU on MS-DOS 6.22 and PSION Developer Kit...')
		
		### Call QEMU...
		#put('VM_DIR="%s"' % (VM_DIR))
		cmd = os.path.join(qemu_path, 'qemu-system-i386')
		cmd += ' -m 64 -L . -k de'
		cmd += ' -boot c'
		cmd += ' -hda "' + disk_sys + '"'	# C:
		cmd += ' -hdb "' + disk_compiler + '"'	# D:
		cmd += ' -hdc "' + disk_temp + '"'	# E:
		cmd += ' -hdd "fat:rw:/' + staging_path + '"'	# F:
		cmd += ' -soundhw pcspk'
		#cmd += ' ' + os.path.realpath(output_path + '/' + cFilename)
		#cmd += ' ' + os.path.realpath(staging_path + '/' + cFilename)
		
		
		r = self.command(cmd)
		put('Returned "' + str(r) + '"')
		
		if (self.exists(buildlogFile)):
			buildLog = self.type(buildlogFile)
			put('Build log: "' + buildLog + '"')
		else:
			put('No build log was created. Oh-oh!')
		
		
		# Check if successfull
		if (self.exists(staging_path + '/' + outputFilename)):
			put('Build seems successfull.')
			put('Copying to build directory...')
			self.copy(staging_path + '/' + outputFilename, output_path + '/' + outputFilename)
		else:
			put('Build seems to have failed, since there is no output file "' + (staging_path + '/' + outputFilename) + '".')
		
