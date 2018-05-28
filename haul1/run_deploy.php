<h1>HAL+HTK Bootstrap Deployer - (C) 2011 Bernhard -HotKey- Slawik, http://www.bernhardslawik.de<h1>
<pre>
<?php
/**
 *
 * This is the deployer ("Generation 0") for the HAL+HTK system ("skynet" / "shadowRunner").
 * HTKs (HAL Translation Kernels), which translate source code from the HAL (HotKey's Awesome/Average Language) to any arbitrary destination language, are themselves written in HAL.
 * This leads to a "chicken-egg-problem": Since HAL itself is not executable, neither are the compilers (HTKs) for this language!
 * Therefore this class initially translates HAL to PHP source code, so any other HTKs (or other HAL source code) can be initially executed.
 *
 * Since this program is used for INITIALLY compiling the "real" compilers from HAL, it may have limited functionality as it only needs to translate the source code of the translators. These normally only use simple string functionality and basic array functions to work properly.
 *
 * You may only need this program ONCE in your life time, or if you substantially extend the HAL language and use these new functions in the compiler source. In these cases you need to modify the HTKs' HAL source codes AND this bootstrapper PHP simultaneously to avoid nasty errors throuout the "generations" to come.
 *
 * 2011-08-19 Bernhard -HotKey- Slawik
 *
 *
 * What it does:
 *	+ Compile "htk_[destination].hal" to destination using bootstrap HTK "htk_php.class.php"
 *	+ Load this freshly compiled HTK
 *	+ Merge all autorun sources to virtual "autorun.hal"
 *	+ Bundle all other HTKs as HAL resource
 *	+ Compile auto-generated info HAL to destination
 *	+ Compile "autorun.hal" to destination
 *	+ Save "Generation 1".
 *
 */

// Setup
$platform = 'php';	// Destination platform of first child
$srcFolder = 'src.hal';
$srcGenFolder = 'src.gen';
$dstFolder = 'deploy';


// HAL files to translate and merge into native child bootstrap
$bootSections = array(
	'htk'		=>	$srcFolder.'/htk_'.$platform.'.hal',
	'auto'		=>	$srcFolder.'/autorun.hal',	// Merges all files neccessary!
	#'deploy'		=>	$srcFolder.'/deploy.hal',
);

// Bundle resources
$resFilenames = array(
	// HTKs' HALs
	'htk_php.hal'	=> $srcFolder.'/htk_php.hal',
	'htk_php.inc.php'	=> $srcFolder.'/htk_php.inc.php',
	
	'htk_js.hal'	=> $srcFolder.'/htk_js.hal',
	'htk_js.inc.js'	=> $srcFolder.'/htk_js.inc.js',
	
	'htk_vbs.hal'	=> $srcFolder.'/htk_vbs.hal',
	'htk_vbs.inc.vbs'	=> $srcFolder.'/htk_vbs.inc.vbs',
	
	'deploy.hal'	=> $srcFolder.'/deploy.hal',
	#'shadowRunner.hal'	=> $srcFolder.'/shadowRunner.hal',
	'autorun.hal'	=> $srcFolder.'/autorun.hal',
	
);


function _put($txt) {
	echo $txt."\n";
	flush();
}
function _putR($txt) {
	echo $txt;
}
define('currPlatform', 'PHPboot');



function doTranslate($lines, $htk) {
	$i = 0;
	foreach($lines as $line) {
		$i++;
		
		# Count indents and de-indent
		$indents = 0;
		while ((strlen($line) > 0) && (substr($line, 0, 1) == "\t")) {$line = substr($line, 1); $indents++;}
		
		$line = trim($line);
		if (strlen($line) == 0) continue;
		if (substr($line, 0, 1) == "#") continue;
		
		//@TODO:	Don't explode tabs inside strings!!!
		$items = explode("\t", $line."\t\t\t\t\t");
		
		// Bootstrapping instructions
		switch($items[0]) {
			case "!MERGE":
				global $srcFolder;
				$mergeFilename = $srcFolder.'/'.$items[1];
				put('Merging source file: "'.$mergeFilename.'"...');
				$mergeLines = file($mergeFilename);
				doTranslate($mergeLines, $htk);
				put('...back from merge with "'.$mergeFilename.'"...');
				break;
				
			default:
				$htk->translateInstruction($items, $line, $indents, $i);
		}
		
	}
}



