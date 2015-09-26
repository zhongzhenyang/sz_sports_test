var competitionUpdate=(function(config,functions){
    return {
        submitForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();
            formObj.options={
                individual:$("#requireTeam").val()
            };
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
                            window.location.href=document.getElementsByTagName('base')[0].href+"user/"+currentUserId+"/me/competitions";
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

    $("#startDate,#deadline").date_input({
        dateToString: function(date) {
            var month = (date.getMonth() + 1).toString();
            var dom = date.getDate().toString();
            if (month.length == 1) month = "0" + month;
            if (dom.length == 1) dom = "0" + dom;
            return date.getFullYear() + "-" + month + "-" + dom;
        }
    });

    $("#category").change(function(){
        var value=$(this).val(),
            src;
        if($("#thumb").val()==""){
            if(value==""){
                src="static/images/frontend/default/teamLogo.png";
            }else{
                src=$(this).find("option:selected").data("logo");
                $("#thumb").val(src);
            }
            $("#thumbShow").attr("src",src);
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
            name:{
                required:true,
                maxlength:32
            },
            athletic_item_id:{
                required:true
            },
            date_started:{
                required:true
            },
            date_reg_end:{
                required:true
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
            },
            site:{
                maxlength:64
            },
            host:{
                maxlength:64
            },
            organizer:{
                maxlength:64
            },
            sponsor:{
                maxlength:64
            },
            intro:{
                maxlength:5000
            },
            requirement:{
                maxlength:5000
            }
        },
        messages:{
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            athletic_item_id:{
                required:config.validErrors.required
            },
            date_started:{
                required:config.validErrors.required
            },
            date_reg_end:{
                required:config.validErrors.required
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
            },
            site:{
                maxlength:config.validErrors.maxLength.replace("${max}",64)
            },
            host:{
                maxlength:config.validErrors.maxLength.replace("${max}",64)
            },
            organizer:{
                maxlength:config.validErrors.maxLength.replace("${max}",64)
            },
            sponsor:{
                maxlength:config.validErrors.maxLength.replace("${max}",64)
            },
            intro:{
                maxlength:config.validErrors.maxLength.replace("${max}",5000)
            },
            requirement:{
                maxlength:config.validErrors.maxLength.replace("${max}",5000)
            }
        },
        submitHandler:function(form) {
            competitionUpdate.submitForm(form);
        }
    });
});