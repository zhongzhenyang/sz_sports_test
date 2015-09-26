$(document).ready(function(){
    $("#myForm").validate({
        rules: {
            email: {
                required:true,
                email:true,
                rangelength:[6, 30]
            },
            password:{
                required:true,
                rangelength:[6, 120]
            }
        },
        messages: {
            email: {
                required:config.validErrors.required,
                email:config.validErrors.email,
                rangelength:config.validErrors.rangeLength.replace("${min}",6).replace("${max}",30)
            },
            password:{
                required:config.validErrors.required,
                rangelength:config.validErrors.rangeLength.replace("${min}",6).replace("${max}",120)
            }
        },
        submitHandler:function(form){
            form.submit();
        }
    });

    $("input[type='password']").keydown(function(e){
        if(e.keyCode==13){
            $("#myForm")[0].submit();
        }
    });
});
