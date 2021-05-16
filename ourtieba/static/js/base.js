$(function () {
    $('[data-toggle="tooltip"]').tooltip()
    $("#log-out").on("click", function () {
        $.post({
            url: "/api/auth/logout",
            success: data => {
                if (data.status) {
                    location.reload();
                } else {
                    alert("Something went wrong. Try again later.")
                }
            },
            dataType: "json"
        })
    })
    $("#new_message").on("click", function () {
        $(this).text("New Messages: 0");  // pretend there is no new message in between, which mostly happens
        window.open('/notifications');
    })
})