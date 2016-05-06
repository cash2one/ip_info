#encoding=utf-8
from django import template
import re
register = template.Library()

# 为了做 filter chain 而设置的“随机”字符串
CHAIN_KEY = '#thxGs4k@FtKKzFi'

'''
设置(替换新增) url 中的指定参数为指定值
@example {{ url|parameter:'page'|set:'4' }} # url 中的 page 参数设为 4
'''
@register.filter(name='parameter')
def parameter(value, parameter):
    removedFirst = re.sub("^(\S+)[?&]%s=\w+(.*)" % parameter, r"\g<1>\g<2>", value)
    return ("%s&%s=%s" if '?' in removedFirst else "%s?%s=%s") % (removedFirst, parameter, CHAIN_KEY)
@register.filter(name='set')
def set(parameter, value):
    return re.sub(CHAIN_KEY, str(value), parameter)


@register.simple_tag
def keyLookup(the_dict, key):
   # Try to fetch from the dict, and if it's not found return an empty string.
   return the_dict.get(key, '')