exports.ymd2date = (dt) => {
    let date = new Date();
    date.setFullYear(parseInt(dt.substring(0, 4)));
    date.setMonth(parseInt(dt.substring(5, 7)) - 1);
    date.setDate(parseInt(dt.substring(8, 10)));
    return date;
}

exports.date2ymd = (date) => {
    let year = date.getFullYear().toString();

    let month = (date.getMonth() + 1).toString();
    if (month.length === 1) month = "0" + month;

    let day = date.getDate().toString();
    if (day.length === 1) day = "0" + day;

    return year + '-' + month + '-' + day;
}

exports.chart_x = (() => {
    let xs = [];
    for (let i = 0; i < 24; i++) {
        let s = i + ":00"
        if (s.length < 5) s = "0" + s
        xs.push(s)
        s = i + ":30"
        if (s.length < 5) s = "0" + s
        xs.push(s)
    }
    return xs;
})()