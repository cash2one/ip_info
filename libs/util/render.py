#encoding=utf8

from django.template import RequestContext
from functools import wraps
from django.shortcuts import render_to_response


def rendr(template_name, channel):
    def inner_render(fn):
        def wrapped(request, *args, **kwargs):
            result = fn(request, *args, **kwargs)
            if type(result) is dict:
                return render_to_response(template_name,
                                       dict(result, **{'data': {'channelName': channel}}),
                                       context_instance=RequestContext(request))
            else:
                return result
        return wraps(fn)(wrapped)
    return inner_render
