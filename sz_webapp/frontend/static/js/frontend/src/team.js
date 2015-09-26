var team=(function(config,functions){
    return {
        join:function(teamId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.teamJoin.replace(":teamId",teamId),
                type:"post",
                data:{

                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.joinTeam);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        unJoin:function(teamId){
            functions.showLoading();
            $.ajax({
                 url:config.ajaxUrls.teamUnJoin.replace(":teamId",teamId),
                 type:"post",
                 data:{

                 },
                 success:function(data){
                     if(data.success){
                         functions.hideLoading();
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
        /**
         *踢出
         * @param teamId
         * @param userId
         */
        kickOut:function(userId,teamId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.teamKickOut.replace(":teamId",teamId),
                type:"post",
                data:{
                    account_id:userId
                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
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
        /**
         *解散
         * @param teamId
         * @pram currentUserId
         */
        dismiss:function(teamId,currentUserId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.teamDismiss.replace(":teamId",teamId),
                type:"post",
                data:{

                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"user/"+currentUserId+"/me";
                        },3000);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        promote:function(userId,teamId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.teamPromote.replace(":teamId",teamId),
                type:"post",
                data:{
                    new_creator_id:userId
                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
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
        }
    }
})(config,functions);
$(document).ready(function(){
    $(".teamLeader").parents("li").prependTo($("#teamMembers"));

    $("#join").click(function(){
        team.join(teamId);
    });
    $("#unJoin").click(function(){
        team.unJoin(teamId);
    });

    $("#dismiss").click(function(){
        if(confirm(config.messages.confirm)){
            team.dismiss(teamId,currentUserId);
        }

    });

    $("#teamMembers").on("click",".kickOut",function(){
        if(confirm(config.messages.confirm)){
            team.kickOut($(this).data("member-id"),teamId);
        }

        return false;
    }).on("click",".promote",function(){
            if(confirm(config.messages.confirm)){
                team.promote($(this).data("member-id"),teamId);
            }

            return false;
        });
    $('#waterfallContainer').waterfall({
        colWidth:192,
        checkImagesLoaded: false,
        path: function(page) {
            return config.ajaxUrls.highlightsOfTeamGetAll.replace(":teamId",teamId)+
                    "?limit=" + config.perLoadCounts.list+"&offset="+(page-1)*config.perLoadCounts.list;
        },
        callbacks: {
            /*
             * 处理ajax返回数方法
             * @param {String} data
             */
            renderData: function (data) {
                if(data.results.length<config.perLoadCounts.list){
                    $('#waterfallContainer').waterfall('pause', function() {
                        $('#waterfall-message').html('<p style="color:#666;">没有更多数据...</p>')
                    });
                }

                var template = $('#waterfallTpl').html();

                return juicer(template, data);
            }
        }
    });
});