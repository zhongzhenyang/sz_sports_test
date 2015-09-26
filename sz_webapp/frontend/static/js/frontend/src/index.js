var index=(function(config,functions){
    return {
        loadCompetitions:function(){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.competitionsGetAll,
                method:"get",
                success:function(data){
                    if(data.success){
                        if(data.results.length!=0){
                            for(var i= 0,len=data.results.length;i<len;i++){
                                data.results[i].typeTxt=config.competitionType[data.results[i].type];
                            }
                        }else{
                            data.noData=true;
                        }
                        var tpl=$("#resultTpl").html();
                        var html=juicer(tpl,data);
                        $("#myList").html(html);
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
    index.loadCompetitions();
});