$("#options").hide();

$body = $("body");

function toggleOptions() {
	$("#options").toggle();
}

function lockform() {
	$("#theform :input").prop("disabled", true);
	$body.addClass("loading");
}

function unlockform() {
	$("#theform :input").prop("disabled", false);
	$body.removeClass("loading");
}

$('#theform').submit(function(event){
	event.preventDefault();
	if(this.checkValidity()) { 
		$.ajax({
			type: "POST",
			url: "/addjob",
			data: $('#theform').serialize(),
			success: function(msg){
				lockform();
				interval = setInterval(checkServerForFile,3000,msg);
				window.panaxworking = false;
				function checkServerForFile(jobid) {
					if (!window.panaxworking) {
						window.panaxworking = true;
						$.ajax({
							type: "GET",
							cache: false,
							url: "/getjob/" + jobid,
							statusCode: {
								404: function() {
									clearInterval(interval);
									unlockform();
								},
								200: function() {
									clearInterval(interval);
									unlockform();
									window.location.href = "/getjob/" + jobid;
								},
								500: function() {
									clearInterval(interval);
									window.alert("Failed to process request. The URL may be incorrect or unsupported.")
									unlockform();
								}
							}
						});
						window.panaxworking = false;
					};
				}

			}
		});}
});

