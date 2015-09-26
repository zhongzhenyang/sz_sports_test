var momentsMgr=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.momentsGetAll,
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
                { "mDataProp": "details",
                    "fnRender":function(oObj){
                        return "<a target='_blank' href='"+oObj.aData.details.image+"'>" +
                            "<img class='thumb' src='"+oObj.aData.details.image+"'></a>";
                    }},
                { "mDataProp": "status",
                    "fnRender":function(oObj){
                        return config.status.image[oObj.aData.status];
                    }},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        var string='<a href="'+oObj.aData.id+'" class="delete">删除</a>';
                        if(oObj.aData.status==config.status.image["-2"]){
                            string+='&nbsp;&nbsp;<a href="'+oObj.aData.id+'" class="yes">通过</a>';
                        }
                        return string;
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
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
                url:config.ajaxUrls.momentsAudit,
                type:"post",
                dataType:"json",
                data:{
                    match_highlight_id:id,
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
        yes:function(id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.momentsAudit.replace(":id",id),
                type:"post",
                dataType:"json",
                data:{
                    match_highlight_id:id,
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

    momentsMgr.createTable();

    $("#searchBtn").click(function(e){
        momentsMgr.tableRedraw();
    });

    $("#myTable").on("click","a.delete",function(){
        if(confirm(config.messages.confirmDelete)){
            momentsMgr.remove($(this).attr("href"));
        }
        return false;
    }).on("click","a.yes",function(){
            momentsMgr.yes($(this).attr("href"));
            return false;
        });
});

