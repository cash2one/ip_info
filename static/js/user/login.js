$(document).ready(function(){
	var post_url = "/user/ajax/";
	$("#submit").bind('click',function(){
		
		var data = {};
		data.username = $("#username").val();
		data.passwd = $("#passwd").val();
		var jsonData = JSON.stringify(data);
		var params = {action:'submit',data:jsonData}
		$.post(post_url,params,function(responseInfo){
			if(responseInfo == 1){
				alert("登录成功");
				window.location.href="/";
			}else{
				tips = document.createElement("div");
				tips.className="info";
				tips.innerHTML="用户名或密码错误，请联系Kavin(分机：8088)";
				$(".info").remove();
				$("#submit").after(tips);
			}
		});
		return false;
	});
});
