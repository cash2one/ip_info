var post_url = "/deploy/ajax/"
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


    // 合并进 master 按钮
    $('#merge_to_master[data-type][data-which]').on('click', function(){
        var type = $(this).attr('data-type');
        var which = $(this).attr('data-which');
        var $submit = $(this)

        $.when($submit)
        .then(function($submit) {
            $submit.button('loading')
        })
        .then(function() {
            return $.when($.get(post_url, {action: 'merge_to_master',type: type,which: which,branchName:$("[name=branch_name]").val()}), delay(3000))
                    .then(function(response) {
                        return response[0]
                    })
        })
        .always(function(response) {
            writeToConsole(response)
	     showInfo(response)
             $submit.button('reset').removeClass('btn-success').addClass('btn-primary')
        })

    });


    $('#generate_online_version[data-type]').on('click', function(){
        var type = $(this).attr('data-type');
        var which = $(this).attr('data-which');
        if (!confirm("确认创建新版本？")) {
            return ;
        }

        var $submit = $(this)

        $.when($submit)
        .then(function($submit) {
            $submit.button('loading')
        })
        .then(function() {
            return $.when($.get(post_url, {action: 'generate_online_version',which: which,type: type}), delay(3000))
                    .then(function(response) {
                        return response[0]
                    })
        })
        .always(function(response) {
            writeToConsole(response)
            $submit.button('reset')
            url = location.href;
            var now_url = url.replace('deploy?','deploy_log?')
            $("#log").load(now_url)
        })
    }); 


   // 版本发布按钮
    $('#publish_version_online_beta[data-version][data-type][data-which]').on('click',function(){
        var version = $(this).attr('data-version');
        var branch_type = $(this).attr('data-type');
        var which = $(this).attr('data-which');
        if (!confirm('确定发布beta版本 ' + version + ' 么？')) {
            return
        }

        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'publish_version_online_beta',
            version: version,
            branch_type: branch_type,
            which: which
        }).done(function() {
            showInfo('上线beta成功！');
            url = location.href;
            var now_url = url.replace('deploy?','deploy_log?')
            $("#log").load(now_url)
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })
    }); 

     $('#publish_version_online_ga[data-version][data-type][data-which]').on('click',function(){
        var version = $(this).attr('data-version');
        var branch_type = $(this).attr('data-type');
        var which = $(this).attr('data-which');
        if (!confirm('确定发布ga版本 ' + version + ' 么？')) {
            return
        }

        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'publish_version_online_ga',
            version: version,
            branch_type: branch_type,
            which: which
        }).done(function() {
            showInfo('上线ga成功！');
            url = location.href;
            var now_url = url.replace('deploy?','deploy_log?')
            $("#log").load(now_url)
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    });

     $('#publish_version_online_smoke[data-version][data-type][data-smoke]').on('click',function(){
        var version = $(this).attr('data-version');
        var branch_type = $(this).attr('data-type');
        var which = $(this).attr('data-smoke');
        if (!confirm('确定发布smoke版本 ' + version + ' 么？')) {
            return
        }

        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'publish_version_online_smoke',
            version: version,
            branch_type: branch_type,
            which: which
        }).done(function() {
            showInfo('上线smoke成功！');
            url = location.href;
            var now_url = url.replace('deploy?','deploy_log?')
            $("#log").load(now_url)
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
            $button.button('reset')
        })

    });

    $('#clear_apc[data-which]').on('click', function(){
        var which = $(this).attr('data-which');
        if (!confirm("确认清除apc？")) {
            return ;
        }
        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'clear_apc',
            which: which
        }).always(function(response) {
            $button.button('reset')
        })

    });
     $('#switch_status[data-type][data-id]').on('click',function(){
        var id = $(this).attr('data-id');
        var branch_type = $(this).attr('data-type');
        var $button = $(this).button('loading')
        $.get(post_url, {
            action: 'switch_status',
            id: id,
            branch_type: branch_type,
        }).done(function() {
//            showInfo('状态切换成功！');
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            writeToConsole(response)
//            $button.button('reset')
            location.reload() 
        })

    });

});




