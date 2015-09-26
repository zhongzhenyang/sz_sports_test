var venuesMgr=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.venuesGetAll,
            "bInfo":true,
            "bLengthChange": false,
            "bFilter": false,
            "bSort":false,
            "bAutoWidth": false,
            "iDisplayLength":config.perLoadCounts.table,
            "sPaginationType":"full_numbers",
            "oLanguage": {
                "sUrl":config.dataTable.langUrl
            },
            "aoColumns": [
                { "mDataProp": "name",
                    "fnRender":function(oObj){
                        return "<a target='_blank' href='user/sites/"+oObj.aData.id+"'>"+oObj.aData.name+"</a>";
                    }},
                { "mDataProp": "tel"},
                { "mDataProp": "status",
                    "fnRender":function(oObj){
                        return config.status.site[oObj.aData.status];
                    }},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        var string='<a href="'+oObj.aData.id+'" class="delete">删除</a>';
                        if(oObj.aData.status==config.status.site["0"]){
                            string+='&nbsp;&nbsp;<a href="'+oObj.aData.id+'" class="yes">通过</a>';
                        }
                        return string;
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    name:"name",
                    value:$("#searchContent").val()
                },{
                    name:"status",
                    value:$("#searchType").val()
                })
            },
            "fnServerData": function(sSource, aoData, fnCallback) {

                //回调函数
                $.ajax({
                    "dataType":'json',
                    "type":"get",
                    "url":sSource,
                    "data":aoData,
                    "success": function (response) {
                        if(response.success===false){
                            functions.ajaxReturnErrorHandler(response.error_code);
                        }else{
                            var json = {
                                "sEcho" : response.sEcho
                            };

                            for (var i = 0, iLen = response.aaData.length; i < iLen; i++) {
                                response.aaData[i].opt="opt";
                            }

                            json.aaData=response.aaData;
                            json.iTotalRecords = response.iTotalRecords;
                            json.iTotalDisplayRecords = response.iTotalDisplayRecords;
                            fnCallback(json);
                        }

                    }
                });
            },
            "fnFormatNumber":function(iIn){
                return iIn;
            }
        });

        return ownTable;
    }

    return {
        ownTable:null,
        createTable:function(){
            this.ownTable=createTable();
        },
        tableRedraw:function(){
            this.ownTable.fnSettings()._iDisplayStart=0;
            this.ownTable.fnDraw();
        },
        remove:function(id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.venuesAudit,
                type:"post",
                dataType:"json",
                data:{
                    site_id:id,
                    status:-1
                },
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        me.ownTable.fnDraw();
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }

                },
                error:function(){
                    functions.ajaxErrorHandler();
                }
            });
        },
        audit:function(id){

            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.venuesAudit,
                type:"post",
                dataType:"json",
                data:{
                    site_id:id,
                    status:1
                },
                success:function(response){
                    if(response.success){
                        functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        me.ownTable.fnDraw();
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

    venuesMgr.createTable();

    $("#searchBtn").click(function(e){
        venuesMgr.tableRedraw();
    });

    $("#myTable").on("click","a.delete",function(){
        if(confirm(config.messages.confirmDelete)){
            venuesMgr.remove($(this).attr("href"));
        }
        return false;
    }).on("click","a.yes",function(){
            venuesMgr.audit($(this).attr("href"));
            return false;
        });
});

