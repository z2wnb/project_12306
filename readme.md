#query_ticket.py 车票查询源码（无票价信息）
#add_price_query_ticket.py 车票查询源码（有票价信息）
#chromedriver.exe selenium浏览器驱动程序

#打包程序命令
pyinstaller -F --icon=ticket.ico query_ticket.py
pyinstaller -F --icon=ticket.ico add_price_query_ticket.py

#运行query_ticket.exe、add_price_query_ticket.exe