$(document).ready(function() {

	// 添加图片按钮样式
	$(".image-selector .file-input").hover(function() {
		$("i.tweet-camera").css({
			"background-position" : "-60px -590px"
		});
	}, function() {
		$("i.tweet-camera").css({
			"background-position" : "-60px -530px"
		});
	});
	
	//上传图片的回调函数
	$(".image-selector .file-input").change(function(){
	});

});