$(document).ready(function(){
    $('#waterfallContainer').waterfall({
        colWidth:192,
        checkImagesLoaded: false,
        path: function(page) {
            return config.ajaxUrls.personalImagesGet+"?page=" + page;
        },
        callbacks: {
            /*
             * 处理ajax返回数方法
             * @param {String} data
             */
            renderData: function (data) {
                var template = $('#waterfallTpl').html();

                return juicer(template, data);
            }
        }
    });
});