//Cookie Getter
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


var load_apis = {//Loads The google api called by $(document).ready
  load: function(source){
    var elem = document.createElement('script');
    elem.setAttribute('src',source);
    elem.setAttribute('async','');
    elem.setAttribute('defer','');
    $('body').prepend(elem);
  },

  init: function(source){
    load_apis.load(source);
  },
}

$(document).ready(function(){
  var source = "https://apis.google.com/js/platform.js"
  load_apis.init(source);
});

var load_auth2={//Loads auth2 When gapi is loaded called by $(window).load
  init: function(){
    gapi.load('auth2',function(){
      auth2 = gapi.auth2.init({
        client_id : SOCIAL_DATA.KEYS.google.SOCIAL_AUTH_GOOGLE_CLIENT_ID,

      });
      auth2.then(function(){
        main_init();
      });
    });
  },
}

var link_login = {// Links The Login Flow to Customized Div whose ID is social_auth_google_login

  link: function(GoogleAuth){
    var permsissions = SOCIAL_DATA.PERMISSIONS.google.SOCIAL_AUTH_GOOGLE_PERMISSIONS;
    GoogleAuth.attachClickHandler('social_auth_google_login',{'scope':permsissions},loginHandler.onSignIn,loginHandler.onFailure)
  },

  init: function(){
    var GoogleAuth = gapi.auth2.getAuthInstance();
    link_login.link(GoogleAuth);
  },
}

var loginHandler = {//Handles Login after clicking link_login

  onSignIn: function(googleUser){
    var GoogleAuth = gapi.auth2.getAuthInstance();
    var id_token = googleUser.getAuthResponse().id_token;
    var base_url = window.location.origin;
    var ajax_url = base_url+"/social-auth/accounts/get-or-create/";
    var userInfo = new Object();
    userInfo.id_token = id_token;
    userInfo.provider = "google";

    console.log(userInfo);
    $.ajax({
      url : ajax_url,
      type : 'POST',
      contentType : 'application/json',
      dataType : 'JSON',
      headers : {'X-CSRFToken':getCookie('csrftoken')},
      data : userInfo,
      success: function(xhr,status,response){
        jsonResponse = response.responseJSON
        loginHandler.onLoginSuccess(jsonResponse);
      },
      error: function(xhr,status,err){console.log(err);},
    });
  },

  onFailure: function(error){
    console.log(error);
  },

  onLoginSuccess: function(jsonResponse){//Called After Ajax Success
    if (jsonResponse["status"] === "success") {
      var perm = SOCIAL_DATA.PERMISSIONS.google.SOCIAL_AUTH_GET_OFFLINE_ACCESS;
      console.log(perm);
      if (perm !== undefined && perm === "true") {//Only executes if true and also has a backend validation
        if (jsonResponse["first_time"] === "true") {
          var GoogleAuth = gapi.auth2.getAuthInstance();
          var base_url = window.location.origin;
          var ajax_url = base_url+"/social-auth/accounts/google-offline-auth-code/"
          GoogleAuth.grantOfflineAccess({
            'scope': SOCIAL_DATA.PERMISSIONS.google.SOCIAL_AUTH_GOOGLE_PERMISSIONS,
            'redirect_uri': 'postmessage',
          }).then(function(resp){
            auth_code = resp.code;

            var code = new Object();
            code.auth_code = auth_code;
            console.log(auth_code);
            $.ajax({
              url: ajax_url,
              type: 'POST',
              contentType : 'application/json',
              dataType : 'JSON',
              headers : {'X-CSRFToken':getCookie('csrftoken')},
              data : code,
              success: function(xhr,status,response){
                jsonResponse = response.responseJSON
                base_url = window.location.origin;
                redirect_url = base_url+jsonResponse["redirect"];
                window.location.href = redirect_url;
              },

              error: function(xhr,status,error){
                console.log(error);
              },
            });
          });
        }
        else if (jsonResponse["first_time"] === "false") {
          base_url = window.location.origin;
          redirect_url = base_url+jsonResponse["redirect"];
          window.location.href = redirect_url;
        }
      }
    }

    else if (jsonResponse["status"] === "error") {
      base_url = window.location.origin;
      redirect_url = base_url+jsonResponse["redirect"];
      window.location.href = redirect_url;
    }
  },
}


function main_init(GoogleAuth){// The function called after auth2 is loaded
  var GoogleAuth = gapi.auth2.getAuthInstance();
  isSignedIn = GoogleAuth.isSignedIn.get();
  if(isSignedIn === true){
    console.log("Already Signed In : Handle Sign In");
    GoogleAuth.signOut();
    link_login.init();
  }
  else {
    link_login.init();
  }
}

$(window).load(function(){//functions called after gapi is loaded
  load_auth2.init();
});