function simpleTranslate($fIn, $htk, $fOut) {
	_putR('Compiling "'.$fIn.'" to "'.$fOut.'"...');
	if (is_file($fOut)) unlink($fOut);
	
	$htk->deployStart();
	
	# Bundle resources
	#$htk->resourceStart();
	#$htk->resourceEnd();
	
	# Translate the given HAL source code using the given HTK
	$htk->translateLibs();
	$htk->translateStart();
	$lines = file($fIn);
	doTranslate($lines, $htk);
	$htk->translateEnd();
	
	# Write output file
	$hOut = fopen($fOut, "wb+");
	fwrite($hOut, $htk->deployEnd());
	fclose($hOut);
	_put('Created "'.$fOut.'".');
}


function deploy($platform, $htk, $resFilenames, $bootSections, $fOut) {
	_putR('Deploying to "'.$fOut.'" using HTK'.$platform.'...');
	if (is_file($fOut)) unlink($fOut);
	
	$htk->deployStart();

	$htk->resourceStart();
	foreach ($resFilenames as $resName => $resFilename) {
		$resData = file_get_contents($resFilename);
		//@TODO:	Encrypt and compress!
		$htk->resourceAdd($resName, $resData);
	}
	$htk->resourceEnd();


		
	// Translate the given HAL source code using the given HTK
	$htk->translateStart();
	$htk->translateLibs();
	// Bootstrap!
	put('Generating HAL source for section [info]...');
	//	Prepend current platform info
	$currPlatform = $platform;
	$linesInfo = explode("\n", '
	//	Info (created by Generation 0)
	CONST	generation	1
	CONST	deployTime	"'.date("Y-m-d H:i:s").'"
	CONST	history	"Created by '.$_SERVER['SCRIPT_NAME'].' as '.$fOut.' ('.$currPlatform.') at '.date("Y-m-d H:i:s").'"
	CONST	currPlatform	"'.$currPlatform.'"

	//	Instantiate HTK
	VAR	htk
	NEW	$htk	HTK'.strtolower($currPlatform).'
	');
	put('Translating HAL and merging to bootstrap...');
	doTranslate($linesInfo, $htk);

	foreach($bootSections as $bootName => $bootFilename) {
		put('Loading HAL source for section ['.$bootName.']: "'.$bootFilename.'"...');
		$lines = file($bootFilename);
		put('Translating HAL and merging to bootstrap...');
		doTranslate($lines, $htk);
	}
	$htk->translateEnd();


	// Write output file
	put('Writing output file "'.$fOut.'"...');
	$hOut = fopen($fOut, "wb+");
	fwrite($hOut, $htk->deployEnd());
	fclose($hOut);

	put('Deploy finished!');
}


// Compile HTKphp to PHP
require_once("htk_php.class.php");
$htkPhpBoot = new HTKphpBoot();
$htkPhpBoot->resourceStart();
foreach ($resFilenames as $resName => $resFilename) {
	$resData = file_get_contents($resFilename);
	//@TODO:	Encrypt and compress!
	$htkPhpBoot->resourceAdd($resName, $resData);
}
$htkPhpBoot->resourceEnd();


$fIn = $srcFolder.'/htk_php.hal';
$fOut = $srcGenFolder.'/htk_php1.php';
simpleTranslate($fIn, $htkPhpBoot, $fOut);
if (!is_file($fOut)) die($fOut.' NOT created! Stopping tool chain.');
require_once($fOut);
$htkPhpBooted = new HTKphp();

/*
// Re-compile itself
$fIn = $srcFolder.'/htk_php.hal';
$fOut = $srcGenFolder.'/htk_php2.php';
simpleTranslate($fIn, $htkPhpBooted, $fOut);
if (!is_file($fOut)) die($fOut.' NOT created! Stopping tool chain.');
require_once($fOut);
$htkPhp = new HTKphp();
*/
$htkPhp = $htkPhpBooted;


if ($platform != "php") {
	// Compile destination platform HTK to PHP
	$fIn = $srcFolder.'/htk_'.$platform.'.hal';
	$fOut = $srcGenFolder.'/htk_'.$platform.'.php';
	simpleTranslate($fIn, $htkPhp, $fOut);
	if (!is_file($fOut)) die($fOut.' NOT created! Stopping tool chain.');
	require_once($fOut);
	$clazzname = 'HTK'.$platform;
	$htkDest = new $clazzname();
} else {
	$htkDest = $htkPhp;
}




$fOut	= $dstFolder.'/child_generation1.'.$platform;

deploy($platform, $htkDest, $resFilenames, $bootSections, $fOut);
?>
</pre>