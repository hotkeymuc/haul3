function AppAssistant(appController) {
}

AppAssistant.prototype.handleLaunch = function(params) {
	//if params doesn't exist then it means a user is launching the app rather than an alarm
	//causing it to launch and we should get out of here.
	if (!params || (params["message"] == undefined)){
		return;
	}
	Mojo.Log.error("Alarm received.");

	// Get the default stage controller
	var stage_controller = this.controller.getStageProxy("");
	if (stage_controller == undefined) {
		Mojo.Log.error("App is closed - alarm ignored.");
		return;
	}
	
	Mojo.Log.error("Alarm activated");
	// Run the function keepAliveTimer to send a keepalive message
	stage_controller.delegateToSceneAssistant("keepAliveTimer");
};
