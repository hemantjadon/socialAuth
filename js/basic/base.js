var load_apis = {

  load_local_js: function(provider){//Loads Extra JS required to make it possible
    var elem = document.createElement('script');
    elem.setAttribute('src','../static/'+provider+'/'+provider+'Login.js');
    elem.setAttribute('type','text/javascript');
    $('body').append(elem);
  },

  init: function(){
    var providers = SOCIAL_DATA.SOCIAL_AUTH_PROVIDERS;
    for (var i = 0; i < providers.length; i++) {
      load_apis.load_local_js(providers[i]);
    }
  },
}

$(document).ready(function(){
  load_apis.init();
});
