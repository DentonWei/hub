/**
 * Created by jet on 2017/11/7.
 */
$(function(){
    var as400 = {
        conn :{
        "host": $('#host').val(),
        "database": $('#database').val(),
        "username": $('#username').val(),
        "password": $('#password').val()
        }
    };
    //把json对象转化为字符串
    as400 = JSON.stringify(as400);
    //点击test按钮 相关业务操作
    $("#test").click(function(){
        $.ajax({
            url :"http://192.168.1.112/hub_migrate/test/",
            dataType : "json",
            async : true,
            type : "post",
            data : as400,
            contentType : "application/json;charset=UTF-8",
            success : function(data){
                console.log(data);
                if(data["success"] === 1){
                    $("#evaluation").html("连接AS400成功！！！")
                }
            },
            error : function(err){
                console.log(err);
            }
        })
    });
    //点击submit按钮 相关业务操作
    $("#submit").click(function(){
        $.ajax({
            url :"http://192.168.1.112/hub_migrate/submit/",
            dataType : "json",
            async : true,
            type : "post",
            data : as400,
            contentType : "application/json;charset=UTF-8",
            success : function(data){
                console.log(data);
                var html;
                html = "<li><input id='stdout7' type='checkbox' >"+data["stdout"][7]+"</li>"+
                       "<li><input id='stdout8' type='checkbox' >"+data["stdout"][8]+"</li>"+
                       "<li><input id='stdout10' type='checkbox' >"+data["stdout"][10]+"</li>";
                $("#tableList").html(html);
            },
            error : function(err){
                console.log(err);
            }
        })
    });

        //把json对象转化为字符串

        $("#create").click(function(){
            var connection = {
                conn:{
                    "host": $('#host').val(),
                    "database": $('#database').val(),
                    "username": $('#username').val(),
                    "password": $('#password').val(),
                    "table" :[$('#stdout7').is(':checked') ? $('#stdout7').parent("li").text(): "",
                              $('#stdout8').is(':checked') ? $('#stdout8').parent("li").text(): "",
                              $('#stdout10').is(':checked') ? $('#stdout10').parent("li").text(): ""],
                    "hive-database" : $('#hive-database').val(),
                    "fields-terminated-by" : $('#terminated').val(),
                    "num-mappers" : $('#mappers').val(),
                    "hive-overwrite" : true,
                    "remarks" : ""
                },
                job:{
                    "name" : $("#jobVaule").val(),
                    "status" : "Running",
                    "type" : 1
                }
            }
            connection = JSON.stringify(connection);
            $.ajax({
                url :"http://192.168.1.112/hub_migrate/create/",
                dataType : "json",
                async : true,
                type : "post",
                data : connection,
                contentType : "application/json;charset=UTF-8",
                success : function(data){
                    console.log(data);
                    if(data.success == 1){
                        window.location.href ="index.html";
                    }
                },
                error : function(err){
                    console.log(err);
                }
            })

        })
})