var nb_photo = parseInt($("#nb_photo").val().trim());
var init_i = parseInt($("#init_i").val().trim());

var left_arrow = $(".left-arrow");
var right_arrow = $(".right-arrow");

$(function () {
    if (nb_photo === 0) {  // hide notice bar if no photos to display
        $("#notice-bar").css("display", "none");
    } else {
        setInterval(() => {  // display notice bar for 1 sec then dismiss
            $("#notice-bar").css("opacity", "0");
        }, 1000)
    }

    $('#main-page').fullpage({
        controlArrows: false,
        onSlideLeave: (section, origin, destination, direction) => {
            let d_index = destination.index + 1;

            // alter index, pad zeros before (just for visual effect)
            let p_index = d_index.toString();
            let p_nb = nb_photo.toString();
            for (let i = 0; i < p_nb.length - p_index.length; i++) {
                p_index = "0" + p_index;
            }
            if (p_index.length <= 1) {
                p_index = "0" + p_index;
            }
            if (p_nb.length <= 1) {
                p_nb = "0" + p_nb;
            }
            $(".index").text(p_index + " / " + p_nb);

            // first restore arrow style
            left_arrow.css("border-color", "transparent #fff transparent transparent").removeAttr("disabled")
            right_arrow.css("border-color", "transparent transparent transparent #fff").removeAttr("disabled")

            // then change if needed
            if (d_index === 1) {
                left_arrow.css("border-color", "transparent grey transparent transparent")
                    .attr("disabled", "disabled");
            }
            if (d_index === nb_photo) {
                right_arrow.css("border-color", "transparent transparent transparent grey")
                    .attr("disabled", "disabled");
            }
        }
    });

    // bind turn-page to arrows
    left_arrow.on("click", () => {
        fullpage_api.moveSlideLeft();
    })
    right_arrow.on("click", () => {
        fullpage_api.moveSlideRight();
    })

    // initial styling, this is necessary because "onSlideLeave" is not triggered when web page is first loaded
    if (init_i <= 1) {
        left_arrow.css("border-color", "transparent grey transparent transparent").attr("disabled", "disabled");
    }
    if (init_i === nb_photo) {
        right_arrow.css("border-color", "transparent transparent transparent grey").attr("disabled", "disabled");
    }

    // click image will open a new tab
    $(".OT_image").on("click", function () {
        window.open(this.src, "_blank");
    })

    // show/hide arrows on mouse over/out page
    window.onmouseover = () => {
        $(".arrow").css("opacity", "1");
    }
    window.onmouseout = () => {
        $(".arrow").css("opacity", "0");
    }
});