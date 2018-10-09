import configparser
import os
import json
import logging

cps = configparser.ConfigParser()


def decorator_auth(func):
    """ 权限验证装饰器
    先获取请求方式method 再根据请求方式取出用户名和密码并进行类型转换
    读取默认配置并对提交过来的信息进行比对
    """
    def wrapper(*args, **kwargs):
        request = args[1]
        un, pwd = "un", "pwd"
        try:
            cps.read(os.path.dirname(__file__) + "/default_scrapyd.conf")
            auth_username, auth_password = cps.get("scrapydart", "auth_username"), cps.get("scrapydart", "auth_password")
        except Exception as err:
            logging.info(err)
            auth_username = auth_password = None
        if not auth_username or not auth_password:
            return func(*args, **kwargs)
        if request.args.get(bytes(un, encoding="utf8")) and request.args.get(bytes(pwd, encoding="utf8")):
            username = str(request.args.get(bytes(un, encoding="utf8"))[0], encoding="utf8")
            password = str(request.args.get(bytes(pwd, encoding="utf8"))[0], encoding="utf8")
            if username == auth_username and password == auth_password:
                return func(*args, **kwargs)
            return {"status": "error", "message": "username or password you entered is incorrect. Please re request"}
        else:
            return {"status": "error", "message": "You have not obtained the authorization."}
        return {"status": "error", "message": "Method Not Allowed"}
    return wrapper

