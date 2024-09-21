import tkinter as tk
# from tkinter import messagebox
import clipboard
from run import info
from bot import parse_consonants_q, isconsonants, homesavetelno, place_impl
import os
import time

INTERVAL = 0.05


def beep():
    os.system("osascript -e 'beep'")


def on_num_key_pressed(n: str):
    on_btnPaste_click()
    lbl_input.set(f'{n} {lbl_input.get()}')
    root.update()
    btnExec.invoke()


# 버튼 클릭 시 실행되는 함수
def on_btnExec_click():
    user_input = txtInput.get()

    if user_input.split(' ')[0].isnumeric():
        result = place_impl(user_input)
    else:
        q, cons = parse_consonants_q(user_input)
        if isconsonants(cons):
            result = info(q, cons)
        else:
            home, homesv, telno = homesavetelno(user_input)
            result = home
            lbl_homesave.set(homesv)
            lbl_telno.set(telno)

    lbl_result.set(result)
    btnHomeCopy.invoke()
    root.update()
    beep()


def on_btnPaste_click():
    text = clipboard.paste()
    lbl_input.set(text)
    lbl_result.set("")
    lbl_homesave.set("")
    lbl_telno.set("")
    root.update()
    # beep()


def on_btnConcat_click():
    text = clipboard.paste()
    concat = f'{lbl_input.get()} {text}'
    lbl_input.set(concat)
    root.update()
    btnExec.invoke()


def on_btnHomeCopy_click():
    time.sleep(INTERVAL)
    text = lbl_result.get()
    clipboard.copy(text)


def on_btnCopyHomeSave_click():
    time.sleep(INTERVAL)
    text = lbl_homesave.get()
    clipboard.copy(text)


def on_btnCopyTelno_click():
    time.sleep(INTERVAL)
    text = lbl_telno.get()
    clipboard.copy(text)


def on_btnRun_click():
    btnPaste.invoke()
    btnExec.invoke()


def on_btnHomeSaveRun_click():
    btnRun.invoke()
    btnCopyHomeSave.invoke()


def update_timer():
    text = clipboard.paste()
    lblClipboard.config(text=text, )
    root.after(200, update_timer)


# 기본 윈도우 생성
root = tk.Tk()
root.title("IAD UI")
root.geometry("850x200")

lblInput = tk.Label(root, text="입 력:")
lblInput.grid(row=0, column=0, padx=3, pady=3, sticky="w")

lbl_input = tk.StringVar()
txtInput = tk.Entry(root, width=50, textvariable=lbl_input)
txtInput.grid(row=0, column=1, padx=3, pady=3)

btnPaste = tk.Button(root, text="붙여넣기(p)", command=on_btnPaste_click)
btnPaste.grid(row=0, column=2, padx=3, pady=3, sticky="w")

btnConcat = tk.Button(root, text="+초성실행(o)", command=on_btnConcat_click)
btnConcat.grid(row=0, column=3, padx=3, pady=3, sticky="w")


lblR1 = tk.Label(root, text="결과 (홈URL):")
lblR1.grid(row=1, column=0, padx=3, pady=3, sticky="w")

lbl_result = tk.StringVar()
txtResult = tk.Entry(root, width=50, textvariable=lbl_result)
txtResult.grid(row=1, column=1, padx=3, pady=3)

btnHomeCopy = tk.Button(root, text="← 복사(h)", command=on_btnHomeCopy_click)
btnHomeCopy.grid(row=1, column=2, padx=3, pady=3, sticky="w")

btnRun = tk.Button(root, text="← 붙이기+실행(r)", command=on_btnRun_click)
btnRun.grid(row=1, column=3, padx=3, pady=3, sticky="w")


lblR2 = tk.Label(root, text="결과 (홈URL저장):")
lblR2.grid(row=2, column=0, padx=3, pady=3, sticky="w")

lbl_homesave = tk.StringVar()
txtHomeSave = tk.Entry(root, width=50, textvariable=lbl_homesave)
txtHomeSave.grid(row=2, column=1, padx=3, pady=3)

btnCopyHomeSave = tk.Button(root, text="← 복사(f)", command=on_btnCopyHomeSave_click)
btnCopyHomeSave.grid(row=2, column=2, padx=3, pady=3, sticky="w")

btnHomeSaveRun = tk.Button(root, text="← 붙이기+실행(s)", command=on_btnHomeSaveRun_click)
btnHomeSaveRun.grid(row=2, column=3, padx=3, pady=3, sticky="e")


lblR3 = tk.Label(root, text="결과 (전화번호):")
lblR3.grid(row=3, column=0, padx=3, pady=3, sticky="w")

lbl_telno = tk.StringVar()
txtTelno = tk.Entry(root, width=50, textvariable=lbl_telno)
txtTelno.grid(row=3, column=1, padx=3, pady=3)

btnCopyTelno = tk.Button(root, text="← 복사(t)", command=on_btnCopyTelno_click)
btnCopyTelno.grid(row=3, column=2, padx=3, pady=3, sticky="w")


btnExec = tk.Button(root, text="실 행 (e)", command=on_btnExec_click)
btnExec.grid(row=5, column=2, padx=3, pady=3, sticky="w")

lblClipboard = tk.Label(root, width=50, text="",  anchor="w")
lblClipboard.grid(row=5, column=1, padx=3, pady=3, sticky="w")


root.bind('p', lambda event: btnPaste.invoke())
root.bind('o', lambda event: btnConcat.invoke())

root.bind('e', lambda event: btnExec.invoke())
root.bind('r', lambda event: btnRun.invoke())
root.bind('s', lambda event: btnHomeSaveRun.invoke())

root.bind('h', lambda event: btnHomeCopy.invoke())
root.bind('f', lambda event: btnCopyHomeSave.invoke())
root.bind('t', lambda event: btnCopyTelno.invoke())

for i in range(1, 9):
    root.bind(str(i), lambda event, num=i: on_num_key_pressed(num))

root.after(1000, update_timer)

# 메인 루프 실행
root.mainloop()


