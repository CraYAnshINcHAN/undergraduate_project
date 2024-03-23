import tkinter as tk

def run_code():
    code = text_box.get("1.0", "end") # 获取文本框中的代码
    exec(code)# 执行代码

window = tk.Tk()# 创建窗口
text_box = tk.Text(window)# 创建文本框
text_box.pack()# 将文本框放置在窗口中

#run_button = tk.Button(window, text="Run", command=run_code)# 创建按钮
#run_button.pack()# 将按钮放置在窗口中


window.mainloop()
