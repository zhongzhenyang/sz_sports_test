var search=(function(config,functions){
    return {
        timer:null,
        offset:0,
        getAllSports:function(callback){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.sportsGetAll,
                method:"get",
                success:function(data){
                    if(data.success){

                        var tpl=$("#sportsTpl").html();
                        var html=juicer(tpl,data);
                        $("#searchCategory").append(html);

                        callback();
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
                url:config.ajaxUrls.search,
                method:"get",
                data:{
                    limit:me.offset==0?2*config.perLoadCounts.list:config.perLoadCounts.list,
                    offset:me.offset,
                    name:$("#searchName").val(),
                    category:$("#searchType").val(),
                    athletic_item_id:$("#searchCategory").val(),
                    loc_state:$("#province").val(),
                    loc_city:$("#city").val(),
                    loc_county:$("#area").val()
                },
                success:function(data){
                    if(data.success){
                        functions.hideLoading();
                        if(data.results.length==0){
                            data.noData=config.messages.noData;
                        }

                        if((me.offset==0&&data.results.length==config.perLoadCounts.list*2)||
                            data.results.length==config.perLoadCounts.list){
                            me.offset+=config.perLoadCounts.list;
                        }else{
                            me.offset=-1;
                        }

                        if($("#searchType").val()=="person"){
                            data.type=1;
                        }else{
                            data.type=2;
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
        },
        init:function(){
            var params=functions.getPathParams(location.href);
            var me=this;
            if(params.type){
                $("#searchType").val(params.type);
            }


            functions.initSelectGroup();
            this.getAllSports(function(){
                if(params.sport_id){
                    $("#searchCategory").val(params.sport_id);
                }
                setTimeout(function(){
                    me.loadData();
                },300);
            });
        }
    }
})(config,functions);
$(document).ready(function(){



    search.init();


    $(window).scroll(function(){
        search.scrollHandler();
    });

    $("#searchBtn").click(function(){
        search.offset=0;
        $("#myList").html("");
        search.loadData();
    });
});