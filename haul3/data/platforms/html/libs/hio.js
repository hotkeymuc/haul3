var hio = {
	_putElement: null,
	_fetchElement: null,
	
	init: function(e) {
		hio._putElement = document.getElementById("hioOut");
		hio._fetchElement = document.getElementById("hioIn");
	},
	put: function(txt) {
		hio._putElement.innerText += txt + '\n';
	},
	put_: function(txt) {
		hio._putElement.innerText += txt;
	},
	shout: function(txt) {
		alert(txt);
	},
	fetch: function() {
		//var txt = this._fetchElement.value;
		//this._fetchElement.value = '';
		txt = prompt('hio.fetch');
		return txt;
	}
};

async function _main_async() {
	// Call main, but be async, so we can have a proper fetch from stdin
	main();
}
function put(txt) {
	hio.put(txt);
}
function put_(txt) {
	hio.put_(txt);
}
function shout(txt) {
	alert(txt);
}

// Simple (prompt)
function fetch() {
	var txt = prompt('hio.fetch');
	return txt;
}
/*
// Modern (async)
var _fetchResolve = null;
function fetch() {
	//var txt = prompt('hio.fetch');
	let txt = await fetch_wait();
	return txt;
}
async function fetch_wait() {
	return new Promise((resolve, reject) => {
		_fetchResolve = resolve;
		//resolve(prompt('fetch_wait'));
	});
}
function hioIn_enter() {
	var txt = hio._fetchElement.value;
	hio._fetchElement.value = '';
	if (_fetchResolve !== null) {
		_fetchResolve(txt);
		_fetchResolve = null;
	}
}
*/

function int_str(i) {
	return ('' + i);
}

//window.onload = function(e) { hio.init(e);};
//document.addEventListener('DOMContentLoaded', hio.init, false);
window.addEventListener('load', hio.init, false)