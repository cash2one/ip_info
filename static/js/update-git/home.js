var post_url = "/update/ajax/"
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


     $('#update_jockjs[data-type]').on('click',function(){
        var which = $("#jockjsbranch").val();
        var type = $(this).attr('data-type');
        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'update_jockjs',
            type: type,
            which: which
        }).done(function() {
            showInfo('更新成功！');
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    });

     $('#update_pages[data-type]').on('click',function(){
        var which = $("#pages").val();
        var type = $(this).attr('data-type');
        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'update_pages',
            type: type,
            which: which
        }).done(function() {
            showInfo('更新成功！');
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    }); 

     $('#update_cms[data-type]').on('click',function(){
        var which = $("#cms").val();
        var type = $(this).attr('data-type');
        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'update_cms',
            type: type,
            which: which
        }).done(function() {
            showInfo('更新成功！');
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    }); 

});




