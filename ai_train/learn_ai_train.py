# -*- coding: utf-8 -*-
"""AI 训练入门闯关（用 NumPy 从零训练）
一课分成几个小步骤。每一步：读一句大白话 → 照着写几行代码 → 点「检查这一步」→ 通过就进入下一步。
只需要安装好 Python（python.org，安装时勾选 Add to PATH），双击 start.bat 启动。
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import tkinter as tk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
from tkinter import messagebox

PROGRESS_FILE = Path.home() / ".ai_train_progress.json"
UI_FONT = "Microsoft YaHei"
CODE_FONT = "Consolas"

# ---------------------------------------------------------------------------
# 课程内容
#   say   : 这一步要做什么（大白话）
#   write : 这一步要加进程序里的代码（照着写）
#   mode  : "last" = 运行后最后一行输出必须等于 expect
#           "test" = 运行后执行 check 里的检查，全部通过才算过
#   hint  : 卡住时的提示
# 每一步的检查都是对「到这一步为止的整个程序」进行的。
# ---------------------------------------------------------------------------
from lessons_train import LESSONS  # 课程内容放在 lessons_train.py


# ---------------------------------------------------------------------------
# 运行与检查
# ---------------------------------------------------------------------------
def norm(text):
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def execute(code, extra=""):
    """把代码（以及可选的检查语句）写入临时文件并运行，返回 (返回码, 输出, 错误)。"""
    work = tempfile.mkdtemp(prefix="pylearn_")
    path = os.path.join(work, "main.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code + "\n\n" + extra + "\n")
    kwargs = {}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    try:
        p = subprocess.run(
            [sys.executable, "-X", "utf8", path],
            cwd=work, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=5, **kwargs,
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TimeoutError: 程序运行超过 5 秒，可能是 while 循环停不下来（忘了让条件变化）"


FULLWIDTH_TO_ASCII = {
    "（": "(", "）": ")", "：": ":", "，": ",", "；": ";",
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "［": "[", "］": "]", "＝": "=", "＋": "+", "－": "-", "＊": "*", "／": "/",
}


def error_message(err, user_lines):
    lines = [l for l in err.strip().splitlines() if l.strip()]
    last = lines[-1] if lines else "未知错误"
    found = re.findall(r'main\.py", line (\d+)', err)
    line_no = int(found[0]) if found else None
    where = line_no if (line_no is not None and line_no <= user_lines) else None

    # 最常见的新手错误：用了中文符号（输入法没切到英文）
    bad = re.search(r"invalid character '(.)'", err)
    if bad and bad.group(1) in FULLWIDTH_TO_ASCII:
        ch = bad.group(1)
        en = FULLWIDTH_TO_ASCII[ch]
        msg = f"你用的是中文符号「{ch}」，Python 只认英文符号「{en}」。"
        if where:
            msg += f"\n请把第 {where} 行里的「{ch}」换成「{en}」。"
        msg += "\n小技巧：打符号前先把输入法切到英文（按 Shift 键，或 Ctrl+空格）。"
        return msg

    msg = "程序出错：" + last
    if where:
        msg += f"\n出错在你的程序第 {where} 行附近"
    return msg


def check_step(step, code):
    """返回 (是否通过, 说明, 程序输出)。"""
    user_lines = len(code.splitlines())
    if step["mode"] == "last":
        rc, out, err = execute(code)
        if rc != 0:
            return False, error_message(err, user_lines), out
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        last = lines[-1] if lines else ""
        if last == step["expect"]:
            return True, "", out
        return False, (
            f"电脑最后说的是：{last or '（什么也没说）'}\n"
            f"应该说的是：{step['expect']}"
        ), out
    rc, out, err = execute(code, step["check"])
    if rc == 0:
        return True, "", out
    return False, error_message(err, user_lines), out


def cumulative_code(lesson, upto):
    """第 upto 步（含）为止，应有的完整程序（用于示范/测试）。"""
    return "\n".join(s["write"] for s in lesson["steps"][: upto + 1])


def load_state():
    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    try:
        PROGRESS_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 界面
# ---------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI 训练入门闯关")
        self.geometry("1180x820")
        self.minsize(1000, 720)
        self.configure(bg="#fafafa")

        data = load_state()
        self.progress = dict(data.get("progress", {}))   # 课id -> 已通过的步数
        self.drafts = dict(data.get("drafts", {}))       # 课id -> 编辑区内容
        self.fails = {}
        self.cur = self._first_open_lesson()
        self.step = min(self.progress.get(LESSONS[self.cur]["id"], 0), len(LESSONS[self.cur]["steps"]) - 1)

        self._build()
        self.show_lesson(self.cur, self.step)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ----- 状态 -----
    def _lid(self, i):
        return LESSONS[i]["id"]

    def _passed(self, i):
        return self.progress.get(self._lid(i), 0)

    def _lesson_done(self, i):
        return self._passed(i) >= len(LESSONS[i]["steps"])

    def _unlocked(self, i):
        return i == 0 or self._lesson_done(i - 1) or self._passed(i) > 0

    def _first_open_lesson(self):
        for i in range(len(LESSONS)):
            if not self._lesson_done(i):
                return i
        return len(LESSONS) - 1

    def _save_all(self):
        self.save_draft()
        save_state({"progress": self.progress, "drafts": self.drafts})

    def save_draft(self):
        if hasattr(self, "editor"):
            self.drafts[self._lid(self.cur)] = self.editor_text()

    def editor_text(self):
        return self.editor.get("1.0", "end-1c")

    # ----- 搭建界面 -----
    def _build(self):
        self.status = tk.Label(self, text="", anchor="w", font=(UI_FONT, 11), bg="#e9e9e9", padx=12, pady=4)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # 左侧目录
        left = tk.Frame(self, bg="#fafafa", width=250)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(12, 6), pady=12)
        left.pack_propagate(False)
        tk.Label(left, text="课程目录", font=(UI_FONT, 14, "bold"), bg="#fafafa", anchor="w").pack(fill=tk.X)
        self.progress_lbl = tk.Label(left, text="", font=(UI_FONT, 11), bg="#fafafa", fg="#555", anchor="w")
        self.progress_lbl.pack(fill=tk.X, pady=(2, 6))
        self.lb = tk.Listbox(left, font=(UI_FONT, 12), activestyle="none", exportselection=False,
                             selectbackground="#cfe8ff", selectforeground="#000")
        self.lb.pack(fill=tk.BOTH, expand=True)
        self.lb.bind("<<ListboxSelect>>", self.on_select)

        # 右侧
        right = tk.Frame(self, bg="#fafafa")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 12), pady=12)

        self.title_lbl = tk.Label(right, text="", font=(UI_FONT, 18, "bold"), bg="#fafafa", anchor="w")
        self.title_lbl.pack(fill=tk.X)
        self.step_lbl = tk.Label(right, text="", font=(UI_FONT, 12, "bold"), bg="#fafafa", fg="#2b7de9", anchor="w")
        self.step_lbl.pack(fill=tk.X, pady=(4, 4))

        tk.Label(right, text="这一步要做什么", font=(UI_FONT, 11, "bold"), bg="#fafafa", fg="#555", anchor="w").pack(fill=tk.X)
        self.say = tk.Text(right, height=4, wrap="word", font=(UI_FONT, 13), bg="#ffffff",
                           relief="solid", bd=1, padx=10, pady=8, state=tk.DISABLED)
        self.say.pack(fill=tk.X)

        tk.Label(right, text="照着写这几行（点「填入」会自动帮你写到编辑区最后）",
                 font=(UI_FONT, 11, "bold"), bg="#fafafa", fg="#555", anchor="w").pack(fill=tk.X, pady=(8, 0))
        self.write_box = tk.Text(right, height=4, font=(CODE_FONT, 13), bg="#f1f7ff",
                                 relief="solid", bd=1, padx=10, pady=6, state=tk.DISABLED)
        self.write_box.pack(fill=tk.X)

        tk.Label(right, text="你的程序（全部写在这里）", font=(UI_FONT, 11, "bold"),
                 bg="#fafafa", fg="#555", anchor="w").pack(fill=tk.X, pady=(8, 0))
        self.editor = tk.Text(right, height=10, font=(CODE_FONT, 13), undo=True, wrap="none",
                              bg="#ffffff", relief="solid", bd=1, padx=8, pady=6,
                              insertbackground="#000", tabs=("1c",))
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind("<Tab>", self._on_tab)
        self.bind("<F5>", lambda e: self.run_code())

        # 按钮
        bar = tk.Frame(right, bg="#fafafa")
        bar.pack(fill=tk.X, pady=8)
        self.btn_prev = self._button(bar, "← 上一步", self.prev_step)
        self.btn_fill = self._button(bar, "填入这几行", self.fill_step)
        self.btn_run = self._button(bar, "运行 (F5)", self.run_code)
        self.btn_check = self._button(bar, "检查这一步 ✔", self.check_now, primary=True)
        self.btn_hint = self._button(bar, "提示", self.show_hint)
        self.btn_answer = self._button(bar, "看答案", self.reveal_answer)
        self.btn_next = self._button(bar, "下一步 →", self.next_step)

        tk.Label(right, text="电脑的回答", font=(UI_FONT, 11, "bold"), bg="#fafafa", fg="#555", anchor="w").pack(fill=tk.X)
        self.output = tk.Text(right, height=6, font=(CODE_FONT, 12), bg="#1e1e1e", fg="#e6e6e6",
                              wrap="word", relief="flat", padx=8, pady=6, state=tk.DISABLED)
        self.output.pack(fill=tk.X)
        self.output.tag_config("ok", foreground="#7CFC00")
        self.output.tag_config("err", foreground="#ff6b6b")
        self.output.tag_config("hint", foreground="#ffd166")
        self.output.tag_config("info", foreground="#9aa0a6")

    def _button(self, parent, text, cmd, primary=False):
        btn = tk.Button(parent, text=text, command=cmd, font=(UI_FONT, 11),
                        bg="#2b7de9" if primary else "#e8e8e8",
                        fg="#ffffff" if primary else "#000000",
                        activebackground="#1f63bd" if primary else "#d0d0d0",
                        relief="flat", padx=12, pady=6, cursor="hand2")
        btn.pack(side=tk.LEFT, padx=(0, 8))
        return btn

    def _on_tab(self, _event):
        self.editor.insert("insert", "    ")
        return "break"

    # ----- 显示辅助 -----
    def _set_text(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state=tk.DISABLED)

    def set_output(self, parts):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", "end")
        for text, tag in parts:
            self.output.insert("end", text, tag or ())
        self.output.config(state=tk.DISABLED)

    def set_status(self, text):
        self.status.config(text="  " + text)

    # ----- 课程与步骤切换 -----
    def refresh_list(self):
        self.lb.delete(0, "end")
        for i, lesson in enumerate(LESSONS):
            if self._lesson_done(i):
                tag = "[已完成]"
            elif i == self.cur:
                tag = "[学习中]"
            elif self._unlocked(i):
                tag = "[可学]"
            else:
                tag = "[未解锁]"
            self.lb.insert("end", f"{i + 1:02d}. {tag} {lesson['title']}")
        self.lb.selection_clear(0, "end")
        self.lb.selection_set(self.cur)
        self.lb.see(self.cur)
        done_lessons = sum(1 for i in range(len(LESSONS)) if self._lesson_done(i))
        self.progress_lbl.config(text=f"已完成 {done_lessons} / {len(LESSONS)} 课")

    def show_lesson(self, i, step=0):
        self.save_draft()
        self.cur = i
        lesson = LESSONS[i]
        self.step = max(0, min(step, len(lesson["steps"]) - 1))
        self.title_lbl.config(text=f"第 {i + 1} 课：{lesson['title']}")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", self.drafts.get(lesson["id"], ""))
        self.editor.edit_reset()
        self.set_output([("先看上面的大白话，再照着写，然后点「检查这一步」。", "info")])
        self.show_step()
        self.refresh_list()

    def show_step(self):
        lesson = LESSONS[self.cur]
        step = lesson["steps"][self.step]
        total = len(lesson["steps"])
        self.step_lbl.config(text=f"第 {self.step + 1} 步 / 共 {total} 步")
        self._set_text(self.say, step["say"])
        self._set_text(self.write_box, step["write"])
        self._update_buttons()

    def _update_buttons(self):
        lesson = LESSONS[self.cur]
        passed = self._passed(self.cur)
        self.btn_prev.config(state=tk.NORMAL if self.step > 0 else tk.DISABLED)
        # 只能走到已经通过的步骤，或者当前可做的那一步
        can_next = self.step < passed and self.step + 1 < len(lesson["steps"])
        self.btn_next.config(state=tk.NORMAL if can_next else tk.DISABLED)
        if self._lesson_done(self.cur) and self.cur + 1 < len(LESSONS):
            self.btn_next.config(text="进入下一课 →", state=tk.NORMAL)
        else:
            self.btn_next.config(text="下一步 →")
        self.btn_check.config(state=tk.NORMAL)

    def on_select(self, _event):
        sel = self.lb.curselection()
        if not sel:
            return
        i = sel[0]
        if i == self.cur:
            return
        if not self._unlocked(i):
            self.set_status("这一课还没解锁，先把前面的课学完。")
            self.lb.selection_clear(0, "end")
            self.lb.selection_set(self.cur)
            return
        self.show_lesson(i, self._passed(i))

    def prev_step(self):
        if self.step > 0:
            self.step -= 1
            self.show_step()

    def next_step(self):
        lesson = LESSONS[self.cur]
        if self._lesson_done(self.cur):
            if self.cur + 1 < len(LESSONS):
                self.show_lesson(self.cur + 1, self._passed(self.cur + 1))
            return
        if self.step < self._passed(self.cur) and self.step + 1 < len(lesson["steps"]):
            self.step += 1
            self.show_step()

    # ----- 动作 -----
    def fill_step(self):
        lesson = LESSONS[self.cur]
        code = lesson["steps"][self.step]["write"]
        text = self.editor_text()
        if text and not text.endswith("\n"):
            text += "\n"
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text + code + "\n")
        self.set_status("已经填入这几行。现在点「检查这一步」。")

    def run_code(self):
        code = self.editor_text()
        rc, out, err = execute(code)
        if rc == 0:
            text = out if out.strip() else "（电脑没有说话。如果想让它说，请用 print。）"
            self.set_output([(text, None)])
            self.set_status("运行完成。")
        else:
            parts = []
            if out:
                parts.append((out, None))
            parts.append((error_message(err, len(code.splitlines())), "err"))
            self.set_output(parts)
            self.set_status("程序出错了，看看红字，照着改。")

    def check_now(self):
        lesson = LESSONS[self.cur]
        step = lesson["steps"][self.step]
        code = self.editor_text()
        ok, msg, out = check_step(step, code)
        if ok:
            if self.step >= self._passed(self.cur):
                self.progress[self._lid(self.cur)] = self.step + 1
            self._save_all()
            parts = [("✅ 对了！", "ok")]
            if out.strip():
                parts.append(("\n电脑说：\n" + out, None))
            self.set_output(parts)
            if self._lesson_done(self.cur):
                if self.cur + 1 < len(LESSONS):
                    self.set_status("这一课学完了！点「进入下一课 →」。")
                else:
                    self.set_status("全部学完了！你已经会用 NumPy 从零训练模型了。")
            else:
                self.set_status("很好，点「下一步 →」继续。")
            self.refresh_list()
            self._update_buttons()
        else:
            key = f"{self._lid(self.cur)}-{self.step}"
            self.fails[key] = self.fails.get(key, 0) + 1
            parts = [("❌ 还没对\n", "err"), (msg, None)]
            if self.fails[key] >= 2:
                parts.append(("\n\n（可以点「提示」看看。实在不行再点「看答案」）", "hint"))
            self.set_output(parts)
            self.set_status("没关系，照着红字改一改，再点「检查这一步」。")
            self._save_all()

    def show_hint(self):
        step = LESSONS[self.cur]["steps"][self.step]
        self.set_output([("提示：\n", "hint"), (step["hint"], "hint")])
        self.set_status("提示只给方向，自己敲一遍最好。")

    def reveal_answer(self):
        if not messagebox.askyesno("看答案", "会把这一步要写的代码直接填进编辑区。\n确定要看吗？"):
            return
        self.fill_step()
        self.set_status("已填入。自己看一眼，再点「检查这一步」。")

    def on_close(self):
        self._save_all()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
