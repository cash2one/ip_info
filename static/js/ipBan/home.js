$(document).ready(function() {

    var projectUrl = '/project/dispatch/'

    // 搜索框相关功能
    $('#searchform').hover(function() {
        if(typeof timer != 'undefined' && timer) {
            clearTimeout(timer)
            timer = null
        }

        $('#searchshortcut').show()
    }, function() {
        if(typeof timer != 'undefined' && timer) {
            clearTimeout(timer)
            timer = null
        }
        timer = setTimeout(function() {
            $('#searchshortcut').hide()
            $('#projectstatus a:not(#projectstatustrigger)').hide()
        }, '1000')
    })
    .find('#projectstatus').hover(function() {
        $('a', $(this)).show()
    }).end()
    .find('#searchboxinput').on('keyup input paste', function() {
        if ($(this).val()) {
            $('#searchButton').addClass('btn-primary')
        } else {
            $('#searchButton').removeClass('btn-primary')
        }
    }).trigger('keyup').end()
    .find('#searchButton').on('click',function(){
        var inputText = $('#searchboxinput').val().trim();

        if (inputText == ''){
            $('#searchHelp').click()
            return false
        }
    }).end()
    .find('#searchHelp').on('click',function(){
        var header = '搜索项目'

        var bodyInfo = [
            '<p></p><ol class=""><li>搜索 <code>pmt 1121</code> 或者 <code>pmt-1121</code> 可以查出 id 为 1121 的 pmt 项目</li>',
            '<li>搜索 <code>hotfix 123</code> 或者 <code>hotfix-123</code> 可以查出 id 为 123 的 hotfix 项目</li>',
            '<li>搜索 <code>author:kavin</code> 或者 <code>author kavin</code> 可以查出创建人是 kavin 的项目</li>',
            '<li>搜索 <code>attr:testing</code> 或者 <code>attr:notesting</code> 可以查出对应类型项目列表</li>',
            '<li>搜索 <code>attr:正在开发</code>  可以查出对应项目进度列表，项目进度有：<code>待开发</code> <code>正在开发</code> <code>正在测试</code> <code>待合并</code> <code>待上线</code> <code>已上线</code> 六种状态</li>',
            '<li>搜索其他将得到项目名称含对应字段的记录</li>',
            '</ol>'].join('')

        showModal(bodyInfo,header)
    })

    // 延期
/*    $('.delayed323').on('click', function() {
        var $button = $(this),
            params = {action: 'delayed', 'projectId': $button.data('project-id')}
//        if (!confirm("确认该项目延期？")) {
//            return ;
//        }  
        $.post(projectUrl, params, $.noop, 'json').done(function() {
//            $button.hide()
              $button.removeClass("delayed");
              $button.val("延期");
              $button.removeAttr("style");
              $button.attr({style:"width:30px;color:#FF0000"});
              $button.attr("disabled","disabled");
//            $button.closest('tr').hide()
        })
    })
*/
    // 归档
    $('.archive').on('click', function() {
        var $button = $(this),
            params = {action: 'archive', 'projectId': $button.data('project-id')}

        $.post(projectUrl, params, $.noop, 'json').done(function() {
            $button.hide()
            $button.closest('tr').hide()
        })
    })

    // 取消归档
    $('.unarchive').on('click', function() {
        var $button = $(this),
            params = {action: 'unarchive', 'projectId': $button.data('project-id')}

        $.post(projectUrl, params, $.noop, 'json').done(function() {
            $button.hide()
            $button.closest('tr').hide()
        })
    })
    //编辑上线时间
    $('.edit-online-date').click(function(){
    	$('#myModal').find('[name=pid]').val($(this).attr('data-pid'));
    	$(this).closest("tr").find('td').each(function(){
    		var target =$(this).attr('data-target');
    		if(typeof target =='undefine'){
    			return true;
    		}
    		$('#myModal').find('[name='+target+']').val($(this).text());
    	})
    	
    	$('#myModal').modal();
    });

})
