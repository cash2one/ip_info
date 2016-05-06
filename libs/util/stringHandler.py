#encoding=utf8

import re
'''
处理html 标签
'''
def post_content_replace(content):
    content = re.sub("<","&lt;",content)
    content = re.sub(">","&gt;",content)
    content = re.sub(" ","&nbsp;",content)
    content = re.sub("\r\n","<br>",content)
    return content

