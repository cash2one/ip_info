var post_url = "/pages/ajax/"
$(document).ready(function(){
    var delay = function(time) {
        return $.Deferred(function(dfd) {
            setTimeout(function() {
                dfd.resolve()
            }, time)
        })
    }

    function writeToConsole(content){
      $("#output_box").html(content);
      return true;
    }


     $('#update_online_pic[data-type]').on('click',function(){
        var type = $(this).attr('data-type');
		if (!confirm('确定更新' + type + '图片么？')) {
            return
        }

        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'update_online_pic',
            type: type
        }).done(function() {
            showInfo('更新成功！');
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    });
    $('#clear_lock').on('click', function(){
        if (!confirm("确认清除锁？")) {
            return ;
        }
        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'clear_lock'
        }).always(function(response) {
            $button.button('reset')
        })

    }); 
    $('#create_lock').on('click', function(){
        if (!confirm("确认生成锁？")) {
            return ;
        }
        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'create_lock'
        }).always(function(response) {
            $button.button('reset')
        })

    }); 
});




