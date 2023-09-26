import tkinter as tk
from tkinter import *
import Pmw

root = tk.Tk()
def __init__(self, **kw):
        optiondefs = (
            ('padx',           1,                   Pmw.INITOPT),
            ('pady',           1,                   Pmw.INITOPT),
            ('framewidth',     1,                   Pmw.INITOPT),
            ('frameheight',    1,                   Pmw.INITOPT),
            ('usecommandarea', self.usecommandarea, Pmw.INITOPT))
        self.defineoptions(kw, optiondefs)
        
        self.root = Tk()
        self.initializeTk(self.root)
        Pmw.initialise(self.root)
        self.root.title(self.appname)
        self.root.geometry('%dx%d' % (self.frameWidth, self.frameHeight))
root.title("PIXOR CAD")

menu_bar = tk.Menu(root)


# Create a file menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open File")
file_menu.add_separator()
file_menu.add_command(label="Save File")
file_menu.add_separator()
file_menu.add_command(label="Save As")
file_menu.add_separator()
file_menu.add_command(label="Import Doc")
file_menu.add_separator()
file_menu.add_command(label="Share Doc")

# Add the file menu to the menu bar
menu_bar.add_cascade(label="File", menu=file_menu)

# Create an edit menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Undo")
edit_menu.add_separator()
edit_menu.add_command(label="Redo")
edit_menu.add_separator()
edit_menu.add_command(label="Cut")
edit_menu.add_separator()
edit_menu.add_command(label="Copy")
edit_menu.add_separator()
edit_menu.add_command(label="Paste")
edit_menu.add_separator()
edit_menu.add_command(label="Cir Redo")
edit_menu.add_separator()
edit_menu.add_command(label="Cir Undo")
edit_menu.add_separator()
edit_menu.add_command(label="Insert Text")
edit_menu.add_separator()


# Add the edit menu to the menu bar
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Create a view menu
view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Create Shortcut")
view_menu.add_separator()
view_menu.add_command(label="Change Contrast")
view_menu.add_separator()
view_menu.add_command(label="Zoom In")
view_menu.add_separator()
view_menu.add_command(label="Zoom Out")
view_menu.add_separator()

# Add the view menu to the menu bar
menu_bar.add_cascade(label="View", menu=view_menu)

# Create a help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About Us")
help_menu.add_separator()
help_menu.add_command(label="Version Details")
help_menu.add_separator()


# Add the help menu to the menu bar
menu_bar.add_cascade(label="Help", menu=help_menu)

# Create a report Bugs menu
rb_menu = tk.Menu(menu_bar, tearoff=0)
rb_menu.add_command(label="About Us")

# Add the help menu to the menu bar
menu_bar.add_cascade(label="Report Bugs", menu=rb_menu)


# Set the menu bar as the window's menu
root.config(menu=menu_bar)


# Frame for Drawing area
f = Frame(root, bg="white", height=1400, width=1400)
f.place(x=200, y=40)


# Create a construction line menu
construction_line_menu = tk.Menu(menu_bar, tearoff=0)
construction_line_menu.add_command(label="Horizontal Line")
construction_line_menu.add_command(label="Vertical Line")
construction_line_menu.add_command(label="Center Line")

# Add the construction line menu to the menu bar
menu_bar.add_cascade(label="Construction Line", menu=construction_line_menu)

# Create a draw tools menu
draw_tools_menu = tk.Menu(menu_bar, tearoff=0)
draw_tools_menu.add_command(label="Line")
draw_tools_menu.add_command(label="Rectangle")
draw_tools_menu.add_command(label="Circle")

# Add the draw tools menu to the menu bar
menu_bar.add_cascade(label="Draw Tools", menu=draw_tools_menu)

# Create a poly tools menu
poly_tools_menu = tk.Menu(menu_bar, tearoff=0)
poly_tools_menu.add_command(label="Polygon")
poly_tools_menu.add_command(label="Ellipse")

# Add the poly tools menu to the menu bar
menu_bar.add_cascade(label="Poly Tools", menu=poly_tools_menu)

# Set the menu bar as the window's menu
root.config(menu=menu_bar)


root.mainloop()
