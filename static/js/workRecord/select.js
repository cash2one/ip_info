var postUrl = '/project/dispatch/'

$(document).ready(function(){
	function init(){
		setContent(1,3,"");
	}

	init();

	function setContent(types, dep, remo) {
    console.log(types)
    console.log(dep)
    console.log(remo)
		var type = 0 
        var action = ''
        if(types==1){ action='get_pmt_list'; type='pmt'}else{action='get_ibug_list'; type='hotfix'}
        var department = ''
        if(dep==3){ department='site'}else{department='iPad'}
        var remote = ''
        remote = remo    
        var params = { 
            type: type,
            department: department,
            remote: remote,
            action: action,
            user: $('#username').data('username').trim()
        }

        var $name = $('#id_name').val('').attr('disabled', 'disabled'),
            $branch = $('#branch').hide().next('input').val('').end(),
            $allRemote = $('#id_allRemote').val(''),
            $release = $('#id_onlineDate').val(''),
            $related = $('#id_relatedId').val('').attr('disabled', 'disabled'),
            $description = $('#id_description')

        $('#loading').show()
        $.getJSON(postUrl, params, function(items) {
            $('#loading').hide()
            var options = ''
            for (i in items) {
                options += '<option value="'
                         + items[i].id
                         + '" data-type="'
                         + params.type
                         + '" data-remote="'
                         + params.remote
                         + '" data-department="'
                         + params.department
                         + '" data-allRemote="'
                         + params.remote
                         + '" data-release-date="'
                         + (items[i].date_release || '')
                         + '" data-name="'
                         + items[i].summary
                         + '" '
                         + (items[i].id == $related.data('value') ? ' selected="selected"' : '')
                         + '>' + items[i].id + ' - ' + items[i].summary + '</option>'
            }

            $related.on('change', function(x) {
                var current = $('option:selected', this)

                if (current.val() > 0) {
                    date = current.attr('data-release-date')
                    if (!date) {
                        now = new Date()
                        date = now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate()
                    }
                    $name.val(current.attr('data-name')).removeAttr('disabled')
                    $allRemote.val(current.attr('data-allRemote')).removeAttr('disabled')
                    $branch.text(current.attr('data-type') + '-' + current.val() + ''+ '-' +current.attr('data-department')).show()
                    $release.val(date).removeAttr('disabled')
                    $description.val('').removeAttr('disabled')

                    if ($('option:selected', $(this)).data('type') == 'pmt') {
                        // 获取 pmt 描述 填充项目描述
                        $.getJSON(postUrl, {action: 'get_pmt', pmt: $(this).val()}, function(result) {
                            // 去除标签，去除多于空格空行
                           $description.val($(result.description).text().replace(/[\n\t]+/g, '\n').replace(/^\n/, ''))
                        })
                    }
                } else {
                    $name.val('').attr('disabled', 'disabled')
                    $branch.text('').hide().next('input').attr('placeholder', '').attr('disabled', 'disabled')
                    $release.val('').attr('disabled', 'disabled')
                    $description.val('').attr('disabled', 'disabled')
                }
            }).empty().wrapInner(options)

            if (options) {
                $related.removeAttr('disabled').change()
            }
        })
	}

    $('#create_project').on('submit', function() {
        $('#submit_create_project').button('loading')
    })

    $(':checkbox').on('click', function(x,y) {
		})

	$('.dep').on('change', function(x,y) {
        if (!$(this).is(':checked')) {
            return
           }
           var dep;
           dep = $(this).val(); 
		   var type
		   if($('#type_1').is(':checked')){
				type = $('#type_1').val();
			} else {
				type = $('#type_2').val();
			};
            var remote='';
            $(".remote").each(function(){
            if($(this).attr("checked"))
            remote += $(this).val()+",";
            });
           setContent(type,dep,remote);
        })


    $('.types').on('change', function(x,y) {
		if (!$(this).is(':checked')) {
			return
           }
            var type;
            type = $(this).val();
			var dep;
			if($('#department_1').is(':checked')){
				dep = $('#department_1').val();
			} else {
				dep = $('#department_2').val();
			};
            var remote='';
			$(".remote").each(function(){
			if($(this).attr("checked")) 
                remote += $(this).val()+",";
           });
		   setContent(type,dep,remote);

        });


			
		$('.remote').click(function(){
            var remote = '';
            $(".remote").each(function(){
            if($(this).attr("checked"))
            remote += $(this).val()+",";
            });
            var dep;
            if($('#department_1').is(':checked')){
                dep = $('#department_1').val();
            } else {
                dep = $('#department_2').val();
            };
           var type
           if($('#type_1').is(':checked')){
                type = $('#type_1').val();
            } else {
                type = $('#type_2').val();
            };
           setContent(type,dep,remote);	
		});


});
