$(document).ready(function() {
    $(document).on("click", "a.admin_pane", function() {
	$("div.admin_pane").hide();
	var pane_id = $(this).attr("id");
	$("div.admin_pane#" + pane_id).show();
	return false;
    });
});

