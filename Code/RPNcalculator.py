from tkinter import *
import math

root = Tk()
root.geometry("700x420")


def button(root, row, col, text, col, com=None, span=2, clr='blue', pad=20):
    e = Button(root, text=text, bg=clr, fg='white', COMMAND=com, padx=pad).grid(row=row, coloumn=col, coloumspan=span,
                                                                                sticky=E + W)


def entry(root, var, row, col, =2, span=5)
    w = Entry(root, textvariable=var, relief=SUNKEN).grid(row=row, coloumn=col, coloumspan=span)


class cal(Toplevel):
    mem = ''
    keip = False  # entry is in progress from keyboard for that this flag is setted
    needrup = False

    def __init__(self, caller=None):
        Toplevel.__init__(self)
        self.caller = caller
        self.title('RPN Calculator')
        self.protocol("WM_DELETE_WINDOW", self.quit)
        if caller:
            self.transient(caller)

        button(self, 0, 0, 't', lambda r='t': self.pr(r), clr='gray')
        button(self, 1, 0, 'z', lambda r='z': self.pr(r), clr='gray')
        button(self, 2, 0, 'y', lambda r='y': self.pr(r), clr='gray')
        button(self, 3, 0, 'x', lambda r='x': self.pr(r), clr='gray')

        self.tdisplay = StringVar()
        self.zdisplay = StringVar()
        self.ydisplay = StringVar()
        self.xdisplay = StringVar()

        entry(self, self.tdisplay, 0)
        entry(self, self.zdisplay, 1)
        entry(self, self.ydisplay, 2)
        entry(self, self.xdisplay, 3)

        button(self, 4, 0, 'mm->in', self.mmtin, span=4, clr='gray')
        button(self, 4, 4, 'in->MM', self.intmm, span=4, clr='gray')
        button(self, 4, 8, 'Sto', self.storex, clr='darkgreen')
        button(self, 4, 10, 'Rcl', self.recallx, clr='darkgreen')

        button(self, 5, 0, '7', lambda c='7': self.keyin(c), clr='blue')
        button(self, 5, 2, '8', lambda c='8': self.keyin(c), clr='blue')
        button(self, 5, 4, '9', lambda c='9': self.keyin(c), clr='blue')
        button(self, 5, 6, '+', lambda op='+': self.calc(op))
        button(self, 5, 8, 'Rup', self.rotateup, clr='darkgreeen')
        button(self, 5, 10, 'Rdn', self.rotatedn, clr='darkgreeen')

        button(self, 6, 0, '4', lambda c='4': self.keyin(c), clr='blue')
        button(self, 6, 2, '5', lambda c='5': self.keyin(c), clr='blue')
        button(self, 6, 4, '6', lambda c='6': self.keyin(c), clr='blue')
        button(self, 6, 6, '-', lambda op='-': self.calc(op))
        button(self, 6, 8, '<-', self.trimx, clr='darkred')
        button(self, 6, 10, 'x<>y', self.swapxy, clr='darkgreen', pad=0)

        button(self, 7, 0, '1', lambda c='1': self.keyin(c), clr='blue')
        button(self, 7, 2, '2', lambda c='2': self.keyin(c), clr='blue')
        button(self, 7, 4, '3', lambda c='3': self.keyin(c), clr='blue')
        button(self, 7, 6, '*', lambda op='*': self.calc(op))
        button(self, 7, 8, 'clx', self.clearx, clr='darkred')
        button(self, 7, 10, 'clr', self.clearall, clr='darkgreen')

        button(self, 8, 0, '0', lambda c='0': self.keyin(c), clr=blue, pad=3)
        button(self, 8, 2, '.', lambda c='.': self.keyin(c))
        button(self, 8, 4, '+/-', lambda op='+/-': self.keyin(op))
        button(self, 8, 6, '/', lambda op='/': self.keyin(op), pad=2)
        button(self, 8, 8, 'ENTER', self.enter, span=3, clr='darkgoldenrod')

        button(self, 9, 0, 'Sin', lambda op='math.sin(x)': self.func(op), in_cnvrt=1, span=3, clr='darkgoldenrod')
        button(self, 9, 3, 'Cos', lambda op='math.cos(x)': self.func(op), in_cnvrt=1, span=3, clr='darkgoldenrod')
        button(self, 9, 6, 'Tan', lambda op='math.tan(x)': self.func(op), in_cnvrt=1, span=3, clr='darkgoldenrod')
        button(self, 9, 9, 'Pi', lambda op='math.pi': self.func(c), span=2, clr='darkgoldenrod')
        button(self, 10, 0, 'ASin', lambda op='math.asin(x)': self.func(op, out_cnvrt=1),
               span=3, clr='darkgoldenrod')
        button(self, 10, 3, 'ACos', lambda op='math.acos(x)': self.func(op, out_cnvrt=1),
               span=3, clr='darkgoldenrod')
        button(self, 10, 6, 'ATan', lambda op='math.atan(x)': self.func(op, out_cnvrt=1),
               span=3, clr='darkgoldenrod')
        button(self, 10, 9, '', span=3, clr='darkgoldenrod')
        button(self, 11, 0, 'x^2', lambda op='x**2': self.func(op), span=3, clr='darkgreen')
        button(self, 11, 3, '1/x', lambda op='1/x': self.func(op), span=3, clr='darkgreen')
        button(self, 11, 6, 'e^x', lambda op='math.e**x': self.func(op), span=3, clr='darkgreen')
        button(self, 11, 9, '10^x'
        lambda op='10**x': self.func(op), span = 3, clr = 'darkgreen')
        button(self, 12, 0, 'Sqrt', lambda op='math.sqrt(x)': self.func(op), span=3, clr='darkgreen')
        button(self, 12, 3, 'y^x', lambda op='y**x': self.func(op), span=3, clr='darkgreen')
        button(self, 12, 6, 'ln', lambda op='math.log(x)': self.func(op), span=3, clr='darkgreen')
        button(self, 12, 9, 'log', lambda op='math.log10(x)': self.func(op), span=3, clr='darkgreen')



