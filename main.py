# -*- coding: utf-8 -*-
import time
import requests
import base64
import ddddocr
from datetime import datetime
from argparse import ArgumentParser

TIME = datetime.today().strftime('%Y-%m-%d')
USERAGENT = "Mozilla/5.0 (Linux; Android 5.0; SM-N9100 Build/LRX21V) > AppleWebKit/537.36 (KHTML, like Gecko) " \
            "Version/4.0 > Chrome/37.0.0.0 Mobile Safari/537.36 > MicroMessenger/6.0.2.56_r958800.520 NetType/WIFI "
PROCESS = ["-------日志-------"]

USERNAME = ""  # 学号
PASSWORD = ""  # 工软校园密码
SCHOOL = "hebgydxwh"  # 学校
PROVINCE = "山东省"  # 省
CITY = "威海市"  # 市
DISTRICT = "环翠区"  # 区
XM = ""  # 姓名
XUEYUAN = "计算机科学与技术学院"  # 学院
OPENID = ""  # openid


class ReportException(Exception):
    """上报异常错误信息"""


# 获取JSESSIONID
def getJSESSIONID():
    header = {
        'User-Agent': USERAGENT,
    }
    url = "http://xy.4009955.com/sfrzwx/auth/login"
    data = {
        "openid": OPENID,
        "dlfs": "zhmm"
    }
    response_res = requests.get(url, data=data, headers=header)
    jid = requests.utils.dict_from_cookiejar(response_res.cookies)['JSESSIONID']
    print('jid')
    PROCESS.append(jid)
    return jid


# 图像识别验证码，调用ddddocr库
def getYzm(jid):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid
    }
    post_url = "http://xy.4009955.com/sfrzwx/wxsq/getYzm"
    response_res = requests.post(post_url, headers=header, cookies=cookie)
    base64code = response_res.json()['data']['content'].split(',')[1]
    imagedata = base64.b64decode(base64code)
    ocr = ddddocr.DdddOcr()
    yzm = ocr.classification(imagedata)
    x = "验证码：" + yzm
    print(x)
    PROCESS.append(x)
    return yzm


# 模拟登录
def login(jid, yzm):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid
    }
    post_url = "http://xy.4009955.com/sfrzwx/wx/login"
    data = {
        "openid": OPENID,
        "dlfs": "zhmm",
        "sjschool": "",
        "sjh": "",
        "yzm:": "",
        "zhschool": SCHOOL,
        "username": USERNAME,
        "password": PASSWORD,
        "code": yzm
    }
    requests.post(post_url, data=data, headers=header, cookies=cookie)


# 获取code,code会用来获取微信服务大厅token
def getCode1(jid):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid
    }
    url = "http://xy.4009955.com/sfrzwx/oauth/authorize?response_type=code&scope=read&client_id=wxfwdt&redirect_uri=http://xy.4009955.com/wxfwdt/&state=tysfrz"
    response_res = requests.get(url, headers=header, cookies=cookie, allow_redirects=False)
    code = response_res.headers['Location'].split('?')[1].split('=')[1].split('&')[0]
    x = "code1:" + code
    print('code1')
    PROCESS.append(x)
    return code


# 获取微信服务大厅token
def getWxfwdttoken(jid, code):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid
    }
    data = {
        "code": code
    }
    post_url = "http://xy.4009955.com/wxfwdt-api/layout_01_01/login/loginYdBycode"
    response_res = requests.post(post_url, json=data, headers=header, cookies=cookie)
    wxfwdttoken = response_res.json()['data']['content']['token']
    x = "wxtoken:" + wxfwdttoken
    PROCESS.append(x)
    return wxfwdttoken


def getCode2(jid, wxtoken):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid,
        "wxfwdtToken": wxtoken
    }
    post_url = "http://xy.4009955.com/sfrzwx/oauth/authorize?response_type=code&scope=read&client_id=jktb&redirect_uri=http://xy.4009955.com/jktb/&state=tysfrz"
    response_res = requests.get(post_url, headers=header, cookies=cookie, allow_redirects=False)
    code = response_res.headers['Location'].split('?')[1].split('=')[1].split('&')[0]
    x = "code2:" + code
    print('code2')
    PROCESS.append(x)
    return code


def getJktbtoken(jid, wxtoken, code):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid,
        "wxfwdtToken": wxtoken
    }
    data = {
        "code": code
    }
    post_url = "http://xy.4009955.com/jktb-api/jktb_01_01/login/loginYdBycode"
    response_res = requests.post(post_url, json=data, headers=header, cookies=cookie)
    jtkbtoken = response_res.json()['data']['content']['token']
    x = "jktoken:" + jtkbtoken
    print('jktoken')
    PROCESS.append(x)
    return jtkbtoken


def getTodayForms(jid, wxtoken, jktoken):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid,
        "wxfwdtToken": wxtoken,
        "jktb_token": jktoken
    }
    post_url = "http://xy.4009955.com/jktb-api/jktb_01_01/homePage/getToadyForms"
    response_res = requests.post(post_url, headers=header, cookies=cookie)
    form = response_res.json()['data']['content'][0]['bdtbslid']
    x = "todayid:" + form
    print('todayid')
    PROCESS.append(x)
    return form


