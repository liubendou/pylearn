records = []      # 所有账目都装在这个列表里，一笔就是一个字典


def show_menu():
    print("\n==== 六本豆无敌牛福记账本 ====")
    print("1. 添加一笔记账")
    print("2. 查看所有记录")
    print("3. 按类别统计")
    print("4. 删除一笔")
    print("5. 退出")


def add_record():
    print("\n--- 记一笔 ---")

    # 1. 问金额，直到输入的是数字才放行
    while True:
        text = input("金额：")
        try:
bu            amount = float(text)
        except ValueError:
            print("金额得是数字，比如 35 或 12.5，再输一次。")
            continue
        break

    # 2. 问类别，不填就归到"其他"
    category = input("类别（吃饭/交通/购物…）：").strip()
    if category == "":
        category = "其他"

    # 3. 拼成字典，塞进列表
    records.append({"amount": amount, "category": category})
    print("记好了：%s %s 元，现在一共 %d 笔。" % (category, amount, len(records)))


def main():
    while True:
        show_menu()
        choice = input("赶紧给我选：")

        if choice == "5":
            print("滚吧")
            break
        elif choice == "1":
            add_record()
        elif choice in ["2", "3", "4"]:
            print("这个功能还没写。")
        else:
            print("没有这个选项，重新选。")


main()


