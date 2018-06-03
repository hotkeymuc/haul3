#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from haul.haul import *
from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.java.writer_java import *

import time	# For waiting in between emu polls


def put(txt):
	print('HAULBuilder_android:\t' + str(txt))


HAULBUILDER_ANDROID_DIR = os.path.dirname(__file__)
JRE_DIR = os.path.abspath('Z:/Apps/_code/AndroidStudio/jre')
ANDROID_SDK_DIR = os.path.abspath('Z:/Data/_code/_sdk/adt-bundle-windows-x86-20130522/sdk')
AVD_NAME = 'Nexus_5X_API_25_x86'	# Which AVD device to use for emulator testing

JAVA_CMD = os.path.abspath(os.path.join(JRE_DIR, 'bin', 'java'))
JAVAC_CMD = os.path.abspath(os.path.join(JRE_DIR, 'bin', 'javac'))
KEYTOOL_CMD = os.path.abspath(os.path.join(JRE_DIR, 'bin', 'keytool'))
JARSIGNER_CMD = os.path.abspath(os.path.join(JRE_DIR, 'bin', 'jarsigner'))
JAVA_RUNTIME_JAR = os.path.abspath(os.path.join(JRE_DIR, 'lib', 'rt.jar'))

ANDROID_ADB_CMD = os.path.abspath(os.path.join(ANDROID_SDK_DIR, 'platform-tools', 'adb'))
ANDROID_JAR = os.path.abspath(os.path.join(ANDROID_SDK_DIR, 'platforms', 'android-25', 'android.jar'))
ANDROID_BUILD_TOOLS_DIR = os.path.abspath(os.path.join(ANDROID_SDK_DIR, 'build-tools', '25.0.0'))
ANDROID_AAPT_CMD = os.path.abspath(os.path.join(ANDROID_BUILD_TOOLS_DIR, 'aapt'))
ANDROID_ZIPALIGN_CMD = os.path.abspath(os.path.join(ANDROID_BUILD_TOOLS_DIR, 'zipalign'))
ANDROID_DEX_JAR = os.path.abspath(os.path.join(ANDROID_BUILD_TOOLS_DIR, 'lib', 'dx.jar'))
EMU_CMD = os.path.abspath(os.path.join(ANDROID_SDK_DIR, 'emulator', 'emulator'))

