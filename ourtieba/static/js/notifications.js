var e = document.createElement("div")
e.className = "alert alert-warning"
e.innerHTML = 'Still in Beta phase. Only the first 10 new notifications will be correctly marked as "new".'
document.getElementsByClassName("container")[1].firstElementChild.prepend(e)

//alert('Still in Beta phase. Only the first 10 new notifications will be correctly marked as "new".')
var is_end = 0;
var cursor_end = 0;

var flag = false;  // flag that forces await on async fetch
var win = $(window);

$("#new_message").text("New Messages: -");  // transitional visual effect

function fetchNtf() {
    flag = false;
    $.get({
        url: "/api/get_ntf?end=" + cursor_end,
        success: data => {
            if (data.status) {
                cursor_end = data.cursor_end;
                is_end = data.is_end;
                let ntfs = data.ntfs;
                for (let i = 0; i < ntfs.length; i++) {
                    let ntf = ntfs[i];
                    // !!IMPORTANT: layout design here
                    $(".ntf-body").append('<div class="ntf-box' + ((ntf.is_new) ? " new-ntf" : "") + '">' +
                        '<div class="ntf-msg">' + ntf.message + '</div>' + '<div class="ntf-time">' + ntf.timestamp
                        + '</div>' + '</div>');
                }
                flag = true;
            }
        }
    })
}

// initial fetch
fetchNtf();

// fetch when scroll reaches end and not is_end
var beforeScrollTop = win.scrollTop();
win.on("scroll", function () {
    let afterScrollTop = $(this).scrollTop();
    let scrollHeight = $(document).height();
    let windowHeight = $(this).height();  // window.innerHeight
    if ((afterScrollTop - beforeScrollTop > 0) && (afterScrollTop + windowHeight >= scrollHeight - 20) && flag && !is_end) {
        fetchNtf();
    }
    beforeScrollTop = afterScrollTop;
});