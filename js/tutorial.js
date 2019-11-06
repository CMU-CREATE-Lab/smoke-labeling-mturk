(function () {
  "use strict";

  var util = new edaplotjs.Util();
  var tutorial_tool;
  var video_test_dialog;
  var is_video_autoplay_tested = false;
  var $next;
  var counter = 0;
  var max_counter = 10;
  var count_down_duration = 0; // in milliseconds
  var count_down_timeout;
  var _allowSubmit = false;

  function resetCountDown() {
    clearTimeout(count_down_timeout);
    $next.removeClass("count-down-" + counter);
    counter = 0;
  }

  function countDown() {
    if (counter == 0) {
      $next.addClass("count-down-0");
    }
    count_down_timeout = setTimeout(function () {
      $next.removeClass("count-down-" + counter);
      if (counter == max_counter) {
        $next.prop("disabled", false);
        counter = 0;
      } else {
        $next.addClass("count-down-" + (counter + 1));
        counter += 1;
        countDown();
      }
    }, count_down_duration);
  }

  function next() {
    $next.prop("disabled", true);
    resetCountDown();
    $(window).scrollTop(0);
    tutorial_tool.next({
      success: function () {
        if (!is_video_autoplay_tested) {
          video_test_dialog.startVideoPlayTest(1000);
          is_video_autoplay_tested = true;
        }
        countDown();
      }
    });
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
      $(noteDiv).css("color", "white");
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
    // Add event to the buttons
    $next = $("#next");
    $next.on("click", function () {
      next();
    });
    $("#label").on("click", function () {
      submitToTurk();
    });
    // Create the object for the tutorial
    tutorial_tool = new edaplotjs.TutorialTool("#tutorial-tool-container", {
      data: tutorial_data, // this is in tutorial_data.js
      on_tutorial_finished: function () {
        $next.hide();
        $("#label").removeClass("force-hidden");
        $("#tutorial-end-text").removeClass("force-hidden");
        $("#tutorial-tool-container").hide();
      }
    });
    // Create the object for video autoplay testing
    video_test_dialog = new edaplotjs.VideoTestDialog();
    // Start the tutorial
    next();
  }

  $(init);
})();