# 个人记账本
# 现在只有菜单。下一步我们来写「添加一笔」。


def show_menu():
    print("\n===== 个人记账本 =====")
    print("1. 添加一笔支出")
    print("2. 查看所有记录")
    print("3. 按类别统计")
    print("4. 删除一笔")
    print("5. 导出 CSV")
    print("6. 退出")


def main():
    while True:
        show_menu()
        choice = input("请输入选项数字：")

        if choice == "6":
            print("再见！")
            break
        elif choice in ["1", "2", "3", "4", "5"]:
            print("这个功能还没写，下一步来写。")
        else:
            print("没有这个选项，请重新输入。")


main()
