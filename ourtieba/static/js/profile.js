var is_current = parseInt($("#is-current").val().trim());
var Uid = parseInt($("#Uid").val().trim());

$("#avatar-upload").on("click", function () {
    $("#uploadImg").trigger('click');
});

$("#uploadImg").on("change", function () {
    uploadImg(this.files[0]);
})

function uploadImg(file) {
    if (file.type.substr(0, 5) !== "image") {
        alert("Invalid File Type!");
        return;
    }
    if (file.size > (3 * 1024 * 1024)) {
        alert("Image Too Large!");
        return;
    }
    const formData = new FormData();
    formData.append("file", file);
    $.ajax({
        method: "post",
        url: "/api/upload?action=uploadavatar",
        data: formData,
        processData: false,
        contentType: false,
        success: (data) => {
            if (data.hasOwnProperty("status")) {
                alert("Successfully uploaded image!");
                location.reload();
            } else {
                alert(data.error.msg);
            }
        }
    })
}

// view original
$("#view-origin").on("click", () => {
    window.open($("#avatar-upload").attr("src"), "_blank");
})

// view info
var cur_page = 1;
var cur_max_page;
var cur_type;

$(".status-box").on("click", function () {
    fetchData($(this).index()/2);  // because of the sep line
})

$(".hide").on("click", () => {
    hidePopup();
})

$(".prev-arrow").on("click", () => {
    cur_page = Math.max(cur_page-1, 1);
    fillData(cur_type);
})
$(".next-arrow").on("click", () => {
    cur_page = Math.min(cur_page+1, cur_max_page);
    fillData(cur_type);
})

var des_dict = {
    0: ((is_current)?"My":"User") + "Posts",
    1: ((is_current)?"My":"User") + "Comments",
    2: ((is_current)?"My":"") + "Subscriptions",
    3: "Browse History",
}
var data_dict = {  // used for caching data
    0: null,  // post data
    1: null, // comment data
    2: null,  // subs data
    3: null,  // history data
}
var cls_dict = {
    0: ".post",
    1: ".comment",
    2: ".subs",
    3: ".history",
}
var page_size_dict = {
    0: 8,
    1: 8,
    2: 5,
    3: 8,
}
function showPopup() {
    $(".pop-up").css("display", "block");
}

function showData(type) {  // 0 = post, 1 = history, 2 = subs
    cur_type = type;
    let l_w = $(".list-wrapper");
    l_w.css("display", "none");  // hide all list-wrappers
    l_w.eq(type).css("display", "block");  // show corresponding list-wrapper
    $(".des-text").text(des_dict[type]);  // add description (it doesn't matter for all or only one)
    fillData(type);
}
function fillData(type) {
    let cur_page_size = page_size_dict[type];
    cur_max_page = Math.max(Math.ceil(data_dict[type]["count"]/cur_page_size), 1);
    let text = cur_page+"/"+cur_max_page;
    $(".index").eq(type).text(text);  // add page info for corresponding list
    // fill data into list for current page
    let cur_index;
    let info = data_dict[type]["info"];
    for (let i=0;i<cur_page_size;i++) {
        cur_index = (cur_page-1)*cur_page_size + i;  // current index of data_dict
        let has_content = cur_index < info.length;  // whether there is no more content
        let cur_node = $(cls_dict[type]).eq(i);  // current content node in the loop
        let cur_info = (has_content) ? info[cur_index] : {};  // current content object in data_dict
        let get_ = function (name) {  /* only define once */
            return (has_content) ? cur_info[name] : "";
        }
        // check status, if deleted assign cur_node to .deleted class else remove
        let status = get_("status").toString();
        let deleted = status === "1" || status === "2";
        if (deleted) {
            cur_node.addClass("deleted");
        } else {
            cur_node.removeClass("deleted");
        }
        let status_text;
        let status_color;
        if (type === 0 || type === 1) {
            switch (status) {case "0": status_text="delete"; status_color="blueviolet"; break; case "1":
                status_text="restore"; status_color="pink"; break; case "2": status_text="banned";
                status_color="grey";}
        }
        let bname = get_("bname");  // all content object have key "bname"
        let bid = get_("Bid");  // all content object have key "bid"
        if (type === 0) {
            let p_title = get_("title");
            let p_time = get_("timestamp");
            let pid = get_("Pid");
            $(".p-title", cur_node).text(p_title).attr("data-href", "/post/"+pid)
                .css("cursor", (deleted)?"default":"pointer");
            $(".p-bname", cur_node).text(bname).attr("data-href", "/board/"+bid)
                .css("cursor", (deleted)?"default":"pointer");
            $(".p-time", cur_node).text(p_time);
            $(".p-del", cur_node).text(status_text).css("color", status_color)
                .css("text-decoration", (status_text==="banned")?"none":"underline")
                .css("cursor", (status_text==="banned")?"default":"pointer")
                .attr("data-pid", pid);
        } else if (type === 3) {
            let h_title = get_("title");
            let is_me = get_("me");
            let h_poster = is_me ? "me" : get_("nickname");
            let h_time = get_("LVT");
            let pid = get_("Pid");
            let uid = get_("Uid");
            $(".h-title", cur_node).text(h_title).attr("data-href", "/post/"+pid)
                .css("cursor", (deleted)?"default":"pointer");
            $(".h-bname", cur_node).text(bname).attr("data-href", "/board/"+bid)
                .css("cursor", (deleted)?"default":"pointer");
            $(".h-poster", cur_node).text(h_poster).css("font-style", (is_me) ? "italic" : "normal")
                .attr("data-href", "/profile/"+uid);
            $(".h-time", cur_node).text(h_time);
        } else if (type === 2){
            let s_cover = (has_content) ? "/cdn/" + get_("cover") : "data:image/gif;base64,iVBORw0KGgo" +
                "AAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgY" +
                "GBgAAAABQABh6FO1AAAAABJRU5ErkJggg==";
            $(".s-cover", cur_node).attr("src", s_cover);
            $(".s-bname", cur_node).text(bname).attr("data-href", "/board/"+bid);
            if (is_current) {
                $(".s-unsub", cur_node).text((has_content) ? "Unsubsribe" : "").attr("data-bid", bid);
            }
        } else {
            let c_text = get_("text");
            let p_title = get_("title");
            let c_time = get_("timestamp");
            let pid = get_("Pid");
            let cid = get_("Cid");
            $(".c-text", cur_node).text(c_text).attr("data-href", "/post/"+pid)
                .css("cursor", (deleted)?"default":"pointer");
            $(".c-ptitle", cur_node).text(p_title).attr("data-href", "/post/"+pid)
                .css("cursor", (deleted)?"default":"pointer");
            $(".c-time", cur_node).text(c_time);
            $(".c-del", cur_node).text(status_text).css("color", status_color)
                .css("text-decoration", (status_text==="banned")?"none":"underline")
                .css("cursor", (status_text==="banned")?"default":"pointer")
                .attr("data-cid", cid);
        }
    }
}
// click to jump
$(".href").on("click", function (){
    location.href = $(this).data("href");
})

