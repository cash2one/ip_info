$(document).ready(function() {
    $('#generate_form').submit(function() {
        if (confirm('该操作可能会耗时近 1 小时，真要干么？')) {
            $(this).data('confirmed', '1')
            return true;
        }

        return false;
    })
})