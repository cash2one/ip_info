var projectUrl = '/ipBan/ajax/'

$(document).ready(function() {
    var $projectMap = $('#project_map'),
        $progress = $('.progress', $projectMap),
        $createBranch = $('#create_branch'),
        $syncToFp = $('#sync_to_fp'),
        $refreshFp = $('#refresh_fp'),
        $markTested = $('#mark_tested'),
        $markMerged = $('#mark_merged'),
        $markPublished = $('#mark_published[data-branch][data-project-id]'),
        $mergeBack = $('#merge_back'),
        $mergedBack = $('#merged_back'),
        $todoChecker = $('input.todo_checker'),
        $archive = $('#archive'),
        $unarchive = $('#unarchive'),
        $refresh_pg = $('#refresh_pg'),
        SECOND = 100,

    delay = function(time) {
        return $.Deferred(function(dfd) {
            setTimeout(function() {
                dfd.resolve()
            }, time)
        })
    }

    progressing = function($button, url, params) {
        $button.button('load')
        $progress.trigger('load')
        return $.when($.get(url, params, $.noop, 'json'), delay(SECOND))
                .always(function() {
                    $progress.trigger('loaded')
                    $button.button('reset')
                })
                .then(function(results_of_post) {
                    return results_of_post[0]
                })
    }

    // 按钮确认过程
    confirm = function($button, event) {
        return $.Deferred(function(dfd) {
            if ($button.hasClass('waiting-confirm')) {
                $button.removeClass('btn-danger waiting-confirm').text($button.data('origin-text'))
                dfd.resolve()
            } else {
                $button.addClass('btn-danger waiting-confirm').data('origin-text', $button.text()).text($button.text() + '  确认？')
                // stopPropagation 以免触发 body click
                event.stopPropagation()
            }
       })
    }

     //修改规则
     function updateRule(focusid) {
     var focusblurid = $(focusid);
     var defval = focusblurid.val();
     $(focusid).dblclick(function () {
     $(focusid).removeAttr("readonly");
     }); 
     focusblurid.blur(function(){
     var thisval = $(this).val();
     var id = $(this).attr('data-id');
     var parent_id = $(this).attr('data-parent-id');
     var value = $(this).attr('value');
     var name = $(this).attr('name');
     var info = $(this).val();
	console.log(value)
	console.log(info)
     var $button = $(this),
     params = { 
         action: 'update_rule_info',
         info: info,
         name: name,
         id: id,
         parent_id: parent_id
     }   
     progressing($button, projectUrl, params)
     .done(function(result) {
        $(focusid).val(thisval);
     })  
    $(focusid).attr("readonly","readonly")
    }); 
  };
     updateRule(".rule_info");
})
