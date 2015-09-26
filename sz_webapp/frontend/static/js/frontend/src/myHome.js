var myHome=(function(config,functions){
    return {
        sports:{},
        attentionBtnCtrl:function(userId){
            $.ajax({
                url:config.ajaxUrls.attentionStatus.replace(":userId",userId),
                method:"get",
                success:function(data){
                    if(data.success){
                        if(data.status=="yes"){
                            $("#attention").remove();
                            $("#unAttention").removeClass("hidden");
                        }else{
                            $("#unAttention").remove();
                            $("#attention").removeClass("hidden");
                        }
                    }else{
                        $("#attention").remove();
                        $("#unAttention").remove();
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        getAllSports:function(){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.sportsGetAll,
                method:"get",
                success:function(data){
                    if(data.success){
                        for(var i= 0,len=data.results.length;i<len;i++){
                            me.sports[data.results[i].id]=data.results[i];
                        }

                        var tpl=$("#sportsTpl").html();
                        var html=juicer(tpl,data);
                        $("#allSports").html(html);

                        //如果已经有那么多个项目，不需要显示添加
                        if($("#sports li").length-1==data.results.length){
                            $("#addSports").parents("li").remove();
                        }
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        loadAttentions:function(userId){
            $.ajax({
                url:config.ajaxUrls.attentionsGetAll.replace(":userId",userId),
                method:"get",
                success:function(data){
                    if(data.success){
                        if(data.results.length==0){
                            $("#attentionsSection").remove();
                        }else{
                            var tpl=$("#attentionTpl").html();
                            var html=juicer(tpl,data);
                            $("#attentions").html(html);
                        }
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        attention:function(el,userId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.attention.replace(":userId",userId),
                type:"post",
                data:{

                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        functions.hideLoading();
                        el.remove();
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        unAttention:function(el,userId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.unAttention.replace(":userId",userId),
                type:"post",
                data:{

                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        functions.hideLoading();
                        el.remove();
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        joinSports:function(sportId,userId){
            var sport=this.sports[sportId];
            $.ajax({
                url:config.ajaxUrls.sportsJoin.replace(":userId",userId),
                type:"post",
                data:{
                    athletic_item_id:sportId
                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        functions.hidePopWindow();

                        var lastLi=$("#sports li:last");

                        var tpl=$("#sportTpl").html();
                        var html=juicer(tpl,sport);
                        $(html).insertBefore(lastLi);

                        //是否还需要显示添加按钮
                        if($("#sports li").length-1==$("#allSports option").length){
                            lastLi.remove();
                        }
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
    myHome.loadAttentions(userId);
    myHome.getAllSports();
    myHome.attentionBtnCtrl(userId);

    $("#addSports").click(function(){
        functions.showPopWindow();
    });

    $("#joinSports").click(function(){
        myHome.joinSports($("#allSports").val(),userId);
    });

    $("#closePopWindow").click(function(){
        functions.hidePopWindow();
    });

    $("#attention").click(function(){
        myHome.attention($(this),userId);
    });
    $("#unAttention").click(function(){
        myHome.unAttention($(this),userId);
    });
    $('#waterfallContainer').waterfall({
        colWidth:192,
        maxPage:1,
        checkImagesLoaded: false,
        path: function(page) {
            return config.ajaxUrls.highlightsOfUserGetAll.replace(":userId",userId)+
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