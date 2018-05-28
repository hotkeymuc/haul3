<?php
/**
 * 2011-07-31
 * This is the bootstrapper ("Generation 0") for the HAL+HTK system ("skynet" / "shadowRunner").
 * HTKs (HAL Translation Kernels), which translate source code from the HAL (HotKey's Awesome/Average Language) to any arbitrary destination language, are themselves written in HAL.
 * This leads to a "chicken-egg-problem": Since HAL itself is not executable, neither are the compilers (HTKs) for this language!
 * Therefore, this class initially translates HAL to PHP source code, so any other HTKs (or other HAL source code) can be initially executed.
 *
 * Since this program is used for INITIALLY compiling the the "real" compilers from HAL, it may have limited functionality as it only needs to translate the source code of the translators. These normally only use simple string functionality and basic array functions to work properly.
 *
 * You may only need this program ONCE in your life time, or if you substantially extend the HAL language and use these new functions in the compiler source. In these cases you need to modify the HTKs' HAL source codes AND this bootstrapper PHP simultaneously to avoid nasty errors throuout the "generations" to come.
 *
 * (C) 2011 Bernhard -HotKey- Slawik
 */

function addSlashesSingle($t) {
	$t = str_replace('\\', '\\\\', $t);
	$t = str_replace('\'', '\\\'', $t);
	return $t;
}

require_once('htk.class.php');
$_RES = array();

class HTKphpBoot extends HTK {
	var $name = 'php';
	var $ext = 'php';
	
	var $data;
	function deployStart() {
		$this->data = '<'.'?php
### Translated from HAL meta language by pre-compiled PHP version of HTKphp, (C)opyright 2011 HotKey/Bernhard Slawik Digital
';
	}

	function write($txt) {
		$this->data .= $txt."\n";
	}


