// insert emoji into editor
$(".emoji-content").on("click", function () {
    editor.execCommand("inserthtml", this.innerHTML);
    dialog.popup.hide();
})
// switch tabs
$(".emoji-page").on("click", function () {
    $(".emoji-page").removeClass("focus");  // remove "focus" class for every class
    $(this).addClass("focus");
    $(".emoji-body").css("display", "none").eq($(this).index()).css("display", "flex");
})
// add unicode characters entered by user
$("#add-emoji").on("click", () => {
    let u_i = $("#user-in");
    $("#fetch").html("&" + UE.utils.unhtml(u_i.val()));  // render on a hidden block
    u_i.val("");  // clear input
    editor.execCommand("inserthtml", document.getElementById("fetch").innerHTML);  // then insert into editor
    dialog.popup.hide();
})