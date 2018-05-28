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
	
	def build(self, inputFilename, sourcePath, stagingPath, outputPath, resources=None, perform_test_run=False):
		
		#CWD = os.getcwd()
		#SKETCHES_DIR = 'Z:\\Data\\_code\\_arduinoWorkspace'
		
		
		put('Starting build...')
		HAULBuilder.build(self, inputFilename, outputPath)
		
		
		put('Cleaning staging path...')
		self.clean(stagingPath)
		
		# stagingPath1 = Emulation of your "sketch" folder. Just blank source, no extras
		stagingPath1 = os.path.realpath(os.path.join(stagingPath, '1'))
		self.clean(stagingPath1)
		#stagingPath2 = Temporary build folder with Arduino-altered source files and includes
		stagingPath2 = os.path.realpath(os.path.join(stagingPath, '2'))
		self.clean(stagingPath2)
		
		put('Copying libraries...')
		
		#@TODO: Use module.imports!
		self.copy('haul/platforms/arduino/lib/hio.c', stagingPath1 + '/hio.c')
		
		#self.mkdir(outputPath + '/sketch')
		#self.copy('haul/platforms/arduino/hio.c', outputPath + '/sketch/hio.c')
		
		
		name = nameByFilename(inputFilename)
		
		cFilename = name + '.c'
		hexFilename1 = cFilename + '.hex'
		hexFilename2 = cFilename + '.with_bootloader.hex'
		hexFilename_final1 = name + '_' + ARDUINO_CPU + '.hex'
		hexFilename_final2 = name + '_' + ARDUINO_CPU + '.with_bootloader.hex'
		
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(sourcePath, inputFilename), SourceReaderClass=HAULReader_py, destFilename=os.path.join(stagingPath1, cFilename), DestWriterClass=HAULWriter_c, dialect=DIALECT_ARDUINO)
		
		if not os.path.isfile(os.path.join(stagingPath1, cFilename)):
			put('Main C file "%s" was not created! Aborting.' % (os.path.join(stagingPath1, cFilename)))
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
		cmd += ' -build-path ' + os.path.realpath(stagingPath2)	#os.path.realpath(outputPath)	#ENV['BUILD_PATH']
		cmd += ' -warnings=none'
		cmd += ' -prefs=build.warn_data_percentage=75'
		#cmd += ' -prefs=runtime.tools.avrdude.path=' + os.path.realpath(ENV['ARDUINO_PATH'] + '/hardware/tools/avr')
		cmd += ' -prefs=runtime.tools.avr-gcc.path=' + os.path.realpath(ARDUINO_DIR + '/hardware/tools/avr')
		#cmd += ' -verbose'
		
		#cmd += ' ' + os.path.realpath(ENV['SRC_PATH'] + '/' + filename)
		#cmd += ' ' + os.path.realpath(outputPath + '/' + cFilename)
		#cmd += ' ' + os.path.realpath(stagingPath + '/' + cFilename)
		cmd += ' ' + os.path.realpath(stagingPath1 + '/' + cFilename)
		
		
		r = self.command(cmd)
		put('Returned "' + str(r) + '"')
		
		
		# Check if successfull
		if (self.exists(stagingPath2 + '/' + hexFilename1)):
			put('Build seems successfull.')
			put('Copying to build directory...')
			self.copy(stagingPath2 + '/' + hexFilename1, outputPath + '/' + hexFilename_final1)
			self.copy(stagingPath2 + '/' + hexFilename2, outputPath + '/' + hexFilename_final2)
		else:
			put('Build seems to have failed, since there is no output file "' + (stagingPath2 + '/' + hexFilename1) + '".')

