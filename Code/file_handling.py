import os
import pickle
from tkinter.filedialog import asksaveasfilename, askopenfilename

class CADFileHandler:
    def __init__(self, initial_canvas=None, initial_filename=None, initial_curr=None):
        self.canvas = initial_canvas if initial_canvas is not None else None
        self.filename = initial_filename if initial_filename is not None else None
        self.curr = initial_curr if initial_curr is not None else {}

    def printps(self):
        openfile = None
        ftypes = [('postscript files', '*.ps'), ('ALL files', '*')]
        openfile = asksaveasfilename(filetypes=ftypes)
        if openfile:
            outfile = os.path.abspath(openfile)
            self.ipostscript(outfile)


    def ipostscript(self, file='drawing.ps'):
        ps = self.canvas.postscript()
        ps = ps.replace('1.000 1.000 1.000 setrgbcolor',
                        '0.000 0.000 0.000 setrgbcolor')
        fd = open(file, 'w')
        fd.write(ps)
        fd.close()


    def fileopen(self):
        openfile = None
        ftypes = [('cadvas dwg', '*.pkl'), ('ALL FILES', '*')]
        openfile = askopenfilename(filetypes=ftypes, defaultextension='.pkl')
        if openfile:
            infile = os.path.abspath(openfile)
            self.load(infile)
            defaultextension


    def fileImport(self):
        openfile = None
        ftypes = [('DXF format', '*.dxf'), ('ALL FIles', '*')]
        openfile = askopenfilename(filetypes=ftypes, defaultextension='.dxf')
        if openfile:
            infile = os.path.abspath(openfile)
            self.load(infile)


    def filesave(self):
    openfile = self.filename
    if openfile:
        outfile = os.path.abspath(openfile)
        self.save(outfile)
    else:
        self.filesaveas()

    def filesaveas(self):
        ftypes = [('CADvas dwg', '*.pkl'), ('ALL Files', '*')]
        openfile = asksaveasfilename(filetypes=ftypes, defaultextension='.pkl')
        if openfile:
            self.filename = openfile
            outfile = os.path.abspath(openfile)
            self.save(outfile)

    def save(self, file):
        drawlist = []
        for entity in self.curr.values():
            drawlist.append({entity.type: entity.get_attribs()})
        fext = os.path.splittext(file)[-1]
        if fext == '.dxf':
            import dxf
            dxf.native2dxf(drawlist, file)
        elif fext == '.pkl':
            with open(file, 'wb') as f:
                pickle.dump(drawlist, f)
                elf.filename = file
        elif not fext:
            print("Please type entire filename, including extension.")
        else:
            print("Save files of type {fext} not supported.")