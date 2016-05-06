var postUrl = '/project/dispatch/';
var projectType = $("#id_type");
var relatedId = $("#id_relatedId");
var plistContainer = [];

$(document).ready(function(){
	$(".btn-info").click(function(){//增加一行数据
		var row = $(".appendItem li").clone();
		row.appendTo(".control-group ul")
	})
	$(".btn-danger").live("click",function(){//删除一行数据
		$(this).closest("li").remove();
	})
})