// send unsub/sub
$(".s-unsub").on("click", function () {
    let me = $(this);
    let Bid = me.attr("data-bid");
    let action = me.attr("data-a");
    $.ajax({
        method: "POST",
        url: "/api/subscribe",
        dataType: "json",
        data: {Bid: Bid, action: action},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                $(".status-num").eq(2).text(data.subs_count);
                me.text((action==="0")?"Subscribe":"Unsubscribe").attr("data-a", (action==="0")?"1":"0")
                    .css("color", (action==="0")?"pink":"red");
                data_dict[2] = null;  // must clear cache, otherwise discrepancy
            }
        }
    })
})

function fetchData(type) {
    // show popup first
    showPopup();
    // if cached, do not fetch new data
    if (data_dict[type]) {return showData(type);}
    // else, go fetch and cache data
    // while data not coming, display loading message (can be simulated by sleeping at server in route "/fetch")
    $(".loading").css("display", "flex");
    $.ajax({
        method: "GET",
        url: "/api/fetch?Uid="+Uid+"&type=" + type,
        success: data => {  // when data retrieved, display them
            $(".loading").css("display", "none");  // hide the loading page
            if (data.status) {
                data_dict[type] = data;
                showData(type);
            } else {
                alert("Something went wrong. Try again later.")
            }
        }
    });
    // clear cache every 10 minutes
    setInterval(() => {
        data_dict[type] = null;
    }, 10*60*1000);
}

$(".close-loading").on("click", hidePopup);

function hidePopup() {
    cur_page = 1;  // reset page to 1
    $(".pop-up").css("display", "none");  // hide popup
    $(".list-wrapper").css("display", "none");  // hide all list-wrappers
}

// delete/restore post
$(".p-del").on("click", function () {
    let button_text = $(this).text();
    if (!(button_text === "delete" || button_text === "restore")){return}
    let Pid = $(this).data("pid");
    let action = (button_text === "delete") ? 1 : 0;
    $.ajax({
        method: "POST",
        url: "/api/post/" + button_text,
        dataType: "json",
        data: {Pid: Pid},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                $(this).text((action)?"restore":"delete").css("color", (action)?"pink":"blueviolet")
                    .css("text-decoration", "underline").css("cursor", "pointer");
                let post = $(this).parent().parent(".post");
                if (action) {
                    post.addClass("deleted");
                } else {
                    post.removeClass("deleted");
                }
            }
        }
    })
})
// delete/restore post
$(".c-del").on("click", function () {
    let button_text = $(this).text();
    if (!(button_text === "delete" || button_text === "restore")){return}
    let Cid = $(this).data("cid");
    let action = (button_text === "delete") ? 1 : 0;
    $.ajax({
        method: "POST",
        url: "/api/comment/" + button_text,
        dataType: "json",
        data: {Cid: Cid},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                $(this).text((action)?"restore":"delete").css("color", (action)?"pink":"blueviolet")
                    .css("text-decoration", "underline").css("cursor", "pointer");
                let cmt = $(this).parent().parent(".comment");
                if (action) {
                    cmt.addClass("deleted");
                } else {
                    cmt.removeClass("deleted");
                }
            }
        }
    })
})

// edit personal info
$(".submit-pi").on("click", function () {
    $.post({
        url: "/api/personal_info/add",
        data: {nickname: $("#nickname").val().trim(), gender: $("#gender").val(),
            phone_number: $("#phone").val().trim(), email: $("#email").val().trim(),
            address: $("#address").val().trim(), date_of_birth: $("#dateOfBirth").val()},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                location.reload();
            }
        }
    })
})