var competitionDetail=(function(config,functions){
    return {
        joinBtnCtrl:function(competitionId){
            $.ajax({
                url:config.ajaxUrls.competitionCanJoin.replace(":competitionId",competitionId),
                method:"get",
                success:function(data){
                    if(data.success){
                        if(data.status=="yes"){
                            $("#join").remove();
                            $("#unJoin").removeClass("hidden");
                        }else{
                            $("#unJoin").remove();
                            $("#join").removeClass("hidden");
                        }
                    }else{
                        $("#join").remove();
                        $("#unJoin").remove();
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        loadMembers:function(competitionId){
            $.ajax({
                url:config.ajaxUrls.competitionTeamsGetAll.replace(":competitionId",competitionId),
                method:"get",
                contentType :"application/json; charset=UTF-8",
                data:{
                    stage:1
                },
                success:function(data){
                    if(data.success){
                        var tpl=$("#memberTpl").html();
                        data.canPersonJoin=(canPersonJoin=="true"?true:false);
                        var html=juicer(tpl,data);
                        $("#members").html(html);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        join:function(el,competitionId){
            functions.showLoading();

            $.ajax({
                url:config.ajaxUrls.competitionJoin.replace(":competitionId",competitionId),
                type:"post",
                data:{

                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        window.location.reload();
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        unJoin:function(el,competitionId){
            functions.showLoading();

            $.ajax({
                url:config.ajaxUrls.competitionUnJoin.replace(":competitionId",competitionId),
                type:"post",
                data:{

                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        window.location.reload();
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        promote:function(el,competitionId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.competitionPromote.replace(":competitionId",competitionId),
                type:"post",
                data:{

                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.competitionPromote);
                        el.remove();
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        }
    }
})(config,functions);
$(document).ready(function(){
    competitionDetail.loadMembers(competitionId);
    competitionDetail.joinBtnCtrl(competitionId);

    $("#promote").click(function(){
        competitionDetail.promote($(this),competitionId);
    });

    $("#join").click(function(){
        competitionDetail.join($(this),competitionId);
    });

    $("#unJoin").click(function(){
        competitionDetail.unJoin($(this),competitionId);
    });
});