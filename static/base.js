$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

$("document").ready(function(){
    setTimeout(function(){
        $("#flash_msg").remove();
    }, 3000 ); 
});

const setCurrentNavBarColor = (navName) => {
    el = document.getElementById(navName)
    el.style.backgroundColor = "#0069d9";
    el.childNodes[0].style.color = "#fff";
}