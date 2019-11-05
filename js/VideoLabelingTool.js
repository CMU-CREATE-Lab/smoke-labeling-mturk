(function () {
  "use strict";

  ////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //
  // Create the class
  //
  var VideoLabelingTool = function (container_selector, settings) {
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    // Variables
    //
    var util = new edaplotjs.Util();
    settings = safeGet(settings, {});
    var $container = $(container_selector);
    var $tool;
    var $tool_videos;
    var video_items = [];
    var $error_text = $('<span class="error-text">Oops!<br>Some errors happened.<br>Please try again later.</span>');
    var $loading_text = $('<span class="loading-text"></span>');
    var $not_supported_text = $('<span class="not-supported-text">We are sorry!<br>Your browser is not supported.</span>');

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    // Private methods
    //
    function init() {
      $tool = $('<div class="video-labeling-tool"></div>');
      $tool_videos = $('<div class="video-labeling-tool-videos"></div>');
      $container.append($tool.append($tool_videos));
      showLoadingMsg();
    }

    // Create a video label element
    // IMPORTANT: Safari on iPhone only allows displaying maximum 16 videos at once
    // UPDATE: starting from Safari 12, more videos are allowed
    function createVideo(i) {
      var $item = $("<a href='javascript:void(0)' class='flex-column'></a>");
      var $caption = $("<div>" + (i + 1) + "</div>");
      // "autoplay" is needed for iPhone Safari to work
      // "preload" is ignored by mobile devices
      // "disableRemotePlayback" prevents chrome casting
      // "playsinline" and "playsInline" prevents playing video fullscreen
      var $vid = $("<video autoplay preload loop muted playsinline playsInline disableRemotePlayback></video>");
      $item.on("click", function () {
        toggleSelect($(this));
      });
      $item.append($vid).append($caption);
      return $item;
    }

    // Update the videos with a new batch of urls
    function updateVideos(video_data, callback) {
      var deferreds = [];
      // Add videos
      for (var i = 0; i < video_data.length; i++) {
        var v = video_data[i];
        var $item;
        if (typeof video_items[i] === "undefined") {
          $item = createVideo(i);
          video_items.push($item);
          $tool_videos.append($item);
        } else {
          $item = video_items[i];
          removeSelect($item);
        }
        $item.data("id", v["id"]);
        var $vid = $item.find("video");
        $vid.one("canplay", function () {
          // Play the video
          util.handleVideoPromise(this, "play");
        });
        if (!$vid.complete) {
          var deferred = $.Deferred();
          $vid.one("canplay", deferred.resolve);
          $vid.one("error", deferred.reject);
          deferreds.push(deferred);
        }
        var src_url = v["url_root"] + v["url_part"];
        // There is a bug that the edge of small videos have weird artifacts on Google Pixel Android 9.
        // The current workaround is to make the thumbnail larger.
        if (util.getAndroidVersion() == 9) {
          src_url = util.replaceThumbnailWidth(src_url, 320);
        }
        $vid.prop("src", src_url);
        util.handleVideoPromise($vid.get(0), "load"); // load to reset video promise
        if ($item.hasClass("force-hidden")) {
          $item.removeClass("force-hidden");
        }
      }
      // Hide exceeding videos
      for (var i = video_data.length; i < video_items.length; i++) {
        var $item = video_items[i];
        if (!$item.hasClass("force-hidden")) {
          $item.addClass("force-hidden");
        }
      }
      // Load and show videos
      callback = safeGet(callback, {});
      util.resolvePromises(deferreds, {
        success: function (data) {
          updateTool($tool_videos);
          if (typeof callback["success"] === "function") callback["success"](data);
        },
        error: function () {
          console.error("Some video urls are broken.");
          showErrorMsg();
        }
      });
    }

    // Toggle the "select" class of a DOM element
    function toggleSelect($element) {
      if ($element.hasClass("selected")) {
        $element.removeClass("selected");
      } else {
        $element.addClass("selected");
      }
    }

    // Remove the "select" class of a DOM element
    function removeSelect($element) {
      if ($element.hasClass("selected")) {
        $element.removeClass("selected");
      }
    }

    function updateTool($new_content) {
      $tool_videos.detach(); // detatch prevents the click event from being removed
      $tool.empty().append($new_content);
    }

    // Show not supported message
    function showNotSupportedMsg() {
      updateTool($not_supported_text);
    }

    // Show error message
    function showErrorMsg() {
      updateTool($error_text);
    }

    // Show loading message
    function showLoadingMsg() {
      updateTool($loading_text);
    }

    function safeGet(v, default_val) {
      return util.safeGet(v, default_val);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    // Public methods
    //
    this.next = function (callback) {
      callback = safeGet(callback, {});
      if (util.browserSupported()) {
        var query_paras = util.parseVars(window.location.search);
        var batch_id = query_paras["batch_id"]; // Starting from 0
        if (typeof batch_id === "undefined") {
          console.error("No 'batch_id' field in the query string.");
          showErrorMsg();
        } else {
          $.getJSON("mturk_batch.json", function (data) {
            var batch = data[parseInt(batch_id)];
            if (typeof batch === "undefined") {
              console.error("No batch data for the batch id.");
              showErrorMsg();
            } else {
              updateVideos(batch, {
                success: function () {
                  if (typeof callback["success"] === "function") callback["success"]();
                }
              });
            }
          }).fail(function () {
            console.error("Error when loading batch data!");
            showErrorMsg();
          });
        }
      } else {
        showNotSupportedMsg();
        console.error("Browser not supported.")
      }
    };

    // Collect labels from the user interface
    this.collectAndRemoveLabels = function () {
      var labels = [];
      $tool_videos.find("a").each(function () {
        var $item = $(this);
        var video_id = $item.data("id");
        if (typeof video_id === "undefined") return;
        var is_selected = $item.hasClass("selected") ? 1 : 0;
        labels.push({
          video_id: video_id,
          label: is_selected
        });
        $item.removeData("id")
      });
      return labels;
    };

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    // Constructor
    //
    init();
  };

  ////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //
  // Register to window
  //
  if (window.edaplotjs) {
    window.edaplotjs.VideoLabelingTool = VideoLabelingTool;
  } else {
    window.edaplotjs = {};
    window.edaplotjs.VideoLabelingTool = VideoLabelingTool;
  }
})();