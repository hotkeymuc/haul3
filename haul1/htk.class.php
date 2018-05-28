<?php
/**
 *
 * Prototype of a HTK (HAL Translation Kernel), a minimalistic compiler that translates HAL source (HotKey's Average Language) a different language
 *
 * 2011-07-17 Bernhard -HotKey- Slawik, http://www.bernhardslawik.de
 *
 */
class HTK {
	var $name = 'unknownPlatform';
	var $ext = '.unknownPlatform';
	function deployStart() {
	}
	
	function translateStart() {
	}
	function translateInstruction($command, $p1, $p2, $p3, $line, $indents) {
	}
	function translateEnd() {
	}
	
	/**
	 * Runs the code it just translated
	 */
	function run() {
	}
	
	function resourceStart() {
	}
	function resourceAdd($resName, $resData) {
	}
	function resourceEnd() {
	}
	
	function deployEnd() {
		return "";
	}
	
}
?>