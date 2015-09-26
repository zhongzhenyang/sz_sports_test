var teamUpdate=(function(config,functions){
    return {
        submitForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();

            formObj.logo=$("#thumb").val();
            formObj.uniform=$("#clothing").val();

            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                contentType :"application/json; charset=UTF-8",
                data:JSON.stringify(formObj),
                success:function(response){
                    if(response.success){
                        $().toastmessage("showSuccessToast",config.messages.optSuccessRedirect);
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"user/teams/"+(teamId?teamId:response.team.id);
                        },3000);
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
$(document).ready(function(){
    if(location.href.indexOf("sport_id")==-1&&location.href.indexOf("update")==-1){
        window.location.href=document.getElementsByTagName('base')[0].href+"user/"+userId+"/me";
    }
    functions.initSelectGroup();

    var params=functions.getPathParams(location.search);
    var sportId=params.sport_id;
    $("#sportId").val(sportId);


    functions.createQiNiuUploader({
        maxSize:config.uploader.sizes.img,
        filter:config.uploader.filters.img,
        uploadBtn:"thumbUploadBtn",
        multipartParams:null,
        uploadContainer:"thumbUploadContainer",
        fileAddedCb:null,
        progressCb:null,
        uploadedCb:function(info,file,up){
            $("#thumbShow").attr("src",info.url);
            $("#thumb").val(info.url);
            //判断图片尺寸
            /*$.get(info.url+"?imageInfo",function(data){
                if(data.width==data.height&&data.width<=500&&data.height<=500){
                    $("#thumbShow").attr("src",info.url);
                    $("#thumb").val(info.url);
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageNotLt500x500);
                }

            });*/
        }
    });

    functions.createQiNiuUploader({
        maxSize:config.uploader.sizes.img,
        filter:config.uploader.filters.img,
        uploadBtn:"clothingUploadBtn",
        multipartParams:null,
        uploadContainer:"clothingUploadContainer",
        fileAddedCb:null,
        progressCb:null,
        uploadedCb:function(info,file,up){
            $("#clothingShow").attr("src",info.url);
            $("#clothing").val(info.url);
            //判断图片尺寸
            /*$.get(info.url+"?imageInfo",function(data){
                if(data.width==data.height&&data.width<=500&&data.height<=500){
                    $("#clothingShow").attr("src",info.url);
                    $("#clothing").val(info.url);
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageNotLt500x500);
                }

            });*/
        }
    });

    $("#myForm").validate({
        ignore:[],
        rules:{
            name:{
                required:true,
                maxlength:32
            },
            abbr_name:{
                required:true,
                maxlength:12
            },
            home_site:{
                required:true,
                maxlength:32
            },
            contact_me:{
                required:true,
                maxlength:32
            },
            loc_state:{
                required:true
            },
            loc_city:{
                required:true
            }
        },
        messages:{
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            abbr_name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",12)
            },
            home_site:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            contact_me:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            loc_state:{
                required:config.validErrors.required
            },
            loc_city:{
                required:config.validErrors.required
            }
        },
        submitHandler:function(form) {
            teamUpdate.submitForm(form);
        }
    });
});