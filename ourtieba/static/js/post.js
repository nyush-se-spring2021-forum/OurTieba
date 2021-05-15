var Uid = parseInt($("#Uid").val().trim());
var Pid = parseInt($("#Pid").val().trim());
var Bid = $("#Bid").val().trim();
var like_btn = $(".like-btn");
var dislike_btn = $(".dislike-btn");

// must add css after DOM render, upper place won't work
like_btn.css("border-radius","5px");
dislike_btn.css("border-radius","5px");

// bind back to board events
$(".to-board-item").on("click", () => {
    location.href = "/board/" + Bid;
})
// set OT_image link
$(".OT_image").on("click", function () {
    // let cur_index = $(".OT_image").index(this);
    let src = $(this).attr("src");
    window.open("/photos?Pid="+Pid+"&src="+src);  // show images within both the post and comment content
})
// prepare ueditor
var ue = UE.getEditor('editor', {
    toolbars: [["emotion", "simpleupload", "insertimage", "insertvideo", "link", "|", "undo", "redo"]],
    autoHeightEnabled: false,
    enterTag: "br",  // user "br" instead of "p" to escape line
    retainOnlyLabelPasted: true, // remove all attributes of pasted tag
    pasteplain: true,  // paste as plaintext
    enableContextMenu: false,
    imageScaleEnabled: false,
    elementPathEnabled: false,
    wordCount: !!Uid,
    maximumWords: 1000
});
ue.ready(() => {
    // get rid of popup messages
    $(".edui-editor-messageholder.edui-default").css({"visibility": "hidden"});

    // lock editor when user not logged-in
    if (!Uid) {
        // disable editor
        ue.setDisabled();

        // add log in display info
        var login_href = "/login?redirect=" + parent.location.href;
        ue.setContent("Please <a href='" + login_href + "' target='_top'>log in</a> to create comment.")

        // disable buttons
        $(".btn-submit").attr("disabled", "disabled");
        $("#btn-preview").attr("disabled", "disabled");
    }

    // disable popup window to modify/clear link
    $(".edui-popup-content").css("display", "none");
})

function sendLike(which, target, id) {  // which: like/dislike, 1=like, 0=like
    let url = which ? "/api/like" : "/api/dislike";
    $.ajax({
        method: "POST",
        url: url,
        dataType: "json",
        data: {target: target, id: id},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                let l_b = $("#"+target.substr(0, 1)+"lb-"+id);
                let d_b = $("#"+target.substr(0, 1)+"db-"+id);
                let f = (which) ? d_b : l_b;
                let u = (which) ? l_b : d_b;
                f.removeClass("active");
                if (data["cur_status"]) {
                    u.addClass("active");
                } else {
                    u.removeClass("active");
                }
                $("#"+target.substr(0, 1)+"l-"+id).text(" "+data["like_count"]);
                $("#"+target.substr(0, 1)+"d-"+id).text(" "+data["dislike_count"]);
            }
        }
    })
}

// like/dislike post/comment
like_btn.on("click", function () {
    let me = this.id;
    sendLike(1, (me.substr(0, 1)==="p")?"post":"comment", me.substring(4, me.length));
})

dislike_btn.on("click", function () {
    let me = this.id;
    sendLike(0, (me.substr(0, 1)==="p")?"post":"comment", me.substring(4, me.length));
})

$(".btn-submit").on("click", () => {
    // check login status
    if (!Uid) {
        alert("Please log in to create a comment!");
        location.href = "/login";
        return
    }
    // check content not null
    if (!ue.hasContents()) {
        alert("You must enter comment content!");
        return
    }
    // if everything ok, send request
    var Pid = $("#Pid").val();
    $.ajax({
        method: "POST",
        url: "/api/comment/add",
        dataType: "json",
        data: {
            Pid: Pid,
            content: ue.getContent().trim(),
            text: ue.getContentTxt().trim()
        },
        success: data => {
            if (data.status !== 1) {
                alert(data.error.msg)
            } else {
                location.href = "/post/" + Pid + "?order=desc";
            }
        }
    })
})

$(".btn-reply").on("click", function () {
    let me = $(this);
    insertReply(me.data("uid"), me.data("uname"), me.data("floor"), me.data("cid"));
})

function insertReply(uid, uname, floor, cid) {
    if (!Uid) {return}  // do not insert any content if not logged in
    ue.ready(() => {
        // set as new text
        ue.setContent('<p><a class="OT_reply" data-cid="'+ cid + '"' +' data-uid="'+uid+'"'+'href="/profile/' +
            uid + '" target="_blank">@' + uname + ' (#' + floor + '):</a>&nbsp;</p>')
        ue.focus(true);  // focus cursor at the end of text
    })
}

$("#btn-preview").on("click", previewComment);

function previewComment() {
    var opener = window.open("", "_blank");
    opener.document.write("<title>Preview Comment</title>");  // window title
    opener.document.write('<link rel="stylesheet" ' +
        'href="/ueditor/themes/iframe.css">')  // style same as in iframe.css
    opener.document.write(ue.getContent());  // content
}

$(".p-del-btn").on("click", function () {
    let pid = $(this).data("pid");
    $.ajax({
        method: "POST",
        url: "/api/post/delete",
        dataType: "json",
        data: {Pid: pid},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                location.href = "/board/" + Bid;
            }
        }
    })
})

$(".c-del-btn").on("click", function () {
    let cid = $(this).data("cid");
    $.ajax({
        method: "POST",
        url: "/api/comment/delete",
        dataType: "json",
        data: {Cid: cid},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                location.href = "/post/" + Pid + "?order=desc";
            }
        }
    })
})