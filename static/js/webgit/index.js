$(document).ready(function(){

    var delay = function(time) {
        return $.Deferred(function(dfd) {
            setTimeout(function() {
                dfd.resolve()
            }, time)
        })
    }

    var git = function(operation, index) {
        loading()
        $.get('/webgit/' + operation + '/' + index)
        .then(function(response) {
            show(response)
        })
    }

    var loading = function() {
        $('#fp_peek_layer').show()
        .find('#loading')
            .show()
        .end()
        .find('#console')
            .hide()
        .end()
    }

    var show = function(content) {
        $('#fp_peek_layer').show()
        .find('#loading')
            .hide()
        .end()
        .find('#console').empty()
            .append('<pre></pre>')
            .find('pre')
                .text(content)
            .end().show()
        .end()
    }

    var hide = function() {
        $('#fp_peek_layer').hide().find('#console').html('')
    }

    $('#fp_peek_layer .nav-pills a').on('click', function() {
        var op = $(this).data('operation')

        $('.nav-pills a').parent('li').removeClass('active')
        $(this).parent('li').addClass('active')

        git(op, $('#fp_peek_layer').data('fp-id'))
    })

    $('.fp-pull').on('click', function() {
        var $button = $(this)
        $button.button('loading')
        $.when($.get('/webgit/gitPull/' + $button.data('fp-id')), delay(1000))
        .then(function() {
            $button.addClass('disabled btn-success').text($button.data('complete-text'))
            return delay(2000)
        })
        .then(function() {
            $button.removeClass('btn-success').button('reset')
        })
    })

    $('.fp-restart').on('click', function() {
        var $button = $(this)
        $button.button('loading')
        $.when($.get('/webgit/gitRestart/' + $button.data('fp-id')), delay(1000))
        .then(function() {
            $button.addClass('disabled btn-success').text($button.data('complete-text'))
            return delay(2000)
        })
        .then(function() {
            $button.removeClass('btn-success').button('reset')
        })
    })

    $('.fp-reset').on('click', function() {
        var $button = $(this)
        $button.button('loading')
        $.when($.get('/webgit/backVersion/' + $button.data('fp-id')), delay(1000))
        .then(function() {
            $button.addClass('disabled btn-success').text($button.data('complete-text'))
            return delay(2000)
        })
        .then(function() {
            $button.removeClass('btn-success').button('reset')
        })
    })

    $('.fp-peek').on('click', function() {
        var $button = $(this),
            $layer = $('#fp_peek_layer')

        var button_on = $button.data('on') == 1

        $('.fp-peek')
        .data('on', 0)
        .addClass('hide')
        .removeClass('active')

        if (button_on == 1) {
            hide()

            $button
            .data('on', 0)
            .addClass('hide')
            .removeClass('active')
        } else {
            var top = ($button.position()).top - 165 // 165 TODO: position magic number
            $('.arrow', $layer).css('top', top + 'px')

            $layer.data('fp-id', $(this).data('fp-id'))
            var op = $('.nav-pills li.active a', $layer).eq(0).data('operation')

            git(op, $(this).data('fp-id'))

            $button
            .data('on', 1)
            .removeClass('hide')
            .addClass('active')
        }
    })
});

