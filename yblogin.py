#!/usr/bin/env python3
# coding=utf-8
import re
from base64 import b64encode
import requests
from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA

BASEURL = 'https://www.yiban.cn/'

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.18 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

'''
模拟 JSEncrypt 加密
加密方式为 PKCS1_v1_5
'''

def rsaEncrypt(password, key):

    cipher = PKCS1_v1_5.new(RSA.importKey(key))
    return b64encode(cipher.encrypt(password.encode()))

'''
易班登陆拿Token
参数: USERNAME, PASSWD
'''

def getUserToken(user, passwd):

    LOGIN_PAGE = BASEURL+'login'
    LOGIN_URL = BASEURL+'login/doLoginAjax'
    r = requests.Session()
    LoginPage = r.get(LOGIN_PAGE)
    RsaKey = re.search(r'data-keys=\'([\s\S]*?)\'',LoginPage.text).group(1)
    KeysTime = re.search(r'data-keys-time=\'(.*?)\'',LoginPage.text).group(1)
    Password = rsaEncrypt(passwd, RsaKey)

    data = {
        'account': user,
        'password': Password,
        'captcha': None,
        'keysTime': KeysTime,
        'is_rember': 1
    }
    
    LoginURL = r.post(LOGIN_URL, headers=header, data=data)
    token = LoginURL.cookies['yiban_user_token']  # -> KeyError Exception
    r.close()
    return token

'''
获取群组信息
返回 JSON 字典
'''

def getInfo(token):

    Get_Group_Info = requests.get(BASEURL+'my/group/type/public', cookies=token)
    group_id = re.search(r'href="/newgroup/indexPub/group_id/(\d+)/puid/(\d+)"', Get_Group_Info.text).group(1)
    puid = re.search(r'href="/newgroup/indexPub/group_id/(\d+)/puid/(\d+)"', Get_Group_Info.text).group(2)

    payload = {
        'puid': puid,
        'group_id': group_id
    }

    Get_Channel_Info = requests.post(BASEURL+'forum/api/getListAjax', cookies=token, data=payload)
    channel_id = Get_Channel_Info.json()['data']['channel_id']

    Get_User_Info = requests.post(BASEURL+'ajax/my/getLogin', cookies=token)
    actor_id = Get_User_Info.json()['data']['user']['id']
    nick = Get_User_Info.json()['data']['user']['nick']

    info = {
        'group_id': group_id,
        'puid': puid,
        'channel_id': channel_id,
        'actor_id': actor_id,
        'nick': nick
    }

    return info
