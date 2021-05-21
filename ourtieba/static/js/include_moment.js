moment.locale("en");

function flask_moment_render(elem) {
    timestamp = moment($(elem).data('timestamp'));
    func = $(elem).data('function');
    format = $(elem).data('format');
    timestamp2 = $(elem).data('timestamp2');
    no_suffix = $(elem).data('nosuffix');
    args = [];
    if (format)
        args.push(format);
    if (timestamp2)
        args.push(moment(timestamp2));
    if (no_suffix)
        args.push(no_suffix);
    $(elem).text(timestamp[func].apply(timestamp, args));
    $(elem).removeClass('flask-moment').show();
}

function flask_moment_render_all() {
    $('.flask-moment').each(function () {
        flask_moment_render(this);
        if ($(this).data('refresh')) {
            (function (elem, interval) {
                setInterval(function () {
                    flask_moment_render(elem)
                }, interval);
            })(this, $(this).data('refresh'));
        }
    })
}

$(document).ready(function () {
    flask_moment_render_all();
});