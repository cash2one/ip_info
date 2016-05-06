$(document).ready(function(){
	var output_box = $("#output_box");
	var post_url = "/tools/ajax/";
	var tips = "当前可以查看的远程目录有<br/> \
		1, /data1/logs/XXX <br/> \
		2, /tmp/XXX <br/> \
		";
	$("#select_server .server").bind('click',function(){
		var server_name = $(this).html();
		var tips = "正在获取"+server_name+"的userlog信息....";
		output_box.val(tips);
		var params = {'action':'fetch_user_log','serverName':server_name}
		$.get(post_url,params,function(response){
			output_box.val(response)
		});
	});

    $("#select_server .jsName").bind('click',function(){
        var js_name = $(this).html();
        console.log(js_name);
        var tips = "正在获取"+js_name+"的mlog信息....";
        output_box.val(tips);
        var params = {'action':'fetch_js_log','jsName':js_name}
        $.get(post_url,params,function(response){
            output_box.val(response)
        });
    });

	
	$("#custom_button").bind('click',function(){
		var path = $("#customPath").val();
		var pattern = /^(\/data1\/logs\/|\/tmp\/)/i;
		var validate = path.search(pattern);
		if(validate == -1 ){
			showInfo(tips);
			return ;
		}else{
			if($('.tips').length){
				$(".tips").remove();
			}
			var server_name = $("#server_select option:selected").val();
			output_box.val("正在获取["+server_name+"]自定义文件。。。");
			params = {'action':'fetch_user_log','serverName':server_name,'path':path};
			
			$.get(post_url,params,function(response){
				output_box.val(response);
			})
		}
	})
	
	$("#helpAcer").bind('click',function(){
		showInfo(tips);
	})
	
});
