records = []


def menu():
    print("\n==== 无敌记账本 ====")
    print("1. 添加一笔记账")
    print("2. 退出")
    print("3..666")


def add():
    print("记一笔帐")
    while True:
        text = input("多少钱呀：")
        try:
            amount = float(text)
        except ValueError:
            print("金额肯定是数字啊别瞎输入")
            continue
        break

    ca = input("类别:").strip()
    if ca == "":
        ca = "其它"

    records.append({"amount": amount, "category": ca})
    print("记好了:%s %s元,现在一共%d笔。" % (ca, amount, len(records)))


def m():
    while True:
        menu()
        c = input("选一个:")
        if c == "2":
            print("成功退出")
            break
        if c == "1":
            add()


m()
