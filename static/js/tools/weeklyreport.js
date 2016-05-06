var postUrl = '/tools/ajax/';
$(document).ready(function(){
	//key up 转换markdown到html
	$('#inputBox').bind('keyup',function(){
		var params = {'action':'transform_to_html','markdown':$(this).val()}
		$.post(postUrl,params,function(response){
			$('#output_box').html(response);
		})
	});
});
