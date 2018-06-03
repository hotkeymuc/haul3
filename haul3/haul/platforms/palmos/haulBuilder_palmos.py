#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.haulReader_py import *
from haul.langs.pas.haulWriter_pas import *

from pdb import PDBFile


# I am using "pywinauto" to remotely control the emulator. Everything else (RPC) failed horribly for me (non-deterministic crashes)
# To install: pip install -U pywinauto
from pywinauto import Application
import time


class HAULBuilder_palmos(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='palmos', lang='pas')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_pas, dialect=DIALECT_PP))
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		libs_path = os.path.join(self.data_path, 'platforms', 'palmos', 'libs')
		tools_path = os.path.join(self.data_path, '..', 'tools')
		pose_path = os.path.join(tools_path, 'platforms', 'palmos', 'pose')
		
		put('Copying libraries...')
		
		pasFilename = name + '.pas'
		exeFilename = name + '.exe'
		
		pasFilenameFull = os.path.join(self.staging_path, pasFilename)
		
		
		put('Translating source to PP...')
		self.translate_project(output_path=self.staging_path)
		
		if not os.path.isfile(pasFilenameFull):
			put('Main Pascal file "%s" was not created! Aborting.' % (pasFilenameFull))
			return False
		
		
		sources = []
		
		put('Copying libraries...')
		for s in self.project.libs:
			self.copy(os.path.join(libs_path, s.name + '.pas'), os.path.join(self.staging_path, s.name + '.pas'))
			sources.append(s.name)
		
		for s in self.project.sources:
			sources.append(s.name)
		
		#@TODO: Convert file to PDB
		put('Converting pas files to PDBs...')
		
		for s in sources:
			pasFilename = self.staging_path + '/' + s + '.pas'
			
			vfsFilename = s + '.pas'
			pdbFilename = self.staging_path + '/' + vfsFilename + '.pdb'
			
			put('Converting "%s" to "%s"...' % (pasFilename, pdbFilename))
			data = self.type(pasFilename)
			
			pdb = PDBFile()
			pdb.set_vfs(name=vfsFilename, data=data)
			self.touch(pdbFilename, pdb.to_file())
			
		
		# Compile it using PP on POSE Emulator
		
		emuFilename = os.path.join(pose_path, 'Emulator_Bound.exe')
		
		put('Starting emulator "%s"...' % (emuFilename))
		app = Application().start(emuFilename)
		
		win = app.top_window()
		win.DrawOutline()
		
		
		#@TODO: Check if the emulator started up in good state
		#time.sleep(10)
		
		
		### Clean emulator
		put('Cleaning source...')
		for s in sources:
			pasFilename = s + '.pas'
			win.TypeKeys('del{SPACE}%s{ENTER}' % (pasFilename))
		
		put('Cleaning binary...')
		win.TypeKeys('del{SPACE}%s{ENTER}' % (exeFilename))
		win.TypeKeys('{ENTER}')
		
		
		### Install local files
		put('Importing into emulator...')
		for s in sources:
			time.sleep(0.2)
			pasFilename = s + '.pas'
			pasPdbFilename = pasFilename + '.pdb'
			pasPdbFilenameAbsolute = os.path.abspath(os.path.join(self.staging_path, pasPdbFilename))
			
			put('Importing "%s" ("%s") into Emulator...' % (pasFilename, pasPdbFilenameAbsolute))
			win.RightClickInput()
			app.PopupMenu.MenuItem('Install Application/Database -> Other').ClickInput()
			
			time.sleep(0.2)
			
			winOpen = app.top_window()
			winOpen.TypeKeys('%s{ENTER}' % (pasPdbFilenameAbsolute))
			
			
		
		time.sleep(0.2)
		
		### Invoke compiler
		pasFilename = name + '.pas'
		exeFilename = name + '.exe'
		put('Compiling "%s" to "%s"...' % (pasFilename, exeFilename))
		
		time.sleep(0.5)
		win.TypeKeys('pp.exe{SPACE}%s{ENTER}' % (pasFilename))
		# Compiling...
		time.sleep(2)
		# OK
		win.TypeKeys('{ENTER}')
		put('Compilation done.')
		
		
		### Exfiltrate
		put('Cleaning host...')
		exePrcFilename = exeFilename + '.prc'
		exePrcFilenameAbsolute = os.path.abspath(os.path.join(self.staging_path, exePrcFilename))
		if os.path.isfile(exePrcFilenameAbsolute):
			os.remove(exePrcFilenameAbsolute)
		
		put('Exporting "%s" back to host...' % (exeFilename))
		win.RightClickInput()
		app.PopupMenu.MenuItem('Export Database').ClickInput()
		winList = app.top_window()
		#put(winList)
		#winList.print_control_identifiers()
		list = winList.ListBox
		#put(list.ItemTexts())
		try:
			list.Select(exeFilename, True)
			winList.OK.ClickInput()
		except Exception as e:
			put('Output file "' + exeFilename + '" was not created! Aborting...')
			return False
		
		time.sleep(0.1)
		winOpen = app.top_window()
		winOpen.TypeKeys('%s{ENTER}' % (exePrcFilenameAbsolute))
		
		time.sleep(1)
		put('Copying "%s" to output directory...' % (exePrcFilename))
		self.copy(exePrcFilenameAbsolute, self.output_path + '/' + exePrcFilename)
		
		
		if (self.project.run_test == True):
			### Test
			put('Testing final binary "%s"...' % (exeFilename))
			time.sleep(0.1)
			win.TypeKeys('%s{ENTER}' % (exeFilename))
			# Running
			put('Running... Close emulator manually when you are done.')
			
			# RightC
			win.RightClickInput()
			app.PopupMenu.MenuItem('Exit').ClickInput()
			
			# Type No ("Save changes?")
			#win.TypeKeys('n')
		
		else:
			### Exit
			put('Quitting emulator...')
			win.RightClickInput()
			app.PopupMenu.MenuItem('Exit').ClickInput()
			# Do not save
			winPrompt = app.top_window()
			winPrompt.TypeKeys('n')
			
			###
			put('Killing emulator...')
			app.kill()
		
		
