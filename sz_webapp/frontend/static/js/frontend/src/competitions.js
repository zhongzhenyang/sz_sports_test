var competitions=(function(config,functions){
    return {
        timer:null,
        sort:1,
        offset:0,
        getAllSports:function(){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.sportsGetAll,
                method:"get",
                success:function(data){
                    if(data.success){

                        var tpl=$("#sportsTpl").html();
                        var html=juicer(tpl,data);
                        $("#searchCategory").append(html);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        loadData:function(){
            var me=this;
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.competitionsGetAll,
                method:"get",
                data:{
                    limit:me.offset==0?2*config.perLoadCounts.list:config.perLoadCounts.list,
                    offset:me.offset,
                    name:$("#searchName").val(),
                    c_type:$("#searchType").val(),
                    athletic_item_id:$("#searchCategory").val(),
                    status:$("#searchStatus").val(),
                    loc_state:$("#province").val(),
                    loc_city:$("#city").val(),
                    loc_county:$("#area").val(),
                    date_published_orderby:me.sort
                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
                        if(data.results.length!=0){
                            for(var i= 0,len=data.results.length;i<len;i++){
                                data.results[i].typeTxt=config.competitionType[data.results[i].c_type];
                            }

                            if((me.offset==0&&data.results.length==config.perLoadCounts.list*2)||
                                data.results.length==config.perLoadCounts.list){
                                me.offset+=config.perLoadCounts.list;
                            }else{
                                me.offset=-1;
                            }
                        }else{
                            data.noData=true;
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
                    me.loadData();
                }
            },200);
        }
    }
})(config,functions);
$(document).ready(function(){
    functions.initSelectGroup();
    competitions.loadData();
    competitions.getAllSports();



    $("#searchBtn").click(function(){
        competitions.offset=0;
        $("#myList").html("");
        competitions.loadData();
    });

    $(window).scroll(function(){
        competitions.scrollHandler();
    });

    $("#sortDate").click(function(){
        if(competitions.sort==1){
            competitions.sort=-1;
            $(this).removeClass("asc").addClass("desc");
        }else{
            competitions.sort=1;
            $(this).removeClass("desc").addClass("asc");
        }
        competitions.offset=0;
        $("#myList").html("");
        competitions.loadData();
    });

});