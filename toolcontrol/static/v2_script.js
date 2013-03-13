$(document).ready(function() {
    $(document).ajaxSend(function(event, xhr, settings) {
	function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
			cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
			break;
                    }
		}
            }
            return cookieValue;
	}
	function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
		(url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
		// or any other URL that isn't scheme relative or absolute i.e relative.
		!(/^(\/\/|http:|https:).*/.test(url));
	}
	function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}
	
	if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	}
    });

    /* DELAY FUNCTION */
    var delay = (function(){
	var timer = 0;
	return function(callback, ms){
 	    clearTimeout (timer);
	    timer = setTimeout(callback, ms);
	};
    })();

    /* SEARCH FUNCTION */
    $('input.search').keyup(function() {
	delay(function(){
	    var search = $("input.search").val();
	    $("div#main").load(window.location.pathname, "search=" + search);
	}, 500 );
    });

    /* ORDERING OF LISTS */
    $(document).on("click", 'a.order_by', function() {
	var order_by = $(this).attr("href").replace("#","");
	var search = $("input.search").val();
	$("div#main").load(window.location.pathname, "search=" + search + "&order_by=" + order_by, function() {
	    if (order_by.substring(0, 1) == "-") {
		$("a#order_by-" + order_by.substring(1)).attr("href", "#" + order_by.substring(1));
	    }
	    else {
		$("a#order_by-" + order_by).attr("href", "#-" + order_by);
	    }
	});
	return false;
    });

    /* ACTION FUNCTION */
    $('select.action').change(function() {
	object_ids = []
	action = $(this).val();

	$("input.object_checkbox").filter(":checked").each(function() {
	    object_ids.push($(this).attr("name"));
	});

	window.location = window.location.pathname + action + "/?object_ids=" + object_ids.toString();
    });

    /* SELECT ALL CHECKBOX */
    $(document).on("click", "input.mark_all", function() {
	if($(this).is(":checked")) {
	    $("input.object_checkbox").attr("checked", true);
	    $("tr.object_line").addClass("selected");
	}
	else {
	    $("input.object_checkbox").attr("checked", false);
	    $("tr.object_line").removeClass("selected");
	}
    });

    /* SHOW DETAILS */
    $(document).on("click", "a.show_details", function() {
	var tool_id = $(this).attr("href").replace("#","");
	var tr_id = "details-" + tool_id;
	if($("tr#" + tr_id).is(":visible")) {
	    $("tr#" + tr_id + " div").slideUp(function() {
		$("tr#" + tr_id).hide();
	    });
	}
	else {
	    $("tr#" + tr_id + " div").load("/version2/vaerktoej/"+tool_id+"/", function() {
		$("tr#" + tr_id).show();
		$("tr#" + tr_id + " div").slideDown();
	    });
	}

	return false;
    });

    /* DROPDOWN MENU */
    $("a.menu-right").click(function(e) {
	e.stopPropagation();
	if($(this).hasClass("dropdown-selected")) {
	    $("div#dropdown").slideToggle(function() {
		$("a.menu-right").removeClass("dropdown-selected");
		$("html").off("click");
	    });
	}
	else {
	    $(this).addClass("dropdown-selected");
	    $("div#dropdown").slideToggle();
	    $("html").click(function() {
		$("div#dropdown").slideToggle(function() {
		    $("a.menu-right").removeClass("dropdown-selected");
		    $("html").off("click");
		});
	    });
	}
	return false;
    });
});
