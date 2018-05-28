### Basic functions
if (!function_exists('put')) {
	function put($txt) {
		echo($txt.chr(10));
		flush();
	}
	function putR($txt) {
		echo($txt);
	}
}

if (!function_exists('file_putString')) {
	function file_putString($filename, $data) {
		$h = fopen($filename, 'wb');
		fwrite($h, $data);
		fclose($h);
	}
	function file_getString($filename) {
		$h = fopen($filename, 'rb');
		$data = fread($h, filesize($filename));
		fclose($h);
		return $data;
	}
	function res_getString($key) {
		global $_RES;
		return $_RES[$key];
	}
	function res_load($key) {
		eval(res_getString($key));
	}
}

### Hybernation code
if (!function_exists('hyber_allowSleep')) {
	$_HY_STATE = '';
	$_HY_PARAM = null;
	function hyber_allowSleep($state, $param) {
		global $_HY_STATE;
		$_HY_STATE = $state;
		global $_HY_PARAM;
		$_HY_PARAM = $param;
	}
}

### Translate/load run-time libraries on-the-fly
# res_load("someLib.inc.php");