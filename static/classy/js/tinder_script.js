$(function() {
  function accept() {
    $('.card').first().addClass('accept');
    $('body').addClass('accept');
    var lastCard = $('<div />', {
        "class": 'card last-card'});
    setTimeout(function() {
      $('body').removeClass('accept');
      $('.card').first().remove();
      $('.card').each(function() {
      var newZ = parseInt($(this).css('transform').split(',')[14]) + 10;
      var newZIndex = parseInt($(this).css('z-index')) + 1;
      $(this).css({
        'transform': 'translate3d(-50%, -50%, ' + newZ + 'px)',
        'z-index': newZIndex
      });
  	});
      $('.cube').append(lastCard);

    }, 300);
  }
  function reject() {
    $('body').addClass('reject');
    $('.card').first().addClass('reject');
    var lastCard = $('<div />', {
        "class": 'card last-card'});
    setTimeout(function() {
      $('body').removeClass('reject');
      $('.card').first().remove();
      $('.card').each(function() {
      var newZ = parseInt($(this).css('transform').split(',')[14]) + 10;
      var newZIndex = parseInt($(this).css('z-index')) + 1;
      $(this).css({
        'transform': 'translate3d(-50%, -50%, ' + newZ + 'px)',
        'z-index': newZIndex
      });
  	});
      $('.cube').append(lastCard);

    }, 300);
  }
  $('.accept').click(function() {
    accept();
  });
  $('.reject').click(function() {
    reject();
  });
  var mouseInitXPosition;
  var track = false;
	$('body').mousedown(function(e) {
    if ($(e.target).hasClass('card')) {
      track = true;
      mouseInitXPosition = e.clientX;
    } else {
      track = false;
    }
  });
  function pixelToDegree(x, width, dir) {
    var factor = 22.5/(width/2);
    var distance;
    if(dir > 0) {
      distance = x
    } else {
      distance = (width - x);
    }
    return distance * factor;
  }
  $('body').mousemove(function(e) {

    if(track) {

      if (e.pageX > mouseInitXPosition) {
      $('.card').first().css({
        'transform': 'translateY(-40%) translateZ(40px) rotateZ(' + pixelToDegree(e.pageX, $('body').width(), 1) + 'deg)'
      });
      } else {
      	 $('.card').first().css({
        'transform': 'translateX(-100%) translateY(-40%) translateZ(40px) rotateZ(-' + pixelToDegree(e.pageX, $('body').width(), -1) + 'deg)'
      });
      }
    }
  });
  $('body').mouseup(function(e) {
    if(track) {
      if (e.pageX > mouseInitXPosition) {
        accept();
      } else if (e.pageX < mouseInitXPosition) {
        reject();
      }
    }
    track = false;
  });
});