	function resourceStart() {
		$this->write('
### Resouces
$_RES = array();');
	}
	function resourceAdd($resName, $resData) {
		global $_RES;
		$_RES[$resName] = $resData;
		
		$resData = addSlashesSingle($resData);
		$this->write('$_RES[\''.$resName.'\'] = \''.($resData).'\';');
		
	}
	function resourceEnd() {
	}
	
	function translateLibs() {
		$this->write(file_get_contents('src.hal/htk_php.inc.php'));
		/*
		$this->write('
### Implementation of Platform Specific Library Functions
if (!function_exists("putR")) {
function put($txt) {
	echo($txt."\n");
	flush();
}
function putR($txt) {
	echo($txt);
}

function file_putString($filename, $data) {
	$h = fopen($filename, "wb");
	fwrite($h, $data);
	fclose($h);
}
function file_getString($filename) {
	$h = fopen($filename, "rb");
	$data = fread($h, filesize($filename));
	fclose($h);
	return $data;
}
function res_getString($key) {
	global $_RES;
	return $_RES[$key];
}
function res_run($key) {
	global $htk;
	$code = res_getString($key);
	$htk->deployStart();
	$htk->translateStart();
	
}

### Load self-bundled Library Resources
# res_load("someLib.inc.php");
}
### End of Libs
');
*/
	}
	
	function translateStart() {
	}
	
	function translateExp($t) {
		//@FIXME: This is just a heuristic!
		// Don't replace inside strings!!
		if (substr($t, 0, 1) == '"') return "'".addSlashesSingle(substr($t, 1, -1))."'";
		if (substr($t, 0, 1) == "'") return "'".addSlashesSingle(substr($t, 1, -1))."'";
		
		$r = $t;
		#$r = str_replace('$', '', $r);
		$r = str_replace('.', '$this->', $r);
		$r = str_replace('_', '', $r);
		#$r = str_replace('[', '(', $r);
		#$r = str_replace(']', ')', $r);
		#$r = str_replace('!=', '<>', $r);
		#$r = str_replace('==', '=', $r);
		return $r;
	}
	
	function translateInstruction($items, $line, $indents, $num=0) {
		$indent = "";
		for ($i = 0; $i < $indents; $i++) $indent .= "\t";
		$p1 = $this->translateExp($items[1]);
		$p2 = $this->translateExp($items[2]);
		$p3 = $this->translateExp($items[3]);
		$p4 = $this->translateExp($items[4]);
		
		switch($items[0]) {
			// Meta comment
			case "##":
				# Just ignore
				break;
				
			// Comment
			case "//":
				$this->write($indent.'// '.$line);
				break;
				
			// Insert Macro
			case "MACRO":
				switch($p1) {
					default:
						$this->write($indent.' ###### UNKNOWN MACRO: '.$p1);
				}
				break;
				
			// Define variable
			case "VAR":
				if ($p2 != "") {
					#$this->write($indent.'var $'.$p1.' = array();');
					$this->write($indent.'$'.$p1.' = array();');
				}
				break;
				
			// Define class variable
			case "PROP":
				if ($p2 != "") $extra = ' = array()'; else $extra = "";
				$this->write($indent.'var $'.$p1.$extra.';');
				break;
				
			// Define constant
			case "CONST":
				##	PHP 5.3.0: $this->write($indent.'const '.$p1.' = '.$p2.';');
				$this->write($indent.'define("'.$p1.'", '.$p2.');');
				break;
				
			// Class
			case "CLASS":
				$this->write($indent.'class '.$p1.' {');
				break;
			case "/CLASS":
				$this->write($indent.'}');
				break;
				
			// Method
			case "METHOD":
				/*
				switch($p1) {
					case "__init": $p1 = "__construct"; break;
					case "__terminate": $p1 = "__destroy"; break;
				}
				*/
				$this->write($indent.'function '.$p1.'('.$p2.') {' );
				break;
			case "/METHOD":
				$this->write($indent.'}');
				$this->write($indent);
				break;
				
			// Function
			case "FUNCTION":
				$this->write($indent.'function '.$p1.'('.$p2.') {' );
				break;
			case "/FUNCTION":
				$this->write($indent.'}');
				$this->write($indent);
				break;
			case "RETURN":
			case "RETURN_REF":
				$this->write($indent.'return '.$p1.';');
				break;
				
			// Set variable
			case "SET":
			case "SET_REF":
				$this->write($indent.$p1.' = '.$p2.';');
				break;
			// Increment
			case "INC":
				if ($p2 != "") {
					$this->write($indent.$p1.' += '.$p2.';');
				} else {
					$this->write($indent.$p1.'++'.';');
				}
				break;
			// Decrement
			case "DEC":
				if ($p2 != "") {
					$this->write($indent.$p1.' -= '.$p2.';');
				} else {
					$this->write($indent.$p1.'--'.';');
				}
				break;
			// Multiply self by
			case "MUL":
				$this->write($indent.$p1.' *= '.$p2.';');
				break;
			// Divide self by
			case "DIV":
				$this->write($indent.$p1.' /= '.$p2.';');
				break;
				
			case "IF":
				$this->write($indent.'if ('.$p1.') {');
				break;
			case "ELSE":
				$this->write($indent.'} else {');
				break;
			case "/IF":
				$this->write($indent.'}');
				break;
			case "SELECT":
				$this->write($indent.'switch ('.$p1.') {');
				break;
			case "/SELECT":
				$this->write($indent.'}');
				break;
			case "CASE":
				$this->write($indent.'case '.$p1.':');
				break;
			case "/CASE":
				$this->write($indent.'break;');
				break;
			case "CASE_ELSE":
				$this->write($indent.'default:');
				break;
				
			case "WHILE_EQ":
				$this->write($indent.'while ('.$p1.' == '.$p2.') {');
				break;
			case "WHILE_NEQ":
				$this->write($indent.'while ('.$p1.' != '.$p2.') {');
				break;
			case "/WHILE":
				$this->write($indent.'}');
				break;
				
			case "FOR":
				$this->write($indent.'for ('.$p1.' = '.$p2.'; '.$p1.' <= '.$p3.'; '.$p1.'++) {');
				break;
			case "FOR_EACH":
				#$this->write($indent.'foreach ('.$p2.' as '.$p1.' => '.$p3.') {');
				$this->write($indent.'foreach ('.$p2.' as '.$p1.') {');
				break;
			case "/FOR":
				$this->write($indent.'}');
				break;
				
			// Call a method
			case "CALL":
				$this->write($indent.$p1.'('.$p2.');');
				break;
			case "CLASS_CALL":
				$this->write($indent.$p1.'->'.$p2.'('.$p3.');');
				break;
			// Call a function, set variable to result
			case "RESULT":
				$this->write($indent.$p1.' = '.$p2.'('.$p3.');');
				break;
			case "CLASS_RESULT_REF":
			case "CLASS_RESULT":
				$this->write($indent.$p1.' = '.$p2.'->'.$p3.'('.$p4.');');
				break;
			// Call a class method/function, set variable
			case "NEW":
				$this->write($indent.$p1.' = new '.$p2.'('.$p3.');');
				break;
			case "END":
				break;
			
			case "put":
				$this->write($indent.'put('.$p1.');');
				break;
			case "putR":
				$this->write($indent.'putR('.$p1.');');
				break;
			
			case "array:len":
				$this->write($indent.$p2.' = count('.$p1.');');
				break;
			case "array:redim":
				#$this->write($indent.'ReDim preserve '.$p1.'('.$p2.')');
				$this->write($indent.'while (count('.$p1.') < '.$p2.') '.$p1.'[] = 0;');
				break;
			
			case "str:prepend":
				$this->write($indent.$p2.' = '.$p1.'.'.$p2.';');
				break;
			case "str:append":
				$this->write($indent.$p2.' .= '.$p1.';');
				break;
			case "str:appendByte":
				$this->write($indent.$p2.' .= chr('.$p1.');');
				break;
			case "str:char":
				$this->write($indent.$p2.' = chr('.$p1.');');
				break;
			case "str:replace":
				$this->write($indent.$p3.' = str_replace('.$p1.', '.$p2.', '.$p3.');');
				break;
			case "str:len":
				$this->write($indent.$p2.' = strlen('.$p1.');');
				break;
			case "str:charCodeAt":
				$this->write($indent.$p3.' = ord(substr('.$p1.', '.$p2.', 1));');
				break;
			case "str:addSlashes":
				$this->write($indent.$p2.' = addslashes('.$p1.');');
				break;
			case "str:explode":
				$this->write($indent.$p3.' = explode('.$p1.', '.$p2.');');
				break;
			case "str:copy":
				$this->write($indent.$p4.' = substr('.$p1.', '.$p2.', '.$p3.');');
				break;

			case "file:putString":
				$this->write($indent.'file_putString('.$p1.', '.$p2.');');
				break;
			case "file:getString":
				$this->write($indent.$p2.' = file_getString('.$p1.');');
				break;
				
			case "res:getString":
				$this->write($indent.$p2.' = res_getString('.$p1.');');
				break;
				
			case "eval":
				$this->write($indent.$p2.' = eval('.$p1.');');
				break;
			default:
				#put("Unknown command=\"".$items[0]."\", in line ".$num."=\"".$line."\"");
				put("Line ".$num.":	Unknown command=\"".$items[0]."\", in line ".$line."\"");
		}
	}
	function translateEnd() {
		#
	}
	
	function deployEnd() {
		$this->write("\n".'?'.'>');
		return $this->data;
	}
	
	function run() {
		eval($this->data);
	}
}
?>