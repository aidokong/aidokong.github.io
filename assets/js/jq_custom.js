$(document).ready(function() {
    $('.read-more-btn').click(function(e) {
        e.preventDefault();
        var $this = $(this);
        var $moreText = $this.siblings('.more-text');
        if ($moreText.is(':visible')) {
            $moreText.slideUp('slow');
            $this.text('Read more');
        } else {
            $moreText.slideDown('slow');
            $this.text('Read less');
        }
    });
});