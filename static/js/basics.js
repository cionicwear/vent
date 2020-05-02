
function TAG(tag, attrs, content) {
    var markup = '<' + tag;
    for (var a in attrs) {
        markup += ' ' + a + '="' + attrs[a] + '"';
    }
    if (content) {
        markup += '>' + content + '</' + tag + '>';
    }
    else {
        markup += '/>';
    }
    return markup;
};

function THUMB(path, size) {
    var src = path + '=s' + size + '-c';
    return TAG('img', {'height':size, 'width':size, 'src':src});
};

function DIV(attrs, content) {
    return TAG('div', attrs, content);
};

function SECTION(attrs, content) {
    return TAG('section', attrs, content);
};

function SPAN(attrs, content) {
    return TAG('span', attrs, content);
};


function createCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name,"",-1);
}