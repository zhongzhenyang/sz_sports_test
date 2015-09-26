var competitionsToAudit=(function(config,functions){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.competitionsGetAll,
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
                        var string="";
                        if(oObj.status>=1){
                            string="<a  target='_blank' href='user/competitions/"+oObj.aData.id+"'>"+oObj.aData.name+"</a>";
                        }else{
                            string="<a  target='_blank' href='user/competitions/"+oObj.aData.id+"/register'>"+oObj.aData.name+"</a>";
                        }
                        return string
                    }},
                { "mDataProp": "athletic_item",
                    "fnRender":function(oObj){
                        return oObj.aData.athletic_item.name;
                    }
                },
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        return '<a href="1/'+oObj.aData.id+'" class="yes">通过</a>&nbsp;&nbsp;'+
                            '<a href="-1/'+oObj.aData.id+'" class="no">不通过</a>';
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    "name":"c_name",
                    "value":$("#searchContent").val()
                },{
                    "name":"athletic_item_id",
                    "value":$("#searchType").val()
                },{
                    "name":"only_apply_league",
                    "value":1
                });
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
        audit:function(id){
            var ids=id.split("/"),status=ids[0];
            id=ids[1];
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.competitionsAudit.replace(":competitionId",id).replace(":result",status),
                type:"post",
                dataType:"json",
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

    competitionsToAudit.createTable();

    $("#searchBtn").click(function(e){
        competitionsToAudit.tableRedraw();
    });

    $("#myTable").on("click","a.yes,a.no",function(){
        competitionsToAudit.audit($(this).attr("href"));
        return false;
    });
});

