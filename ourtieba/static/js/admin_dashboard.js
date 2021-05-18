var target_dict = {
    0: "board",
    1: "post",
    2: "comment",
}
var cls_dict = {
    0: "Bid",
    1: "Pid",
    2: "Cid",
}

$("#admin-logout").on("click", function () {
    $.post({
        url: "/admin/auth/logout",
        success: data => {
            if (!data.status) {
                alert("Something went wrong. Try again later.");
            } else {
                location.href = "/admin/login";
            }
        }
    })
})

function manageTarget(action, target) {  // action: 0=delete, 1=restore; target: 0=board, 1=post, 2=comment
    let id = $('#'+cls_dict[target]).val().trim();
    $.ajax({
        method: 'post',
        url: "/admin/"+target_dict[target]+"/"+((action)?"restore":"delete"),
        dataType: 'json',
        data: {Bid: id, Pid: id, Cid: id},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                alert(((action)?'Restore ':'Delete ')+target_dict[target]+id+' successful!');
            }
            clearInput(target);
        }
    });
}

function resolve(ele) {
    let Rid = ele.getAttribute("data-rid");
    $.ajax({
        method: 'post',
        url: "/admin/report/resolve",
        dataType: 'json',
        data: {Rid: Rid},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                alert('Resolve successful!');
            }
            location.reload();
        }
    });
}

function manageUser(action) {  // action: 0=ban, 1=unban
    let Uid = $('#Uid').val().trim();
    let days = $('#days').val().trim();
    $.ajax({
        method: 'post',
        url: "/admin/user/"+((action)?"unban":"ban"),
        dataType: 'json',
        data: {Uid: Uid, days: days},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                alert(((action)?'Unban':'Ban')+' user'+Uid+' successful!');
            }
            $("#Uid").val("");
            $("#days").val("");
        }
    });
}

function clearInput(target) {
    $('#'+cls_dict[target]).val("");
}

$(".mt-btn").on("click", function () {
    let action = $(this).data("action");
    let target = $(this).data("target");
    manageTarget(action, target);
})

$(".mu-btn").on("click", function () {
    let action = $(this).data("action");
    manageUser(action);
})

$("#create-btn").on("click", () => {
    window.open('/admin/create');
})

$(".resolve-btn").on("click", function () {
    resolve(this);
})