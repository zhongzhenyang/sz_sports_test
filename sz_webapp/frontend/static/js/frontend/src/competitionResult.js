var competitionResult=(function(config,functions){
    return {
        loadSectionRecords:function(competitionId,competitionFixtureId){
            $.ajax({
                url:config.ajaxUrls.cRSectionRecordsGetAll.replace(":competitionId",competitionId).
                    replace(":competitionFixtureId",competitionFixtureId),
                method:"get",
                contentType :"application/json; charset=UTF-8",
                data:{

                },
                success:function(data){
                    if(data.success){
                        if(data.results.length==0){
                            $("#sectionRecords").remove();
                        }else{
                            var tpl=$("#sectionRecordTpl").html();
                            data.canCtrl=(currentUserId==managerId?true:false);
                            var html=juicer(tpl,data);
                            $("#sectionRecords tbody").html(html);
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
        loadGoalRecords:function(competitionId,competitionFixtureId){
            $.ajax({
                url:config.ajaxUrls.cRGoalRecordsGetAll.replace(":competitionId",competitionId).
                    replace(":competitionFixtureId",competitionFixtureId),
                method:"get",
                contentType :"application/json; charset=UTF-8",
                data:{

                },
                success:function(data){
                    if(data.success){
                        if(data.results.length==0){
                            $("#goalRecords").remove();
                        }else{
                            var tpl=$("#goalRecordTpl").html();
                            data.canCtrl=(currentUserId==managerId?true:false);
                            for(var i= 0,len=data.results.length;i<len;i++){
                                data.results[i].team=data.results[i]["competition_team.team"];
                                data.results[i].scorer=data.results[i]["scorer.account"];
                                data.results[i].assistant=data.results[i]["assistant.account"];
                            }
                            var html=juicer(tpl,data);
                            $("#goalRecords tbody").html(html);
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
        remove:function(competitionId,competitionFixtureId){
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.cRDelete.replace(":competitionId",competitionId).
                    replace(":competitionFixtureId",competitionFixtureId),
                type:"post",
                contentType :"application/json; charset=UTF-8",
                data:{

                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccessRedirect);
                        window.history.go(-1);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        },
        addScoreForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        window.location.reload();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        addSectionRecordSubmitForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        window.location.reload();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        addGoalRecordSubmitForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        window.location.reload();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        deleteSectionRecord:function(el){
            var id=el.attr("href");
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.cRSectionRecordDelete,
                type:"post",
                contentType :"application/json; charset=UTF-8",
                data:{
                    id:id
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
        },
        deleteGoalRecord:function(el,competitionFixtureId){
            var id=el.attr("href");
            functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.cRGoalRecordDelete,
                type:"post",
                contentType :"application/json; charset=UTF-8",
                data:{
                    competition_fixture_id:competitionFixtureId,
                    match_goal_id:id
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
        },
        loadAllTeamPlayers:function(competitionId,competitionFixtureId){
            $.ajax({
                url:config.ajaxUrls.cRTeamMembers.replace(":competitionId",competitionId).
                    replace(":competitionFixtureId",competitionFixtureId),
                method:"get",
                contentType :"application/json; charset=UTF-8",
                data:{

                },
                success:function(data){
                    if(data.success){
                        var array=[];
                        array=data.results.p1_members.concat(data.results.p2_members);
                        var tpl=$("#playerTpl").html();
                        var html=juicer(tpl,{
                            results:array
                        });
                        $(".players").append(html);
                    }else{
                        functions.ajaxReturnErrorHandler(data.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        editSubmitForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        location.reload();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        }
    }
})(config,functions);



jQuery.validator.addMethod("time", function(value, element) {
    var time = /^[0-9]{1,2}:[0-6]{1}[0-9]{1}$/;
    return this.optional(element) || (time.test(value));
}, config.validErrors.formatError);

$(document).ready(function(){
    $("#returnTop").click(function(){
        $("html,body").scrollTop(0);
    });
    if(goalRequire=="true"){
        competitionResult.loadGoalRecords(competitionId,competitionFixtureId);
    }else{
        competitionResult.loadSectionRecords(competitionId,competitionFixtureId);
    }

    $("#date").date_input({
        dateToString: function(date) {
            var month = (date.getMonth() + 1).toString();
            var dom = date.getDate().toString();
            if (month.length == 1) month = "0" + month;
            if (dom.length == 1) dom = "0" + dom;
            return date.getFullYear() + "-" + month + "-" + dom;
        }
    });

    $('#search1').marcoPolo({
        url:config.ajaxUrls.searchPeople,
        param:"name",
        minChars:2,
        formatData:function(data){
            return data.results;
        },
        formatItem: function (data, $item) {
            return data.fullname + '(' + data.email+')';
        },
        onSelect: function (data, $item) {
            if(typeof data =="string"){
                this.val(data);
            }else{
                $("#notary").val(data.id);
                this.val(data.fullname);
            }
        }
    });
    $('#search2').marcoPolo({
        url:config.ajaxUrls.searchPeople,
        param:"name",
        minChars:2,
        formatData:function(data){
            return data.results;
        },
        formatItem: function (data, $item) {
            return data.fullname + '(' + data.email+')';
        },
        onSelect: function (data, $item) {
            if(typeof data =="string"){
                this.val(data);
            }else{
                $("#referee").val(data.id);
                this.val(data.fullname);
            }
        }
    });


    competitionResult.loadAllTeamPlayers(competitionId,competitionFixtureId);

    $("#delete").click(function(){
        if(confirm(config.messages.confirm)){
            competitionResult.remove(competitionId,competitionFixtureId);
        }
    });
    $("#edit").click(function(){
        $("#popWindow3").removeClass("hidden");
    });

    $("#addScore").click(function(){
        $("#popWindow").removeClass("hidden");
    });

    $("#addSectionRecord").click(function(){
        $("#popWindow2").removeClass("hidden");
    });
    $("#sectionRecords").on("click",".delete",function(){
        competitionResult.deleteSectionRecord($(this),competitionFixtureId);
        return false;
    });
    $("#addGoalRecord").click(function(){
        $("#popWindow1").removeClass("hidden");
    });
    $("#goalRecords").on("click",".delete",function(){
        competitionResult.deleteGoalRecord($(this),competitionFixtureId);
        return false;
    });


    $(".closePopWindow").click(function(){
        $(this).parents(".popWindow").addClass("hidden");
    });

    $('#waterfallContainer').waterfall({
        colWidth:192,
        checkImagesLoaded: false,
        path: function(page) {
            return config.ajaxUrls.highlightsOfCompetitionResultGetAll.replace(":competitionId",competitionId).
                replace(":competitionFixtureId",competitionFixtureId)+
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

    functions.createQiNiuUploader({
        maxSize:config.uploader.sizes.img,
        filter:config.uploader.filters.img,
        uploadBtn:"addImage",
        multipartParams:null,
        uploadContainer:"addImageContainer",
        fileAddedCb:null,
        progressCb:null,
        uploadedCb:function(info,file,up){
            $.ajax({
                url:config.ajaxUrls.highlightsAdd,
                type:"post",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify({
                    competition_fixture_id:competitionFixtureId,
                    details:{
                        image:info.url
                    }
                }),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.imageWaitAudit);
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            })
        }
    });

    $("#myForm").validate({
        ignore:[],
        rules:{
            p1_score:{
                required:true,
                number:true
            },
            p2_score:{
                required:true,
                number:true
            }
        },
        messages:{
            p1_score:{
                required:config.validErrors.required,
                number:config.validErrors.number
            },
            p2_score:{
                required:config.validErrors.required,
                number:config.validErrors.number
            }
        },
        submitHandler:function(form) {
            if(confirm(config.messages.confirm)){
                competitionResult.addScoreForm(form);
            }
        }
    });
    $("#myForm1").validate({
        ignore:[],
        rules:{
            time_scored:{
                required:true,
                time:true
            },
            team_id:{
                required:true
            },
            scorer_id:{
                required:true
            },
            assistant_id:{
                required:true
            }

        },
        messages:{
            time_scored:{
                required:config.validErrors.required,
                time:config.validErrors.formatError
            },
            team_id:{
                required:config.validErrors.required
            },
            scorer_id:{
                required:config.validErrors.required
            },
            assistant_id:{
                required:config.validErrors.required
            }
        },
        submitHandler:function(form) {
            competitionResult.addGoalRecordSubmitForm(form);
        }
    });
    $("#myForm2").validate({
        ignore:[],
        rules:{
            sn:{
                required:true
            },
            p1_scores:{
                required:true
            },
            p2_scores:{
                required:true
            }
        },
        messages:{
            sn:{
                required:config.validErrors.required
            },
            p1_scores:{
                required:config.validErrors.required
            },
            p2_scores:{
                required:config.validErrors.required
            }
        },
        submitHandler:function(form) {
            competitionResult.addSectionRecordSubmitForm(form);
        }
    });
    $("#myForm3").validate({
        ignore:[],
        rules:{
            date_started:{
                required:true
            },
            round:{
                number:true
            },
            sn:{
                number:true
            },
            site:{
                required:true
            }
        },
        messages:{
            date_started:{
                required:config.validErrors.required
            },
            round:{
                number:config.validErrors.number
            },
            sn:{
                number:config.validErrors.number
            },
            site:{
                required:config.validErrors.required
            }
        },
        submitHandler:function(form) {
            competitionResult.editSubmitForm(form);
        }
    });
});