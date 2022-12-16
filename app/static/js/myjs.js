/* */
function viewDict(dict) {

    var word = dict.innerHTML
    var rlist = getDict(word);
    var deco_word = '<span class="dict-word">'+word+'</span>'
        
    rlist.forEach((x, i) => 
        toastr.success('', deco_word + ' : ' + x, {
            timeOut: 8000,
            positionClass: "toast-top-full-width",
            closeButton: true,
            showDuration: 200,
            closeDuration: 0,
            hideDuration: 200,
        })
    );
}

function getDict(text) {
    var result ='';
    text = text.replaceAll(' ', '_').toLowerCase();
    
    $.ajax({
      type: "GET",
      url: "/api/v1/mytube/dictionary/" + text,
      async: false
    }).done(function (response) {
      result = response.data          
    });
    //console.log('result2 : ' + result);
    return result;
}

function fancyTimeFormat(duration)
{   
    // Hours, minutes and seconds
    var hrs = ~~(duration / 3600);
    var mins = ~~((duration % 3600) / 60);
    var secs = ~~duration % 60;
    var dat  = Math.round((duration % 1) * 10);

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";

    if (hrs > 0) {
        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    }

    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    ret += "." + dat
    return ret;
}