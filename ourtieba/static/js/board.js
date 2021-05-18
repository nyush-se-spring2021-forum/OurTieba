var Uid = parseInt($("#Uid").val().trim());
var title_input = $("#title");
var w_c = $(".word-count");
var sub_btn = $(".sub-btn");
var unsub_btn = $(".unsub-btn");
var redirect_href = "/login?redirect=" + location.href;
var like_btn = $(".like-btn");
var dislike_btn = $(".dislike-btn");

// must add css after DOM render, upper place won't work
like_btn.css("border-radius","5px");
dislike_btn.css("border-radius","5px");

// prepare ueditor
var ue = UE.getEditor('editor', {
    toolbars: [["emotion", "simpleupload", "insertimage", "insertvideo", "link", "|", "undo", "redo"]],
    autoHeightEnabled: false,
    enterTag: "br",  // user "br" instead of "p" to escape line
    retainOnlyLabelPasted: true, // remove all attributes of pasted tag
    pasteplain: true,  // paste as plaintext
    enableContextMenu: false,
    imageScaleEnabled: false,
    elementPathEnabled : false,
    wordCount: !!Uid,
    maximumWords: 2000
});
ue.ready(() => {
    // get rid of popup messages
    $(".edui-editor-messageholder.edui-default").css({ "visibility": "hidden" });

    // lock editor when user not logged-in
    if (!Uid) {
        // disable title
        title_input.attr("disabled", "disabled").attr("placeholder", "You must log in to create a post!");

        // disable editor
        ue.setDisabled();

        // add log in display info
        var login_href = "/login?redirect=" + parent.location.href;
        ue.setContent("Please <a href='" + login_href + "' target='_top'>log in</a> to create post.")

        // disable buttons
        $(".btn-submit").attr("disabled", "disabled");
        $("#btn-preview").attr("disabled", "disabled");
    }

    // disable popup window to modify/clear link
    $(".edui-popup-content").css("display", "none");
})

// set preview-img link
$(".preview-img").on("click", function () {
    let Pid = this.getAttribute("data-Pid");
    window.open("/photos?Pid="+Pid);  // show images within the post content
})

// monitor title word count
title_input.on("keyup", function () {
    let count = $(this).val().length;
    let is_exceed = count > 150;
    w_c.text((is_exceed?"Title length exceeded! ":"")+count+"/150").css("color", is_exceed?"#d00303":"#aaa");
})

function sendSub(action) {  // action: sub/unsub, 1=sub, 0=unsub
    let hide_btn = action ? sub_btn: unsub_btn;
    let show_btn = action ? unsub_btn: sub_btn;
    $.ajax({
        method: "POST",
        url: "/api/subscribe",
        dataType: "json",
        data: {Bid: $("#Bid").val().trim(), action: action},
        success: (data) => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                hide_btn.css("display", "none");
                show_btn.css("display", "inline");
                alert(action ? "You are the No."+data.subs_count+" subscriber of this board!"
                    :"Unsubscribe successful!");
                $(".text-num").text(data.subs_count);
            }
        }
    })
}

// unsubscribe button events
unsub_btn.on("mouseenter", function () {
    $(this).text("Leave");
}).on("mouseleave", function () {
    $(this).text("Joined");
}).on("click", function () {
    if (!Uid) {
        location.href = redirect_href;
    }
    sendSub(0);
})

// subscribe button events
sub_btn.on("mouseenter", function () {
    $(this).text("Now!");
}).on("mouseleave", function () {
    $(this).text("Join");
}).on("click", function () {
    if (!Uid) {
        location.href = redirect_href;
    }
    sendSub(1);
})

function sendLike(which, target, id) {  // which: like/dislike, 1=like, 0=dislike
    if (!Uid) {
        return location.href = "/login";
    }
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
// like/dislike post
like_btn.on("click", function () {
    let me = this.id;  // plb-xxx
    sendLike(1, (me.substr(0, 1)==="p")?"post":"comment", me.substring(4, me.length));
})

dislike_btn.on("click", function () {
    let me = this.id;
    sendLike(0, (me.substr(0, 1)==="p")?"post":"comment", me.substring(4, me.length));
})

// submit post
$(".btn-submit").on("click", () => {
    // check login status
    if (!Uid) {
        alert("Please log in to create a post!");
        location.href = "/login";
        return
    }
    // check title not null
    var title = title_input.val().trim();
    if (!title) {
        alert("You must enter a title!");
        return
    }
    // if everything ok, send request
    var Bid = $("#Bid").val()
    $.ajax({
        method: "POST",
        url: "/api/post/add",
        dataType: "json",
        data: {
            Bid: Bid,
            title: title,
            content: ue.getContent().trim(),
            text: ue.getContentTxt().trim()
        },
        success: data => {
            if (data.status !== 1) {
                alert(data.error.msg);
            } else {
                location.href = "/board/" + Bid + "?order=newest"
            }
        }
    })
})

$("#btn-preview").on("click", previewPost);

function previewPost() {
    let opener = window.open("", "_blank");
    opener.document.write("<title>Preview Post</title>");  // window title
    opener.document.write('<link rel="stylesheet" ' +
        'href="/ueditor/themes/iframe.css">')  // style same as in iframe.css
    opener.document.write('<p style="font-size: 2rem">' + title_input.val() + '</p>')  // title
    opener.document.write('<div style="height: 0; width: 100%; border-top: 2px dashed black">' +
        '</div>')  // a separate line
    opener.document.writeln(ue.getContent());  // content
}