$(document).ready(function(){
	$("#logout").bind('click',function(){
       		$.post('/user/ajax',{action:'logout'},function(response){
       			if(response == 1){
       					alert("退出成功！");
       					window.location.href="/";
       			}
       		})
       })
});

//显示简单警告信息
function showAlert(message){
	showModal(message,'警告');
}

//显示简单提示信息
function showInfo(message){
	showModal(message,"消息");
}

//显示爱房弹出浮层信息
function showModal(modalBody,modalHeader,modalFooter){
    $modal = $(
        ['<div class="modal hide" id="aifangModal" style="display:none;">',
            '<div class="modal-header">',
                '<button type="button" class="close" data-dismiss="modal">x</button>',
                '<h3 id="modal-header">提示</h3>',
            '</div>',
            '<div class="modal-body" id="modal-body"></div>',
            '<div class="modal-footer" id="modal-footer">',
                '<a id="modal-footer-close" href="#" class="btn" data-dismiss="modal">关闭</a>',
            '</div>',
        '</div>'].join('')
        ).appendTo($('body'))

    if (!!modalBody){
        $("#modal-body", $modal).html(modalBody);
    }else{
        $("#modal-body", $modal).html("");
    }

    if (!!modalHeader) {
        $("#modal-header", $modal).html(modalHeader);
    }else{
        $("#modal-header", $modal).html("提示");
    }

    if (!!modalFooter) {
        $("#modal-footer", $modal).html(modalFooter);
    }


    $modal.modal("show")
    return $modal
}
