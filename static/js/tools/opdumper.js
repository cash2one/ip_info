var post_url = "/tools/ajax/";
$(document).ready(function(){
    $('#submit').bind('click',function(){
        var phpScript = $("#inputBox").val();
        $.get(post_url,{'action':'get_opcode','script':phpScript},function(response){
            $("#outputBox").empty().html(response); 
        })
    });
});
