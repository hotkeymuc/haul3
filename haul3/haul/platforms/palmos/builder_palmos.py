#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.pas.writer_pas import *

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
		pose_path = self.get_path('POSE_PATH', os.path.abspath(os.path.join(self.tools_path, 'platforms', 'palmos', 'pose')))
		
		put('Copying libraries...')
		
		pas_filename = name + '.pas'
		exe_filename = name + '.exe'
		
		pas_filename_full = os.path.join(self.staging_path, pas_filename)
		
		
		put('Translating source to PP...')
		self.translate_project(output_path=self.staging_path)
		
		if not os.path.isfile(pas_filename_full):
			raise HULBuildError('Main Pascal file "{}" was not created!'.format(pas_filename_full))
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
			pas_filename = self.staging_path + '/' + s + '.pas'
			
			vfsFilename = s + '.pas'
			pdbFilename = self.staging_path + '/' + vfsFilename + '.pdb'
			
			put('Converting "%s" to "%s"...' % (pas_filename, pdbFilename))
			data = self.type(pas_filename)
			
			pdb = PDBFile()
			pdb.set_vfs(name=vfsFilename, data=data)
			self.touch(pdbFilename, pdb.to_file())
			
		
		# Compile it using PP on POSE Emulator
		
		pose_cmd = os.path.join(pose_path, 'Emulator_Bound.exe')
		
		put('Starting emulator "%s"...' % (pose_cmd))
		app = Application().start(pose_cmd)
		
		win = app.top_window()
		win.DrawOutline()
		
		
		#@TODO: Check if the emulator started up in good state
		#time.sleep(10)
		
		
		### Clean emulator
		put('Cleaning source...')
		for s in sources:
			pas_filename = s + '.pas'
			win.TypeKeys('del{SPACE}%s{ENTER}' % (pas_filename))
		
		put('Cleaning binary...')
		win.TypeKeys('del{SPACE}%s{ENTER}' % (exe_filename))
		win.TypeKeys('{ENTER}')
		
		
		### Install local files
		put('Importing into emulator...')
		for s in sources:
			time.sleep(0.2)
			pas_filename = s + '.pas'
			pas_pdb_filename = pas_filename + '.pdb'
			pas_pdb_filename_full = os.path.abspath(os.path.join(self.staging_path, pas_pdb_filename))
			
			put('Importing "%s" ("%s") into Emulator...' % (pas_filename, pas_pdb_filename_full))
			win.RightClickInput()
			app.PopupMenu.MenuItem('Install Application/Database -> Other').ClickInput()
			
			time.sleep(0.2)
			
			winOpen = app.top_window()
			winOpen.TypeKeys('%s{ENTER}' % (pas_pdb_filename_full))
			
			
		
		time.sleep(0.2)
		
		### Invoke compiler
		pas_filename = name + '.pas'
		exe_filename = name + '.exe'
		put('Compiling "%s" to "%s"...' % (pas_filename, exe_filename))
		
		time.sleep(0.5)
		win.TypeKeys('pp.exe{SPACE}%s{ENTER}' % (pas_filename))
		# Compiling...
		time.sleep(2)
		# OK
		win.TypeKeys('{ENTER}')
		put('Compilation done.')
		
		
		### Exfiltrate
		put('Cleaning host...')
		exe_prc_filename = exe_filename + '.prc'
		exe_prc_filename_full = os.path.abspath(os.path.join(self.staging_path, exe_prc_filename))
		if os.path.isfile(exe_prc_filename_full):
			os.remove(exe_prc_filename_full)
		
		put('Exporting "%s" back to host...' % (exe_filename))
		win.RightClickInput()
		app.PopupMenu.MenuItem('Export Database').ClickInput()
		winList = app.top_window()
		#put(winList)
		#winList.print_control_identifiers()
		list = winList.ListBox
		#put(list.ItemTexts())
		try:
			list.Select(exe_filename, True)
			winList.OK.ClickInput()
		except Exception as e:
			raise HULBuildError('Output file "{}" was not created on emulator!'.format(exe_filename))
			return False
		
		time.sleep(0.1)
		winOpen = app.top_window()
		winOpen.TypeKeys('%s{ENTER}' % (exe_prc_filename_full))
		
		time.sleep(1)
		put('Copying "%s" to output directory...' % (exe_prc_filename))
		self.copy(exe_prc_filename_full, self.output_path + '/' + exe_prc_filename)
		
		
		if (self.project.run_test == True):
			### Test
			put('Testing final binary "%s"...' % (exe_filename))
			time.sleep(0.1)
			win.TypeKeys('%s{ENTER}' % (exe_filename))
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
		
		return True
		
