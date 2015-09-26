var competitionResultUpdate=(function(config,functions){
    return {
        loadMembers:function(competitionId,stage){
            var me=this;
            var url=config.ajaxUrls.competitionTeamsGetAll.replace(":competitionId",competitionId);
            if(stage==3){
                url=config.ajaxUrls.competitionTeamsGetAll1.replace(":competitionId",competitionId)
            }
            $.ajax({
                url:url,
                method:"get",
                data:{
                    stage:stage
                },
                success:function(data){
                    if(data.success){
                        if(stage==3){
                            //如果没有结果，有可能是只有16只队伍直接进淘汰赛
                            if($.isEmptyObject(data.results)){
                                data.results=[];
                                me.loadMembers(competitionId,2);
                            }else{
                                data.array=[];
                                for(var i in data.results){
                                    data.array=data.array.concat(data.results[i]);
                                }

                                data.results=data.array;
                            }
                        }
                        var tpl=$("#playerTpl").html();
                        var html=juicer(tpl,data);
                        $("#player1").append(html);
                        $("#player2").append(html);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        submitForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccessRedirect);
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"user/competitions/"+competitionId;
                        },3000);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        }
    }
})(config,functions);


$(document).ready(function(){
    var params=functions.getPathParams(location.href);
    if(params.group){
        $("#group").val(params.group);
    }
    if(params.position){
        $("#position").val(params.position);
    }

    competitionResultUpdate.loadMembers(competitionId,stage);

    $("#date").date_input({
        dateToString: function(date) {
            var month = (date.getMonth() + 1).toString();
            var dom = date.getDate().toString();
            if (month.length == 1) month = "0" + month;
            if (dom.length == 1) dom = "0" + dom;
            return date.getFullYear() + "-" + month + "-" + dom;
        }
    });

    $(".selectPlayer").change(function(){
        var selected=$(this).find("option:selected");
        var logo=selected.data("logo");
        var name=selected.text();

        $(this).parent().find(".name").text(name);
        $(this).parent().find(".thumb").attr("src",logo);
    });

    $('#search1').marcoPolo({
        url:config.ajaxUrls.searchPeople,
        param:"name",
        minChars:2,
        formatData:function(data){
            return data.results;
        },
        formatItem: function (data, $item) {
            return data.fullname + '(' + data.email+')';
        },
        onSelect: function (data, $item) {
            $("#notary").val(data.id);
            this.val(data.fullname);
        }
    });
    $('#search2').marcoPolo({
        url:config.ajaxUrls.searchPeople,
        param:"name",
        minChars:2,
        formatData:function(data){
            return data.results;
        },
        formatItem: function (data, $item) {
            return data.fullname + '(' + data.email+')';
        },
        onSelect: function (data, $item) {
            $("#referee").val(data.id);
            this.val(data.fullname);
        }
    });

    $("#myForm").validate({
        ignore:[],
        rules:{
            p1:{
                required:true
            },
            p2:{
                required:true
            },
            date_started:{
                required:true
            },
            round:{
                number:true
            },
            sn:{
                number:true
            },
            site:{
                required:true
            }
        },
        messages:{
            p1:{
                required:config.validErrors.required
            },
            p2:{
                required:config.validErrors.required
            },
            date_started:{
                required:config.validErrors.required
            },
            round:{
                number:config.validErrors.number
            },
            sn:{
                number:config.validErrors.number
            },
            site:{
                required:config.validErrors.required
            }
        },
        submitHandler:function(form) {
            competitionResultUpdate.submitForm(form);
        }
    });
});