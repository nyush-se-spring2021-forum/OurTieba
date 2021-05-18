var target = $("#target").val().trim();
var id = $("#id").val().trim();

$("#report-submit").on("click", () => {
    let r_reason = $("#r-reason").val().trim();
    if (r_reason.length === 0) {
        return alert("Please state your reason!");
    }
    $.post({
        url: "/api/report/add",
        data: {target: target, id: id, reason: r_reason},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                alert("Thanks for your report!");
                window.close();
            }
        },
        dataType: "json"
    })
})