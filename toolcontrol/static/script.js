$(document).ready(function() {
    var timeout_id;

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

    $("div#content").load("/tool_list/");
    $("div#banner_left").load("/tool_banner/");
    $("div.popup#add").load("/tool_form/");

    // Print handling
    $(document).on("click", "a.print", function() {
	window.print();
	return false;
    });

    // Popup handling
    $(document).on("click", "a.popup", function() {
	var id = $(this).attr("id");
	var popupBox = "div.popup#"+id;

	if(id == "add") {
	    if($(this).attr("href") == "#add_many_tools") {
		var object_type = "add_many_tools";
	    }
	    else {
		var object_type = $("table#index_navigation td.selected").attr("id");
	    }
	    $("div.popup#add").load("/"+object_type+"_form/");
	}

	//Set the center alignment padding + border
	var popMargTop = ($(popupBox).height() + 24) / 2; 
	var popMargLeft = ($(popupBox).width() + 24) / 2; 
	
	$(popupBox).css({ 
	    'margin-top' : -popMargTop,
	    'margin-left' : -popMargLeft
	});

	//Fade in the popup
	$(popupBox).fadeIn('slow');
		
	// Add the mask to body
	$('body').append('<div id="mask"></div>');
	$('#mask').fadeIn('fast');
	
	return false;
    });
    
    // When clicking on the mask layer the popup closes
    $(document).on('click', "div#mask", function() { 
	$('#mask').fadeOut('fast', function() {
	    $('#mask').remove();
	}); 
	$('div.popup').fadeOut('slow'); 
    });

    // Navigation for the main page
    $("table#index_navigation td").click(function() {
	$('body').append('<div id="mask"></div>');
	$('body').append('<img id="loader" src="/static/ajax-loader.gif">');
	$('#mask').fadeIn('fast');
	$("td.selected").removeClass("selected");
	$(this).addClass("selected");

	var page_to_load = $(this).attr("id");
	$("div#banner_left").load("/"+page_to_load+"_banner/");
	$("div.popup#add").load("/"+page_to_load+"_form/");
	$("div#content").load("/"+page_to_load+"_list/", function() {
	    $("#loader").remove();
	    $('#mask').fadeOut('fast', function() {
		$('#mask').remove();
	    });
	});
	
	// Reset the search box
	$("input#search").val("");
    });

    // Creating or editing an object
    $(document).on("click", "input.add", function() {
	var object_type = $('form.add').attr("id");
	$.post("/"+object_type+"_form/", $('form.add').serialize(), function(data) {
	    if(data.status == "success") {
		// Reload the page
		if(object_type == "loan" || object_type == "reservation" || object_type == "add_many_tools") {
		    $("div#content").load("/tool_list/");
		}
		else if(object_type == "container_loan") {
		    $("div#content").load("/container_list/");
		}
		else {
		    $("div#content").load("/"+object_type+"_list/");
		}
		set_message(data.response);
		
		// Close the popup
		$('#mask').fadeOut('fast', function() {
		    $('#mask').remove();
		}); 
		$('div.popup').fadeOut('slow'); 
	    }
	    else {
		$("div.popup#add").html(data.response);
	    }
	});

	return false;
    });

    // Search function
    var delay = (function(){
	var timer = 0;
	return function(callback, ms){
 	    clearTimeout (timer);
	    timer = setTimeout(callback, ms);
	};
    })();

    $('input#search').keyup(function() {
	delay(function(){
	    var search = $("input#search").val();
	    var object_type = $("table#index_navigation td.selected").attr("id"
);
	    $("div#content").load("/"+object_type+"_list/", 
				  "search="+search);
	}, 500 );
    });

    // Action functions
    $(document).on("change", "form#banner select", function() {
	var object_type = $("table#index_navigation td.selected").attr("id");
	var action = $("form#banner select option:selected").attr("name");
	var search = $("input#search").val();

	object_ids = []

	$("input.object_checkbox").filter(":checked").each(function() {
	    object_ids.push($(this).attr("name"));
	});

	if (action == "loan") {
	    var popupBox = "div.popup#add";
	    
	    $(popupBox).load("/loan_form/", function() {
		$("input#id_tools").attr("value", object_ids.toString());
		
		//Set the center alignment padding + border
		var popMargTop = ($(popupBox).height() + 24) / 2; 
		var popMargLeft = ($(popupBox).width() + 24) / 2; 
		
		$(popupBox).css({ 
		    'margin-top' : -popMargTop,
		    'margin-left' : -popMargLeft
		});

	    });

            //Fade in the popup
	    $(popupBox).fadeIn('slow');
	    
	    // Add the mask to body
	    $('body').append('<div id="mask"></div>');
	    $('#mask').fadeIn('fast');
	}
	else if (action == "container_loan") {
	    var popupBox = "div.popup#add";

	    $(popupBox).load("/container_loan_form/", function() {
		$("input#id_containers").attr("value", object_ids.toString());
		//Set the center alignment padding + border
		var popMargTop = ($(popupBox).height() + 24) / 2; 
		var popMargLeft = ($(popupBox).width() + 24) / 2; 
		
		$(popupBox).css({ 
		    'margin-top' : -popMargTop,
		    'margin-left' : -popMargLeft
		});
	    });

            //Fade in the popup
	    $(popupBox).fadeIn('slow');
	    
	    // Add the mask to body
	    $('body').append('<div id="mask"></div>');
	    $('#mask').fadeIn('fast');
	}
	else if (action == "reserve") {
	    var popupBox = "div.popup#add";
	    
	    $(popupBox).load("/reservation_form/", function() {
		$("input#id_tools").attr("value", object_ids.toString());
		//Set the center alignment padding + border
		var popMargTop = ($(popupBox).height() + 24) / 2; 
		var popMargLeft = ($(popupBox).width() + 24) / 2; 
		
		$(popupBox).css({ 
		    'margin-top' : -popMargTop,
		    'margin-left' : -popMargLeft
		});
	    });
	    
            //Fade in the popup
	    $(popupBox).fadeIn('slow');
	    
	    // Add the mask to body
	    $('body').append('<div id="mask"></div>');
	    $('#mask').fadeIn('fast');
	}
	else {
	    $.post("/"+object_type+"_action/", "object_ids=" + object_ids.toString() + "&action=" + action, function(data) {
		$("div#content").load("/"+object_type+"_list/", "search="+search);
		set_message(data.response);
	    });
	}
	
	$(this).val("nothing");
    });

    // Show tool history
    $(document).on("click", "a.show_history", function() {
	var tool = $(this).attr("id");

	if($("tr#"+tool+".history").is(":visible")) {
	    $("tr#"+tool+".history div").slideUp(function() {
		$("tr#"+tool+".history").hide();
	    });
	}
	else {
	    $("tr#" + tool + ".history div").load("/event_list/", "tool_id=" + tool, function() {
		$("tr#"+tool+".history").show();
		$("tr#"+tool+".history div").slideDown();
	    });
	}

	return false;
    });

    // Show loans for a loaner
    $(document).on("click", "a.show_loans", function() {
	var loaner = $(this).attr("id");
	var object_type = $("table#index_navigation td.selected").attr("id");
	
	if($("tr#"+loaner+".history").is(":visible")) {
	    $("tr#"+loaner+".history div").slideUp(function() {
		$("tr#"+loaner+".history").hide();
	    });
	}
	else {
	    $("tr#" + loaner + ".history div").load("/loan_list/", "loaner_id=" + loaner + "&object_type=" + object_type, function() {
		$("tr#"+loaner+".history").show();
		$("tr#"+loaner+".history div").slideDown();
	    });
	}

	return false;
    });


    // Show tools for a model
    $(document).on("click", "a.show_model_tools", function() {
	var model = $(this).attr("id");

	if($("tr#"+model+".tools").is(":visible")) {
	    $("tr#"+model+".tools div").slideUp(function() {
		$("tr#"+model+".tools").hide();
	    });
	}
	else {
	    $("tr#" + model + ".tools div").load("/simple_tool_list/", "model_id=" + model + "&show_model=false", function() {
		$("tr#"+model+".tools").show();
		$("tr#"+model+".tools div").slideDown();
	    });
	}

	return false;
    });

    // Show tools for a category
    $(document).on("click", "a.show_category_tools", function() {
	var category = $(this).attr("id");
	if($("tr#"+category+".tools").is(":visible")) {
	    $("tr#"+category+".tools div").slideUp(function() {
		$("tr#"+category+".tools").hide();
	    });
	}
	else {
	    $("tr#" + category + ".tools div").load("/simple_tool_list/", "category_id=" + category + "&show_model=true", function() {
		$("tr#"+category+".tools").show();
		$("tr#"+category+".tools div").slideDown();
	    });
	}

	return false;
    });

    // Show tools for a container
    $(document).on("click", "a.show_container_tools", function() {
	var container = $(this).attr("id");
	if($("tr#"+container+".tools").is(":visible")) {
	    $("tr#"+container+".tools div").slideUp(function() {
		$("tr#"+container+".tools").hide();
	    });
	}
	else {
	    $("tr#" + container + ".tools div").load("/simple_tool_list/", "container_id=" + container + "&show_model=true", function() {
		$("tr#"+container+".tools").show();
		$("tr#"+container+".tools div").slideDown();
	    });
	}
	return false;
    });

    // Message handling
    function set_message(message) {
	clearTimeout(timeout_id);

	$("div#messages").html("<p>"+message+"</p>");

	//Set the center alignment padding + border
	var popMargTop = ($("div#messages").height() + 20) / 2; 
	var popMargLeft = ($("div#messages").width() + 20) / 2; 
	
	$("div#messages").css({ 
	    'margin-top' : -popMargTop,
	    'margin-left' : -popMargLeft
	});

	$("div#messages").fadeIn();

	timeout_id = setTimeout(function() {
	    $("div#messages").fadeOut();
	}, 5000);
    }

    // Click sort link
    $(document).on("click", "a.set_sorting", function() {
	$('body').append('<div id="mask"></div>');
	$('body').append('<img id="loader" src="/static/ajax-loader.gif">');
	$('#mask').fadeIn('fast');

	var object_type = $("table#index_navigation td.selected").attr("id");
	var search = $("input#search").val();
	var sorting = $(this).attr("id");
	$("div#content").load("/" + object_type + "_list/", "search=" + search + "&sorting=" + sorting, function() {
	    $("#loader").remove();
	    $('#mask').fadeOut('fast', function() {
		$('#mask').remove();
	    });
	});
	
	return false;
    });

    // Click order link
    $(document).on("click", "a.set_ordering", function() {
	$('body').append('<div id="mask"></div>');
	$('body').append('<img id="loader" src="/static/ajax-loader.gif">');
	$('#mask').fadeIn('fast');

	var object_type = $("table#index_navigation td.selected").attr("id");
	var search = $("input#search").val();
	var ordering = $(this).attr("id");

	$("div#content").load("/"+object_type+"_list/", "search="+search+"&ordering="+ordering, function() {
	    $("#loader").remove();
	    $('#mask').fadeOut('fast', function() {
		$('#mask').remove();
	    });
	});

	return false;
    });

    // Handle edits
    $(document).on("click", "a.edit", function() {
	var object_type = $(this).attr("id");
	var object_id = $(this).attr("href").replace("#","");
	$("div.popup#add").load("/"+object_type+"_form/", "id="+object_id, function() {
	    var popupBox = "div.popup#add";
	    
	    //Set the center alignment padding + border
	    var popMargTop = ($(popupBox).height() + 24) / 2; 
	    var popMargLeft = ($(popupBox).width() + 24) / 2; 
	    
	    $(popupBox).css({ 
		'margin-top' : -popMargTop,
		'margin-left' : -popMargLeft
	    });
	    
	    //Fade in the popup
	    $(popupBox).fadeIn('slow');
	    
	    // Add the mask to body
	    $('body').append('<div id="mask"></div>');
	    $('#mask').fadeIn('fast');
	});
	return false;
    });

    // When clicking an input box, mark the whole line
    $(document).on("click", "input.object_checkbox", function() {
	var object_id = $(this).attr("name");
	$("tr.object_line#"+object_id).toggleClass("selected");
    });

    // Menu handling
    $(document).on("click", "div#menu", function() {
	$("div#menu_hidden").slideDown();

	// Click a menu link
	$(document).on("click", "div.menu_item", function() {
	    window.location.href = "/"+$(this).attr("id");
	    return false;
	});

	$("body").click(function() {
	    $("div#menu_hidden").slideUp();
	    $("body").off("click");
	});

    });

    // Mark all-checkbox
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
    
    // Delete something
    $(document).on("click", "a.delete", function() {
	var object_type = $("table#index_navigation td.selected").attr("id");
	$("div.popup#delete form").attr("action", "/"+object_type+"_delete/");
	$("div.popup#delete p").text("Er du sikker på, at du vil slette " + $(this).attr("id") + "?");
	$("div.popup#delete input#id").attr("value", $(this).attr("href").replace("#",""));
	
	var popupBox = "div.popup#delete";
	//Set the center alignment padding + border
	var popMargTop = ($(popupBox).height() + 24) / 2; 
	var popMargLeft = ($(popupBox).width() + 24) / 2; 
	
	$(popupBox).css({ 
	    'margin-top' : -popMargTop,
	    'margin-left' : -popMargLeft
	});
	
        //Fade in the popup
	$(popupBox).fadeIn('slow');
	
	// Add the mask to body
	$('body').append('<div id="mask"></div>');
	$('#mask').fadeIn('fast');
	
	return false;
    });

    // Handle deletes when confirmed
    $(document).on("submit", "form#delete", function() {
	var id = $("div.popup#delete input#id").attr("value");
	var object_type = $("table#index_navigation td.selected").attr("id");
	var search = $("input#search").val();
	$.post($(this).attr("action"), "id="+id, function(data) {
	    $("tr.object_line#"+id).fadeOut();
	    set_message(data.response);
	});

	// Close the popup
	$('#mask').fadeOut('fast', function() {
	    $('#mask').remove();
	}); 
	$('div.popup').fadeOut('slow'); 

	return false;
    });

    $(document).on("click", "a.delete_event", function() {
	var object_id = $(this).attr("href").replace("#","");
	var search = $("input#search").val();

	$.get("/event_delete/", "id="+object_id, function(data) {
	    set_message(data.response);
	    $("div#content").load("/tool_list/", "search="+search);
	});
	return false;
    });

    $(document).on("click", "a.delete_reservation", function() {
	var object_id = $(this).attr("href").replace("#","");
	var search = $("input#search").val();

	$.get("/reservation_delete/", "id="+object_id, function(data) {
	    set_message(data.response);
	    $("div#content").load("/tool_list/", "search="+search);
	});
	return false;
    });


    // When adding a tool, if the model is changed, update service and price
    $(document).on("change", "select#id_model", function() {
	var id = $(this).val();
	$.getJSON("/model_object/", "id="+id, function(data) {
	    var model = $.parseJSON(data.model)[0];
	    $("input#id_service_interval").val(model.fields.service_interval);
	    if (model.fields.price != 0) {
		$("input#id_price").val(model.fields.price);
	    }
	});
    });

    // Inline forms
    $(document).on('click', 'img.add_inline', function() {
	var id = $(this).attr("id");
	if($("tr.add_inline#" + id).is(":visible")) {
	    $("tr.add_inline#" + id + " div").slideUp(function() {
		$("tr.add_inline#" + id).hide();
		$("tr.add_inline#" + id + " div").text("Inline form ikke hentet korrekt")
	    });
	}
	else {
	    $("tr.add_inline#" + id + " div").load("/" + id + "_inline_form/", function() {
		$("tr.add_inline#" + id).show();
		$("tr.add_inline#" + id + " div").slideDown();
	    });
	}
	
    });
    $(document).on("click", "input.add_inline", function() {
	var id = $(this).attr("id");

	$.post("/"+id+"_inline_form/", $('form.add').serialize(), function(data) {
	    if(data.status == "success") {
		$("tr.add_inline#" + id + " div").slideUp(function() {
		    $("tr.add_inline#" + id).hide();
		});
		$("select#id_" + id).append($("<option></option>")
					    .attr("value", data.value)
					    .text(data.name));
		$("tr.add_inline#" + id + " div").text("Inline form ikke hentet korrekt")
		set_message(data.response);
	    }
	    else {
		$("tr.add_inline#" + id + " div").html(data.response);
	    }
	});

	return false;
    });

    $(document).on("click", "a.admin_pane", function() {
	$("div.admin_pane").hide();
	var pane_id = $(this).attr("id");
	$("div.admin_pane#" + pane_id).show();
	return false;
    });

});
