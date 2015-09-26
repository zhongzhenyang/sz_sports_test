var sportsUpdate=(function(config,functions){
    return{
        submitForm:function(form){
            var formObj=$(form).serializeObject();
            formObj.options={
                goals_require:$("#goals_require").val(),
                branch_require:$("#branch_require").val(),
                goal_difference_require:$("#goal_difference_require").val(),
                individual_enable:true
            };
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
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"admin/athletics/";
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

    functions.createQiNiuUploader({
        maxSize:config.uploader.sizes.img,
        filter:config.uploader.filters.img,
        uploadBtn:"thumbUploadBtn",
        multipartParams:null,
        uploadContainer:"thumbUploadContainer",
        fileAddedCb:null,
        progressCb:null,
        uploadedCb:function(info,file,up){
            //判断图片尺寸
            $.get(info.url+"?imageInfo",function(data){
                if(data.width==200&&data.height==200){
                    $("#thumb").attr("src",info.url);
                    $("#drawing").val(info.url);
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageNot200X200);
                }

            });
        }
    });

    $("#myForm").validate({
        ignore:[],
        rules:{
            name:{
                required:true,
                maxlength:32
            },
            profile:{
                required:true
            },
            goals_require:{
                required:true
            },
            branch_require:{
                required:true
            },
            goal_difference_require:{
                required:true
            }
        },
        messages:{
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            profile:{
                required:config.validErrors.required
            },
            goals_require:{
                required:config.validErrors.required
            },
            branch_require:{
                required:config.validErrors.required
            },
            goal_difference_require:{
                required:config.validErrors.required
            }

        },
        submitHandler:function(form) {
            sportsUpdate.submitForm(form);
        }
    });
});
