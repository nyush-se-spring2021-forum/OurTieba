// send round query for update, /get_log?t=timstamp
// return: new message count between session["last_check"] and t
//
// ON login: session["last_check"] = User.lastCheck
// ON CLICK new_message button:
//      fetch data between session["last_check"] and current timestamp
// 	    session["last_check"] = current timestamp
// 	    User.lastCheck = current timestamp

function getLog() {
    $.ajax({
        method: "GET",
        url: "/api/get_log?t=" + new Date().getTime() / 1000,
        success: data => {
            let count = (data.code===200) ? data.new_count : 0;
            $("#new_message").text("New Messages: " + count);
        }
    })
    setTimeout(getLog, 5000);
}
window.onload = function () {
    getLog();
}