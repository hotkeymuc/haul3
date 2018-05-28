<pre>
<?php
/**
 * Static HAL multi platform compiler
 *
 * This file compiles a given HAL file to all given environments/platforms.
 * It uses a HTK (HAL Translation Kernel) to handle each environment/platform.
 * It also bundles the given resource files into the destination files.
 *
 * 2011-07-24 Bernhard -HotKey- Slawik
 */

function put($txt) {
	echo $txt."\n";
}

#require_once("htk_vbs.class.php");
#require_once("htk_js.class.php");
require_once("htk_php.class.php");

// HTK to use (i.e. destination platform)
$htks = array(
	#new HTK_VBS(),
	#new HTK_JS(),
	new HTKphpBoot(),
);

// Input HAL source file to compile
#$fIn = 'shadowRunner.hal';
#$fIn = 'htk_php.hal';
$fIn = 'htk_vbs.hal';
put('Loading HAL-Source "'.$fIn.'"...');
$lines = file('src.hal/'.$fIn);

// Load resources
$resFilenames = array(
#	'runtime.hal'	=> 'src.hal/runtime.hal'
#	'htk_php.hal'	=> 'src.hal/htk_php.hal'
);

$resources = array();
foreach ($resFilenames as $resName => $resFilename) {
	$resources[$resName] = file_get_contents($resFilename);
}



function deploy($lines, $htk, $resources, $fOut) {
	
	$htk->deployStart();
	
	# Bundle resources
	$htk->resourceStart();
	foreach($resources as $resName => $resData) {
		$htk->resourceAdd($resName, $resData);
	}
	$htk->resourceEnd();
	
	# Translate the given HAL source code using the given HTK
	$htk->translateStart();
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
		$htk->translateInstruction($items, $line, $indents, $i);
	}
	$htk->translateEnd();
	
	
	# Write output file
	$hOut = fopen($fOut, "wb+");
	fwrite($hOut, $htk->deployEnd());
	
	//@TODO: Add resources...
	
	fclose($hOut);
}


foreach($htks as $htk) {
	put('Deploying via HTK ['.$htk->name.']...');
	$dir = "deploy/".$htk->name;
	if (!is_dir($dir)) mkdir($dir);
	$fOut = $dir."/".$fIn.$htk->ext;
	
	put('Saving output "'.$fOut.'"...');
	deploy($lines, $htk, $resources, $fOut);
}

?>
</pre>