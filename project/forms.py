#encoding=utf-8
from django import forms
from project.models import Memo

#rewrite choicefield to fix validate problem
from django.forms.fields import ChoiceField


class IntegerChoiceField(ChoiceField):
    def validate(self, value):
        super(ChoiceField, self).validate(value)
        if value and not value.isdigit():
            raise forms.ValidationError(value + "不是数字")


class NewProject(forms.Form):
    TYPE_CHOICES = (
        ('1', 'PMT'),
        ('2', 'Hotfix'),
                     )
    DEP_CHOICES = ( 
        ('3', 'site'),
        ('4', 'ipad'),
        ('5', 'tw'),
        ('6', 'api'),
                     )
    REMOTE_CHOICES = ( 
        ('anjuke', 'anjuke'),
        ('haozu', 'haozu'),
        ('jinpu', 'jinpu'),
#        ('member', 'member'),
        ('anjuke_usersite', 'anjuke_usersite'),
#        ('zufang_usersite', 'zufang_usersite'),
#        ('shangpu_usersite', 'shangpu_usersite'),
#        ('pad_usersite', 'pad_usersite'),
#        ('member_usersite', 'member_usersite'),
#        ('uapi_usersite', 'uapi_usersite'),
#        ('touch_usersite', 'touch_usersite'),        
        ('wechat', 'wechat'),
        ('java', 'java'),
        ('anjuke_chat', 'anjuke_chat'),
        ('cms', 'cms'),
        ('api_usersite','api_usersite'),
        ('ajkapi','ajkapi'),
        ('hzapi','hzapi'),
        ('hzold','hzold'),
        ('jpapi','jpapi'),
        ('anlife','anlife'),
                     )

#    PMT_TYPE = (
#        ('1',"单人开发"),
#        ('2',"多人开发（主分支）"),
#        ('3',"多人开发（分支）"),
#                )

    #项目类型 1：PMT  2：Hotfix
    type = forms.ChoiceField(TYPE_CHOICES, label='项目类型', initial='1', required=True)
    #department
    department = forms.ChoiceField(DEP_CHOICES, label='所属部门', initial='1', required=True)
    #REMOTE  例如只创建二手房分支
    remote = forms.ChoiceField(REMOTE_CHOICES, label='分支仓库', initial='1', required=True)
    #所有分支仓库
    allRemote = forms.CharField(label='所选仓库')
    #项目相关联id 可以是pmt 也可以是ibug id
    relatedId = IntegerChoiceField(label='关联 PMT/IBUG', required=False)
    #备注
    suffix = forms.CharField(label='Git Branch', max_length=20, required=False)
    #项目名称
    name = forms.CharField(label='项目名称')
    #测试类型 1:需测试 2:无需测试
    #testType = forms.ChoiceField(PTEST_TYPE, label='是否需要测试', initial='1', required=True)
    #pmt类型 1:单人开发 2:多人开发（主分支）3,多人开发（分支）
    pmtType = forms.CharField(required=False)
    #父项目 id
    parent = IntegerChoiceField(required=False)
    #上线时间
    onlineDate = forms.DateField(label='上线日期', widget=forms.DateInput(attrs={'placeholder': 'yyyy-MM-dd'}))
    #创建人
    createPerson = forms.CharField(label='创建人')
    #项目描述
    description = forms.CharField(label='项目描述', required=False, widget=forms.Textarea(attrs={'cols': 10, 'rows': 5}))

    def clean(self):
        return self.cleaned_data

    def clean_relatedId(self):
        data = self.cleaned_data['relatedId']
        if not data.isdigit():
            raise forms.ValidationError(u"请选择关联 PMT/IBUG。")

        return data


class MemoForm(forms.Form):
    '''
    上线备忘表单
    '''
    #表单id
    memoId = forms.IntegerField(required=True)

    #备忘类型
    type = forms.ChoiceField(Memo.MEMO_TYPE, label='上线备忘类型', initial='1', required=True)

    #备忘说明
    content = forms.CharField(label='备忘', widget=forms.Textarea(attrs={'class': 'ctnText', 'rows': 5}), required=True)

class DelayForm(forms.Form):
    '''
    项目延期表单
    '''
    #计划上线日期
    onlineDate = forms.DateField(label='计划上线日期', widget=forms.DateInput(attrs={'placeholder': 'yyyy-MM-dd'}))
    #延期时长
    delayDate = forms.CharField(label='延期时长')
    #责任人
    person = forms.CharField(label='责任人')

    #延期原因
    delayReason = forms.CharField(label='延期原因', widget=forms.Textarea(attrs={'rows': 5}), required=True)
