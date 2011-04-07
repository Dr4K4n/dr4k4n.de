$(document).ready(function(){

    $(".ie").load("js/ie.html"); // Load the IE warning into a div with a class of ie

    $(".flash").delay(2000).slideUp("slow");
    
    $(".error").delay(5000).slideUp("slow");    
        
    $(".twitter").load("/backend/getTweets"); // Load twitter feeds
    
    $("#page_menu_show").click(function () {
        $("#page_parent").toggle();
        $("#page_parent_label").toggle();
    });

	$('.dropdown').each(function () {
		$(this).parent().eq(0).hoverIntent({
			timeout: 100,
			over: function () {
				var current = $('.dropdown:eq(0)', this);
				current.slideDown();
			},
			out: function () {
				var current = $('.dropdown:eq(0)', this);
				current.fadeOut();
			}
		});
	});	

    $(".dropdown a").hover(function () {
        $(this).stop(true).animate({paddingLeft: "35px"}, {duration: 50, easing: 'easeOutBack'});
    }, function () {
        $(this).stop(true).animate({paddingLeft: "10px"}, {duration: 250, easing: 'easeOutBounce'});
    });
    
});
