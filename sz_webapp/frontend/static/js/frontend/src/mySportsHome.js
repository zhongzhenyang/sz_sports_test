var mySportsHome=(function(config,functions){
    return {
        submitForm:function(form){
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
        unJoinSports:function(sportId,userId){
            $.ajax({
                url:config.ajaxUrls.sportsUnJoin.replace(":userId",userId),
                type:"post",
                data:{
                    athletic_item_id:sportId
                },
                success:function(data){
                    if(data.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        window.location.href=document.getElementsByTagName('base')[0].href+"user/"+userId+"/me/";
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
    $("#unJoinSports").click(function(){
        mySportsHome.unJoinSports(sportId,userId);
    });

    $("#editInfo").click(function(){
        $("#popWindow").removeClass("hidden");
    });

    $("#closePopWindow").click(function(){
        functions.hidePopWindow();
    });
    $("#myForm").validate({
        rules:{
            goodAt:{
                maxlength:32
            },
            number:{
                maxlength:2,
                number:true
            },
            sportAge:{
                required:true,
                maxlength:2,
                number:true
            }
        },
        messages:{
            goodAt:{
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            number:{
                maxlength:config.validErrors.maxLength.replace("${max}",2),
                number:config.validErrors.number
            },
            sportAge:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",2),
                number:config.validErrors.number
            }
        },
        submitHandler:function(form) {
            mySportsHome.submitForm(form);
        }
    });
    $('#waterfallContainer').waterfall({
        colWidth:192,
        checkImagesLoaded: false,
        maxPage:1,
        path: function(page) {
            return config.ajaxUrls.highlightsOfUserAthleticGetAll.replace(":userId",userId).replace(":athleticId",sportId)+
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