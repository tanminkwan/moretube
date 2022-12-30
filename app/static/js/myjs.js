/* */
function viewDict(dict) {

    if(typeof toastr == 'undefined')return;

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

function getSubtitles(url){

  var result = null;
  $.ajax({
    type: "GET",
    url: url,
    async: false,
    success: function (response) {
      result = response;
    }
  });
  return result;

}

function retrieveSubtitles(subtitles, caption_ul, isWeight=false, division=[], division_title='Section'){

  $(caption_ul).empty();

  var len = 0;

  $(subtitles).each(function(i,val)
  {

    //var start = (Math.round(val.start * 10) / 10);
    var end = (Math.round(val.end * 10) / 10);
    //var line = ""+i+" : "+start+" ~ "+end+" "+val.text;
    var line = '<div class="row-li">';
    if(val.hasOwnProperty('text_c')){
      line += '<div class="column0_1" onclick="openToast('+""+i+')">'
    }else{
      line += '<div class="column0_2">'
    }
    line += ""+i+'</div><div class="column1">'+"~ "+fancyTimeFormat(end)+
      '</div><div class="column2">'+val.text+'</div>';
    if(isWeight==true){
      len += val.len;
      line += '<div class="column3">'+len+'</div></div>';
    }else{
      line += '</div>';
    }
    if(division.length > 0){ 
      if(division.includes(i)){
        var ind = division.indexOf(i)+1 ;
        $(caption_ul).append('<li class="division-li" id="div-'+ ind +'" start="'+i+'">'+ division_title + ' ' + ind +"</li>")
      }
    }
    $(caption_ul).append('<li class="caption-li" id="li-'+ i +'">'+ line +"</li>");

  });

}

function subtitleScroll(x) {
  //$('#caption-ul').scrollTop($('#caption-ul li:eq('+x+')').offset().top);
  if(x==0){
    $('#caption-ul').scrollTop($('#caption-ul li:nth-child(1)').position().top - $('#caption-ul li:first').position().top);
  }else{
    //$('#caption-ul').scrollTop($('#caption-ul li:nth-child('+x+')').position().top - $('#caption-ul li:first').position().top);
    $('#caption-ul').scrollTop($('#caption-ul #'+x).position().top - $('#caption-ul li:first').position().top);
  }
  $('#'+x).css("background-color","white")
  //$("caption-ul").get(x).scrollIntoView();
}

function getcaptions(url, isWeight=false, division=[], division_title='Section') {

  $.ajax({
    type: "GET",
    url: url
  }).done(function (response) {
      //captions = jQuery.parseJSON(response);
      captions = response.data;
      //console.log(captions)
      $("#caption-ul").empty();

      var len = 0;

      $(response.data).each(function(i,val)
      {

        //var start = (Math.round(val.start * 10) / 10);
        var end = (Math.round(val.end * 10) / 10);
        //var line = ""+i+" : "+start+" ~ "+end+" "+val.text;
        var line = '<div class="row-li">';
        if(val.hasOwnProperty('text_c')){
          line += '<div class="column0_1" onclick="openToast('+""+i+')">'
        }else{
          line += '<div class="column0_2">'
        }
        line += ""+i+'</div><div class="column1">'+"~ "+fancyTimeFormat(end)+
          '</div><div class="column2">'+val.text+'</div>';
        if(isWeight==true){
          len += val.len;
          line += '<div class="column3">'+len+'</div></div>';
        }else{
          line += '</div>';
        }
        if(division.length > 0){ 
          if(division.includes(i) || i==0){
            var ind = i==0 ? 1 : division.indexOf(i)+2 ;
            $("#caption-ul").append('<li class="caption-li division-li" id="div-'+ ind +'">'+ division_title + ' ' + ind +"</li>")
          }
        }
        $("#caption-ul").append('<li class="caption-li" id="li-'+ i +'">'+ line +"</li>");

      });

      window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight);
      
  }).fail(function (response) {
      console.log('get caption failed');
  });

}

