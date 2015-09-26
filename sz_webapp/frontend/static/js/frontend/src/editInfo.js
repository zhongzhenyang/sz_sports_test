var editInfo=(function(config,functions){
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
                        $().toastmessage("showSuccessToast",config.messages.optSuccessRedirect);
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"user/"+userId+"/me";
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

    $("#birthday").date_input({
        dateToString: function(date) {
            var month = (date.getMonth() + 1).toString();
            var dom = date.getDate().toString();
            if (month.length == 1) month = "0" + month;
            if (dom.length == 1) dom = "0" + dom;
            return date.getFullYear() + "-" + month + "-" + dom;
        }
    });

    functions.initSelectGroup();



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

    $("#myForm").validate({
        ignore:[],
        rules:{
            fullname:{
                required:true,
                maxlength:32
            },
            genre:{
                required:true
            },
            birthday:{
                required:true
            },
            contact_me:{
                required:true,
                maxlength:32
            },
            loc_address:{
                required:true
            },
            loc_state:{
                required:true
            },
            loc_city:{
                required:true
            },
            intro:{
                maxlength:500
            }
        },
        messages:{
            fullname:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            genre:{
                required:config.validErrors.required
            },
            birthday:{
                required:config.validErrors.required
            },
            contact_me:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            loc_address:{
                required:config.validErrors.required
            },
            loc_state:{
                required:config.validErrors.required
            },
            loc_city:{
                required:config.validErrors.required
            },
            intro:{
                maxlength:config.validErrors.maxLength.replace("${max}",500)
            }
        },
        submitHandler:function(form) {
            editInfo.submitForm(form);
        }
    });
});