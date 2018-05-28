/*
	HAUL I/O for webOS (JavaScript)
*/

var HIO_OUT = 0;

function put(data) {
	console.log(data);
	
	if (HIO_OUT) {
		HIO_OUT.innerHTML += data + '<br />\n';
	}
}
//put('hio.js');

function shout(data) {
	
	if (typeof Mojo == 'undefined') {
		// Use alert
		alert(data);
		
	} else {
		// Alert is not available in mojo Apps
		/*
		Mojo.Controller.getAppController().showBanner({
			messageText: data,
			soundClass: "alerts"
		}, {}, "");
		
		
		//this.controller.showAlertDialog({
		Mojo.Controller.getAppController().showAlertDialog({
			onChoose: function(value) {},
			message: 'showAlertDialog',
			choices:[{label:'OK', value:'1', type:'dismiss'}]
		});
		*/
		put('<strong>' + data + '</strong>');
		
	}
	
}

function fetch() {
	return prompt('Input');
}

function int_str(i) {
	return '' + (i);
}

function $(elId) {
	return document.getElementById(elId);
}
function hio_init() {
	//put('hio_init...');
	HIO_OUT = $('hio_out');
	
	//put('main...');
	main();
	
}
window.onload = hio_init;