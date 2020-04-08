# bb_alert
slot availability pinger for bigbasket (during coronavirus lockdown)

+ python 3.7
+ add cookie string and address_id in settings.py file
+ pip install -r requirements.txt
+ use `https://notify.run/` for registering your apps (android / desktop).
+ python -m ping
+ add to crontab or deploy as lambda function


- crontab path issue: python path should be fully qualified one.

### settings.py
- ADDR_INT_ID - integer `(can be found from checkout page [https://www.bigbasket.com/co/checkout/?x=0&spni=12&addr={ADDR_INT_ID}])`
- COOKIE - string
