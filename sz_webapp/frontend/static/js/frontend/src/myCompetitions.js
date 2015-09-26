var myCompetitions=(function(config,functions){
    return {
        promote:function(competitionId){
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
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        loadData:function(){
            $.ajax({
                url:config.ajaxUrls.competitionsOfUserGetAll,
                method:"get",
                data:{
                    offset:0,
                    limit:100
                },
                success:function(data){
                    if(data.success){
                        if(data.results.length!=0){
                            for(var i= 0,len=data.results.length;i<len;i++){
                                data.results[i].typeTxt=config.competitionType[data.results[i].c_type];
                                data.results[i].statusTxt=config.competitionStatus[data.results[i].status];
                            }
                        }else{
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
        }
    }
})(config,functions);
$(document).ready(function(){
    myCompetitions.loadData();

    $("#myTable").on("click",".promote",function(){
        myCompetitions.promote($(this).attr("href"));
        return false;
    })
});