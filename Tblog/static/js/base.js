$(document).ready(function(){
    var location = window.location.href;
    var id = location.substring(location.lastIndexOf('/')+1);
    if (id === "") id="home";
    $("#"+id).addClass("active");
});