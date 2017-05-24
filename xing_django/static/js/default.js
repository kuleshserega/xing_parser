$(document).ready(function(){
  $('.messages').find('.alert').each(function(){
    var el = $(this);
    setTimeout(function(){
      el.fadeOut(500, function(){
       el.remove();
      });
    }, 4000);
  });
});