var myMessages=(function(config,functions){
    return {
        loadData:function(userId){
            $.ajax({
                url:config.ajaxUrls.messagesGetAll.replace(":userId",userId),
                method:"get",
                data:{

                },
                success:function(data){
                    if(data.success){
                        if(data.results.length==0){
                            data.noData=config.messages.noData;
                        }else{
                            for(var i= 0,len=data.results.length;i<len;i++){
                                data.results[i].typeTxt=config.messageType[data.results[i].category];
                                data.results[i].statusTxt=config.messageStatus[data.results[i].status];
                            }
                        }
                        var tpl=$("#trTpl").html();
                        var html=juicer(tpl,data);
                        $("#myTable tbody").html(html);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        handleMsg:function(userId,el){
            var messageId=el.attr("href");
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.messageHandle.replace(":userId",userId).replace(":messageId",messageId),
                method:"post",
                data:{
                   result:el.data("result")
                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        el.parents("tr").remove();
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
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
    myMessages.loadData(userId);

    $("#myTable").on("click",".ctrl",function(){
        myMessages.handleMsg(userId,$(this));
        return false;
    })
});