# coding:utf-8

import os

basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

timezone_name = u'Asia/Shanghai'

qiniu_bucket = "sz-sports"
qiniu_baseurl = "http://7xjeh2.com1.z0.glb.clouddn.com/"
qiniu_ak = "7KCkWAenEUPZoP0NZBA4ByhkpWoqe5qcyUoaAxP0"
qiniu_sk = "jmUvHCSvTNdg030wVGErI-5yehv4nNb04P9cB2Hp"

USER_APP_NAME = u'石竹运动'
USER_ENABLE_EMAIL = True
USER_ENABLE_USERNAME = False
USER_ENABLE_RETYPE_PASSWORD = True
USER_ENABLE_CHANGE_USERNAME = False
USER_ENABLE_CONFIRM_EMAIL = False
USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL = True
USER_SEND_PASSWORD_CHANGED_EMAIL = False
USER_AUTO_LOGIN_AFTER_RESET_PASSWORD = False
USER_LOGIN_URL = '/login'
USER_LOGOUT_URL = '/logout'
USER_REGISTER_URL = '/register'
USER_FORGOT_PASSWORD_URL = '/forgot-password'
WTF_CSRF_ENABLED = False

account_default_profile = 'http://192.168.2.104:5000/static/images/frontend/default/profile.png'
team_default_logo = 'http://192.168.2.104:5000/static/images/frontend/default/teamLogo.png'
team_default_uniform = 'http://192.168.2.104:5000/static/images/frontend/default/clothing.png'
