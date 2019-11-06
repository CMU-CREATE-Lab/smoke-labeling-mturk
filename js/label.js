(function () {
  "use strict";

  var util = new edaplotjs.Util();
  var video_labeling_tool;
  var video_test_dialog;
  var $submit;
  var counter = 0;
  var max_counter = 10;
  var count_down_duration = 2000; // in milliseconds
  var count_down_timeout;
  var _allowSubmit = false;

  function resetCountDown() {
    clearTimeout(count_down_timeout);
    $submit.removeClass("count-down-" + counter);
    counter = 0;
  }

  function countDown() {
    if (counter == 0) {
      $submit.addClass("count-down-0");
    }
    count_down_timeout = setTimeout(function () {
      $submit.removeClass("count-down-" + counter);
      if (counter == max_counter) {
        $submit.prop("disabled", false);
        counter = 0;
      } else {
        $submit.addClass("count-down-" + (counter + 1));
        counter += 1;
        countDown();
      }
    }, count_down_duration);
  }

  function gup(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regexS = "[\\?&]" + name + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec(window.location.href);
    if (results == null)
      return "";
    else
      return unescape(results[1]);
  }

  function submitToTurk() {
    if (gup("assignmentId") != "") {
      var jobkey = gup("assignmentId");
      if (gup("hitId") != "") {
        jobkey += "|" + gup("hitId");
      }
      if (gup("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE") {
        $("input").attr("disabled", "true");
        _allowSubmit = false;
      } else {
        _allowSubmit = true;
      }
      $("#mturk-assignmentId").attr("value", gup("assignmentId"));
      $("#mturk_form").attr('method', "POST");
      if (gup("turkSubmitTo") != "") {
        $("#mturk_form").attr('action', gup("turkSubmitTo") + '/mturk/externalSubmit');
      }
    }
    $("#mturk_form").submit();
    // For some reasons you need this
    return false;
  }

  function checkIfTaskAccepted() {
    if (gup("assignmentId") === "ASSIGNMENT_ID_NOT_AVAILABLE") {
      $("body").empty();
      $("body").css("background", "white");
      var noteDiv = $("<div class='container'><h3>Please accept the HIT.</h3></div>");
      $(noteDiv).css("margin-left", "auto");
      $(noteDiv).css("margin-right", "auto");
      $(noteDiv).css("text-align", "center");
      var img = $("<img></img>")
      $(img).attr("src", "https://c2.staticflickr.com/4/3665/11276962563_8fc141d195.jpg");
      /* image from https://flic.kr/p/ibvo62 */
      $(img).css("width", "600px");
      $(noteDiv).append(img);
      $("body").append(noteDiv);
      $("input").attr("disabled", "true");
      _allowSubmit = false;
    } else {
      _allowSubmit = true;
    }
  }

  function init() {
    // Check if worker accept the task
    checkIfTaskAccepted();
    // Add workaround for Safari iOS
    util.addVideoClearEvent();
    // Create the object for loading and showing videos
    video_labeling_tool = new edaplotjs.VideoLabelingTool("#labeling-tool-container");
    // Create the object for video autoplay testing
    video_test_dialog = new edaplotjs.VideoTestDialog();
    // Scroll the page to the top
    $(window).scrollTop(0);
    // Set and disable the submit button
    $submit = $("#submit");
    $submit.prop("disabled", true);
    resetCountDown();
    // Load and show videos
    video_labeling_tool.next({
      success: function () {
        // Add the click event for submission
        $submit.on("click", function () {
          $submit.prop("disabled", true);
          var labels = video_labeling_tool.collectAndRemoveLabels();
          console.log(labels);
          $("#label-data").attr("value", JSON.stringify(labels));
          $("#batch-id").attr("value", gup("batch_id"));
          submitToTurk();
        });
        // Check if video plays
        video_test_dialog.startVideoPlayTest(1000);
        // Start timer for the submission button
        countDown();
      }
    });
  }

  $(init);
})();