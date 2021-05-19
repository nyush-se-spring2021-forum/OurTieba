$(function () {
    $("#btn_submit").on("click", function () {
        let uname = $("#uname").val().trim();
        let nickname = $("#nickname").val().trim();
        let password = $("#password").val().trim();
        let rpassword = $("#repeat-password").val().trim();
        let u_err = $("#username-err");

        if (password !== rpassword) {
            u_err.html("Passwords don't match.").show();
        } else if (uname !== "" && nickname !== "" && password !== "") {
            $.ajax({
                url: '/api/auth/register',
                type: 'post',
                dataType: 'json',
                data: {uname: uname, password: password, nickname: nickname},
                success: function (response) {
                    if (response.status !== 0) {
                        location.href = "/";
                    } else {
                        let msg = response.error['msg'];
                        u_err.html(msg).show();
                    }

                }
            });
        }
    });
});