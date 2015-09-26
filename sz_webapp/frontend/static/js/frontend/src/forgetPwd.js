var forgetPwd=(function(config,functions){
    return {
        submitForm:function(form){
            var formObj=$(form).serializeObject();
            functions.showLoading();
            $.ajax({
                url:$(form).attr("action"),
                type:"post",
                dataType:"json",
                data:formObj,
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        $("#tip").removeClass("hidden");
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
        rules:{
            email:{
                required:true,
                email:true,
                rangelength:[6, 30]
            }
        },
        messages:{
            email:{
                required:config.validErrors.required,
                email:config.validErrors.email,
                rangelength:config.validErrors.rangeLength.replace("${min}",6).replace("${max}",30)
            }
        },
        submitHandler:function(form) {
            forgetPwd.submitForm(form);
        }
    });
});