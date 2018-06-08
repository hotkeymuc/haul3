#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from haul.utils import *
from haul.builder import *

from haul.langs.py.reader_py import *
from haul.langs.java.writer_java import *

import time	# For waiting in between emu polls


def put(txt):
	print('HAULBuilder_android:\t' + str(txt))


class HAULBuilder_android(HAULBuilder):
	def __init__(self):
		HAULBuilder.__init__(self, platform='android', lang='java')
		
		self.set_translator(HAULTranslator(HAULReader_py, HAULWriter_java))
		
	
	def build(self, project):
		
		HAULBuilder.build(self, project=project)
		
		name = self.project.name
		
		#@TODO: MAke package name customizable!
		
		appNamespace = 'wtf.haul'
		android_app_id = appNamespace + '.' + name
		android_app_version = '0.0.1'
		app_activity_id = 'wtf.haul.HaulActivity'	#android_app_id + '.MainActivity'
		
		data_libs_path = os.path.join(self.data_path, 'platforms', 'android', 'libs')
		data_res_path = os.path.join(self.data_path, 'platforms', 'android', 'res')
		
		res_path = os.path.abspath(os.path.join(self.staging_path, 'res'))
		src_path = os.path.abspath(os.path.join(self.staging_path, 'src'))
		class_path = os.path.abspath(os.path.join(self.staging_path, 'build'))
		
		
		#java_filename = name.capitalize() + '.java'
		java_filename = name + '.java'
		#class_filename = name.capitalize() + '.class'
		class_filename = name + '.class'
		package_src_path = os.path.join(src_path, 'wtf', 'haul')
		package_class_path = os.path.join(class_path, 'wtf', 'haul')
		
		
		java_filename_full = os.path.join(package_src_path, java_filename)
		class_filename_full = os.path.join(package_class_path, class_filename)
		haul_info_filename = os.path.join(package_src_path, 'HaulInfo.java')
		haul_info_class_filename = os.path.join(package_class_path, 'HaulInfo.class')
		
		manifest_filename_full = os.path.join(self.staging_path, 'AndroidManifest.xml')
		dex_filename_full = os.path.join(self.staging_path, 'classes.dex')
		keystore_filename = os.path.join(self.staging_path, 'appkey.keystore')
		keystore_source_filename = os.path.join(self.staging_path, 'appkey.keystore.input')
		
		apk_filename_raw = os.path.join(self.staging_path,  android_app_id + '_' + android_app_version + '_raw.apk')
		apk_filename_signed = os.path.join(self.staging_path,  android_app_id + '_' + android_app_version + '_signed.apk')
		apk_filename_aligned = os.path.join(self.staging_path,  android_app_id + '_' + android_app_version + '_aligned.apk')
		#apk_filename_final = os.path.join(output_path,  android_app_id + '_' + android_app_version + '.apk')
		apk_filename_final = os.path.join(self.output_path,  name + '.apk')
		
		
		#jre_path = os.path.abspath('Z:/Apps/_code/AndroidStudio/jre')
		jre_path = self.get_path('JRE_PATH', os.path.abspath(os.path.join(self.tools_path, 'jre')))
		
		JAVA_CMD = os.path.abspath(os.path.join(jre_path, 'bin', 'java'))
		JAVAC_CMD = os.path.abspath(os.path.join(jre_path, 'bin', 'javac'))
		KEYTOOL_CMD = os.path.abspath(os.path.join(jre_path, 'bin', 'keytool'))
		JARSIGNER_CMD = os.path.abspath(os.path.join(jre_path, 'bin', 'jarsigner'))
		JAVA_RUNTIME_JAR = os.path.abspath(os.path.join(jre_path, 'lib', 'rt.jar'))
		
		#android_sdk_path = os.path.abspath('Z:/Data/_code/_sdk/adt-bundle-windows-x86-20130522/sdk')
		#android_sdk_path = self.get_path('ANDROID_SDK_PATH')
		android_sdk_path = self.get_path('ANDROID_SDK_HOME', os.path.abspath(os.path.join(self.tools_path, 'android')))
		ANDROID_ADB_CMD = os.path.abspath(os.path.join(android_sdk_path, 'platform-tools', 'adb'))
		ANDROID_JAR = os.path.abspath(os.path.join(android_sdk_path, 'platforms', 'android-25', 'android.jar'))
		ANDROID_BUILD_TOOLS_DIR = os.path.abspath(os.path.join(android_sdk_path, 'build-tools', '25.0.0'))
		ANDROID_AAPT_CMD = os.path.abspath(os.path.join(ANDROID_BUILD_TOOLS_DIR, 'aapt'))
		ANDROID_ZIPALIGN_CMD = os.path.abspath(os.path.join(ANDROID_BUILD_TOOLS_DIR, 'zipalign'))
		ANDROID_DEX_JAR = os.path.abspath(os.path.join(ANDROID_BUILD_TOOLS_DIR, 'lib', 'dx.jar'))
		
		EMU_CMD = os.path.abspath(os.path.join(android_sdk_path, 'emulator', 'emulator'))
		AVD_NAME = 'Nexus_5X_API_25_x86'	# Which AVD device to use for emulator testing
		
		
		
		put('Cleaning staging paths...')
		self.clean(src_path)
		self.clean(class_path)
		self.mkdir(os.path.join(src_path, 'wtf'))
		self.mkdir(os.path.join(src_path, 'wtf', 'haul'))
		
		
		
		put('Preparing path names...')
		for s in self.project.sources:
			s.dest_filename = package_src_path + '/' + s.name + '.java'
		
		put('Translating sources to Java...')
		self.translate_project(output_path=package_src_path)
		
		if not os.path.isfile(java_filename_full):
			raise HAULBuildError('Main Java file "{}" was not created!'.format(java_filename_full))
			return False
		
		
		put('Staging Android app...')
		
		
		put('Copying libraries...')
		src_files = []
		for s in self.project.libs:
			lib_filename_data = data_libs_path + '/' + s.name + '.java'
			f = os.path.join(src_path, 'wtf', 'haul', s.name + '.java')
			self.copy(lib_filename_data, f)
			src_files.append(f)
		
		src_files.append(java_filename_full)
		
		
		put('Creating haulInfo...')
		haulInfo = '''package wtf.haul;

//import %s;

public class HaulInfo {
	public static final %s MainClass = new %s();
}
''' % (android_app_id, name, name)
# % (android_app_id, name.capitalize(), name.capitalize())
		self.touch(haul_info_filename, haulInfo)
		src_files.append(haul_info_filename)
		
		if not os.path.isfile(haul_info_filename):
			raise HAULBuildError('haul_info file "{}" was not created!'.format(haul_info_filename))
			return False
		
		
		put('Copying activities...')
		f = os.path.join(src_path, 'wtf', 'haul', 'HaulActivity.java')
		self.copy(os.path.join(data_res_path, 'HaulActivity.java'), f)
		src_files.append(f)
		
		
		
		put('Preparing resources..')
		self.clean(res_path)
		
		self.mkdir(os.path.join(res_path, 'drawable'))
		self.copy(os.path.join(data_res_path, 'icon_64x64.png'), os.path.join(res_path, 'drawable', 'icon.png'))
		
		self.mkdir(os.path.join(res_path, 'values'))
		stringsXml = '''<resources>
    <string name="app_name">%s</string>
</resources>''' % (name)
		self.touch(os.path.join(res_path, 'values', 'strings.xml'), stringsXml)
		
		
		
		put('Compiling to Java Class...')
		# http://geosoft.no/development/android.html
		cmd = '"' + JAVAC_CMD + '"'
		#cmd += ' -verbose'
		cmd += ' -classpath ".";"{}";"{}";"{}"'.format(src_path, class_path, ANDROID_JAR)
		cmd += ' -bootclasspath "{}"'.format(JAVA_RUNTIME_JAR)
		cmd += ' -sourcepath "{}"'.format(src_path)	#(staging_path)
		cmd += ' -source 1.7'	# Must target 1.7 or below?! Or else "Unsupported class file version 52.0"
		cmd += ' -target 1.7'	# Must target 1.7 or below?! Or else "Unsupported class file version 52.0"
		cmd += ' -d "{}"'.format(class_path)
		#cmd += ' "{}"'.format(os.path.join(src_path, '*'))
		cmd += ' {}'.format(' '.join(src_files))
		#cmd += ' "{}"'.format(os.path.join(self.staging_path, '*.java'))
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(class_filename_full):
			put(r)
			raise HAULBuildError('Main class file "{}" was not created!'.format(class_filename_full))
			return False
		
		if not os.path.isfile(haul_info_class_filename):
			put(r)
			raise HAULBuildError('HAUL info class file "{}" was not created!'.format(haul_info_class_filename))
			return False
		
		
		
		put('Compiling to DEX...')
		cmd = JAVA_CMD + ' -jar "{}"'.format(ANDROID_DEX_JAR)
		#cmd += 'com.android.dex.Dex'
		cmd += ' --dex'
		#cmd += ' --verbose'
		cmd += ' --output="{}"'.format(dex_filename_full)
		cmd += ' "{}"'.format(class_path)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(dex_filename_full):
			put(r)
			raise HAULBuildError('DEX classes file "{}" was not created!'.format(dex_filename_full))
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
''' % (android_app_id, android_app_version, name, app_activity_id, name)
		# "@string/app_name"
		self.touch(manifest_filename_full, m)
		
		if not os.path.isfile(manifest_filename_full):
			raise HAULBuildError('Manifest file "{}" was not created!'.format(manifest_filename_full))
			return False
		
		
		
		put('Packaging to APK...')
		cmd =  ANDROID_AAPT_CMD
		cmd += ' package'
		cmd += ' -v'
		cmd += ' -f'
		#cmd += ' -M "%s"' % (manifest_filename_full)	# Only specify if it is not the root one
		cmd += ' -S "%s"' % (res_path)
		cmd += ' -I "%s"' % (ANDROID_JAR)
		cmd += ' -F "%s"' % (apk_filename_raw)
		cmd += ' "%s"' % (self.staging_path)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(apk_filename_raw):
			put(r)
			raise HAULBuildError('APK file "{}" was not created!'.format(apk_filename_raw))
			return False
		
		
		
		put('Generating keystore "%s"...' % (keystore_filename))
		keystore_password = '123456'	#'haul_123456_keystore'
		key_fullname = 'HAUL Builder'
		key_org_unit_name = 'HAUL'
		key_org_name = 'HotKey'
		key_city_name = 'WTF'
		key_state_name = 'WTF'
		key_country = 'de'
		key_affirmative = 'ja'	# yes	#@FIXME: This depends on the language of the JRE keytool... Argh!
		key_name = 'haul_key_' + name
		key_password = '123456'	#'654321haul_key'
		ENTER = '\n'
		
		keystore_input = keystore_password + ENTER
		keystore_input += keystore_password + ENTER
		keystore_input += key_fullname + ENTER
		keystore_input += key_org_unit_name + ENTER
		keystore_input += key_org_name + ENTER
		keystore_input += key_city_name + ENTER
		keystore_input += key_state_name + ENTER
		keystore_input += key_country + ENTER
		keystore_input += key_affirmative + ENTER
		keystore_input += key_password + ENTER
		keystore_input += ENTER
		self.touch(keystore_source_filename, keystore_input)
		
		cmd = KEYTOOL_CMD
		cmd += ' -genkey '
		cmd += ' -v'
		cmd += ' -keystore "%s"' % (keystore_filename)
		cmd += ' -alias %s' % (key_name)
		cmd += ' -keyalg RSA'
		cmd += ' -keysize 2048'
		cmd += ' -validity 10000'
		cmd += ' <' + keystore_source_filename
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(keystore_filename):
			put(r)
			raise HAULBuildError('Keystore file "{}" was not created!'.format(keystore_filename))
			return False
		
		
		
		put('Signing APK file...')
		
		cmd = JARSIGNER_CMD
		cmd += ' -verbose'
		cmd += ' -keystore "%s"' % (keystore_filename)
		cmd += ' -storepass %s' % (keystore_password)
		cmd += ' -keypass %s' % (key_password)
		cmd += ' -signedjar "%s"' % (apk_filename_signed)
		cmd += ' "%s"' % (apk_filename_raw)
		cmd += ' %s' % (key_name)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(apk_filename_signed):
			put(r)
			raise HAULBuildError('Signed APK file "{}" was not created!'.format(apk_filename_signed))
			return False
		
		
		
		put('Aligning APK file...')
		cmd = ANDROID_ZIPALIGN_CMD
		cmd += ' -v 4'
		cmd += ' "%s"' % (apk_filename_signed)
		cmd += ' "%s"' % (apk_filename_aligned)
		r = self.command(cmd)
		#put(r)
		
		if not os.path.isfile(apk_filename_aligned):
			put(r)
			raise HAULBuildError('Aligned APK file "{}" was not created!'.format(apk_filename_aligned))
			return False
		
		
		put('Copying file to output directory "%s"...' % (apk_filename_final))
		self.copy(apk_filename_aligned, apk_filename_final)
		
		
		# Test
		if (self.project.run_test == True):
			
			devName = self.obtainAdbDevice()
			
			
			put('Uninstalling old APK "%s" using ADB...' % (android_app_id))
			cmd = ANDROID_ADB_CMD
			cmd += ' uninstall'
			cmd += ' %s' % (android_app_id)
			r = self.command(cmd)
			put(r)
			#@FIXME This can throw an exception if it wasn't installed before (which is not an error at all)
			
			
			put('Installing "%s" to device "%s" using ADB...' % (android_app_id, devName))
			cmd = ANDROID_ADB_CMD
			cmd += ' install'
			#cmd += ' -t'	# Allow test
			cmd += ' -r'	# Overwrite
			#cmd += ' -g'	# Grant all runtime permissions
			cmd += ' %s' % (apk_filename_aligned)
			r = self.command(cmd)
			put(r)
			
			
			put('Running "%s"...' % (android_app_id))
			cmd = ANDROID_ADB_CMD
			cmd += ' shell'
			cmd += ' am start'
			cmd += ' -n %s/%s' % (android_app_id, app_activity_id)
			r = self.command(cmd)
			put(r)
			
			#@FIXME: Check if it exited with error! e.g. "Error type 2"
			
		
		put('Done.')
		return True
	
	
	def obtainAdbDevice(self):
		"Find and/or start a new AVD"
		devName = self.checkDevice()
		if (devName != None):
			# Okay, was already running.
			return devName
		
		
		put('Launching AVD "%s"...' % (AVD_NAME))
		
		os.environ['ANDROID_HOME'] = android_sdk_path
		os.environ['ANDROID_SDK_ROOT'] = android_sdk_path
		
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
	

