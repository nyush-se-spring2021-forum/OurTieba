$(function () {
    $("#btn_submit").on("click", function () {
        let aname = $("#aname").val().trim();
        let password = $("#password").val().trim();

        if (aname !== "" && password !== "") {
            $.ajax({
                url: '/admin/auth/login',
                type: 'post',
                dataType: 'json',
                data: {aname: aname, password: password},
                success: function (response) {
                    let msg = "";
                    if (response.status !== 0) {
                        window.location = "/admin/dashboard";
                    } else {
                        msg = response.error['msg'];
                        $("#username-err").html(msg).show();

                    }

                }
            });
        }
    });
});