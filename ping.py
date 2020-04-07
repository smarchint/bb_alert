import requests
import json
import logging
import functools

from settings import COOKIE as COOKIE_STR

from notify_run import Notify

# create logger with 'spam_application'
logger = logging.getLogger("bb_alert")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(f'bb_alert.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


API_TIMEOUT = 20  # sec

def notify():
    notify = Notify()
    notify.send('Bigbasket may be available. check it out NOW !!!')


def parse_cookie_to_dict(cookie):
    acc = {}
    for i in cookie.split(';'):
        k, v = i.split('=',1)
        acc[k.strip()] = v.strip()
    return acc

def request_to_curl_str(request):
    req = request
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = req.method
    uri = req.url
    data = req.body
    headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
    headers = " -H ".join(headers)
    return command.format(method=method, headers=headers, data=data, uri=uri)

def cookie_dict_to_str(cookie_dict):
    return "; ".join([str(x)+"="+str(y) for x,y in cookie_dict.items()])


def log_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Exception as e:
            logger.exception(e)
    return wrapper


@log_exception
def ping():
    BASE_URL = 'https://www.bigbasket.com/basket/?ver=2'
    # PING_URL = 'https://www.bigbasket.com/co/update-po/'
    PING_URL = 'https://www.bigbasket.com/co/delivery-preferences-new/'
    COOKIE = parse_cookie_to_dict(COOKIE_STR)

    response = requests.get(BASE_URL, cookies=COOKIE)
    COOKIE.update(response.cookies.get_dict())
    headers = {
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    headers["cookie"] = cookie_dict_to_str(COOKIE)
    headers['x-csrftoken'] = COOKIE["csrftoken"]
    headers['x-requested-with'] =  'XMLHttpRequest'
    headers['user-agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    headers['origin'] = BASE_URL
    headers['referer'] = 'https://www.bigbasket.com/co/checkout/?x=0&spni=12&addr=151568892'

    logger.info(f"\n {COOKIE} \n {headers}")
    response = requests.get(PING_URL, cookies=COOKIE, headers=headers, timeout=API_TIMEOUT)
    logger.info(f"{response.text}")

    resp_dict = response.json()
    if resp_dict["status"] == "failure":
        logger.info("PING_RESULT: FAILURE")
    else:
        logger.info("PING_RESULT: SUCCESS")
        notify()

    # response = requests.get("https://www.bigbasket.com/account/me", cookies=COOKIE, headers=headers)
    # import pdb; pdb.set_trace()

if __name__ == "__main__":
    ping()

