function highlight_errors(error_field_ids) {
    $(document).ready(function () {
        $.each($('.form-control'), function (key, element) {
            if ($.inArray(element.id, error_field_ids) > -1) {
                $(element).parent().addClass('has-error');
            }
        });
    });
}