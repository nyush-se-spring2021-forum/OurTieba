// Add query params without while preserving current params
function setParam(name, value) {
    const l = window.location;

    /* build params */
    const params = {};
    const x = /(?:\??)([^=&?]+)=?([^&?]*)/g;
    const s = l.search;
    for (let r = x.exec(s); r; r = x.exec(s)) {
        r[1] = decodeURIComponent(r[1]);
        if (!r[2]) r[2] = '%%';
        params[r[1]] = r[2];
    }

    /* set param */
    params[name] = encodeURIComponent(value);

    /* build search */
    let search = [];
    for (let i in params) {
        let p = encodeURIComponent(i);
        const v = params[i];
        if (v !== '%%') p += '=' + v;
        search.push(p);
    }
    search = search.join('&');

    /* execute search */
    l.search = search;
}
