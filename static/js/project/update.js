var postUrl = '/project/dispatch/'

$(document).ready(function(){
        //漏选仓库
        function updated (name,data) {
 for(var i in data){
 $("input[value='"+data[i]+"']").attr("checked","checked");
 $("input[value='"+data[i]+"']").attr("disabled","disabled");
 }
     $(':checkbox').on('click', function(e) {
var jqDom = $(this),
status = jqDom.attr("checked"),
remote = e.target.value,
projectId = jqDom.data("project"),
branch = jqDom.data("branch"),
repositoryGroup = $('input[name='+name+']'),
repositories = [],
result;

repositoryGroup.each(function(i,ele){
        if (ele.checked) {
                repositories.push(ele.value);
        }
});
result = repositories.join(',');
alert("当前所选仓库为："+result);
        var $button = $(this),
        params = {
            action: 'update_remote',
            remote : result,
            projectId : projectId,
            branch : branch
        }

        return $.when($.post(postUrl, params,'json'))
                .fail(function() {
                    showModal('出错了...')
                })
                .then(function(results_of_post) {
                    return results_of_post[0]
                })

       })
}

        var data = $('.remote').attr('data-remote');
        console.log(data);
        if (typeof(data) != "undefined")
        {
        data = data.split(",");
        }

        updated("remote",data);
});
