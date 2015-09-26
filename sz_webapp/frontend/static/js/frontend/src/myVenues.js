
var myVenues=(function(config,functions){
    return {
        loadData:function(){
            $.ajax({
                url:config.ajaxUrls.venuesOfUserGetAll,
                method:"get",
                data:{
                    offset:0,
                    limit:100
                },
                success:function(data){
                    if(data.success){
                        if(data.results.length==0){
                            data.noData=config.messages.noData;
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
        remove:function(el){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.venueDelete.replace(":siteId",el.attr("href")),
                type:"post",
                data:{

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
            })
        }
    }
})(config,functions);
$(document).ready(function(){
    myVenues.loadData();

    $("#myTable").on("click",".delete",function(){
        if(confirm(config.messages.confirm)){
            myVenues.remove($(this));
        }
        return false;
    })
});