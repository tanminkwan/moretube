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