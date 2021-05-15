var range = editor.selection.getRange(),
        link = range.collapsed ? editor.queryCommandValue( "link" ) : editor.selection.getStart(),
        url,
        text = $G('text'),
        rangeLink = domUtils.findParentByTagName(range.getCommonAncestor(),'a',true),
        orgText;
link = domUtils.findParentByTagName( link, "a", true );
if(link){
        url = utils.html(link.getAttribute( '_href' ) || link.getAttribute( 'href', 2 ));

        if(rangeLink === link && !link.getElementsByTagName('img').length){
            text.removeAttribute('disabled');
            orgText = text.value = link[browser.ie ? 'innerText':'textContent'];
        }else{
            text.setAttribute('disabled','true');
            text.value = lang.validLink;
        }

    }else{
        if(range.collapsed){
            text.removeAttribute('disabled');
            text.value = '';
        }else{
            text.setAttribute('disabled','disabled');
            text.value = lang.validLink;
        }
}
$G("title").value = url ? link.title : "";
$G("href").value = url ? url: '';
$focus($G("href"));

var allowed_schemes = ["http://","https://","ftp://"];

function handleDialogOk(){
    var href =$G('href').value.replace(/^\s+|\s+$/g, '');
    if(href){
        if(!hrefStartWith(href,allowed_schemes)) {
            href  = "https://" + href;
        }
        var obj = {
            'href' : href,  // fake href
            'target' : "_blank",  // force target be _blank
            'title' : $G("title").value.replace(/^\s+|\s+$/g, ''),
            '_href': window.location.protocol+"//"+window.location.host+"/redirect?link="
                + encodeURIComponent(href)  // true href
        };

        //修改链接内容的情况太特殊了，所以先做到这里了
        //todo:情况多的时候，做到command里
        if(orgText && text.value !== orgText){
            link[browser.ie ? 'innerText' : 'textContent'] =  obj.textValue = text.value;
            range.selectNode(link).select()
        }
        if(range.collapsed){
            obj.textValue = text.value;
        }
        // if text is empty, use default one
        if (!obj.textValue) {
            obj.textValue = obj.href;
        }
        editor.execCommand('link',utils.clearEmptyAttrs(obj) );
        dialog.close();
    }
}
dialog.onok = handleDialogOk;
$G('href').onkeydown = $G('title').onkeydown = function(evt){
    evt = evt || window.event;
    if (evt.keyCode === 13) {
        handleDialogOk();
        return false;
    }
};

$G("msg").innerHTML = '<p>If scheme not specified, will add "https://" in front. ' + lang.httpPrompt + '</p>';

function hrefStartWith(href,arr){
    href = href.replace(/^\s+|\s+$/g, '');
    for (let i=0;i<arr.length;i++) {
        let scheme = arr[i];
        if (href.indexOf(scheme) === 0) {
            return true;
        }
    }
    return false;
}