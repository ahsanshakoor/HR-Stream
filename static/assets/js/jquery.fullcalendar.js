!function ($) {
    "use strict";

    var CalendarApp = function () {
        this.$body = $("body")
        this.$modal = $('#event-modal'),
            this.$event = ('#external-events div.external-event'),
            this.$calendar = $('#calendar'),
            this.$saveCategoryBtn = $('.save-category'),
            this.$categoryForm = $('#add-category form'),
            this.$extEvents = $('#external-events'),
            this.$calendarObj = null
    };


    /* on drop */
    CalendarApp.prototype.onDrop = function (eventObj, date) {
        var $this = this;
        // retrieve the dropped element's stored Event Object
        var originalEventObject = eventObj.data('eventObject');
        var $categoryClass = eventObj.attr('data-class');
        // we need to copy it, so that multiple events don't have a reference to the same object
        var copiedEventObject = $.extend({}, originalEventObject);
        // assign it the date that was reported
        copiedEventObject.start = date;
        if ($categoryClass)
            copiedEventObject['className'] = [$categoryClass];
        // render the event on the calendar
        $this.$calendar.fullCalendar('renderEvent', copiedEventObject, true);
        // is the "remove after drop" checkbox checked?
        if ($('#drop-remove').is(':checked')) {
            // if so, remove the element from the "Draggable Events" list
            eventObj.remove();
        }
    },
        /* on click on event */
        CalendarApp.prototype.onEventClick = function (calEvent, jsEvent, view) {
            var $this = this;
            $("#form_main_div").remove();
            $("#form_label").remove();
            $("#time_log_update").append("<label id='form_label'>Change Time Log </label>");
             if (calEvent.className == 'bg-primary2') {$("#time_log_update").append("<div id='form_main_div' class='input-group'><input class='form-control' hidden type=text value='" + calEvent.id + "' /><input class='form-control' readonly type=text value='" + calEvent.title + "' /><input id='update_time' disabled class='form-control timepicker fa fa-clock-o' type=text value='" + calEvent.time + "' /><span class='input-group-append'><button id='time_log_save' type='submit' class='btn btn-primary btn-md'>Save</button></span></div>");
}
             else {$("#time_log_update").append("<div id='form_main_div' class='input-group'><input class='form-control' hidden type=text value='" + calEvent.id + "' /><input class='form-control' readonly type=text value='" + calEvent.title + "' /><input id='update_time' class='form-control timepicker fa fa-clock-o' type=text value='" + calEvent.time + "' /><span class='input-group-append'><button id='time_log_save' type='submit' class='btn btn-primary btn-md'>Save</button></span></div>");
}

            // alert(calEvent.className);
            if (calEvent.className == 'bg-primary2') {
                $('#time_log_save').remove();
                $('#time_log_submit').hide();
            }
            else{
                $('#time_log_submit').show();
            }
            $this.$modal.modal({
                backdrop: 'static'
            });
            $this.$modal.find('.delete-event').show().end().find('.save-event').hide().end().find('.delete-event').unbind('click').click(function () {
                const id = calEvent.id
                $.ajax({
                    type: 'GET',
                    url: "/delete_time_log/" + id + "/",
                    data: {},

                    success: function (response) {
                        let events = response["events"];
                    }
                });
                $this.$calendarObj.fullCalendar('removeEvents', function (ev) {

                    return (ev._id == calEvent._id);

                });
                $this.$modal.modal('hide');
            });
            $this.$modal.find('#time_log_submit').unbind('click').click(function () {
                calEvent.time = $('#time_log_update').find("input[id=update_time]").val();
                const start_time = $('#time_log_update').find("input[id=update_time]").val();
                const token = $('#time_log_update').find('input[name=csrfmiddlewaretoken]').val()
                const id = calEvent.id;
                const submit_status = 'SUBMITTED';
                $.ajax({
                    async: false,
                    type: 'POST',
                    url: "/update_time_log/",
                    data: {id, start_time, csrfmiddlewaretoken: token, submit_status},

                    success: function (response) {
                        let events = response["events"];
                    }
                });
                $this.$calendarObj.fullCalendar('updateEvent', calEvent);
                // $("#time_log_update").empty()
                $this.$modal.modal('hide');
                window.location.reload();
                return false;
            });
            $this.$modal.find('form').on('submit', function () {
                calEvent.time = $('#time_log_update').find("input[id=update_time]").val();
                const start_time = $('#time_log_update').find("input[id=update_time]").val();
                const token = $('#time_log_update').find('input[name=csrfmiddlewaretoken]').val()
                const id = calEvent.id;
                $.ajax({
                    async: false,
                    type: 'POST',
                    url: "/update_time_log/",
                    data: {id, start_time, csrfmiddlewaretoken: token},

                    success: function (response) {
                        let events = response["events"];
                    }
                });
                $this.$calendarObj.fullCalendar('updateEvent', calEvent);
                // $("#time_log_update").empty()
                $this.$modal.modal('hide');
                return false;
            });

        },
        /* on select */
        CalendarApp.prototype.onSelect = function (start, end, allDay) {
            $('#add_event').modal('show');
            // alert(start)
            // let today_date = JSON.stringify(start)
            //     today_date = today_date.slice(1,11)
            var today_date = moment(start, "yyyy-MM-DD").format("MM/DD/YYYY");
            // alert(today_date)
            $('#id_date').remove();
            $('#date_div').append("<input class='form-control' type='text' name='date' id='id_date'/>")
            $('#id_date').val(today_date)
            $('#id_date').prop("readonly", true);
            // var $this = this;
            //     $this.$modal.modal({
            //         backdrop: 'static'
            //     });
            // var form = $("<form></form>");
            // form.append("<div class='row'></div>");
            // form.find(".row")
            //     .append("<div class='col-md-12'><div class='form-group'><label class='control-label'>Event Name</label><input class='form-control' type='text' name='title'/></div></div>")
            //     .append("<div class='col-md-12'><div class='form-group'><label class='control-label'>Category</label><select class='select form-control' name='category'></select></div></div>")
            //     .find("select[name='category']")
            //     .append("<option value='bg-danger'>Danger</option>")
            //     .append("<option value='bg-success'>Success</option>")
            //     .append("<option value='bg-purple'>Purple</option>")
            //     .append("<option value='bg-primary'>Primary</option>")
            //     .append("<option value='bg-pink'>Pink</option>")
            //     .append("<option value='bg-info'>Info</option>")
            //     .append("<option value='bg-inverse'>Inverse</option>")
            //     .append("<option value='bg-orange'>Orange</option>")
            //     .append("<option value='bg-brown'>Brown</option>")
            //     .append("<option value='bg-teal'>Teal</option>")
            //     .append("<option value='bg-warning'>Warning</option></div></div>");
            // $this.$modal.find('.delete-event').hide().end().find('.save-event').show().end().find('.modal-body').empty().prepend(form).end().find('.save-event').unbind('click').click(function () {
            //     form.submit();
            // });
            // $this.$modal.find('form').on('submit', function () {
            //     var title = form.find("input[name='title']").val();
            //     var beginning = form.find("input[name='beginning']").val();
            //     var ending = form.find("input[name='ending']").val();
            //     var categoryClass = form.find("select[name='category'] option:checked").val();
            //     if (title !== null && title.length != 0) {
            //         $this.$calendarObj.fullCalendar('renderEvent', {
            //             title: title,
            //             start:start,
            //             end: end,
            //             allDay: false,
            //             className: categoryClass
            //         }, true);
            //         $this.$modal.modal('hide');
            //     }
            //     else{
            //         alert('You have to give a title to your event');
            //     }
            //     return false;
            //
            // });
            $this.$calendarObj.fullCalendar('unselect');
        },
        CalendarApp.prototype.enableDrag = function () {
            //init events
            $(this.$event).each(function () {
                // create an Event Object (http://arshaw.com/fullcalendar/docs/event_data/Event_Object/)
                // it doesn't need to have a start or end
                var eventObject = {
                    title: $.trim($(this).text()) // use the element's text as the event title
                };
                // store the Event Object in the DOM element so we can get to it later
                $(this).data('eventObject', eventObject);
                // make the event draggable using jQuery UI
                $(this).draggable({
                    zIndex: 999,
                    revert: true,      // will cause the event to go back to its
                    revertDuration: 0  //  original position after the drag
                });
            });
        }
    /* Initializing */
    CalendarApp.prototype.init = function () {
        this.enableDrag();
        /*  Initialize the calendar  */
        var date = new Date();
        var d = date.getDate();
        var m = date.getMonth();
        var y = date.getFullYear();
        var form = '';
        var today = new Date($.now());

        var defaultEvents = [];
        $.ajax({
            async: false,
            type: 'GET',
            url: "/task_event/",
            data: {},

            success: function (response) {
                let events = response["events"];
                defaultEvents = events
            }
        });
        var $this = this;
        $this.$calendarObj = $this.$calendar.fullCalendar({
            slotDuration: '00:15:00', /* If we want to split day time each 15minutes */
            minTime: '08:00:00',
            maxTime: '19:00:00',
            defaultView: 'month',
            handleWindowResize: true,
            height: $(window).height() - 200,
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay'
            },
            events: defaultEvents,
            editable: true,
            droppable: true, // this allows things to be dropped onto the calendar !!!
            eventLimit: true, // allow "more" link when too many events
            selectable: true,
            drop: function (date) {
                $this.onDrop($(this), date);
            },
            select: function (start, end, allDay) {
                $this.onSelect(start, end, allDay);
            },
            eventClick: function (calEvent, jsEvent, view) {
                $this.onEventClick(calEvent, jsEvent, view);
            }

        });

        //on new event
        this.$saveCategoryBtn.on('click', function () {
            var categoryName = $this.$categoryForm.find("input[name='category-name']").val();
            var categoryColor = $this.$categoryForm.find("select[name='category-color']").val();
            if (categoryName !== null && categoryName.length != 0) {
                $this.$extEvents.append('<div class="external-event bg-' + categoryColor + '" data-class="bg-' + categoryColor + '" style="position: relative;"><i class="mdi mdi-checkbox-blank-circle m-r-10 vertical-middle"></i>' + categoryName + '</div>')
                $this.enableDrag();
            }

        });
    },

        //init CalendarApp
        $.CalendarApp = new CalendarApp, $.CalendarApp.Constructor = CalendarApp

}(window.jQuery),

//initializing CalendarApp
    function ($) {
        "use strict";
        $.CalendarApp.init()
    }(window.jQuery);
