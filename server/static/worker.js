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

function deletecard(jobid) {
        if ( $("#" + jobid).length ) {
                $("#" + jobid).remove();
        };
}


function addcard(jobid, title) {
        var text = '<div class="col-sm-3" id="' + jobid + '"> <div class="card"> <img class="card-img-top img-fluid" src="/spinner.gif" alt="Creating Image"><div style="text-align: center; font-weight: bold;" class="card-block">' + title + '</div> </div> </div>';
        $('#cards').append(text);
	$('html,body').animate({scrollTop: $('#' + jobid).offset().top});
}

function failcard(jobid, title) {
        deletecard(jobid, title);

        var text = '<div class="col-sm-3" id="' + jobid + '"> <div class="card"> <div style="text-align: center; color: red; font-weight: bold;" class="card-block">' + title + ': Export failed.</div><div style="text-align: center;" class="card-block"> <a style="color: white;" onclick="deletecard(\'' + jobid + '\');" class="btn btn-danger">Hide</a></div> </div> </div>';
        $('#cards').append(text);
}


function finishcard(jobid, title) {
	deletecard(jobid);

	var text = '<div class="col-sm-3" id="' + jobid + '"> <div class="card"> <img class="card-img-top img-fluid" src="/getjob/' + jobid + '" alt="Final Image"><div style="text-align: center; font-weight: bold;" class="card-block">' + title + '</div> <div style="text-align: center; color: white;" class="card-block"> <a href="/getjob/' + jobid + '" class="btn btn-primary">Download</a> <a onclick="deletecard(\'' + jobid + '\');" class="btn btn-danger">Hide</a></div> </div> </div>';
	$('#cards').append(text);
}

$('#theform').submit(function(event){
	event.preventDefault();
	if(this.checkValidity()) { 
		$.ajax({
			type: "POST",
			url: "/addjob",
			data: $('#theform').serialize(),
			success: function(msg){
				var title = ($("#title").val() ? $("#title").val() : "No title");
				var interval = setInterval(checkServerForFile,3000,msg, title);
				window.panaxworking = false;
				addcard(msg, title);

				function checkServerForFile(jobid, title) {

					if (!window.panaxworking) {
						window.panaxworking = true;
						$.ajax({
							type: "GET",
							cache: false,
							url: "/getjob/" + jobid,
							statusCode: {
								404: function() {
									clearInterval(interval);
									failcard(jobid, title);
									return;
								},
								200: function() {
									clearInterval(interval);
									finishcard(jobid, title);
									return;
								},
								500: function() {
									clearInterval(interval);
									failcard(jobid, title);
									return;
								}
							}
						});
						window.panaxworking = false;
					};
				}

			}
		});}
});

