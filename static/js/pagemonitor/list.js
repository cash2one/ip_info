//$(function(){
var post_url = "/pagemonitor/ajax/"
    //删除条目
    function del(id){
        if(confirm("确认删除?")){
            var url = '/pagemonitor/delitem';
            $.ajax({
                  type: 'GET',
                  url: url,
                  data: {'id':id},
                  dataType: 'json',
                  success: function(re){
                      if(re.result == 0){
                          window.location.reload();
                      }else{
                          alert('删除失败');
                      }
                  },
                  error:function(){
                      alert('删除失败');
                  }
            });
        }
    }
    function startMonitor(){
        var url = '/pagemonitor/startMonitor';
        $.ajax({
              type: 'GET',
              async:false,
              url: url,
              data: {},
              dataType: 'json',
              success: function(re){
                  if(re.result == 0){
                      alert('触发成功！');
                      window.open('/pagemonitor/log/?status=0','_self');
                  }else{
                      alert('触发失败');
                  }
              },
              error:function(){
                  alert('触发失败');
              }
        });
    }
/*    function updateDb(){
        var url = '/pagemonitor/updateDb';
        $.ajax({
              type: 'GET',
              async:false,
              url: url,
               
              data: {},
              dataType: 'json',
              success: function(re){
                  if(re.result == 0){
                      alert('触发成功！');
                      window.open('/pagemonitor','_self');
                  }else{
                      alert('触发失败');
                  }
              },
              error:function(){
                  alert('触发失败');
              }
        });
    }


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
    $('#update_url[data-url]').on('click', function(){
        var u = $(this).attr('data-url');
        if (!confirm("确认修改URL？")) {
            return ;
        }

        var $submit = $(this)

        $.when($submit)
        .then(function($submit) {
            $submit.button('loading')
        })
        .then(function() {
            return $.when($.get(post_url, {action: 'update_url',u: u}), delay(3000))
                    .then(function(response) {
                        return response[0]
                    })
        })
        .always(function(response) {
            writeToConsole(response)
            $submit.button('reset')
        })
    }); 
});
*/
