var challenge=(function(config,functions){
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
                        $().toastmessage("showSuccessToast",config.messages.challengeSuccess);
                        setTimeout(function(){
                            window.location.href=document.getElementsByTagName('base')[0].href+"user/"+currentUserId+"/me";
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
            $("#notary").val(data.id);
            this.val(data.fullname);
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
            $("#referee").val(data.id);
            this.val(data.fullname);
        }
    });

    $("#myForm").validate({
        ignore:[],
        rules:{
            p1:{
                required:true
            },
            p2:{
                required:true
            },
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
            p1:{
                required:config.validErrors.required
            },
            p2:{
                required:config.validErrors.required
            },
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
            challenge.submitForm(form);
        }
    });
});