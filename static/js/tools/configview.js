$(document).ready(function(){
	var output_box = $("#output_box");
	var post_url = "/tools/ajax/";
	var tips = "当前可以查看的远程目录有<br/> \
		1, /data1/logs/XXX <br/> \
		2, /tmp/XXX <br/> \
		";
	$("#select_server .server").bind('click',function(){
		var server_name = $(this).html();
		var tips = "正在获取"+server_name+"的配置文件列表....";
		output_box.val(tips);
		var params = {'action':'fetch_config_list','serverName':server_name}
		$.get(post_url,params,function(response){
			var stringRes = JSON.parse(response);
			var htmlUlBox = document.createElement("ul");
			htmlUlBox.id = "htmlUlBox";
			if(stringRes.length>0){
				for(var i=0;i<stringRes.length;i++){
					var li = document.createElement("li");
					var itemRes = stringRes[i];
					//如果是文件夹，给tdir标签，并打上baseUri属性 ps.写得比较傻
					if(itemRes.type == "d"){
						var acher = document.createElement("a");
						acher.className = "tdir";
						acher.baseUri = itemRes.baseUri;
						acher.href= "javascript:;"
						acher.sname = itemRes.sname;
						acher.baseUri = itemRes.baseUri;
						acher.innerHTML = itemRes.fname;
						acher.addEventListener("click",dirClickEvent);
						li.appendChild(acher);
						htmlUlBox.appendChild(li);
					}else if(itemRes.type == "f"){
						var acher = document.createElement("a");
						acher.className = "tfile";
						acher.href= "javascript:;"
						acher.sname = itemRes.sname;
						acher.innerHTML = itemRes.fname;
						acher.addEventListener("click",fileClickEvent)
						li.appendChild(acher);
						htmlUlBox.appendChild(li);
					}
				}
			}
			output_box.html($(htmlUlBox)).append("<div class='clear'></div>");
		
		});
	});
	
	//单击目录后的事件
	var dirClickEvent = function(){
		var baseUri = this.baseUri;
		var fileName = this.innerHTML;
		var serverName = this.sname;
		params = {'action':'fetch_config_list','baseUri':baseUri,'fileName':fileName,'serverName':serverName};
		$.get(post_url,params,function(response){
			var stringRes = JSON.parse(response);
			var htmlUlBox = document.createElement("ul");
			htmlUlBox.id = "htmlUlBox";
			if(stringRes.length>0){
				for(var i=0;i<stringRes.length;i++){
					var li = document.createElement("li");
					var itemRes = stringRes[i];
					//如果是文件夹，给tdir标签，并打上baseUri属性 ps.写得比较傻
					if(itemRes.type == "d"){
						var acher = document.createElement("a");
						acher.className = "tdir";
						acher.baseUri = itemRes.baseUri;
						acher.href= "javascript:;"
						acher.sname = itemRes.sname;
						acher.innerHTML = itemRes.fname;
						acher.addEventListener("click",dirClickEvent);
						li.appendChild(acher);
						htmlUlBox.appendChild(li);
					}else if(itemRes.type == "f"){
						var acher = document.createElement("a");
						acher.className = "tfile";
						acher.baseUri = itemRes.baseUri;
						acher.href= "javascript:;"
						acher.sname = itemRes.sname;
						acher.innerHTML = itemRes.fname;
						acher.addEventListener("click",fileClickEvent)
						li.appendChild(acher);
						htmlUlBox.appendChild(li);
					}
				}
			}
			console.log(htmlUlBox);
			output_box.html($(htmlUlBox)).append("<div class='clear'></div>");
		
		});
		
	}
	
	//单击文件后的事件，当然是读文件
	var fileClickEvent = function(){
		var baseUri = this.baseUri;
		var fileName = this.innerHTML;
		var serverName = this.sname;
		params = {'action':'cat_config_file','baseUri':baseUri,'fileName':fileName,'serverName':serverName};
		$.get(post_url,params,function(response){
			output_box.html(response).append("<div class='clear'></div>");
		
		});
	}
});
