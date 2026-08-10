var result = [];
var BaseUrl = "https://www.lightnovel.fun";
var baseBody = {
    "is_encrypted": 0,
    "platform": "pc",
    "client": "web",
    "sign": "",
    "gz": 0,
    "d": {
        "parent_gid": 3,
        "security_key": JSON.parse(decodeURIComponent(cookie.getKey(BaseUrl, "lk_security_key")))
    }
};
var headers = {
    "User-Agent": "Mozilla/5.0 (Android 11; Mobile; rv:142.0) Gecko/142.0 Firefox/142.0",
    "Content-Type": "application/json",
    "Cookie": cookie.getCookie(BaseUrl)
};
[
    ["轻小说", 3],
    ["漫画", 33]
].forEach(([tag, id]) => {
    result.push({
        title: tag,
        url: null,
        style: {
            layout_flexGrow: 1,
            layout_flexBasisPercent: 1
        }
    });
    baseBody.d.parent_gid = id;
    let sorts = java.post(BaseUrl + "/proxy/api/category/get-categories", JSON.stringify(baseBody), headers).body();
    JSON.parse(sorts).data.forEach(sort => {
        let url = BaseUrl + "/proxy/api/category/get-article-by-cate,";
        baseBody.d.gid = sort.gid;
        baseBody.d.page = "{{page === 1 ? 1 : source.getVariable()}}";
        url += JSON.stringify({
            "body": JSON.stringify(baseBody),
            "headers": headers,
            "method": "POST"
        });
        result.push({
            title: sort.name,
            url: url,
            style: {
                layout_flexGrow: 1,
                layout_flexBasisPercent: tag === "漫画" ? 0.2 : 0.25
            }
        });
    })
});
JSON.stringify(result);