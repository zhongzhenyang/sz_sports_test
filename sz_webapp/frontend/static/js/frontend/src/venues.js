var venuses=(function(config,functions){
    return {
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
                url:config.ajaxUrls.venuesGetAll,
                method:"get",
                data:{
                    limit:me.offset==0?2*config.perLoadCounts.list:config.perLoadCounts.list,
                    offset:me.offset,
                    name:$("#searchName").val(),
                    athletic_item_id:$("#searchCategory").val(),
                    loc_state:$("#province").val(),
                    loc_city:$("#city").val(),
                    loc_country:$("#area").val()
                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
                        if(data.results.length!=0){

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
    venuses.loadData();
    venuses.getAllSports();


    $("#searchBtn").click(function(){
        competitions.offset=0;
        $("#myList").html("");
        venuses.loadData();
    });

    $(window).scroll(function(){
        venuses.scrollHandler();
    });
});