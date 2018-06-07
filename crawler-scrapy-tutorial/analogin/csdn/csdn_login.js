/*
*   @author: TimLie
*   @time: 2018-05-18
*   @email: yaolx@csdn.net
*   @github: https://github.com/TimYao
*   
*/ 
define( function () {
    var $user = $( '.user-name' );  
    var $password = $( '.pass-word' );
    var $login = $( '.logging' );
    var $form = $( '#fm1' );
    var $mess = $( '.error-mess' );
    var $mess_txt = $mess.find( '#error-message' );
    var wrap = $(".third-part");
    var showMoreBtn = $(".show_more");
    var regMob = /^\d{11}$/;
    var mloginurl = $( '#mloginurl' );
    var mobile_auth = $(".mobile-auth");
    var $gps = $("#gps");
    var $login_trigger = $('.js_login_trigger');
    var $loginUserC = $('.js_login_user');
    var $recordLoginUserC = $loginUserC.filter('.login-opacity');
    var $js_enter__register = $('.js_enter__register');
    var js_login_title = $('.js_login_title');
    var js_code_text = $('.js_code_text');
    var trim = $.trim;
    
    function init () {
      $user.bind( 'keyup', function ( evt ) {
        var et = evt || window.event;
        inputFocus( et );
      } );
      
      $user.bind( 'blur', function ( evt ) {
          var v = trim($user.val());
          if (regMob.test(v)){
              asyQuery({
                url: CFG.API_URL+"account/mobileservice?action=mobileIsBound",
                data: {
                  umobile: v
                },
                success: function(dt) {
                  if (dt.status) {
                      mloginurl.attr("href",CFG.API_URL+"account/login_mobile_verification_code?umobile="+$user.val());
                      mobile_auth.show();
                  } else {
                      mloginurl.attr("href","");
                      mobile_auth.hide();
                  }
                }
              });
          }	
        });
  
      $password.bind('blur', function() {
          var p = trim($password.val());
          $password.val(p);
      })
      $password.bind( 'keyup', function ( evt ) {
        var et = evt || window.event;
        inputFocus( et );
      } );
  
      $login.bind( 'click', function () {
        var p = trim($password.val());
        $password.val(p);
        if ( $user.val() == '' )
        {
          $mess.show();
          $mess_txt.html( '请输入用户名！' );
        }
        else if ( $password.val() == '' )
        {
          $mess.show();
          $mess_txt.html( '请输入密码！' );
        }
        else
        {
          $mess.hide();
          if(window.SMSdk && SMSdk.getDeviceId)
            $("#fkid").val(SMSdk.getDeviceId());
          $form.submit();
        }
      } );
  
      if (navigator.geolocation){
            navigator.geolocation.getCurrentPosition(function(position){
                $gps.val(position.coords.latitude+","+position.coords.longitude)
            }, function(){
                console.log("无法获取用户信息");
            });
        }
  
      // 触发
      $login_trigger.on('click', function () {
          var activeLoginUser = $(this).closest('.js_login_user');
          var isRegister = $(this).hasClass('js_status_register');
          var $recordLoginIndex = $recordLoginUserC.index();
          var activeLoginIndex = activeLoginUser.index();
          if($recordLoginIndex === activeLoginIndex){
             return false;
          }
          if(isRegister){
              $js_enter__register.triggerHandler('click');
          }
          if(!activeLoginUser){
              return false;
          }
          animateSet({curObj:activeLoginUser,nextObj:$recordLoginUserC},function(){
              $recordLoginUserC = activeLoginUser;
          });
          return false;
      })
      // 注册二维码展示
      $js_enter__register.bind('click', function(){
          var text, iText, iNumText, codeText;
          if(this.status){
              text = '扫码登录';
              iText = '立即注册';
              iNumText = '还没有CSDN账号?';
              codeText = '微信登录';
              $login_trigger.show();
              this.status = undefined;
          }else{
              text = '注册账号';
              iText = '立即登录';
              iNumText = '已经有账号?';
              codeText = '微信注册';
              $login_trigger.hide();
              this.status = true;
          }
          js_login_title.text(text);
          js_code_text.text(codeText);
          $(this).text(iText).closest('.js_register_text').find('span').text(iNumText);
          return false;
      })
  
    }
  
    $( '.change-code' ).bind( 'click', function () {
        $("#yanzheng").attr( "src", CFG.API_URL+"ajax/verifyhandler.ashx?rand=" + new Date()/100 );
        return false;
      } );
    
    showMoreBtn.bind("click",function(){
        wrap.toggleClass("third-part-new");
        return false;
    });
  
    function inputFocus ( et ) {
      var keyCode = et.keyCode;
  
      if ( keyCode == 13 )
      {
        if ( $user.val() == '' )
        {
          $user.get( 0 ).focus();
        }
        else if ( $password.val() == '' )
        {
          $password.get( 0 ).focus();
        }
        else
        {
          if(window.SMSdk && SMSdk.getDeviceId)
            $("#fkid").val(SMSdk.getDeviceId());
          $form.submit();
        }
      }
    }
    // tab切换动画
    function animateSet(opt,callback){
      var opts, curObj, nextObj;
      opts = opt ? opt : null;
      if(!opts){
          return false;
      }
      curObj = opts.curObj || null;
      nextObj  = opts.nextObj || null;
      clearTimeout(curObj[0].t);
      clearTimeout(curObj[0].t1);
      if(!curObj || !nextObj){
          return false;
      }
      if(support_css3('animation')){
  
          curObj.addClass('login-user__move');
          curObj[0].t = setTimeout(function(){
              curObj.addClass('hide');
              curObj.addClass('login-opacity');
              curObj.removeClass('login-user__move');
              nextObj.removeClass('hide');
              nextObj.addClass('login-code__move');
          },250);
          curObj[0].t1 = setTimeout(function(){
              nextObj.removeClass('login-opacity');
              nextObj.removeClass('login-code__move');
          },500);
  
      }else{
  
          curObj.addClass('hide');
          nextObj.removeClass('hide');
          nextObj.removeClass('login-opacity');
      }
      callback ?  callback() : void(0);
  }
    // css3判定
    function support_css3(){
      var div = document.createElement('div'),
          vendors = 'Ms O Moz Webkit'.split(' '),
          len = vendors.length;
  
      return function(prop) {
          if ( prop in div.style ) return true;
  
          prop = prop.replace(/^[a-z]/, function(val) {
              return val.toUpperCase();
          });
  
          while(len--) {
              if ( vendors[len] + prop in div.style ) {
                  return true;
              }
          }
          return false;
      };
  }
  
    asyQuery = function(conf) {
      return $.ajax({
        url: conf.url,
        type: conf.type || 'GET',
        data: conf.data || {},
        dataType: 'json',
        success: function(dt) {
          if (typeof conf.success === "function") {
            conf.success(dt);
          }
        }
      });
    };
        
    return {
      init: init
    }
  } );