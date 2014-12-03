var _unavailable_dates = undefined;

function init_datepicker(id_from, id_to, unavailable_dates) {
    if (unavailable_dates !== undefined && unavailable_dates.length > 0) {
        _unavailable_dates = unavailable_dates;
        $('.datepicker').datepicker({autoclose: true, beforeShowDay: onBeforeShowDay, startDate: new Date()});
    }
    else {
        $('.datepicker').datepicker({autoclose: true, startDate: new Date()});
    }

    $('#' + id_from).datepicker().on('changeDate', function (e) {
        $('#' + id_to).datepicker('setStartDate', $('#' + id_from).val());
    });
}

function onBeforeShowDay(date) {
    for (var index = 0; index < _unavailable_dates.length; index++) {
        sd = new Date(_unavailable_dates[index].start);
        ed = new Date(_unavailable_dates[index].end);
        if (sd <= date && date <= ed) {
            return {'enabled': false, 'classes': 'disabled-date', 'tooltip': 'Tool is not available on this day.'};
        }
    }
    return {'enabled': true, 'classes': '', 'tooltip': ' '};
}