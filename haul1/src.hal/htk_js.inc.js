// ### Basic functions
var _PUT_CACHE = "";
function put(txt) {
	if (_PUT_CACHE.length > 0) {
		txt = _PUT_CACHE + txt;
		_PUT_CACHE = "";
	}
	if (typeof WScript == "object")
		WScript.StdOut.WriteLine(txt)
	else if (typeof console == "object")
		console.log(txt);
	else
		alert(txt);
}
function putR(txt) {
	_PUT_CACHE = _PUT_CACHE + txt
}
function file_putString(filename, data) {
	if (typeof ActiveXObject != "undefined") {
		var fso = new ActiveXObject("Scripting.FileSystemObject");
		var f = fso.CreateTextFile(filename, true);
		f.Write(data);
		f.Close();
	} else if (supports_html5_storage()) {
		localStorage.setItem(filename, data);
	} else {
		put("No other way to save, so I will output it here: " + encodeURI(data));
	}
}
function file_getString(filename) {
	var data = "";
	if (typeof ActiveXObject != "undefined") {
		var fso = new ActiveXObject("Scripting.FileSystemObject");
		if (fso.FileExists(filename)) {
			var f = fso.OpenTextFile(filename, 1);
			data = f.ReadAll();
			f.Close();
		}
	} else if (supports_html5_storage()) {
		data = localStorage.getItem(filename);
	} else {
		put("No way to read data on this system... :-(");
	}
	return data;
}
function res_getString(key) {
	return _RES[key];
}
function res_load(key) {
	eval(res_getString(key));
}
function replaceAll(t,ss,sr){
	if (typeof t != "string") return "";
	var temp = t.split(ss);
	return temp.join(sr);
}
function supports_html5_storage() {
	try {
		return "localStorage" in window && window["localStorage"] !== null;
	} catch (e) {
		return false;
	}
}


// ### Hybernation code
var _HY_STATE = "";
var _HY_PARAM = null;
function hyber_allowSleep(state, param) {
	_HY_STATE = state;
	_HY_PARAM = param;
}

// ### Translate/load run-time libraries on-the-fly
// res_load("someLib.inc.php");