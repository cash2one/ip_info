var post_cookie_url = "/cookie/ajax/"
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


     $('#update_version_cookie[data-version][data-branch][data-type]').on('click',function(){
        var version = $(this).attr('data-version');
        var branch_name = $(this).attr('data-branch');
        var type = $(this).attr('data-type');
        var which = $(this).attr('data-which');
		if (!confirm('确定更新cookie版本 ' + version + ' 么？')) {
            return
        }

        var $button = $(this).button('loading')
        $.get(post_cookie_url, {
            action: 'update_version_cookie',
            version: version,
            branch_name: branch_name,
            type: type,
            which: which
        }).done(function() {
            showInfo('更新成功！');
            url = location.href;
            var now_url = url.replace('cookie?','cookie_log?')
            $("#log").load(now_url)
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    });

     $('#delete_version_cookie[data-version][data-branch][data-type]').on('click',function(){
        var branch_name = $(this).attr('data-branch')
        var version = $(this).attr('data-version');
        var type = $(this).attr('data-type');
        var which = $(this).attr('data-which');
        if (!confirm('确定删除cookie版本 ' + version + ' 么？')) {
            return
        }

        var $button = $(this).button('loading')
        $.get(post_cookie_url, {
            action: 'delete_version_cookie',
            version: version,
            type: type,
            which: which,
            branch_name: branch_name
        }).done(function() {
            showInfo('删除成功！');
            url = location.href;
            var now_url = url.replace('cookie?','cookie_log?')
            $("#log").load(now_url)
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    });

});