class HAULBuilder_android(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='android', lang='java')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_java))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		#@TODO: MAke package name customizable!
		
		appNamespace = 'wtf.haul'
		appId = appNamespace + '.' + name
		appVersion = '0.0.1'
		appActivityId = 'wtf.haul.HaulActivity'	#appId + '.MainActivity'
		
		dataLibsPath = os.path.join(self.data_path, 'platforms', 'android', 'libs')
		dataResPath = os.path.join(self.data_path, 'platforms', 'android', 'res')
		
		resPath = os.path.join(self.staging_path, 'res')
		srcPath = os.path.join(self.staging_path, 'src')
		classPath = os.path.join(self.staging_path, 'build')
		
		
		#javaFilename = name.capitalize() + '.java'
		javaFilename = name + '.java'
		#classFilename = name.capitalize() + '.class'
		classFilename = name + '.class'
		packageSrcPath = os.path.join(srcPath, 'wtf', 'haul')
		packageClassPath = os.path.join(classPath, 'wtf', 'haul')
		
		
		javaFilenameFull = os.path.join(packageSrcPath, javaFilename)
		classFilenameFull = os.path.join(packageClassPath, classFilename)
		haulInfoFilename = os.path.join(packageSrcPath, 'HaulInfo.java')
		haulInfoClassFilename = os.path.join(packageClassPath, 'HaulInfo.class')
		
		manifestFilename = os.path.join(self.staging_path, 'AndroidManifest.xml')
		dexFilename = os.path.join(self.staging_path, 'classes.dex')
		keystoreFilename = os.path.join(self.staging_path, 'appkey.keystore')
		keystoresource_filename = os.path.join(self.staging_path, 'appkey.keystore.input')
		
		apkFilenameRaw = os.path.join(self.staging_path,  appId + '_' + appVersion + '_raw.apk')
		apkFilenameSigned = os.path.join(self.staging_path,  appId + '_' + appVersion + '_signed.apk')
		apkFilenameAligned = os.path.join(self.staging_path,  appId + '_' + appVersion + '_aligned.apk')
		#apkFilenameFinal = os.path.join(output_path,  appId + '_' + appVersion + '.apk')
		apkFilenameFinal = os.path.join(self.output_path,  name + '.apk')
		
		
		put('Cleaning staging paths...')
		self.clean(srcPath)
		self.clean(classPath)
		self.mkdir(os.path.join(srcPath, 'wtf'))
		self.mkdir(os.path.join(srcPath, 'wtf', 'haul'))
		
		
		
		put('Preparing path names...')
		for s in self.project.sources:
			s.dest_filename = packageSrcPath + '/' + s.name + '.java'
		
		put('Translating sources to Java...')
		self.translate_project(output_path=packageSrcPath)
		
		if not os.path.isfile(javaFilenameFull):
			put('Main Java file "%s" was not created! Aborting.' % (javaFilenameFull))
			return False
		
		
		put('Staging Android app...')
		
		
		put('Copying libraries...')
		srcFiles = []
		for s in self.project.libs:
			lib_filename_data = dataLibsPath + '/' + s.name + '.java'
			f = os.path.join(srcPath, 'wtf', 'haul', s.name + '.java')
			self.copy(lib_filename_data, f)
			srcFiles.append(f)
		
		srcFiles.append(javaFilenameFull)
		
		
		put('Creating haulInfo...')
		haulInfo = '''package wtf.haul;

//import %s;

public class HaulInfo {
	public static final %s MainClass = new %s();
}
''' % (appId, name, name)
# % (appId, name.capitalize(), name.capitalize())
		self.touch(haulInfoFilename, haulInfo)
		srcFiles.append(haulInfoFilename)
		
		if not os.path.isfile(haulInfoFilename):
			put('haulInfo file "%s" was not created! Aborting.' % (haulInfoFilename))
			return False
		
		
		
		put('Copying activities...')
		f = os.path.join(srcPath, 'wtf', 'haul', 'HaulActivity.java')
		self.copy(os.path.join(dataResPath, 'HaulActivity.java'), f)
		srcFiles.append(f)
		
		
		
		put('Preparing resources..')
		self.clean(resPath)
		
		self.mkdir(os.path.join(resPath, 'drawable'))
		self.copy(os.path.join(dataResPath, 'icon_64x64.png'), os.path.join(resPath, 'drawable', 'icon.png'))
		
		self.mkdir(os.path.join(resPath, 'values'))
		stringsXml = '''<resources>
    <string name="app_name">%s</string>
</resources>''' % (name)
		self.touch(os.path.join(resPath, 'values', 'strings.xml'), stringsXml)
		
		
		
		put('Compiling to Java Class...')
		# http://geosoft.no/development/android.html
		cmd = JAVAC_CMD
		#cmd += ' -verbose'
		cmd += ' -classpath ".";"%s";"%s";"%s"' % (srcPath, classPath, ANDROID_JAR)
		cmd += ' -bootclasspath "%s"' % (JAVA_RUNTIME_JAR)
		cmd += ' -sourcepath "%s"' % (srcPath)	#(staging_path)
		cmd += ' -source 1.7'	# Must target 1.7 or below?! Or else "Unsupported class file version 52.0"
		cmd += ' -target 1.7'	# Must target 1.7 or below?! Or else "Unsupported class file version 52.0"
		cmd += ' -d "%s"' % (classPath)
		#cmd += ' "%s"' % (os.path.join(srcPath, '*'))
		cmd += ' %s' % (' '.join(srcFiles))
		#cmd += ' "%s"' % (os.path.join(self.staging_path, '*.java'))
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(classFilenameFull):
			put(r)
			put('Main class file "%s" was not created! Aborting.' % (classFilenameFull))
			return False
		
		if not os.path.isfile(haulInfoClassFilename):
			put(r)
			put('HAUL info class file "%s" was not created! Aborting.' % (haulInfoClassFilename))
			return False
		
		
		
		put('Compiling to DEX...')
		cmd = JAVA_CMD + ' -jar "%s"' % (ANDROID_DEX_JAR)
		#cmd += 'com.android.dex.Dex'
		cmd += ' --dex'
		#cmd += ' --verbose'
		cmd += ' --output="%s"' % (dexFilename)
		cmd += ' "%s"' % (classPath)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(dexFilename):
			put(r)
			put('DEX classes file "%s" was not created! Aborting.' % (dexFilename))
			return False
		
		
		
		put('Creating manifest...')
		m = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Created by HAUL Builder for Android -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
	package="%s"
	android:versionCode="1"
	android:versionName="%s">
	<uses-sdk
		android:minSdkVersion="8"
		android:targetSdkVersion="17" />
	<application
		android:allowBackup="true"
		android:icon="@drawable/icon"
		android:label="%s">
		<activity
			android:name="%s"
			android:label="%s"
			android:exported="true">
		</activity>
	</application>
