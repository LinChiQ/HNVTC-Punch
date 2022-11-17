from hashlib import md5
import requests
import yaml
import time
import re
import json


def GetPW(password):
    a = md5(password.encode('utf-8'))
    a = a.hexdigest()
    if (len(a) > 5):
        a = a[0:5] + "a" + a[5:len(a)]
    if (len(a) > 10):
        a = a[0:10] + "b" + a[10:len(a)]
    a = a[0:len(a) - 2]
    return a


def ReadLastConfig(headers):
    time_stamp = int(round(time.time() * 1000))
    url = 'http://xsgl.hnvtc.cn/student/content/student/temp/zzdk/lastone'
    params = {'_t_s_': time_stamp}
    req = requests.get(url, params=params, headers=headers)
    try:
        last_data = json.loads(req.text)
        print("获取上次数据成功！")
    except Exception as e:
        print("获取上次失败！", e)
    return last_data


def HandleData(last_data, zzdk_token):
    data = {
        'dkdz': last_data['dkdz'],
        'dkdzZb': '117.01291,32.621414',
        'dkly': 'weixin',
        'zzdk_token': zzdk_token,
        'dkd': last_data['dkd'],
        'jzdSheng.dm': last_data['jzdSheng']['dm'],
        'jzdShi.dm': last_data['jzdShi']['dm'],
        'jzdXian.dm': last_data['jzdXian']['dm'],
        'jzdValue': last_data['jzdSheng']['dm'] + ',' + last_data['jzdShi']['dm'] + ',' + last_data['jzdXian']['dm'],
        'jzdDz': last_data['jzdDz'],
        'jzdDz2': last_data['jzdDz2'],
        'lxdh': last_data['lxdh'],
        'sfzx': last_data['sfzx'],
        'sfzx1': '在校',
        'twM.dm': last_data['twM']['dm'],
        'tw1': last_data['twM']['mc'],
        'tw1M.dm': '',
        'tw11': '',
        'tw2M.dm': '',
        'tw12': '',
        'tw3M.dm': '',
        'tw13': '',
        'yczk.dm': last_data['yczk']['dm'],
        'yczk1': last_data['yczk']['mc'],
        'fbrq': '',
        'jzInd': '0',
        'jzYy': '',
        'zdjg': '',
        'fxrq': '',
        'brJccry.dm': last_data['brJccry']['dm'],
        'brJccry1': last_data['brJccry']['mc'],
        'jkm': '',
        'jkm1': '',
        'xcm': '',
        'xcm1': '',
        'xgym': '',
        'xgym1': '',
        'hsjc': '',
        'hsjc1': '',
        'bz': '',
        'operationType': last_data['operationType'],
        'dm': '',
    }
    return data


def GetToken(headers):
    time_stamp = int(round(time.time() * 1000))
    params = {'_t_s_': time_stamp}
    url = 'http://xsgl.hnvtc.cn/student/wap/menu/student/temp/zzdk/_child_/edit'
    req = requests.get(url, headers=headers, params=params)
    zzdk_token = re.search(
        r'<input class="hidden" type="text" id="zzdk_token" name="zzdk_token" value="(.*?)"/>', req.text)
    if not zzdk_token:
        return False
    return zzdk_token.group(1)


def ReadConfigData():
    try:
        with open('/root/HNPunch/config.yaml', 'r', encoding='utf-8') as f:
            configs = yaml.safe_load_all(f.read())
            return configs
    except Exception as e:
        print("读取错误", e)
        exit(0)


def Punch(headers, punch_data):
    url = 'http://xsgl.hnvtc.cn/student/content/student/temp/zzdk'
    time_stamp = int(round(time.time() * 1000))
    req = requests.post(url, headers=headers, data=punch_data,
                        params={'_t_s_': time_stamp})
    try:
        text = json.loads(req.text)
    except Exception as e:
        print("打卡错误！", e)
        return False
    success = text['result']
    if success is True:
        print("打卡成功！")
        return True
    else:
        error_info = text['errorInfoList'][0]['message']
        print("打卡失败！", error_info)
        return False


def Login(headers, username, password):
    login_url = "http://xsgl.hnvtc.cn/student/website/login"
    data = {'uname': username, 'pd_mm': GetPW(password)}
    login = requests.post(login_url, headers=headers, data=data)
    try:
        print(username, "获取Cookie成功！")
        cookies = login.headers['Set-Cookie']
    except Exception as e:
        print(username, "获取Cookie失败！")
        return False
    return cookies


def main(configs):
    for config in configs:
        headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 10; WLZ-AN00 Build/HUAWEIWLZ-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4343 MMWEBSDK/20220903 Mobile Safari/537.36 MMWEBID/4162 MicroMessenger/8.0.28.2240(0x28001C57) WeChat/arm64 Weixin NetType/3gnet Language/zh_CN ABI/arm64"}
        username, password = str(config['username']), str(
            config['password'])
        cookies = Login(headers, username, password)
        headers['Cookie'] = cookies
        zzdk_token = GetToken(headers)
        if zzdk_token is False:
            print(username, "登陆失败！")
            print()
            continue
        last_data = ReadLastConfig(headers)
        punch_data = HandleData(last_data, zzdk_token)
        Punch(headers, punch_data)
        print()


if __name__ == "__main__":
    configs = ReadConfigData()
    main(configs)
