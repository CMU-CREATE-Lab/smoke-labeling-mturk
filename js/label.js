(function () {
  "use strict";

  var util = new edaplotjs.Util();
  var video_labeling_tool;
  var video_test_dialog;
  var $next;
  var counter = 0;
  var max_counter = 10;
  var count_down_duration = 2000; // in milliseconds
  var count_down_timeout;

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

  function init() {
    util.addVideoClearEvent();;
    video_labeling_tool = new edaplotjs.VideoLabelingTool("#labeling-tool-container");
    video_test_dialog = new edaplotjs.VideoTestDialog();
    $next = $("#next");
    $next.prop("disabled", true);
    $next.on("click", function () {
      var labels = video_labeling_tool.collectAndRemoveLabels();
      console.log(labels);
      $next.prop("disabled", true);
    });
    resetCountDown();
    $(window).scrollTop(0);
    video_labeling_tool.next({
      success: function () {
        video_test_dialog.startVideoPlayTest(1000);
        countDown();
      }
    });
  }

  $(init);
})();