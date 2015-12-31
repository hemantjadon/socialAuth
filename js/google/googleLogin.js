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
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail());
  },

  onFailure: function(error){
    console.log(error);
  },
}


function main_init(GoogleAuth){// The function called after auth2 is loaded
  var GoogleAuth = gapi.auth2.getAuthInstance();
  isSignedIn = GoogleAuth.isSignedIn.get();
  if(isSignedIn === true){
    console.log("Already Signed In : Handle Sign In");
  }
  else {
    link_login.init();
  }
}

$(window).load(function//functions called after gapi is loaded
  load_auth2.init();
});
