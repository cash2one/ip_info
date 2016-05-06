$(function(){
    var desc_box = $("#desc_box");
    $("#id_type_3").live('click',function(){
        if($(this).attr("checked")){
            desc_box.show();
        }else{
            desc_box.find("textarea").val('');
            desc_box.hide();
        }
    });
    if($("#id_type_3").attr("checked")){
        desc_box.show();
    }

    var param = window.location.search.split('?id=');
    if(param[1]){
        $("#submit_create_project").html("确认编辑")
        var id = param[1];
        var url = '/pagemonitor/getPitem';
        $.ajax({
              type: 'GET',
              url: url,
              data: {'id':id},
              dataType: 'json',
              success: function(re){
                  if(re){
                      $("#create_project").attr('action','?id='+id)
                      $("#id_name").val(re.desc);
                      $("#id_url").val(re.url);
                      $("#id_groupTpye option[value='"+re.group_id+"']").attr("selected","selected");
                      $("#id_pdescription").val(re.content);
                      var types = (re.type).split(',');
                      for (key in types){
                          $("#id_type_"+(types[key]-1)).attr("checked","checked")
                          if(types[key]==4){
                              desc_box.show();
                          }
                      }
                  }else{
                      alert('获取失败');
                  }
              },
              error:function(){
                  alert('获取失败');
              }
        });
    }
});