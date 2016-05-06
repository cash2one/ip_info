var projectUrl = '/project/dispatch/'
var webgitUrl = '/webgit/dispatch/'

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
        SECOND = 1000,

    delay = function(time) {
        return $.Deferred(function(dfd) {
            setTimeout(function() {
                dfd.resolve()
            }, time)
        })
    }

    progressing = function($button, url, params) {
        $button.button('loading')
        $progress.trigger('loading')
        console.log(url)
        console.log(params)
        return $.when($.post(url, params, $.noop, 'json'), delay(SECOND))
                .always(function() {
                    $progress.trigger('loaded')
                    $button.button('reset')
                })
                .fail(function() {
                    showModal('出错了...')
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

    // 配合 confirm()，点击空白处后恢复确认按钮状态
    $('body').on('click', function() {
        $('.waiting-confirm').each(function() {
            $(this).removeClass('btn-danger waiting-confirm').text($(this).data('origin-text'))
        })
    })

    isTodoEmpty = function() {
//        return $('#project_todos input.todo_checker').length == 0
    }

    confirmEmptyTodo = function() {
        return $.Deferred(function(dfd) {
            showModal().confirmModal({
                'heading': '确认 Todo List',
                'body': '确定不需要任何 Todo List 吗？',
                'confirming' : '确认',
                'closing': '关闭',
                'callback': function() {
                    dfd.resolve()
                }
            })
        })
    }

    // 进度条动画
    $progress.on('loading', function() {
        $(this).addClass('progress-striped active')
    }).on('loaded', function() {
        $(this).removeClass('progress-striped active')
    })

    // accordion 中的链接 stopPropagation, 以防触发 accordion
    $('a.accordion-link').on('click', function(e) {
        e.stopPropagation()
    })

    // 创建分支 按钮
    $createBranch.on('click', function(e) {
        var $button = $(this),
            params = {
                action: 'create_branch',
                projectId: $button.data('project-id')
            }

        confirm($button, e)
        .then(function() {
            return progressing($button, projectUrl, params)
        })
        .done(function(result) {
            if (result.data.branch) {
                $button.text($button.data('complete-text'))
                $projectMap.removeClass('project_status_1').addClass('project_status_2')
            } else {
                showModal(result.message, $button.data('fail-text'))
            }
        })
    })

    // 同步到 fp 环境按钮
    $syncToFp.on('click', function(e) {
        var $button = $(this),
            params = {
                action: 'rsync_to_dev',
                branchName: $button.data('branch'),
                projectId: $button.data('project-id'),
                remote: $button.data('remote'),
                fpxx:$("[name=fpxx]").val()
            }

        ;(isTodoEmpty() ? confirmEmptyTodo() : confirm($button, e))
        .then(function(result) {
            return progressing($button, webgitUrl, params)
        })
        .done(function(result) {
            if (result.result) {
                $button.text($button.data('complete-text'))
                $('span.fp_name').text(result.data.fp)
                $projectMap.removeClass('project_status_2').addClass('project_status_3')
                location.reload()
            } else {
//                showModal(result.message, $button.data('fail-text'))
                alert(result.message)
            }
        })
    })

    // 更新 fp 环境代码按钮
    $refreshFp.on('click', function() {
        var $button = $(this),
            params = {
                action: 'refresh_fp',
                fpId: $button.data('fp-id')
            }

        progressing($button, projectUrl, params)
        .done(function(result) {
            if (result.result) {
                showModal(result.message)
            }
        })
    })



	function checked () {
    $(':checkbox').on('click', function(e) {
    var jqDom = $(this),
    status = jqDom.attr("checked"),
    branch_name = jqDom.data('branch'),
    remote = e.target.value,
    name = jqDom.attr("name"),
    repositoryGroup = $('input[name='+name+']'),
    repositories = [],
    result;
    
    repositoryGroup.each(function(i,ele){
    	if (ele.checked) {
    		repositories.push(ele.value);
    	}
    });
    result = repositories.join(',');
       console.log(branch_name);
       console.log(result);
        var $button = $(this),
        params = {
            action: 'update_create_version',
            remote : result,
            branch_name : branch_name 
        }
         progressing($button, projectUrl, params)
         .done(function(result) {
         })
       })
     }

	checked();


     //修改上线时间
     function updateDate(focusid) {
     var focusblurid = $(focusid);
     var defval = focusblurid.val();
     $(focusid).dblclick(function () {
     $(focusid).removeAttr("readonly");
     }); 
     focusblurid.blur(function(){
     var thisval = $(this).val();
     var date = $(this).val();
     var project_id = $(this).attr('data-project-id');
     var $button = $(this),
     params = { 
         action: 'update_date',
         date: date,
         project_id: project_id
     }   
     if (defval != thisval){
     progressing($button, projectUrl, params)
     .done(function(result) {
        $(focusid).val(thisval);
     })  
     }   
    $(focusid).attr("readonly","readonly")
    }); 
  };

     updateDate("#date");



	
    
     function clickHandler(e) {
	var value = e.target.value;
	console.log(value);
        var branch_name = $(this).attr('data-branch');
        var $button = $(this),
        params = {
            action: 'update_gc',
            branch_name:branch_name,
            gc: value
        }

         progressing($button, projectUrl, params)
         .done(function(result) {
         })
       }



$('input[type="radio"]').on("click", clickHandler);


    //rebase master
    $('#rebase_master[data-type][data-branch]').on('click', function() {
        var branch_name = $(this).attr('data-branch');
        var branch_type = $(this).attr('data-type');
        var $button = $(this),
        params = {
            action: 'rebase_master',
            branch_name: branch_name,
            branch_type: branch_type,
            projectId: $button.data('project-id')
        }
        progressing($button, projectUrl, params)
        .done(function(result) {
            if (result.result) {
                showModal(result.message)
            }
        })
    })


     $('#create_new_branch[data-type][data-branch]').on('click',function(){
        var branch_name = $(this).attr('data-branch');
        var branch_type = $(this).attr('data-type');
        var $button = $(this).button('loading')
        $.get(projectUrl, {
            action: 'create_new_branch',
            branch_name: branch_name,
            branch_type: branch_type,
            projectId: $button.data('project-id')
        }).done(function() {
            showInfo('创建成功！');
            location.reload()
        }).fail(function() {
            showInfo('出错了');
        }).always(function(response) {
            $button.button('reset')
        })

    });



    //测试环境更新到最新代码
    $refresh_pg.on('click', function() {
        var $button = $(this),
        params = {
            action: 'refresh_pg',
            projectId: $button.data('project-id'),
            remote: $button.data('remote'),
            fpxx:$("[name=fpxx]").val()
        }
        progressing($button, projectUrl, params)
        .done(function(result) {
            if (result.result) {
                showModal(result.message)
            }else{
                 alert(result.message)
            }
        })
    })

    // 测试完成按钮
    $markTested.on('click', function(e) {
        var $button = $(this),
            params = {
                action: 'test_completed',
                projectId: $button.data('project-id')
            }

        ;(isTodoEmpty() ? confirmEmptyTodo() : confirm($button, e))
        .then(function() {
            return progressing($button, projectUrl, params)
        })
        .done(function(result) {
            if (result.result) {
                $button.text($button.data('complete-text')).addClass('disabled')
                $projectMap.removeClass('project_status_3 project_status_2').addClass('project_status_4')
                location.reload()
            } else {
                showModal(result.message, '无法完成测试')
            }
        })

    })

    // 合并完成按钮
    $markMerged.on('click', function(e) {
        var $button = $(this),
            params = {
                action: 'update_status',
                projectId: $button.data('project-id'),
                value: 5
            }

        confirm($button, e)
        .then(function() {
            return progressing($button, projectUrl, params)
        })
        .done(function(result) {
            $button.text($button.data('complete-text')).addClass('disabled')
            $projectMap.removeClass('project_status_4').addClass('project_status_5')
        })
    })

    // 已经合并回来源分支
    $mergedBack.on('click', function(e) {
        e.stopPropagation()
        var $button = $(this),
            params = {
                action: 'merged_back',
                projectId: $button.data('project-id'),
            }

        confirm($button, e)
        .then(function() {
            return progressing($button, projectUrl, params)
        })
        .done(function(result) {
            if (result.result) {
                $button.text($button.data('complete-text')).addClass('disabled')
                $projectMap.removeClass('project_status_4').addClass('project_status_5')
            } else {
                showModal(result.message, $button.data('fail-text'))
            }
        })
    })

    // 合并入 master 按钮
    $mergeBack.on('click', function(e) {
        e.stopPropagation()

        var $button = $(this),
            params = {
                action: 'merge_back',
                projectId: $button.data('project-id'),
                branch: $button.data('branch')
            }

        confirm($button, e)
        .then(function() {
            return progressing($button, projectUrl, params)
        })
        .done(function(result) {
            if (result.result) {
                $button.text($button.data('complete-text')).addClass('disabled')
                $projectMap.removeClass('project_status_4').addClass('project_status_5')

                showModal(result.message, $button.data('success-text'))
            } else {
                showModal(result.message, $button.data('fail-text'))
            }
        })
    })


    $('#mark_published[data-branch]').on('click', function() {
        var branch_name = $(this).attr('data-branch');
        console.log(branch_name);
        var $button = $(this),
        params = {
            action: 'published',
            branch_name: branch_name,
            projectId: $button.data('project-id')
        }
        progressing($button, projectUrl, params)
        .done(function(result) {
            $button.text($button.data('complete-text')).addClass('disabled')
            $projectMap.removeClass('project_status_5').addClass('project_status_6')
        })
    })



    // todo list checkbox
    $todoChecker.on('click', function(e) {
        e.stopPropagation()

        var $checkbox = $(this),
            params = {
                action: 'mark_memo_done',
                memoId: $checkbox.data('memo-id'),
                done: $checkbox.is(':checked') ? 1 : 0
            }

        $.post(projectUrl, params, $.noop, 'json')
        .done(function(result) {
            var labels = $checkbox.siblings('span.label')
            if (result.data.done == 1) {
                labels.filter('.done').show()
                labels.filter('.undone').hide()
            } else {
                labels.filter('.done').hide()
                labels.filter('.undone').show()
            }
        });
    })

    // 归档
    $archive.on('click', function() {
        var $button = $(this),
            params = {
                action: 'archive',
                projectId: $button.data('project-id')
            }

        $.post(projectUrl, params, $.noop, 'json')
        .done(function() {
            $button.hide()
            $unarchive.show();
            $projectMap.addClass('archived')
        })
    })

    // 取消归档
    $unarchive.on('click', function() {
        var $button = $(this),
            params = {
                action: 'unarchive',
                projectId: $button.data('project-id')
            }

        $.post(projectUrl, params, $.noop, 'json')
        .done(function() {
            $button.hide()
            $archive.show();
            $projectMap.removeClass('archived')
        })
    })


    // popover 提示
    $('body').on('click', function() {
        $('#branch_help, #project_help').popover('hide')
    })
    .find('#branch_help').popover({
        placement: 'right',
        trigger: 'click'
    }).end()
    .find('#project_help').popover({
        placement: 'bottom',
        trigger: 'click'
    }).end()
    .find('#branch_help, #project_help').on('click', function(e) {
        $(this).popover('toggle')
        e.stopPropagation()
    }).end()

    // 项目创建完后第一次进入该页面会带入 #cb
    // 触发创建分支事件
    if (window.location.hash == '#cb') {
        if ($createBranch.is(':visible')) {
            $createBranch.trigger('click').trigger('click')
        }
    }
})
