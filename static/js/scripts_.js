$newp1 = $("<p>Model chosen: <span class='res' id='modele_choisi'></span></p>");
$newp2 = $("<p>Elapsed time for the 'Tag generation' task: <span class='res' id ='te'></span></p>");
$newp3 = $("<p>List of tags: <span class='res' id='res1'></span></p>");
$imgdiv = $("<span id='CLICK'>Click here:</span><img id='button_go' src='static/images/button0.jpg' />");

function toggle_button(active){
    if (active==1) $("#divimg").append($imgdiv);  else $("#divimg").empty();
}

$(document).ready(function() {
    //onclick actions _ for submitted
    toggle_button(1);

    $(document).on('click','#button_go',function(){
        //input
        console.log('button clicked');
        toggle_button(0); // disable click
        var question = $("#QU_id").val();
        var model = $("form input[type='radio']:checked").val();
        console.log (question, model);
        //indicating loading

        $('#output').empty();
        $('#qu3').empty();
        $('#output_error').empty();
        $('#output').text("Loading results for model '" + model + "' and question: '" + question + "'")
        ApplyStyle("#output");
        //launch background tasks
        send_job(question, model);
        //check if output has been received
        //update with ajax if done
    });

    //onclick actions _ entering question
    var clickinput = 0 ;
    $(document).on('click','#QU_id',function(){
        console.log('input clicked');
        if (clickinput == 0) {
            $(this).val("");
            clickinput = 1;
        }
    });
});

///////////////////////// functions //////////////////////////////
function ApplyStyle(elem) {
    $(elem).css("paddingLeft", "60px");
    $(elem).css("fontWeight","500");
    $(elem).css("color","#99004d");
    $(elem).css("fontStyle","italic");
}

function send_job(question, model){
  // Ajax POST request to upload_file() in the API
    var formData = new FormData();
    formData.append('input_user', question);
    formData.append('model', model);
    $.ajax({
        type: 'POST',
        url: Flask.url_for('create_job'),
        data: formData,
        cache: false,
        processData: false,
        contentType: false
    })
        // If done, get the status of the background job that was started and launch function to do when finished
        .done((response) => {
              console.log("AJAX response retrieved:");
              console.log(response.status);
              console.log(response.data.job_ID, ' ', response.data.model);
              MODEL = response.data.model;
              console.log(MODEL);
              get_status(response.data.job_ID, MODEL, 0);
        })

        .fail((error) => {
            console.log("ajax fail on send_job: " + error);
            toggle_button(1);
        });
}

function get_status(jobID, MODEL,i){
    $.ajax({
          type: 'GET',
          url: '/job',
          data: 'jid=' + jobID
    })
          .done((response) => {
              const jobStatus = response.data.jobStatus;
              console.log('Attempt n° ' + i);
              console.log('jid = ' + jobID);
              console.log('jobStatus = ' + jobStatus);
              if (jobStatus == 'finished') {
                  // Parse the returned JSON and displays output
                  console.log('JOB FINI');
                  main_output = response.data.list_tags_or_errmsg;
                  te = response.data.te;
                  err = response.data.iserror;
                  console.log('err value: ' + err )
                  if (err == true) {display_output(MODEL, '', te, true, main_output);} //job finished, but the task could not be completed properly.
                  else {display_output(MODEL, main_output, te, false, '');}
                  toggle_button(1);
                  return true;
              }
              else if (jobStatus == 'stopped' || jobStatus == 'canceled' || jobStatus == 'failed' || jobStatus == 'no job found!') {
                  console.log(response);
                  toggle_button(1);
                  if (jobStatus == 'no job found!') {errmsg = 'No job found. Request terminated.'}
                  else {errmsg = "The job is in status '" + jobStatus + "'."}
                  display_output(MODEL, listtags, te, true, errmsg);
                  return false;
              }

              // If the task hasn't been finished, try again in 1 second.
              else{                                                           //#queued, started, deferred, scheduled
                  setTimeout(function() {
                      i=i+1;
                      console.log('Next round for i: ' + i);
                      console.log('');
                      get_status(jobID, MODEL, i);
                  }, 1000);
              }
          })
          .fail((error) => {
              console.log("ajax fail on get_status: " + error);
              toggle_button(1);
          });
}

display_output = function (model, listtags, te, joberr, err_msg) {
  //clean any previous content
  $('#output').empty();
  $('#qu3').empty();
  $('#output_error').empty();

  if (joberr==true) {
    $('#output_error').append(err_msg);
    ApplyStyle("#output_error");
  }
  else {
    //update content
    $('#qu3').append('Results:');
    console.log('success ___: ' + model + ' _ ' + te + ' _ ' + listtags);
    $('#output').append($newp1);
    $('#output').append($newp2);
    $('#output').append($newp3);
    $('#modele_choisi').empty();
    $('#modele_choisi').text(model);
    $('#te').empty();
    $('#te').text(te);
    $('#res1').empty();
    $('#res1').text(listtags);
  }
}
