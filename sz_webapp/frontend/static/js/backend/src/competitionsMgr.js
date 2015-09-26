var competitionsMgr=(function(config,functions){

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
                        if(oObj.aData.status>=1){
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
                { "mDataProp": "c_type",
                    "fnRender":function(oObj){
                        return config.competitionType[oObj.aData.c_type];
                    }
                },
                { "mDataProp": "stick",
                    "fnRender":function(oObj){
                        if(oObj.aData.stick){
                            return "是";
                        }else{
                            return "";
                        }
                    }
                },
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        var string="";
                        if(oObj.aData.stick==""){
                            string+='<a href="'+oObj.aData.id+'" class="top">置顶</a>&nbsp;&nbsp;';
                        }

                        if(oObj.aData.status ==0){
                            string+= '<a href="'+oObj.aData.id+'" class="delete">删除</a>';
                        }

                        return string;
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
                });
            },
            "fnServerData": function(sSource, aoData, fnCallback) {

                //回调函数
                $.ajax({
                    "dataType":'json',
                    "type":"get",
                    "url":sSource,
                    "data":aoData,
                    contentType :"application/json; charset=UTF-8",
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
        top:function(id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.competitionTop.replace(":competitionId",id),
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
        },
        delete:function(id){
            functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.competitionDelete.replace(":competitionId",id),
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

    competitionsMgr.createTable();

    $("#searchBtn").click(function(e){
        competitionsMgr.tableRedraw();
    });

    $("#myTable").on("click","a.delete",function(){
        if(confirm(config.messages.confirmDelete)){
            competitionsMgr.delete($(this).attr("href"));
        }
        return false;
    }).on("click","a.top",function(){
            competitionsMgr.top($(this).attr("href"));
            return false;
        });
});

