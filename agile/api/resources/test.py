import time
import datetime

if __name__ == "__main__":
    date = "week"
    # 接收一下表格的all()数据，然后根据一系列操作来返回数据
    if date == "month":
        pass
    elif date == "week":
        # locaTime = time.strftime("%Y-%m-%d", time.localtime())
        frontTime = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        for i in range(6):
            behindTime = frontTime - week
            print(str(frontTime) + " - " + str(week) + " = " + str(behindTime))
            frontTime = behindTime

