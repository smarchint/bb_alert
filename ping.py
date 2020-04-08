import requests
import json
import logging
import functools

from settings import COOKIE as COOKIE_STR, ADDR_INT_ID, DEBUG

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
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s  %(funcName)20s() - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


API_TIMEOUT = 20  # sec
DELIVERY_PREFERENCE_API = "https://www.bigbasket.com/co/delivery-preferences-new/"
UPDATE_PO_API = "https://www.bigbasket.com/co/update-po/"
DEFAULT_API = DELIVERY_PREFERENCE_API
BASE_URL = 'https://www.bigbasket.com/basket/?ver=2'


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


def check_update_po(COOKIE, headers):
    headers['referer'] = BASE_URL
    response = requests.post(UPDATE_PO_API, data={"addr_id": ADDR_INT_ID}, cookies=COOKIE, headers=headers, timeout=API_TIMEOUT)
    try:
        resp_dict = response.json()
        logger.info(f"{UPDATE_PO_API} : {resp_dict}")
        if resp_dict["status"] == "failure":
            return False
        return True
    except Exception as e:
        logger.warning(f"{UPDATE_PO_API} : {response.text}")
        logger.exception(e)
        return False


def check_delivery_preferece(COOKIE, headers):
    headers['referer'] = f'https://www.bigbasket.com/co/checkout/?x=0&spni=12&addr={ADDR_INT_ID}'
    response = requests.get(DELIVERY_PREFERENCE_API, cookies=COOKIE, headers=headers, timeout=API_TIMEOUT)
    try:
        resp_dict = response.json()
        logger.info(f"{DELIVERY_PREFERENCE_API} : {resp_dict}")
        if resp_dict["error_code"] in [1000, 1005] and resp_dict["details"].get("checkout_slot_failure_message"):
            return False
        return True
    except Exception as e:
        logger.warning(f"{DELIVERY_PREFERENCE_API} : {response.text}")
        logger.exception(e)
        return False


def check_slot_availability(COOKIE, headers):
    if check_update_po(COOKIE, headers):
        if check_delivery_preferece(COOKIE, headers):
            return True
    return False


@log_exception
def ping(api="delivery-preferences-new"):
    PING_URL = DELIVERY_PREFERENCE_API if DEFAULT_API == DELIVERY_PREFERENCE_API else UPDATE_PO_API
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
    headers['referer'] = BASE_URL

    # logger.info(f"\n {COOKIE} \n {headers}")


    '''
    check-update-po:
        if /update-po is failure : FAILURE end
        else : /check-delivery-preference-new

    check-delivery-preference-new:
        if checkout_slot_failure_message exists: FAILURE
        else SUCCESS
    
    observation:
        update-po succeds when SLOTS_EXISTS ?? [toCHECK]
    '''

    if check_slot_availability(COOKIE, headers):
        logger.info("PING_RESULT: SUCCESS")
        if not DEBUG:
            notify()
    else:
        logger.info("PING_RESULT: FAILURE")


    # response = requests.get("https://www.bigbasket.com/account/me", cookies=COOKIE, headers=headers)
    # import pdb; pdb.set_trace()

if __name__ == "__main__":
    ping()

