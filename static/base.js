$(function () {
    console.log("active les tooltips")
    $('[data-toggle="tooltip"]').tooltip()
})

$("document").ready(function(){
    setTimeout(function(){
        $("#flash_msg").remove();
    }, 3000 ); 
});