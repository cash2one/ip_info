$(document).ready(function(){
    var input_table = document.getElementById('input_table');
    var tr_cnt = document.getElementById('tr_cnt');
    var count = parseInt(tr_cnt.value);
    var max_input_num = count;
    $('#add_input').bind('click',function(){
        max_input_num = max_input_num + 1;
        count = count + 1;
        tr_cnt.value = count;

        var tr_new = document.createElement("tr");
        tr_new.className = "custom_tr";
        tr_new.innerHTML = '<td><input name="name_'+max_input_num+'" style="width:100px;"/></td>'+
                            '<td><input name="type_'+max_input_num+'" style="width:150px;"/></td>'+
                            '<td><select name="require_'+max_input_num+'" style="width:100px;"><option value="2">否</option><option value="1">是</option></select></td>'+
                            '<td><input name="example_'+max_input_num+'" style="width:150px;"/></td>'+
                            '<td><input name="desc_'+max_input_num+'" style="width:150px;"/></td>'+
                            '<td><input type="button" value="删除" class="del_tr" style="width:50px;"/></td>';
        input_table.appendChild(tr_new);

        if ($('.del_tr')) {
            $(".del_tr").each(function(){
                $(this).bind('click',function(){
                    count = count - 1;
                    tr_cnt.value = count;
                    this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);
                });
            });
        }
    });
    if ($('.del_tr')) {
        $(".del_tr").each(function(){
            $(this).bind('click',function(){
                count = count - 1;
                tr_cnt.value = count;
                this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);
            });
        });
    }



    var output_table = document.getElementById('output_table');
    var out_cnt = document.getElementById('out_cnt');
    var count_out = parseInt(out_cnt.value);
    var max_output_num = count_out;
    $('#add_output').bind('click',function(){
        max_output_num = max_output_num + 1;
        count_out = count_out + 1;
        out_cnt.value = count_out;

        var tr_new = document.createElement("tr");
        tr_new.className = "custom_tr";
        tr_new.innerHTML = '<td><input name="rname_'+max_output_num+'" style="width:100px;"/></td>'+
                            '<td><input name="rtype_'+max_output_num+'" style="width:150px;"/></td>'+
                            '<td><input name="rexample_'+max_output_num+'" style="width:150px;"/></td>'+
                            '<td><input name="rdesc_'+max_output_num+'" style="width:150px;"/></td>'+
                            '<td><input type="button" value="删除" class="del_out" style="width:50px;"/></td>';
        output_table.appendChild(tr_new);

        if ($('.del_out')) {
            $(".del_out").each(function(){
                $(this).bind('click',function(){
                    count_out = count_out - 1;
                    out_cnt.value = count_out;
                    this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);
                });
            });
        }
    });
    if ($('.del_out')) {
        $(".del_out").each(function(){
            $(this).bind('click',function(){
                count_out = count_out - 1;
                out_cnt.value = count_out;
                this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);
            });
        });
    }



    var form_2 = document.getElementById('form_2');
    if (form_2) {
        $('#submit_button').bind('click',function(){
            res = true;
            $(".custom_tr input").each(function(){
                if (this.value == "") {
                    res = false;
                    alert('请填写参数属性');
                    return false;
                }
            });
            if (res == true) {
                form_2.submit();
            }
        });
    }



    var form_3 = document.getElementById('form_3');
    if (form_3) {
        $('#submit_button').bind('click',function(){
            res = true;

            var inter_name = document.getElementById('inter_name');
            var desc = document.getElementById('desc');
            var url = document.getElementById('url');
            var version_select = $("#version_select").val()
            var input_version = $("#input_version").val()
            if(version_select == 0){
                $("#version").val(input_version);
            }else{
                $("#version").val(version_select);
            }
            if (inter_name.value == "") {
                res = false;
                alert('请填写接口名');
            } else if (desc.value == "") {
                res = false;
                alert('请填写详细描述');
            } else if (url.value == "") {
                res = false;
                alert('请填写url');
            }else if ($("#version").val() == "") {
                res = false;
                $("#input_version").focus();
                alert('填写版本号');
            }

            $(".custom_tr input").each(function(){
                if (res == false) {
                    return false;
                }
                if (this.value == "") {
                    res = false;
                    alert('请填写参数属性');
                    return false;
                }
            });
            if (res == true) {
                form_3.submit();
            }
        });
    }

    $("#version_select").change(function(){
        var version_select = $("#version_select").val()
        if(version_select == 0){
            $("#input_version_span").show();
            $("#input_version").focus();
        }else{
            $("#input_version_span").hide();
        }
    });
});
