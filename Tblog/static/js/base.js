$(document).ready(function(){
    var location = window.location.href;
    if (location.lastIndexOf("?") != -1){
        var id = location.substring(location.lastIndexOf('/')+1,location.lastIndexOf("?"));
    }else{
    var id = location.substring(location.lastIndexOf('/')+1)
    }
    if (id === "") id="home";
    $("#"+id).addClass("active");
});