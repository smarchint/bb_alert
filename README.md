# bb_alert
slot availability pinger for bigbasket (during coronavirus duration)

+ python 3.7
+ add cookie string in settings.py file
+ pip install -r requirements.txt
+ use `https://notify.run/` for registering your apps (android / desktop).
+ python -m ping
+ add to crontab or deploy as lambda function



- crontab path issue: python path should be fully qualified one.
- might require to change the addr param at [code here](https://github.com/SaikumarChintada/bb_alert/blob/master/ping.py#L86)
- addr id can be obtained from checkout page
