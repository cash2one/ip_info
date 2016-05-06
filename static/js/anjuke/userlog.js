$(document).ready(function(){
	var output_box = $("#output_box");
	var post_url = "/deploy/ajax/";
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
	
	$("#custom_button").bind('click',function(){
		var path = $("#customPath").val();
		var pattern = /^(\/data1\/logs\/|\/tmp\/)/i;
		var validate = path.search(pattern);
		if(validate == -1 ){
			var tipBoxDiv = createTipBox(tips,2);
			$(".tips").remove();
			$(this).after(tipBoxDiv);
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
		var tipBoxDiv = createTipBox(tips,1);
		$(".tips").remove();
		$("#custom_button").after(tipBoxDiv);
	})
	
});
	/**
	 * 
 * @param {Object} content 提示内容
 * @param {Object} type 提示类型 1为info  2为error
	 */
	function createTipBox(content,type){
		var tipBox = document.createElement("div");
		if(type==1){
			tipBox.className = "info tips";
		}else{
			tipBox.className = "error tips";
		}
		tipBox.style.width = "200px";
		tipBox.innerHTML = content;
		return tipBox;
	}
