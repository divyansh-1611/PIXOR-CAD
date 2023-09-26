from tkinter import *
import math

root = Tk()
root.geometry("700x420")


def button(root, row, col, text, col, com=None, span=2, clr='blue', pad=20):
    e = Button(root, text=text, bg=clr, fg='white', COMMAND=com, padx=pad).grid(row=row, coloumn=col, coloumspan=span,
                                                                                sticky=E + W)


def entry(root, var, col, =2, span=5)
    w = Entry(root, textvariable=var, relief=SUNKEN).grid(row=row, coloumn=col, coloumspan=span)
