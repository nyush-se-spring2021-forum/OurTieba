// parse url to find "redirect" param (this is needed because login requests may come from iframes)
var query = window.location.search.substring(1);
var vars = query.split("&");
var r_link;
vars.forEach((e) => {
    if (e.startsWith("redirect=")) {
        r_link = e.substring(9);
    }
})

$(function () {
    $("#btn_submit").on("click", function () {
        let uname = $("#uname").val().trim();
        let password = $("#password").val().trim();

        if (uname !== "" && password !== "") {
            $.ajax({
                url: '/api/auth/login',
                type: 'post',
                dataType: 'json',
                data: {uname: uname, password: password},
                success: function (response) {
                    let msg = "";
                    if (response.status !== 0) {
                        if (!r_link) {
                            let ref = document.referrer;
                            if (ref.trim().length === 0) {
                                location.href = "/";
                                return
                            }
                            r_link = (ref.indexOf(location.protocol+"//"+location.host) === 0) ?
                                ref : "/redirect?link="+ref;
                        }
                        location.href = r_link;
                    } else {
                        msg = response.error['msg'];
                        $("#username-err").html(msg).show();

                    }

                }
            });
        }
    });
});