def submit(jid, jktoken, todayid):
    header = {
        'User-Agent': USERAGENT,
    }
    cookie = {
        "JSESSIONID": jid,
        "jktb_token": jktoken
    }
    data = {"list": [
        {"zjlx": 3, "list": [{"column": "c001", "content": "校内"}, {"column": "c002", "content": "校外"}],
         "value": ["c001"]}, {"zjlx": 5, "list": [{"column": "gSheng", "content": "山东省"},
                                                  {"column": "gShi", "content": "威海市"},
                                                  {"column": "gQu", "content": "环翠区"}], "value": ""}, {"zjlx": 3,
                                                                                                          "list": [{
                                                                                                              "column": "c010",
                                                                                                              "content": "37.2℃及以下"},
                                                                                                              {
                                                                                                                  "column": "c012",
                                                                                                                  "content": "37.3℃-38.4℃（请及时就医并在3天内进行3次核酸检测）"},
                                                                                                              {
                                                                                                                  "column": "c013",
                                                                                                                  "content": "38.5℃及以上（请及时就医并在3天内进行3次核酸检测）"}],
                                                                                                          "value": [
                                                                                                              "c010"]},
        {"zjlx": 3, "list": [{"column": "c014", "content": "没有出现不适症状"},
                             {"column": "c015", "content": "乏力、咳嗽、流涕等感冒症状"},
                             {"column": "c016", "content": "呕吐、腹泻等消化道不适"},
                             {"column": "c017", "content": "与传染病无关的不适症状"}], "value": ["c014"]}, {"zjlx": 3,
                                                                                                            "list": [{
                                                                                                                "column": "c018",
                                                                                                                "content": "未被隔离"},
                                                                                                                {
                                                                                                                    "column": "c019",
                                                                                                                    "content": "居家隔离观察（需要医护人员上门核酸采样）"},
                                                                                                                {
                                                                                                                    "column": "c020",
                                                                                                                    "content": "校外集中隔离点隔离观察"}],
                                                                                                            "value": [
                                                                                                                "c018"]},
        {"zjlx": 3, "list": [{"column": "c003", "content": "未接种"}, {"column": "c004", "content": "已接种第一针"},
                             {"column": "c005", "content": "已接种第二针"},
                             {"column": "c006", "content": "已接种第三针"}], "value": ["c005"]}, {"zjlx": 3, "list": [
            {"column": "c007", "content": "绿码"},
            {"column": "c008", "content": "灰码（请在到威海后第1、第2、第4天各完成1次核酸检测）"},
            {"column": "c009", "content": "黄码"}, {"column": "c010", "content": "红码"}], "value": ["c007"]},
        {"zjlx": 3, "list": [{"column": "c028", "content": "未出校"},
                             {"column": "c029", "content": "出校，未离开威海（须填报出行方式和外出地点）"},
                             {"column": "c030", "content": "离威"}], "value": ["c028"]},
        {"zjlx": 2, "list": [{"column": "c031", "content": ""}], "value": ""},
        {"zjlx": 3, "list": [{"column": "c021", "content": "是"}, {"column": "c022", "content": "否"}],
         "value": ["c022"]}, {"zjlx": 1, "list": [{"column": "c023", "content": ""}], "value": ""},
        {"zjlx": 3, "list": [{"column": "c024", "content": "是"}, {"column": "c025", "content": "否"}],
         "value": ["c025"]}, {"zjlx": 1, "list": [{"column": "c026", "content": ""}], "value": ""},
        {"zjlx": 2, "list": [{"column": "c027", "content": ""}], "value": ""}], "isEdit": 1, "tbzt": 0, "syxgcs": 2,
        "tbrq": TIME, "mrtbjzsj": "22:10", "xm": XM, "zzjgmc": XUEYUAN,
        "bdtbslid": todayid, "bdmc": "学生每日健康填报"}

    post_url = "http://xy.4009955.com/jktb-api/jktb_01_01/homePage/saveForm"
    response_res = requests.post(post_url, json=data, headers=header, cookies=cookie)
    x = "finalRes:" + response_res.content.decode()
    print(x)
    PROCESS.append(x)


def tianbao():
    for _ in range(5):
        try:
            jid = getJSESSIONID()
            yzm = getYzm(jid)
            login(jid, yzm)
            wxcode = getCode1(jid)
            wxtoken = getWxfwdttoken(jid, wxcode)
            jkcode = getCode2(jid, wxtoken)
            jktoken = getJktbtoken(jid, wxtoken, jkcode)
            todayid = getTodayForms(jid, wxtoken, jktoken)
            submit(jid, jktoken, todayid)
        except Exception as e:
            PROCESS.append("❌ fail,retrying......\n")
            PROCESS.extend(list(e.args))
            print(e.args)
            time.sleep(5)
        else:
            PROCESS.append("✔ success\n填报已完成")
            res = '\n'.join(PROCESS)
            with open("result.txt", "w", encoding="utf-8") as Result:
                Result.write(res)
            return

    raise ReportException("5 times failed. Report end.")


if __name__ == '__main__':
    parser = ArgumentParser(description='HITwh疫情上报')
    parser.add_argument('username', help='登录用户名')
    parser.add_argument('password', help='登录密码')
    # parser.add_argument('school', help='学校')
    # parser.add_argument('province', help='省')
    # parser.add_argument('city', help='市')
    # parser.add_argument('district', help='区')
    parser.add_argument('xm', help='姓名')
    parser.add_argument('xueyuan', help='学院')
    parser.add_argument('openid', help='openid')
    args = parser.parse_args()

    USERNAME = args.username
    PASSWORD = args.password
    # SCHOOL = args.school
    # PROVINCE = args.province
    # CITY = args.city
    # DISTRICT = args.district
    XM = args.xm
    XUEYUAN = args.xueyuan
    OPENID = args.openid

    tianbao()
