var moreCompetition=(function(config,functions){
    return {
        timer:null,
        offset:0,
        loadData:function(type,offset){
            var me=this;
            var url="";
            if(type=="user"){
                url=config.ajaxUrls.moreCompetitionsOfUser.replace(":userId",userId);
            }else if(type=="userSport"){
                url=config.ajaxUrls.moreCompetitionsOfUserSport.replace(":athleteId",athleteId).replace(":athleticId",athleticId);
            }else{
                url=config.ajaxUrls.moreCompetitionsOfTeam.replace(":teamId",teamId);
            }
            $.ajax({
                url:url,
                method:"get",
                data:{
                    offset:offset,
                    limit:me.offset==0?config.perLoadCounts.list*2:config.perLoadCounts.list
                },
                success:function(data){
                    if(data.success){
                        if((me.offset==0&&data.results.length==config.perLoadCounts.list*2)||
                            data.results.length==config.perLoadCounts.list){
                            me.offset+=config.perLoadCounts.list;
                        }else{
                            me.offset=-1;
                        }
                        for(var i= 0,len=data.results.length;i<len;i++){
                            data.results[i].latest_rank_addition=data.results[i]["latest_rank.addition"];
                        }

                        var tpl=$("#resultTpl").html();
                        var html=juicer(tpl,data);
                        $("#myList").append(html);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        scrollHandler:function(){
            var me=this;
            if(me.timer){
                clearTimeout(me.timer);
                me.timer=null;
            }
            me.timer=setTimeout(function(){
                if(($(document).height()-$(window).height()<=$(window).scrollTop()+340)&&me.offset!=-1){
                    me.loadData(moreCompetition.type,moreCompetition.offset);
                }
            },200);
        }
    }
})(config,functions);
$(document).ready(function(){
    var params=functions.getPathParams(location.href);
    moreCompetition.type=params.type;
    moreCompetition.loadData(moreCompetition.type,moreCompetition.offset);


    $(window).scroll(function(){
        moreCompetition.scrollHandler();
    });


});