</manifest>
''' % (appId, appVersion, name, appActivityId, name)
		# "@string/app_name"
		self.touch(manifestFilename, m)
		
		if not os.path.isfile(manifestFilename):
			put('Manifest file "%s" was not created! Aborting.' % (manifestFilename))
			return False
		
		
		
		put('Packaging to APK...')
		cmd =  ANDROID_AAPT_CMD
		cmd += ' package'
		cmd += ' -v'
		cmd += ' -f'
		#cmd += ' -M "%s"' % (manifestFilename)	# Only specify if it is not the root one
		cmd += ' -S "%s"' % (resPath)
		cmd += ' -I "%s"' % (ANDROID_JAR)
		cmd += ' -F "%s"' % (apkFilenameRaw)
		cmd += ' "%s"' % (self.staging_path)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(apkFilenameRaw):
			put(r)
			put('APK file "%s" was not created! Aborting.' % (apkFilenameRaw))
			return False
		
		
		
		put('Generating keystore "%s"...' % (keystoreFilename))
		keystorePassword = '123456'	#'haul_123456_keystore'
		keyFullName = 'HAUL Builder'
		keyOrgUnitName = 'HAUL'
		keyOrgName = 'HotKey'
		keyCityName = 'WTF'
		keyStateName = 'WTF'
		keyCountry = 'de'
		keyAffirmative = 'ja'	# yes	#@FIXME: This depends on the language of the JRE keytool... Argh!
		keyName = 'haul_key_' + name
		keyPassword = '123456'	#'654321haul_key'
		ENTER = '\n'
		
		keystoreInput = keystorePassword + ENTER
		keystoreInput += keystorePassword + ENTER
		keystoreInput += keyFullName + ENTER
		keystoreInput += keyOrgUnitName + ENTER
		keystoreInput += keyOrgName + ENTER
		keystoreInput += keyCityName + ENTER
		keystoreInput += keyStateName + ENTER
		keystoreInput += keyCountry + ENTER
		keystoreInput += keyAffirmative + ENTER
		keystoreInput += keyPassword + ENTER
		keystoreInput += ENTER
		self.touch(keystoresource_filename, keystoreInput)
		
		cmd = KEYTOOL_CMD
		cmd += ' -genkey '
		cmd += ' -v'
		cmd += ' -keystore "%s"' % (keystoreFilename)
		cmd += ' -alias %s' % (keyName)
		cmd += ' -keyalg RSA'
		cmd += ' -keysize 2048'
		cmd += ' -validity 10000'
		cmd += ' <' + keystoresource_filename
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(keystoreFilename):
			put(r)
			put('Keystore file "%s" was not created! Aborting.' % (keystoreFilename))
			return False
		
		
		
		put('Signing APK file...')
		
		cmd = JARSIGNER_CMD
		cmd += ' -verbose'
		cmd += ' -keystore "%s"' % (keystoreFilename)
		cmd += ' -storepass %s' % (keystorePassword)
		cmd += ' -keypass %s' % (keyPassword)
		cmd += ' -signedjar "%s"' % (apkFilenameSigned)
		cmd += ' "%s"' % (apkFilenameRaw)
		cmd += ' %s' % (keyName)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(apkFilenameSigned):
			put(r)
			put('Signed APK file "%s" was not created! Aborting.' % (apkFilenameSigned))
			return False
		
		
		
		put('Aligning APK file...')
		cmd = ANDROID_ZIPALIGN_CMD
		cmd += ' -v 4'
		cmd += ' "%s"' % (apkFilenameSigned)
		cmd += ' "%s"' % (apkFilenameAligned)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(apkFilenameAligned):
			put(r)
			put('Aligned APK file "%s" was not created! Aborting.' % (apkFilenameAligned))
			return False
		
		
		put('Copying file to output directory "%s"...' % (apkFilenameFinal))
		self.copy(apkFilenameAligned, apkFilenameFinal)
		
		
		# Test
		if (self.project.run_test == True):
			
			devName = self.obtainAdbDevice()
			
			
			put('Uninstalling old APK "%s" using ADB...' % (appId))
			cmd = ANDROID_ADB_CMD
			cmd += ' uninstall'
			cmd += ' %s' % (appId)
			r = self.command(cmd)
			put(r)
			#@FIXME This can throw an exception if it wasn't installed before (which is not an error at all)
			
			
			put('Installing "%s" to device "%s" using ADB...' % (appId, devName))
			cmd = ANDROID_ADB_CMD
			cmd += ' install'
			#cmd += ' -t'	# Allow test
			cmd += ' -r'	# Overwrite
			#cmd += ' -g'	# Grant all runtime permissions
			cmd += ' %s' % (apkFilenameAligned)
			r = self.command(cmd)
			put(r)
			
			
			put('Running "%s"...' % (appId))
			cmd = ANDROID_ADB_CMD
			cmd += ' shell'
			cmd += ' am start'
			cmd += ' -n %s/%s' % (appId, appActivityId)
			r = self.command(cmd)
			put(r)
			
			#@FIXME: Check if it exited with error! e.g. "Error type 2"
			
		
		put('Done.')
		
	
	
	def obtainAdbDevice(self):
		"Find and/or start a new AVD"
		devName = self.checkDevice()
		if (devName != None):
			# Okay, was already running.
			return devName
		
		
		put('Launching AVD "%s"...' % (AVD_NAME))
		
		os.environ['ANDROID_HOME'] = ANDROID_SDK_DIR
		os.environ['ANDROID_SDK_ROOT'] = ANDROID_SDK_DIR
		
		# https://developer.android.com/studio/run/emulator-commandline.html
		cmd = EMU_CMD
		#cmd += ' -help-environment'
		#cmd += ' -help-all'
		#cmd += ' -list-avds'
		cmd += ' -avd %s' % (AVD_NAME)
		r = self.command(cmd, faf=True)	# faf = fire-and-forget = do not wait for result
		#put(r)
		
		
		put('Waiting for ADB device to come up...')
		time.sleep(10)
		while (devName == None):
			devName = self.checkDevice()
			time.sleep(2)
		put('Waiting some more to settle...')
		time.sleep(5)
		
	
	def checkDevice(self):
		"Check for running devices, return the most recent one"
		put('Polling ADB devices...')
		cmd = ANDROID_ADB_CMD
		cmd += ' devices'
		#cmd += ' --help'
		r = self.command(cmd)
		#put(r)
		
		devName = None
		ls = r.split('\n')
		for l in ls:
			l = l.strip()
			if (l.startswith('List of devices')): continue
			if (len(l) == 0): continue
			if (not '\t' in l): continue	# Devices have a trailing TAB and "devices"
			#if (l.startswith('emulator-')):
			devName = l.split('\t')[0].strip()
		return devName
	

