$(document).ready(function(){

    $(".ie").load("js/ie.html"); // Load the IE warning into a div with a class of ie

    $(".flash").delay(2000).slideUp("slow");
    
    $(".error").delay(5000).slideUp("slow");    
        
    $(".twitter").load("/backend/getTweets"); // Load twitter feeds
    
    $(".dropdown").each(function () {
        $(this).parent().eq(0).hover(function () {
            $(".dropdown:eq(0)", this).show();
        }, function () {
            $(".dropdown:eq(0)", this).hide();
        });
    });
    
});
