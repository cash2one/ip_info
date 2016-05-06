var jobnum = 1;
var plannum = 1;
$(function(){
	/* 页面加载 */
	var jnum = parseInt($("#jobnum").val());
	if(jnum>1){
		jobnum = jnum;
	}
	var pnum = parseInt($("#plannum").val());
	if(pnum>1){
		plannum = pnum;
	}
	/* 页面加载 结束*/

	/* 点击本周工作 添加事件 */
	$("a.add_job").click(function(){
		jobnum ++;
		add_job_plan(1,jobnum);
	});

	/* 点击本周工作 删除事件 */
	$("a.del_job").click(function(){
		jobnum --;
		if(jobnum>0){
			del_job_plan(1,jobnum);
		}else{
			jobnum++;
		}
	});

	/* 点击下周计划 添加事件 */
	$("a.add_plan").click(function(){
		plannum ++;
		add_job_plan(2,plannum);
	});

	/* 点击下周计划 删除事件 */
	$("a.del_plan").click(function(){
		plannum --;
		if(plannum>0){
			del_job_plan(2,plannum);
		}else{
			plannum++;
		}
	});

	/* 提交表单 */
    $(".submit").click(function(){
    	/* 检测工作 */
    	for(i=1;i<=jobnum;i++){
    		if($("#job"+i).val()==""){
    			alert("工作"+i+"不能为空");
    			$("#job"+i).focus();
    			return false;
    		}
    	}
    	/* 检测计划 */
    	for(i=1;i<=plannum;i++){
    		if($("#plan"+i).val()==""){
    			alert("计划"+i+"不能为空");
    			$("#plan"+i).focus();
    			return false;
    		}
    	}
    	/* 检测收获 */
    	if($("#harvest").val()==""){
			alert("收获不能为空");
			$("#harvest").focus();
			return false;
		}
    	/* 检测不足 */
    	if($("#trouble").val()==""){
			alert("不足不能为空");
			$("#trouble").focus();
			return false;
		}

	   $("#jobnum").val(jobnum);
	   $("#plannum").val(plannum);
	   $("#team_form").submit();
    });

    /* 添加新邮件 */
    $("#add_new_email").click(function(){
    	$("#addpanel").append("<p><input type='text' name='newemail' class='newemailtxt'/> &nbsp;<a class='delemail' href='javascript:void(0)'>删除 -</a></p>");
    });

    /* 邮件全选 */
    $(".email_chooseall").click(function(){
    	$(".email_checkbox").attr("checked",true);
    });

    /* 邮件全取消 */
    $(".email_delall").click(function(){
    	$(".email_checkbox").attr("checked",false);
    });

    /* 删除自定义邮件 */
    $(".delemail").live("click",function(){
    	$(this).parent("p").remove();
    });

})

/* 添加
 * type : 添加类型 1：job 2：plan
 * num : 号码 第几个 jobnum plannum
 * */
function add_job_plan(type,num){
	switch(type){
		case 1:
			ty = "工作";
			to = "jobdiv";
			name = "job"
			break;
		case 2:
			ty = "计划";
			to = "plandiv";
			name = "plan"
			break;
	}
	tit = ty + num ;
	name = name + num ;
	html = '<div class="list"><label> '+tit+'</label><input type="text" name="'+name+'" id="'+name+'"></textarea><div class="clear"></div></div>';
	$("#"+to).append(html);
}

/* 删除
 * type : 添加类型 1：job 2：plan
 * num : 号码 第几个 jobnum plannum
 * */
function del_job_plan(type,num){
	switch(type){
		case 1:
			to = "jobdiv";
			break;
		case 2:
			to = "plandiv";
			break;
	}
	$("#"+to+" .list").eq(num).remove();
}
