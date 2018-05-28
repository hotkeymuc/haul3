#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.pas.haulWriter_pas import *



#QEMU_DIR = 'Z:\\Apps\\_emu\\qemu'
HAULBUILDER_DOS_DIR = os.path.dirname(__file__)
VM_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'vm')
QEMU_DIR = os.path.join(HAULBUILDER_DOS_DIR, 'qemu')

class HAULBuilder_dos(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='pas', platform='dos')
	
	def build(self, inputFilename, sourcePath, stagingPath, outputPath, resources=None, perform_test_run=False):
		
		put('Starting build...')
		HAULBuilder.build(self, inputFilename, outputPath)
		
		name = nameByFilename(inputFilename)
		stagingPath = os.path.realpath(stagingPath)
		
		pasFilename = name[0:8] + '.pas'
		outputFilename = name[0:8] + '.exe'
		pasFilenameFull = os.path.join(stagingPath, pasFilename)
		
		put('Staging to "%s"...' % (stagingPath))
		
		put('Cleaning staging path...')
		self.clean(stagingPath)
		
		put('Copying libraries...')
		#self.copy('haul/platforms/dos/lib/hio.pas', stagingPath + '/hio.pas')
		
		#@TODO: Use module.imports!
		libs = ['sys', 'hio']
		for l in libs:
			self.copy('haul/platforms/dos/lib/' + l + '.pas', stagingPath + '/' + l + '.pas')
		
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(sourcePath, inputFilename), SourceReaderClass=HAULReader_py, destFilename=pasFilenameFull, DestWriterClass=HAULWriter_pas, dialect=DIALECT_TURBO)
		
		if not os.path.isfile(pasFilenameFull):
			put('Main Pascal file "%s" was not created! Aborting.' % (pasFilenameFull))
			return False
			
		
		
		put('Preparing VM automation...')
		disk_sys = os.path.join(VM_DIR, 'sys_msdos622.disk')
		disk_compiler = os.path.join(VM_DIR, 'app_tp70.disk')
		disk_empty = os.path.join(VM_DIR, 'empty.disk')
		disk_temp = os.path.join(stagingPath, 'tmp.disk')
		
		# Create/clear temp scratch disk
		self.copy(disk_empty, disk_temp)
		buildlogFile = os.path.join(stagingPath, 'build.log')
		#self.touch(buildlogFile, '# Build log')
		self.rm_if_exists(buildlogFile)
		self.rm_if_exists(os.path.join(stagingPath, outputFilename))
		
		
		DOS_SYS_DIR = 'C:'
		DOS_COMPILER_DRIVE = 'D'
		DOS_COMPILER_DIR = DOS_COMPILER_DRIVE + ':'
		DOS_STAGING_DIR = 'F:'
		DOS_TEMP_DIR = 'E:'
		DOS_LOG_FILE = DOS_TEMP_DIR + '\\build.log'	#DOS_LOG_FILE = DOS_STAGING_DIR + '\\build.log'
		
		TP_PATH = DOS_COMPILER_DIR + '\\TP70'
		TP_BIN_PATH = TP_PATH + '\\BIN'
		TP_UNITS_PATH = TP_PATH + '\\UNITS'
		TP_ARGS = '-DSomeSymbol'
		
		CRLF = '\r\n'
		
		# Startup prolog...
		autoexec = 'ECHO.' + CRLF
		
		autoexec += 'SMARTDRV /C /X' + CRLF
		
		autoexec = 'CLS' + CRLF
		autoexec += 'SET TEMP=E:' + CRLF
		autoexec += 'ECHO haulBuilder_dos' + CRLF
		autoexec += 'ECHO.' + CRLF
		
		# Compile...
		autoexec += ':COMPILE' + CRLF
		autoexec += 'ECHO ----------------------------------------' + CRLF
		#autoexec += 'ECHO Staging dir:' + CRLF
		#autoexec += 'DIR ' + DOS_STAGING_DIR + ' /B' + CRLF
		
		autoexec += 'ECHO Staging...' + CRLF
		#autoexec += 'COPY ' + DOS_STAGING_DIR + '\*.pas ' + DOS_TEMP_DIR + CRLF
		DOS_IN_FILE = DOS_TEMP_DIR + '\\' + pasFilename
		DOS_OUT_FILE = DOS_TEMP_DIR + '\\' + outputFilename
		
		
		autoexec += 'ECHO Build log >' + DOS_LOG_FILE + CRLF
		autoexec += DOS_COMPILER_DRIVE + ':' + CRLF
		autoexec += 'CD ' + DOS_COMPILER_DIR + CRLF
		
		# Compile all files
		pasFiles = []
		for l in libs:
			autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + l + '.pas ' + DOS_TEMP_DIR + CRLF
			pasFiles.append(DOS_TEMP_DIR + '\\' + l + '.pas')
		autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + pasFilename + ' ' + DOS_TEMP_DIR + CRLF
		pasFiles.append(DOS_TEMP_DIR + '\\' + pasFilename)
		
		
		autoexec += 'ECHO ----------------------------------------' + CRLF
		for p in pasFiles:
			TP_CMD = TP_BIN_PATH + '\\TPC ' + p + ' -U' + TP_UNITS_PATH + ' -U' + DOS_TEMP_DIR + ' ' + TP_ARGS
			autoexec += 'ECHO Executing "' + TP_CMD + '"...' + CRLF
			autoexec += 'ECHO ' + TP_CMD + ' >>' + DOS_LOG_FILE + CRLF
			autoexec += TP_CMD + ' >>' + DOS_LOG_FILE + CRLF
		
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
			
			#autoexec += DOS_OUT_FILE + ' >>' + DOS_LOG_FILE + CRLF
			
			autoexec += DOS_OUT_FILE + CRLF
			
			autoexec += 'ECHO ----------------------------------------' + CRLF
			autoexec += 'PAUSE' + CRLF
			
			autoexec += 'ECHO ----------------------------------------' + CRLF
		
		
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
		
		
		self.touch(os.path.join(stagingPath, 'AUTOEXEC.BAT'), autoexec)
		
		
		put('Compiling using QEMU on MS-DOS 6.22 and Turbo Pascal 7.0...')
		
		### Call QEMU...
		#put('VM_DIR="%s"' % (VM_DIR))
		cmd = os.path.join(QEMU_DIR, 'qemu-system-i386')
		cmd += ' -m 64 -L . -k de'
		cmd += ' -boot c'
		cmd += ' -hda "' + disk_sys + '"'	# C:
		cmd += ' -hdb "' + disk_compiler + '"'	# D:
		cmd += ' -hdc "' + disk_temp + '"'	# E:
		cmd += ' -hdd "fat:rw:/' + stagingPath + '"'	# F:
		cmd += ' -soundhw pcspk'
		#cmd += ' ' + os.path.realpath(outputPath + '/' + cFilename)
		#cmd += ' ' + os.path.realpath(stagingPath + '/' + cFilename)
		
		
		r = self.command(cmd)
		put('Returned "' + str(r) + '"')
		
		buildLog = self.type(buildlogFile)
		put('Build log: "' + buildLog + '"')
		
		# Check if successfull
		if (self.exists(stagingPath + '/' + outputFilename)):
			put('Build seems successfull.')
			put('Copying to build directory...')
			self.copy(stagingPath + '/' + outputFilename, outputPath + '/' + outputFilename)
		else:
			put('Build seems to have failed, since there is no output file "' + (stagingPath + '/' + outputFilename) + '".')
		
