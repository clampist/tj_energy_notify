tj_energy_notify
================

自动查询并记录寝室所剩电量，在不足以支撑三天时发邮件提醒多人，支持中文无乱码，并记录数据


Linux 版 `tj_energy_notify.py`
---
设置好发送帐号密码和接受帐号，加入 crontab 即可正常工作

crontab.example

    # replace /path/to/tj_energy_notify.py with the real path
    30 10,16 * * * python /path/to/tj_energy_notify.py


GAE 版 ` tj_energy_notify_sae.py`
---

将 `tj_energy_notify.py` 移植到 GAE, 后续将支持更多寝室

Demo: http://notify.archpy.info
