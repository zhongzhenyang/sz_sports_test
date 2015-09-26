var moreCompetitionResult=(function(config,functions){
    return {
        timer:null,
        offset:0,
        type:"user",
        loadData:function(type,offset){
            var me=this;
            var url="";
            if(type=="user"){
                url=config.ajaxUrls.moreCROfUser.replace(":userId",userId);
            }else if(type=="userSport"){
                url=config.ajaxUrls.moreCROfUserSport.replace(":athleteId",athleteId).replace(":athleticId",athleticId);
            }else{
                url=config.ajaxUrls.moreCROfTeam.replace(":teamId",teamId);
            }
            $.ajax({
                url:url,
                method:"get",
                data:{
                    limit:me.offset==0?config.perLoadCounts.list*2:config.perLoadCounts.list,
                    offset:offset
                },
                success:function(data){
                    if(data.success){
                        if((me.offset==0&&data.results.length==config.perLoadCounts.list*2)||
                            data.results.length==config.perLoadCounts.list){
                            me.offset+=config.perLoadCounts.list;
                        }else{
                            me.offset=-1;
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
                    me.loadData(moreCompetitionResult.type,moreCompetitionResult.offset);
                }
            },200);
        }
    }
})(config,functions);
$(document).ready(function(){
    var params=functions.getPathParams(location.href);
    moreCompetitionResult.type=params.type;
    moreCompetitionResult.loadData(moreCompetitionResult.type,moreCompetitionResult.offset);


    $(window).scroll(function(){
        moreCompetitionResult.scrollHandler();
    });
});