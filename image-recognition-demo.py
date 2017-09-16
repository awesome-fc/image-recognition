# coding=utf-8

"""
应用场景：新图片存储到OSS，自动对图片进行归类存储。
方案分析：
    step1：通过OSS的Put或者Post事件的触发函数计算服务
    step2：函数服务里通过调用阿里云的图像识别服务，实时分析出图片内容
    step3：解析识别的结果，归类存储到OSS不同的bucket中
前置：
    step1: 开通日志服务，并授权函数服务
    step2: 开通oss，并创建2个bucket， one bucket for watching，one bucket for 'plant, animal' image
    step3: 开通图像识别服务
"""

from urlparse import urlparse

import oss2
import logging
import json
import urllib2
import datetime
import base64
import hmac
import hashlib


# 处理主函数
def handler(event, context):
    # event is json string, parse it
    logger = logging.getLogger()
    logger.info('start recognition')

    evt = json.loads(event)
    endpoint = 'oss-{0}.aliyuncs.com'.format(evt['events'][0]['region'])
    creds = context.credentials
    logger.info(evt['events'][0]['oss']['bucket']['name'])
    auth = oss2.StsAuth(creds.accessKeyId, creds.accessKeySecret, creds.securityToken)

    # watched bucket
    bucket = oss2.Bucket(auth, endpoint, evt['events'][0]['oss']['bucket']['name'])

    # one bucket for catalog
    bucket_catalog = oss2.Bucket(auth, endpoint, '<your catalog bucket>')

    obj_key = evt['events'][0]['oss']['object']['key']
    logger.info('obj key:' + obj_key)
    # get object
    content = bucket.get_object(obj_key)
    data = content.read()

    try:
        # call image recognition api
        result = detect_pic(base64.b64encode(data))
        logger.info('detect result:' + result)
        result = json.loads(result)

        # 分类存储
        for item in result['tags']:
            logger.info('start to foreach, value=' + item['value'])
            # 植物
            if item['value'] == '植物':
                logger.info('put plant bucket')
                bucket_catalog.put_object('plant/' + obj_key, data)
            # 动物
            elif item['value'] == '动物':
                logger.info('put animal bucket')
                bucket_catalog.put_object('animal/' + obj_key, data)

    except IOError, e:
        logging.error('image recognition happens error, msg=' + e.strerror)
        return 'error'
    return 'ok'


'''
   图像识别调用
    1. 开通识别服务：https://help.aliyun.com/document_detail/53385.html
    2. 因为图像识别服务不支持临时ak验证，需要创建子账户accesskey
'''


def detect_pic(content):
    ak_id = '< your sub-account ak_id>'
    ak_secret = '<your sub-account ak_sr>'
    options = {
        'url': 'https://dtplus-cn-<your service region>.data.aliyuncs.com/image/tag',
        'method': 'POST',
        'body': json.dumps({"type": 1, "content": content}, separators=(',', ':')),
        'headers': {
            'accept': 'application/json',
            'content-type': 'application/json',
            'date': get_current_date(),
            'authorization': ''
        }
    }
    body = ''
    if 'body' in options:
        body = options['body']
    body_md5 = ''
    if not body == '':
        body_md5 = to_md5_base64(body)
    url_path = urlparse(options['url'])
    if url_path.query != '':
        url_path = url_path.path + "?" + url_path.query
    else:
        url_path = url_path.path
    string_to_sign = options['method'] + '\n' + options['headers']['accept'] + '\n' + body_md5 + '\n' + options['headers'][
        'content-type'] + '\n' + options['headers']['date'] + '\n' + url_path
    signature = to_sha1_base64(string_to_sign, ak_secret)
    auth_header = 'Dataplus ' + ak_id + ':' + signature
    options['headers']['authorization'] = auth_header
    request = None
    method = options['method']
    url = options['url']
    if 'GET' == method or 'DELETE' == method:
        request = urllib2.Request(url)
    elif 'POST' == method or 'PUT' == method:
        request = urllib2.Request(url, body)
    request.get_method = lambda: method
    for key, value in options['headers'].items():
        request.add_header(key, value)
    try:
        conn = urllib2.urlopen(request)
        response = conn.read()
        return response
    except urllib2.HTTPError, e:
        print e.read()
        raise SystemExit(e)


# 获取当前时间
def get_current_date():
    date = datetime.datetime.strftime(datetime.datetime.utcnow(), "%a, %d %b %Y %H:%M:%S GMT")
    return date


# md5
def to_md5_base64(str_body):
    hash = hashlib.md5()
    hash.update(str_body)
    return hash.digest().encode('base64').strip()


# sha1
def to_sha1_base64(string_to_sign, secret):
    hmacsha1 = hmac.new(secret, string_to_sign, hashlib.sha1)
    return base64.b64encode(hmacsha1.digest())
