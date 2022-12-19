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

function getcaptions(url) {

  $.ajax({
    type: "GET",
    url: url
  }).done(function (response) {
      //captions = jQuery.parseJSON(response);
      captions = response;
      //console.log(captions)
      $("#caption-ul").empty();
      $(response).each(function(i,val)
      {
        var start = (Math.round(val.start * 10) / 10);
        var end   = (Math.round(val.end * 10) / 10);
        
        //var line = ""+i+" : "+start+" ~ "+end+" "+val.text;
        var line = '<div class="row">';
        if(val.hasOwnProperty('text_c')){
          line += '<div class="column0_1" onclick="openToast('+""+i+')">'
        }else{
          line += '<div class="column0_2">'
        }
        line += ""+i+'</div><div class="column1">'+"~ "+fancyTimeFormat(end)+
          '</div><div class="column2">'+val.text+'</div></div>';
        //console.log(val.duration)
        //$.each(val,function(key,val)
        //{
        //  line = line + key + ": " + val + " "; 
          //console.log(key + " : " + val);     
        //});
        $("#caption-ul").append('<li class="caption-li" id="li-'+ i +'">'+ line +"</li>");
        //console.log(i + " : " + val);

      });

      window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight);
      
  }).fail(function (response) {
      console.log('get caption failed');
  });

}

