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


HAULBUILDER_PALMOS_DIR = os.path.dirname(__file__)
POSE_DIR = os.path.join(HAULBUILDER_PALMOS_DIR, 'vm')

class HAULBuilder_palmos(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, lang='pas', platform='palmos')
	
	def build(self, inputFilename, sourcePath, stagingPath, outputPath, resources=None, perform_test_run=False):
		
		put('Starting build...')
		HAULBuilder.build(self, inputFilename, outputPath)
		
		#perform_test_run = True	# Call output file after compilation?
		stagingPath = os.path.realpath(stagingPath)
		put('Staging to "%s"...' % (stagingPath))
		
		put('Copying libraries...')
		#self.copy('haul/platforms/dos/lib/hio.pas', stagingPath + '/hio.pas')
		
		#@TODO: Use module.imports!
		#libs = ['sys', 'hio']
		libs = ['hio']
		for l in libs:
			self.copy('haul/platforms/palmos/lib/' + l + '.pas', stagingPath + '/' + l + '.pas')
		
		name = nameByFilename(inputFilename)
		pasFilename = name + '.pas'
		exeFilename = name + '.exe'
		
		pasFilenameFull = os.path.join(stagingPath, pasFilename)
		
		put('Translating source...')
		m = self.translate(name=name, sourceFilename=os.path.join(sourcePath, inputFilename), SourceReaderClass=HAULReader_py, destFilename=pasFilenameFull, DestWriterClass=HAULWriter_pas, dialect=DIALECT_PP)
		
		if not os.path.isfile(pasFilenameFull):
			put('Main Pascal file "%s" was not created! Aborting.' % (pasFilenameFull))
			return False
		
		
		#@TODO: Convert file to PDB
		put('Converting pas files to PDBs...')
		sources = []
		for l in libs:
			sources.append(l)
		sources.append(name)
		
		for s in sources:
			pasFilename = stagingPath + '/' + s + '.pas'
			
			vfsFilename = s + '.pas'
			pdbFilename = stagingPath + '/' + vfsFilename + '.pdb'
			
			put('Converting "%s" to "%s"...' % (pasFilename, pdbFilename))
			data = readFile(pasFilename)
			
			pdb = PDBFile()
			pdb.set_vfs(name=vfsFilename, data=data)
			writeFile(pdbFilename, pdb.to_file())
			
		
		# Compile it using PP on POSE Emulator
		
		emuFilename = os.path.join(POSE_DIR, 'Emulator_Bound.exe')
		
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
			pasPdbFilenameAbsolute = os.path.join(stagingPath, pasPdbFilename)
			
			put('Importing "%s" ("%s") into Emulator...' % (pasFilename, pasPdbFilenameAbsolute))
			win.RightClickInput()
			app.PopupMenu.MenuItem('Install Application/Database -> Other').ClickInput()
			
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
		exePrcFilenameAbsolute = os.path.join(stagingPath, exePrcFilename)
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
		self.copy(exePrcFilenameAbsolute, outputPath + '/' + exePrcFilename)
		
		
		if perform_test_run:
			### Test
			put('Testing final binary "%s"...' % (exeFilename))
			time.sleep(0.1)
			win.TypeKeys('%s{ENTER}' % (exeFilename))
			# Running
			put('Running... Close emulator manually when you are done.')
		
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
		
		
