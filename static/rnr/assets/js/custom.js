var notificationTimeout;

//Shows updated notification popup
var updateNotification = function (task, notificationText, newClass) {
    var notificationPopup = $('.notification-popup ');
    notificationPopup.find('.task').text(task);
    notificationPopup.find('.notification-text').text(notificationText);
    notificationPopup.removeClass('hide success');
    // If a custom class is provided for the popup, add It
    if (newClass)
        notificationPopup.addClass(newClass);
    // If there is already a timeout running for hiding current popup, clear it.
    if (notificationTimeout)
        clearTimeout(notificationTimeout);
    // Init timeout for hiding popup after 3 seconds
    notificationTimeout = setTimeout(function () {
        notificationPopup.addClass('hide');
    }, 9000);
};
$('#demo_form').on("submit", function (e) {
    e.preventDefault();
     $.ajax({
                type: 'POST',
                url: '/demo/',
                data: $(this).serialize(),
                success: function (json) {
                    demo = JSON.stringify(json, null, 4);
                    demo = JSON.parse(demo);
                    updateNotification(demo['response_date_name'], '  your request for demo has been received.');
                    $("#demo_form")[0].reset();

                }
            });
});