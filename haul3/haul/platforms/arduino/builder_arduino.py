#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.c.writer_c import *

EMULARE_BOARD_TEMPLATE = '''<board>
  <doc-version>0.1</doc-version>
  <components>
    <component>
      <name>ATMega 1</name>
      <dll>components\ATMega.dll</dll>
      <title>ATMega</title>
      <version>1.0.0.0</version>
      <specific>
        <ATMega>
          <Program>Z:\Apps\_emu\ArduinoEmu\emulare_1.9\examples\Communication\ASCIITable.cpp.hex</Program>
          <SerialPort>
          </SerialPort>
        </ATMega>
      </specific>
      <position>
        <x>0</x>
        <y>0</y>
      </position>
    </component>
  </components>
  <wires />
</board>
'''

class HAULBuilder_arduino(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='arduino', lang='cpp')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_c, dialect=DIALECT_ARDUINO))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		#arduino_path = 'Z:\\Apps\\_code\\arduino-1.6.13'
		#arduino_path = 'Z:\\Apps\\_code\\Arduino'
		arduino_path = self.get_path('ARDUINO_PATH', os.path.abspath(os.path.join(self.tools_path, 'platforms', 'arduino', 'arduino')))
		put('Using Arduino in "{}"'.format(arduino_path))
		
		arduino_cpu = 'atmega328'
		
		
		cFilename = name + '.cpp'
		hexFilename1 = cFilename + '.hex'
		hexFilename2 = cFilename + '.with_bootloader.hex'
		hexFilename_final1 = name + '_' + arduino_cpu + '.hex'
		hexFilename_final2 = name + '_' + arduino_cpu + '.with_bootloader.hex'
		
		
		# staging_path_1 = Emulation of your "sketch" folder. Just blank source, no extras
		staging_path_1 = os.path.abspath(os.path.join(self.staging_path, '1'))
		self.clean(staging_path_1)
		#staging_path_2 = Temporary build folder with Arduino-altered source files and includes
		staging_path_2 = os.path.abspath(os.path.join(self.staging_path, '2'))
		self.clean(staging_path_2)
		
		
		put('Copying libraries...')
		libsPath = os.path.join(self.data_path, 'platforms/arduino/libs')
		
		for s in self.project.libs:
			lib_filename_data = libsPath + '/' + s.name + '.h'
			self.copy(lib_filename_data, staging_path_1 + '/' + s.name + '.h')
		
		
		put('Translating sources to C...')
		self.translate_project(output_path=staging_path_1)
		
		if not os.path.isfile(os.path.join(staging_path_1, cFilename)):
			raise HULBuildError('Main C file "{}" was not created!'.format(os.path.join(staging_path_1, cFilename)))
			return False
		
		
		put('Compiling...')
		
		### Use Arduino builder
		cmd = os.path.realpath(arduino_path + '/arduino-builder')
		#cmd += ' -dump-prefs'
		cmd += ' -logger=machine'
		cmd += ' -fqbn=arduino:avr:diecimila:cpu=' + arduino_cpu
		cmd += ' -hardware ' + os.path.realpath(arduino_path + '/hardware')
		#cmd += ' -hardware ' + os.path.realpath('C:\\Users\\HotKey\\AppData\\Local\\Arduino15\\packages')
		#cmd += ' -hardware ' + os.path.realpath(ENV['WORKSPACE_PATH'] + '/hardware')
		cmd += ' -tools ' + os.path.realpath(arduino_path + '/tools-builder')
		cmd += ' -tools ' + os.path.realpath(arduino_path + '/hardware/tools/avr')
		#cmd += ' -tools ' + os.path.realpath('C:\\Users\\HotKey\\AppData\\Local\\Arduino15\\packages')
		cmd += ' -built-in-libraries ' + os.path.realpath(arduino_path + '/libraries')
		#cmd += ' -libraries ' + os.path.realpath(ENV['WORKSPACE_PATH'] + '/libraries')
		cmd += ' -ide-version=10613'
		cmd += ' -build-path ' + os.path.realpath(staging_path_2)	#os.path.realpath(self.output_path)	#ENV['BUILD_PATH']
		cmd += ' -warnings=none'
		cmd += ' -prefs=build.warn_data_percentage=75'
		#cmd += ' -prefs=runtime.tools.avrdude.path=' + os.path.realpath(ENV['ARDUINO_PATH'] + '/hardware/tools/avr')
		cmd += ' -prefs=runtime.tools.avr-gcc.path=' + os.path.realpath(arduino_path + '/hardware/tools/avr')
		#cmd += ' -verbose'
		
		#cmd += ' ' + os.path.realpath(ENV['SRC_PATH'] + '/' + filename)
		#cmd += ' ' + os.path.realpath(self.output_path + '/' + cFilename)
		#cmd += ' ' + os.path.realpath(stagingPath + '/' + cFilename)
		cmd += ' ' + os.path.realpath(staging_path_1 + '/' + cFilename)
		
		
		r = self.command(cmd)
		put('Returned "' + str(r) + '"')
		
		
		# Check if successfull
		if (self.exists(staging_path_2 + '/' + hexFilename1)):
			put('Compilation seems successfull.')
			
			put('Copying to output directory...')
			self.copy(staging_path_2 + '/' + hexFilename1, self.output_path + '/' + hexFilename_final1)
			self.copy(staging_path_2 + '/' + hexFilename2, self.output_path + '/' + hexFilename_final2)
		
		else:
			raise HAULBuildError('Build seems to have failed, since there is no output file "{}".'.format(staging_path_2 + '/' + hexFilename1))
			return False
			
		
		if (self.project.run_test == True):
			# Run Emulare
			emulare_path = self.get_path('EMULARE_PATH', os.path.abspath(os.path.join(self.tools_path, 'platforms', 'arduino', 'emulare')))
			
			
			put('Emulating using Emulare...')
			# Emulare 1.9 does not have command line arguments for loading a file.
			# But it will load the last opened board!
			cmd = os.path.join(emulare_path, 'emulare.exe')
			self.command(cmd)
			
			#@TODO: Upload it using avrdude and virtual com0com port
			
			pass
		
		put('Done.')
		return True
		
