var competitionDetailIng=(function(config,functions){
    return {
        /*
         *load淘汰赛比赛
         */
        loadResult:function(competitionId){
            $.ajax({
                url:config.ajaxUrls.competitionResultGetAll.replace(":competitionId",competitionId),
                method:"get",
                data:{
                    stage:3
                },
                success:function(data){
                    if(data.success){
                        if(data.fixtures.length!=0){
                            var tpl=$("#resultTpl").html();
                            var html;

                            for(var i= 0,len=data.fixtures.length;i<len;i++){
                                var p1=functions.findElInArray(data.c_teams,"id",data.fixtures[i].p1);
                                var p2=functions.findElInArray(data.c_teams,"id",data.fixtures[i].p2);

                                data.fixtures[i].p1=p1.team;
                                data.fixtures[i].p2=p2.team;

                                html=juicer(tpl,data.fixtures[i]);
                                $("#"+data.fixtures[i].addition).html(html).
                                    attr("href","user/"+data.fixtures[i]["competition_id"]+"/competition-fixtures/"+data.fixtures[i].id);
                            }
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
        /**
         *load小组赛比赛
         *优化的时候考虑不要一个个append，而是采用html方法一次性加载
         */
        loadResult1:function(competitionId){
            $.ajax({
                url:config.ajaxUrls.competitionResultGetAll.replace(":competitionId",competitionId),
                method:"get",
                data:{
                    stage:2
                },
                success:function(data){
                    if(data.success){
                        if(data.fixtures.length!=0){

                            var tpl=$("#result1Tpl").html();
                            var html;
                            for(var i= 0,len=data.fixtures.length;i<len;i++){

                                var p1=functions.findElInArray(data.c_teams,"id",data.fixtures[i].p1);
                                var p2=functions.findElInArray(data.c_teams,"id",data.fixtures[i].p2);

                                data.fixtures[i].p1=p1.team;
                                data.fixtures[i].p2=p2.team;
                                data.fixtures[i].group=p1.current_rank.group;

                                html=juicer(tpl,data.fixtures[i]);
                                $("#list"+data.fixtures[i].group).append(html);
                            }
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
        /**
         *load预选赛比赛
         */
        loadResult2:function(competitionId){
            $.ajax({
                url:config.ajaxUrls.competitionResultGetAll.replace(":competitionId",competitionId),
                method:"get",
                data:{
                    stage:1
                },
                success:function(data){
                    if(data.success){
                        if(data.fixtures.length!=0){
                            for(var i= 0,len=data.fixtures.length;i<len;i++){
                                var p1=functions.findElInArray(data.c_teams,"id",data.fixtures[i].p1);
                                var p2=functions.findElInArray(data.c_teams,"id",data.fixtures[i].p2);

                                data.fixtures[i].p1=p1.team;
                                data.fixtures[i].p2=p2.team;
                            }

                            var tpl=$("#result2Tpl").html();
                            var html=juicer(tpl,{
                                results:data.fixtures
                            });
                            $("#result2").html(html);
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
        /**
         *load积分榜
         */
        loadIntegrals:function(competitionId,stage){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.competitionRanks.replace(":competitionId",competitionId),
                method:"get",
                data:{
                    stage:stage>=2?2:stage
                },
                success:function(data){
                    if(data.success){
                        if(data.c_teams.length!=0){
                            for(var i= 0,len=data.c_teams.length;i<len;i++){
                                data.c_teams[i]["num"]=i+1;
                            }

                            var tpl=$("#integralTpl").html();
                            data.goalDifference=goalDifference;
                            data.playerIsPerson=playerIsPerson;
                            var html=juicer(tpl,data);
                            $("#integral tbody").html(html);
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
        setStage:function(competitionId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.competitionSetStage.replace(":competitionId",competitionId),
                type:"post",
                data:{
                    stage:$("#stage").val()
                },
                success:function(data){
                    if(data.success){
                        functions.hidePopWindow();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        setTimeout(function(){
                            window.location.reload();
                        },3000);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        end:function(competitionId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.competitionSetStatus.replace(":competitionId",competitionId),
                type:"post",
                data:{
                    status:2
                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        setTimeout(function(){
                            window.location.reload();
                        },3000);
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

    $("#stageTxt").text(function(index,text){
        return config.competitionStage[text];
    });

    if(competitionType==2){
        if(stage==3){
            competitionDetailIng.loadResult(competitionId);
        }

        competitionDetailIng.loadIntegrals(competitionId,stage);

        if(stage>=2){
            competitionDetailIng.loadResult1(competitionId);
        }
    }

    competitionDetailIng.loadResult2(competitionId);

    $("#end").click(function(){
        if(confirm(config.messages.confirm)){
            competitionDetailIng.end(competitionId);
        }
    });

    $("#returnTop").click(function(){
        $("html,body").scrollTop(0);
    });

    $("#setStage").click(function(){
        functions.showPopWindow();
    });

    $("#closePopWindow").click(function(){
        functions.hidePopWindow();
    });

    $("#setStageSubmit").click(function(){
        competitionDetailIng.setStage(competitionId);
    });

    $('#waterfallContainer').waterfall({
        colWidth:192,
        checkImagesLoaded: false,
        path: function(page) {
            return config.ajaxUrls.highlightsOfCompetitionGetAll.replace(":competitionId",competitionId)+
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