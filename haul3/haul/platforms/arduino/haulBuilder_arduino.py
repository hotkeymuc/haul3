#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.c.haulWriter_c import *



#ARDUINO_DIR = 'Z:\\Apps\\_code\\arduino-1.6.13'
ARDUINO_DIR = 'Z:\\Apps\\_code\\Arduino'
ARDUINO_CPU = 'atmega328'

class HAULBuilder_arduino(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='c', platform='arduino')
	
	def build(self, source_path, source_filename, output_path, staging_path, data_path, resources=None, perform_test_run=False):
		
		HAULBuilder.build(self, source_path=source_path, source_filename=source_filename, output_path=output_path, staging_path=staging_path, data_path=data_path, resources=resources, perform_test_run=perform_test_run)
		
		
		# staging_path_1 = Emulation of your "sketch" folder. Just blank source, no extras
		staging_path_1 = os.path.realpath(os.path.join(staging_path, '1'))
		self.clean(staging_path_1)
		#staging_path_2 = Temporary build folder with Arduino-altered source files and includes
		staging_path_2 = os.path.realpath(os.path.join(staging_path, '2'))
		self.clean(staging_path_2)
		
		put('Copying libraries...')
		libsPath = os.path.join(data_path, 'platforms/arduino/libs')
		
		#@TODO: Use module.imports!
		self.copy(os.path.join(libsPath, 'hio.c'), staging_path_1 + '/hio.c')
		
		#self.mkdir(output_path + '/sketch')
		#self.copy('haul/platforms/arduino/hio.c', output_path + '/sketch/hio.c')
		
		
		name = nameByFilename(source_filename)
		
		cFilename = name + '.c'
		hexFilename1 = cFilename + '.hex'
		hexFilename2 = cFilename + '.with_bootloader.hex'
		hexFilename_final1 = name + '_' + ARDUINO_CPU + '.hex'
		hexFilename_final2 = name + '_' + ARDUINO_CPU + '.with_bootloader.hex'
		
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(source_path, source_filename), SourceReaderClass=HAULReader_py, destFilename=os.path.join(staging_path_1, cFilename), DestWriterClass=HAULWriter_c, dialect=DIALECT_ARDUINO)
		
		if not os.path.isfile(os.path.join(staging_path_1, cFilename)):
			put('Main C file "%s" was not created! Aborting.' % (os.path.join(staging_path_1, cFilename)))
			return False
		
		
		put('Compiling...')
		
		### Use Arduino builder
		cmd = os.path.realpath(ARDUINO_DIR + '/arduino-builder')
		#cmd += ' -dump-prefs'
		cmd += ' -logger=machine'
		cmd += ' -fqbn=arduino:avr:diecimila:cpu=' + ARDUINO_CPU
		cmd += ' -hardware ' + os.path.realpath(ARDUINO_DIR + '/hardware')
		#cmd += ' -hardware ' + os.path.realpath('C:\\Users\\HotKey\\AppData\\Local\\Arduino15\\packages')
		#cmd += ' -hardware ' + os.path.realpath(ENV['WORKSPACE_PATH'] + '/hardware')
		cmd += ' -tools ' + os.path.realpath(ARDUINO_DIR + '/tools-builder')
		cmd += ' -tools ' + os.path.realpath(ARDUINO_DIR + '/hardware/tools/avr')
		#cmd += ' -tools ' + os.path.realpath('C:\\Users\\HotKey\\AppData\\Local\\Arduino15\\packages')
		cmd += ' -built-in-libraries ' + os.path.realpath(ARDUINO_DIR + '/libraries')
		#cmd += ' -libraries ' + os.path.realpath(ENV['WORKSPACE_PATH'] + '/libraries')
		cmd += ' -ide-version=10613'
		cmd += ' -build-path ' + os.path.realpath(staging_path_2)	#os.path.realpath(output_path)	#ENV['BUILD_PATH']
		cmd += ' -warnings=none'
		cmd += ' -prefs=build.warn_data_percentage=75'
		#cmd += ' -prefs=runtime.tools.avrdude.path=' + os.path.realpath(ENV['ARDUINO_PATH'] + '/hardware/tools/avr')
		cmd += ' -prefs=runtime.tools.avr-gcc.path=' + os.path.realpath(ARDUINO_DIR + '/hardware/tools/avr')
		#cmd += ' -verbose'
		
		#cmd += ' ' + os.path.realpath(ENV['SRC_PATH'] + '/' + filename)
		#cmd += ' ' + os.path.realpath(output_path + '/' + cFilename)
		#cmd += ' ' + os.path.realpath(stagingPath + '/' + cFilename)
		cmd += ' ' + os.path.realpath(staging_path_1 + '/' + cFilename)
		
		
		r = self.command(cmd)
		put('Returned "' + str(r) + '"')
		
		
		# Check if successfull
		if (self.exists(staging_path_2 + '/' + hexFilename1)):
			put('Build seems successfull.')
			put('Copying to build directory...')
			self.copy(staging_path_2 + '/' + hexFilename1, output_path + '/' + hexFilename_final1)
			self.copy(staging_path_2 + '/' + hexFilename2, output_path + '/' + hexFilename_final2)
		else:
			put('Build seems to have failed, since there is no output file "' + (staging_path_2 + '/' + hexFilename1) + '".')

