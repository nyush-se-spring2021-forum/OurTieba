var cover_src = cover_src || "cover/OurTieba.png";

$("#admin-logout").on("click", function () {
    $.post({
        url: "/admin/auth/logout",
        success: data => {
            if (!data.status) {
                alert("Something went wrong. Try again later.");
            } else {
                location.href = "/admin/login";
            }
        },
        dataType: "json"
    })
})

$("#board-name").on("keyup", function () {
    let count = $(this).val().length;
    let is_exceed = count > 40;
    $(".name-count").text((is_exceed?"Name length exceeded! ":"")+count+"/40")
        .css("color", is_exceed?"#d00303":"#aaa");
})
$("#board-des").on("keyup", function () {
    let count = $(this).val().length;
    let is_exceed = count > 200;
    $(".des-count").text((is_exceed?"Description length exceeded! ":"")+count+"/200")
        .css("color", is_exceed?"#d00303":"#aaa");
})

// upload cover
$("#cover-upload").on("change", function () {
    let file = this.files[0];
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
        url: "/admin/upload?action=uploadcover",
        data: formData,
        processData: false,
        contentType: false,
        success: (data) => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                cover_src = data.src;
                $(this).css("background", 'url('+'/cdn/'+ data.src+')')
                    .css("background-size", "cover");
            }
        }
    })
})

// cancel
$("#btn-cancel").on("click", () => {
    window.close();
})

// create
$("#btn-create").on("click", function () {
    $.post({
        url: "/admin/board/add",
        data: {name:$("#board-name").val().trim(), description:$("#board-des").val().trim(), cover:cover_src},
        success: data => {
            if (!data.status) {
                alert(data.error.msg);
            } else {
                alert("Create board successful!");
                location.reload();
            }
        }
    })
})