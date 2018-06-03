#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.pas.writer_pas import *



class HAULBuilder_dos(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='dos', lang='pas')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_pas, dialect=DIALECT_TURBO))
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		
		stagingPath = os.path.realpath(self.staging_path)
		
		libsPath = os.path.join(self.data_path, 'platforms', 'dos', 'libs')
		vm_path = os.path.join(self.data_path, 'platforms', 'dos', 'vm')
		qemu_path = os.path.abspath(os.path.join(self.data_path, '../tools/qemu'))	#@FIXME
		
		pasFilename = name[0:8] + '.pas'
		outputFilename = name[0:8] + '.exe'
		pasFilenameFull = os.path.join(stagingPath, pasFilename)
		
		put('Staging to "%s"...' % (stagingPath))
		
		
		put('Preparing path names...')
		for s in self.project.sources:
			s.dest_filename = stagingPath + '/' + s.name[0:8] + '.pas'
		for s in self.project.libs:
			s.dest_filename = stagingPath + '/' + s.name[0:8] + '.pas'
		
		
		put('Copying libraries...')
		for s in self.project.libs:
			self.copy(os.path.join(libsPath, s.name + '.pas'), os.path.join(stagingPath, s.name + '.pas'))
		
		
		put('Translating source to TP...')
		self.translate_project(output_path=stagingPath)
		
		if not os.path.isfile(pasFilenameFull):
			put('Main Pascal file "%s" was not created! Aborting.' % (pasFilenameFull))
			return False
			
		
		
		put('Preparing VM automation...')
		disk_sys = os.path.join(vm_path, 'sys_msdos622.disk')
		disk_compiler = os.path.join(vm_path, 'app_tp70.disk')
		disk_empty = os.path.join(vm_path, 'empty.disk')
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
		for l in self.project.libs:
			l = s.name
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
		
		
		if (self.project.run_test == True):
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
		cmd = os.path.join(qemu_path, 'qemu-system-i386')
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
			self.copy(stagingPath + '/' + outputFilename, self.output_path + '/' + outputFilename)
		else:
			put('Build seems to have failed, since there is no output file "' + (stagingPath + '/' + outputFilename) + '".')
		
