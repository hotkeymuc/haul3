#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
		
		
		data_libs_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'dos', 'libs'))
		vm_path = os.path.abspath(os.path.join(self.data_path, 'platforms', 'dos', 'vm'))
		qemu_path = self.get_path('QEMU_PATH', os.path.abspath(os.path.join(self.tools_path, 'qemu')))
		
		
		pas_filename = name[0:8] + '.pas'
		exe_filename = name[0:8] + '.exe'
		pas_filename_full = os.path.abspath(os.path.join(self.staging_path, pas_filename))
		exe_filename_full = os.path.abspath(os.path.join(self.staging_path, exe_filename))
		
		put('Staging to "%s"...' % (self.staging_path))
		
		
		put('Preparing path names...')
		for s in self.project.sources:
			s.dest_filename = self.staging_path + '/' + s.name[0:8] + '.pas'
		for s in self.project.libs:
			s.dest_filename = self.staging_path + '/' + s.name[0:8] + '.pas'
		
		
		put('Copying libraries...')
		for s in self.project.libs:
			self.copy(os.path.join(data_libs_path, s.name + '.pas'), os.path.join(self.staging_path, s.name + '.pas'))
		
		
		put('Translating source to TP...')
		self.translate_project(output_path=self.staging_path)
		
		if not os.path.isfile(pas_filename_full):
			raise HAULBuildError('Main Pascal file "{}" was not created!'.format(pas_filename_full))
			return False
			
		
		put('Preparing VM automation...')
		disk_sys = os.path.join(vm_path, 'sys_msdos622.disk')
		disk_compiler = os.path.join(vm_path, 'app_tp70.disk')
		disk_empty = os.path.join(vm_path, 'empty.disk')
		disk_temp = os.path.join(self.staging_path, 'tmp.disk')
		
		# Create/clear temp scratch disk
		self.copy(disk_empty, disk_temp)
		build_log_filename = os.path.abspath(os.path.join(self.staging_path, 'build.log'))
		self.rm_if_exists(build_log_filename)
		self.rm_if_exists(os.path.abspath(os.path.join(self.staging_path, exe_filename)))
		
		
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
		DOS_IN_FILE = DOS_TEMP_DIR + '\\' + pas_filename
		DOS_OUT_FILE = DOS_TEMP_DIR + '\\' + exe_filename
		
		
		autoexec += 'ECHO Build log >' + DOS_LOG_FILE + CRLF
		autoexec += DOS_COMPILER_DRIVE + ':' + CRLF
		autoexec += 'CD ' + DOS_COMPILER_DIR + CRLF
		
		# Compile all files
		pas_files = []
		for l in self.project.libs:
			l = s.name
			autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + l + '.pas ' + DOS_TEMP_DIR + CRLF
			pas_files.append(DOS_TEMP_DIR + '\\' + l + '.pas')
		autoexec += 'COPY ' + DOS_STAGING_DIR + '\\' + pas_filename + ' ' + DOS_TEMP_DIR + CRLF
		pas_files.append(DOS_TEMP_DIR + '\\' + pas_filename)
		
		
		autoexec += 'ECHO ----------------------------------------' + CRLF
		for p in pas_files:
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
		
		
		self.touch(os.path.join(self.staging_path, 'AUTOEXEC.BAT'), autoexec)
		
		
		put('Compiling using QEMU on MS-DOS 6.22 and Turbo Pascal 7.0...')
		
		### Call QEMU...
		cmd = os.path.join(qemu_path, 'qemu-system-i386')
		cmd += ' -m 64 -L . -k de'
		cmd += ' -boot c'
		cmd += ' -hda "' + disk_sys + '"'	# C:
		cmd += ' -hdb "' + disk_compiler + '"'	# D:
		cmd += ' -hdc "' + disk_temp + '"'	# E:
		cmd += ' -hdd "fat:rw:/' + os.path.abspath(self.staging_path) + '"'	# F:
		cmd += ' -soundhw pcspk'
		#cmd += ' ' + os.path.realpath(outputPath + '/' + cFilename)
		#cmd += ' ' + os.path.realpath(self.staging_path + '/' + cFilename)
		
		
		r = self.command(cmd)
		put('Returned "' + str(r) + '"')
		
		if (self.exists(build_log_filename)):
			build_log_text = self.type(build_log_filename)
			put('Build log: "' + build_log_text + '"')
		else:
			put('No build log was created! Uh-oh!')
		
		# Check if successfull
		if (self.exists(exe_filename_full)):
			put('Compilation seems successfull.')
			
			put('Copying to output directory...')
			self.copy(exe_filename_full, self.output_path + '/' + exe_filename)
		else:
			raise HAULBuildError('Build seems to have failed, since there is no output file "{}".'.format(exe_filename_full))
			return False
		
		return True
		
