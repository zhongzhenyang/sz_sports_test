var editPwd=(function(config,functions){
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
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        window.location.href=document.getElementsByTagName('base')[0].href+"logout";
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
    $("#myForm").validate({
        ignore:[],
        rules:{
            password:{
                required:true,
                rangelength:[6, 20]
            },
            new_password:{
                required:true,
                rangelength:[6, 20]
            },
            newConfirmPwd:{
                equalTo:"#pwd"
            }
        },
        messages:{
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangeLength.replace("${min}",6).replace("${max}",20)
            },
            new_password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangeLength.replace("${min}",6).replace("${max}",20)
            },
            newConfirmPwd:{
                equalTo:config.validErrors.equalTo
            }
        },
        submitHandler:function(form) {
            editPwd.submitForm(form);
        }
    });
});