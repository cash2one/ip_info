#encoding=utf8
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from libs.git import Git
import MySQLdb
import os
import json
import sys
import pycurl
import datetime
import time
from datetime import datetime
from time import mktime
from time import mktime as mktime
from django.contrib.auth.decorators import login_required
from account.decorators import group_required
from django.core.exceptions import ValidationError
from uaBan.models import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from auth.models import user_groups
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from django.db.models.query import QuerySet
from django.db.models.query import RawQuerySet
from django.db.models import Count
from django.shortcuts import render

@login_required(login_url='/login')
def auction_report(request):
    data = {}
    data['channelName'] = 'tools'
    return render(request, 'tools/auction_report.html', {
        'data':data
    })
