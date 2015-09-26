$(document).ready(function(){

    $("#myForm").validate({
        onkeyup:false,
        rules:{
            email:{
                required:true,
                email:true,
                remote:config.ajaxUrls.emailExistOrNot,
                rangelength:[6, 30]
            },
            fullname:{
                required:true,
                maxlength:32
            },
            password:{
                required:true,
                rangelength:[6, 20]
            },
            confirmPwd:{
                equalTo:"#password"
            }
        },
        messages:{
            email:{
                required:config.validErrors.required,
                email:config.validErrors.email,
                remote:config.validErrors.emailExist,
                rangelength:config.validErrors.rangeLength.replace("${min}",6).replace("${max}",30)
            },
            fullname:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangeLength.replace("${min}",6).replace("${max}",20)
            },
            confirmPwd:{
                equalTo:config.validErrors.equalTo
            }
        },
        submitHandler:function(form) {
            form.submit();
        }
    });
});