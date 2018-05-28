# This is lib.php, it gets inlined in every php output file for platform specific stuff.
$CR = chr(10)

function put($t) {
	echo($t.$CR);
}

function arr_set_int($l):
	$r = array();
	for ($i = 0; $i < $l; $i++) {
		$r[] = 0;
	}
	return $r;

function file_getAll($path) {
	return res_getAll($path);
}

function res_getAll($path) {
	return file_get_contents($path);
}

/*
class Stream {
	var $url = '';
	function __construct($) {
		$this->url = $url;
	}
	public function getAll() {
		
	}
}
*/
