import math
import pickle
import os
from   tkinter import *
from   tkinter.filedialog import *
import main
# from   toolbarbutton import ToolBarButton
# import tkrpncalc
# import txtdialog
# import entities
import pprint
import entities


geomcolor = 'black'     # color of geometry entities
constrcolor = 'magenta' # color of construction entities
textcolor = 'cyan'      # color of text entities
dimcolor = 'red'        # color of dimension entities
rubbercolor = 'yellow'  # color of (temporary) rubber elements


#===========================================================================
# 
# Math & geometry utility functions
# 
#===========================================================================

def intersection(cline1, cline2):
    #Return intersection (x,y) of 2 clines expressed as (a,b,c) coeff.
    a,b,c = cline1
    d,e,f = cline2
    i = b*f-c*e
    j = c*d-a*f
    k = a*e-b*d
    if k:
        return (i/k, j/k)
    else:
        return None


def line_circ_inters(x1, y1, x2, y2, xc, yc, r):
    '''Return list of intersection pts of line defined by pts x1,y1 and x2,y2
    and circle (cntr xc,yc and radius r). Uses algorithm from Paul Bourke's web page.'''
    intpnts = []
    num = (xc - x1)*(x2 - x1) + (yc - y1)*(y2 - y1)
    denom = (x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1)
    if denom == 0:
        return
    u = num / denom
    xp = x1 + u*(x2-x1)
    yp = y1 + u*(y2-y1)

    a = (x2 - x1)**2 + (y2 - y1)**2
    b = 2*((x2-x1)*(x1-xc) + (y2-y1)*(y1-yc))
    c = xc**2+yc**2+x1**2+y1**2-2*(xc*x1+yc*y1)-r**2
    q = b**2 - 4*a*c
    if q == 0:
        intpnts.append((xp, yp))
    elif q:
        u1 = (-b+math.sqrt(abs(q)))/(2*a)
        u2 = (-b-math.sqrt(abs(q)))/(2*a)
        intpnts.append(((x1 + u1*(x2-x1)), (y1 + u1*(y2-y1))))
        intpnts.append(((x1 + u2*(x2-x1)), (y1 + u2*(y2-y1))))
    return intpnts

def p2p_dist(p1, p2):
    """Return the distance between two points"""
    x, y = p1
    u, v = p2
    return math.sqrt((x-u)**2 + (y-v)**2)


def same_pt_p(p1, p2):
    '''Return True if p1 and p2 are within 1e-10 of each other.'''
    if p2p_dist(p1, p2) < 1e-6:
        return True
    else:
        return False

def para_lines(cline, d):
    """Return 2 parallel lines straddling line, offset d."""
    a, b, c = cline
    c1 = math.sqrt(a**2 + b**2)*d
    cline1 = (a, b, c + c1)
    cline2 = (a, b, c - c1)
    return (cline1, cline2)

def ang_bisector(p0, p1, p2, f=0.5):
    """Return cline coefficients of line through vertex p0, factor=f
    between p1 and p2."""
    ang1 = math.atan2(p1[1]-p0[1], p1[0]-p0[0])
    ang2 = math.atan2(p2[1]-p0[1], p2[0]-p0[0])
    deltang = ang2 - ang1
    ang3 = (f * deltang + ang1)*180/math.pi
    return angled_cline(p0, ang3)

def cnvrt_2pts_to_coef(pt1, pt2):
    """Return (a,b,c) coefficients of cline defined by 2 (x,y) pts."""
    x1, y1 = pt1
    x2, y2 = pt2
    a = y2 - y1
    b = x1 - x2
    c = x2*y1-x1*y2
    return (a, b, c)

def angled_cline(pt, angle):
    """Return cline through pt at angle (degrees)"""
    ang = angle * math.pi / 180
    dx = math.cos(ang)
    dy = math.sin(ang)
    p2 = (pt[0]+dx, pt[1]+dy)
    cline = cnvrt_2pts_to_coef(pt, p2)
    return cline

def perp_line(cline, pt):
    """Return coeff of newline thru pt and perpend to cline."""
    a, b, c = cline
    x, y = pt
    cnew = a*y - b*x
    return (b, -a, cnew)

def p2p_angle(p0, p1):
    """Return angle (degrees) from p0 to p1."""
    return math.atan2(p1[1]-p0[1], p1[0]-p0[0])*180/math.pi

#=======================================================================
    # Construction
    # construction lines (clines) are "infinite" length lines
    # described by the equation:            ax + by + c = 0
    # they are defined by coefficients:     (a, b, c)
    #
    # circles are defined by coordinates:   (pc, r)
#=======================================================================

def cline_box_intrsctn(cline, box):
    """Return tuple of pts where line intersects edges of box."""
    x0, y0, x1, y1 = box
    pts = []
    segments = [((x0, y0), (x1, y0)),
                ((x1, y0), (x1, y1)),
                ((x1, y1), (x0, y1)),
                ((x0, y1), (x0, y0))]
    for seg in segments:
        pt = intersection(cline, cnvrt_2pts_to_coef(seg[0], seg[1]))
        if pt:
            if p2p_dist(pt, seg[0]) <= p2p_dist(seg[0], seg[1]) and \
               p2p_dist(pt, seg[1]) <= p2p_dist(seg[0], seg[1]):
                if pt not in pts:
                    pts.append(pt)
    return tuple(pts)

def cline_gen(self, cline, rubber=0, regen=False):
    '''Generate clines from coords (a,b,c) in ECS (mm) values.'''
        
# extend clines 500 canvas units beyond edge of canvas
    w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
    toplft = self.cp2ep((-500, -500))
    botrgt = self.cp2ep((w+500, h+500))
    trimbox = (toplft[0], toplft[1], botrgt[0], botrgt[1])
    endpts = cline_box_intrsctn(cline, trimbox)
    if len(endpts) == 2:
        p1 = self.ep2cp(endpts[0])
        p2 = self.ep2cp(endpts[1])
        if rubber:
            if self.rubber:
                self.canvas.coords(self.rubber, p1[0], p1[1], p2[0], p2[1])
            else:
                self.rubber = self.canvas.create_line(p1[0], p1[1],
                                                      p2[0], p2[1],
                                                      fill=constrcolor,
                                                      tags='r')
        else:
            if self.rubber:
                self.canvas.delete(self.rubber)
                self.rubber = None
            handle = self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                             fill=constrcolor, tags='c')
            self.canvas.tag_lower(handle)
            attribs = (cline, constrcolor)
            e = entities.CL(attribs)
            self.curr[handle] = e
            if not regen:
                self.cl_list.append(cline)

    def regen_all_cl(self, event=None):
        """Delete existing clines, remove them from self.curr, and regenerate

        This needs to be done after pan or zoom because the "infinite" length
        clines are not really infinite, they just hang off the edge a bit. So
        when zooming out, new clines need to be generated so they extend over
        the full canvas. Also, when zooming in, some clines are completely off
        the canvas, so we need a way to keep them from getting lost."""
        
        cl_keylist = [k for k, v in self.curr.items() if v.type is 'cl']
        for handle in cl_keylist:
            self.canvas.delete(handle)
            del self.curr[handle]
        for cline in self.cl_list:
            self.cline_gen(cline, regen=True)

    def hcl(self, pnt=None):
        """Create horizontal construction line from one point or y value."""

        message = 'Pick pt or enter value for horizontal constr line'
        message += self.shift_key_advice
        self.updateMessageBar(message)
        proceed = 0
        if self.pt_stack:
            p = self.pt_stack.pop()
            proceed = 1
        elif self.float_stack:
            y = self.float_stack.pop()*self.unitscale
            p = (0, y)
            proceed = 1
        elif pnt:
            p = self.cp2ep(pnt)
            cline = angled_cline(p, 0)
            self.cline_gen(cline, rubber=1)
        if proceed:
            cline = angled_cline(p, 0)
            self.cline_gen(cline)

    
    def p2p_angle(p0, p1):
        """Return angle (degrees) from p0 to p1."""
        return math.atan2(p1[1]-p0[1], p1[0]-p0[0])*180/math.pi

    def vcl(self, pnt=None):
        """Create vertical construction line from one point or x value."""

        message = 'Pick pt or enter value for vertical constr line'
        message += self.shift_key_advice
        self.updateMessageBar(message)
        proceed = 0
        if self.pt_stack:
            p = self.pt_stack.pop()
            proceed = 1
        elif self.float_stack:
            x = self.float_stack.pop()*self.unitscale
            p = (x, 0)
            proceed = 1
        elif pnt:
            p = self.cp2ep(pnt)
            cline = angled_cline(p, 90)
            self.cline_gen(cline, rubber=1)
        if proceed:
            cline = angled_cline(p, 90)
            self.cline_gen(cline)

    def hvcl(self, pnt=None):
        """Create a horizontal & vertical construction line pair at a point."""

        message = 'Pick pnt or enter coords for vertical & horizontal constr lines'
        message += self.shift_key_advice
        self.updateMessageBar(message)
        if self.pt_stack:
            p = self.pt_stack.pop()
            self.cline_gen(angled_cline(p, 0))
            self.cline_gen(angled_cline(p, 90))

    def acl(self, pnt=None):
        """Create construction line thru a point, at a specified angle."""
        
        if not self.pt_stack:
            message = 'Pick pnt for angled construction line or enter coordinates'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif self.pt_stack and self.float_stack:
            p0 = self.pt_stack[0]
            ang = self.float_stack.pop()
            cline = angled_cline(p0, ang)
            self.cline_gen(cline)
        elif len(self.pt_stack) > 1:
            p0 = self.pt_stack[0]
            p1 = self.pt_stack.pop()
            cline = cnvrt_2pts_to_coef(p0, p1)
            self.cline_gen(cline)
        elif self.pt_stack and not self.float_stack:
            message = 'Specify 2nd point or enter angle in degrees'
            message += self.shift_key_advice
            self.updateMessageBar(message)
            if pnt:
                p0 = self.pt_stack[0]
                p1 = self.cp2ep(pnt)
                ang = p2p_angle(p0, p1)
                cline = angled_cline(p0, ang)
                self.cline_gen(cline, rubber=1)

    def clrefang(self, p3=None):
        """Create a construction line at an angle relative to a reference."""
        
        if not self.pt_stack:
            message = 'Specify point for new construction line'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif not self.float_stack:
            self.updateMessageBar('Enter offset angle in degrees')
        elif len(self.pt_stack) == 1:
            message = 'Pick first point on reference line'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif len(self.pt_stack) == 2:
            message = 'Pick second point on reference line'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif len(self.pt_stack) == 3:
            p3 = self.pt_stack.pop()
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            baseangle = p2p_angle(p2, p3)
            angoffset = self.float_stack.pop()
            ang = baseangle + angoffset
            cline = angled_cline(p1, ang)
            self.cline_gen(cline)

    def abcl(self, pnt=None):
        """Create an angular bisector construction line."""
        
        if not self.float_stack and not self.pt_stack:
            message = 'Enter bisector factor (Default=.5) or specify vertex'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif not self.pt_stack:
            message = 'Specify vertex point'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif len(self.pt_stack) == 1:
            self.updateMessageBar('Specify point on base line')
        elif len(self.pt_stack) == 2:
            self.updateMessageBar('Specify second point')
            if pnt:
                f = .5
                if self.float_stack:
                    f = self.float_stack[-1]
                p2 = self.cp2ep(pnt)
                p1 = self.pt_stack[-1]
                p0 = self.pt_stack[-2]
                cline = ang_bisector(p0, p1, p2, f)
                self.cline_gen(cline, rubber=1)
        elif len(self.pt_stack) == 3:
            f = .5
            if self.float_stack:
                f = self.float_stack[-1]
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            p0 = self.pt_stack.pop()
            cline = ang_bisector(p0, p1, p2, f)
            self.cline_gen(cline)

    
    def midpoint(p1, p2, f=.5):
        """Return point part way (f=.5 by def) between points p1 and p2."""
        return (((p2[0]-p1[0])*f)+p1[0], ((p2[1]-p1[1])*f)+p1[1])

    def lbcl(self, pnt=None):
        """Create a linear bisector construction line."""
        
        if not self.pt_stack and not self.float_stack:
            message = 'Enter bisector factor (Default=.5) or specify first point'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif not self.pt_stack:
            message = 'Specify first point'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif len(self.pt_stack) == 1:
            message = 'Specify second point'
            message += self.shift_key_advice
            self.updateMessageBar(message)
            if pnt:
                f = .5
                if self.float_stack:
                    f = self.float_stack[-1]
                p2 = self.cp2ep(pnt)
                p1 = self.pt_stack[-1]
                p0 = midpoint(p1, p2, f)
                baseline = cnvrt_2pts_to_coef(p1, p2)
                newline = perp_line(baseline, p0)
                self.cline_gen(newline, rubber=1)
        elif len(self.pt_stack) == 2:
            f = .5
            if self.float_stack:
                f = self.float_stack[-1]
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            p0 = midpoint(p1, p2, f)
            baseline = cnvrt_2pts_to_coef(p1, p2)
            newline = perp_line(baseline, p0)
            self.cline_gen(newline)

    
    def perpcl(self, pnt=None):
        """Create a perpendicular cline through a selected point."""
        
        if not self.obj_stack:
            self.updateMessageBar('Pick line to be perpendicular to')
            self.set_sel_mode('items')
        else:
            message = 'Select point for perpendicular construction'
            message += self.shift_key_advice
            self.updateMessageBar(message)
            self.set_sel_mode('pnt')
            obj = self.obj_stack[0]
            if not obj:
                return
            item = obj[0]
            baseline = (0,0,0)
            if self.canvas.type(item) == 'line':
                if 'c' in self.canvas.gettags(item):
                    baseline = self.curr[item].coords
                elif 'g' in self.canvas.gettags(item):
                    p1, p2 = self.curr[item].coords
                    baseline = cnvrt_2pts_to_coef(p1, p2)
            if self.pt_stack:
                p = self.pt_stack.pop()
                newline = perp_line(baseline, p)
                self.cline_gen(newline)
                self.obj_stack.pop()
            elif pnt:
                p = self.cp2ep(pnt)
                newline = perp_line(baseline, p)
                self.cline_gen(newline, rubber=1)

    def ccirc_gen(self, cc, tag='c'):
        """Create constr circle from a CC object. Save to self.curr."""

        coords, color = cc.get_attribs()
        handle = self.circ_draw(coords, color, tag=tag)
        self.curr[handle] = cc
        self.canvas.tag_lower(handle)

    def ccirc(self, p1=None):
        '''Create a construction circle from center point and
        perimeter point or radius.'''
        
        self.circ(p1=p1, constr=1)


    #=======================================================================
    # Geometry
    # geometry line parameters are stored in GL objects.
    # geometry lines are finite length segments between 2 pts: p1, p2
    # lines are defined by coordinates:         (p1, p2)
    #
    #=======================================================================

    def line_draw(self, coords, color, arrow=None, tag='g'):
        """Create and display line segment between two pts. Return ID.

        This is a low level method that accesses the canvas directly &
        returns tkid. The caller can save to self.curr if needed."""
        
        p1, p2 = coords
        xa, ya = self.ep2cp(p1)
        xb, yb = self.ep2cp(p2)
        tkid = self.canvas.create_line(xa, ya, xb, yb,
                                       fill=color, tags=tag, arrow=arrow)
        return tkid

def line(self, p1=None):
        '''Create line segment between 2 points. Enable 'rubber line' mode'''
        
        rc = rubbercolor
        if not self.pt_stack:
            message = 'Pick start point of line or enter coords'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif self.pt_stack and p1:
            p0 = self.pt_stack[-1]
            x, y = self.ep2cp(p0)   # fixed first point (canvas coords)
            xr, yr = p1             # rubber point (canvas coords)
            x0, y0 = p0             # fixed first point (ECS)
            x1, y1 = self.cp2ep(p1) # rubber point (ECS)
            strcoords = "(%1.3f, %1.3f)" % ((x1-x0)/self.unitscale,
                                            (y1-y0)/self.unitscale)
            if self.rubber:
                self.canvas.coords(self.rubber, x, y, xr, yr)
            else:
                self.rubber = self.canvas.create_line(x, y, xr, yr,
                                                      fill=rc, tags='r')
            if self.rtext:
                self.canvas.delete(self.rtext)
            self.rtext = self.canvas.create_text(xr+20, yr-20,
                                                 text=strcoords,
                                                 fill=textcolor)
            self.updateMessageBar('Specify end point of line')
        elif len(self.pt_stack) > 1:
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            coords = (p1, p2)
            attribs = (coords, geomcolor)
            e = entities.GL(attribs)
            self.gline_gen(e)
            if self.rubber:
                self.canvas.delete(self.rubber)
                self.rubber = None
            if self.rtext:
                self.canvas.delete(self.rtext)
                self.rtext = None


class Draw(main.app_ui):
    """A 2D CAD application using the Tkinter canvas. The canvas is wrapped
    by 'Zooming', (slightly modified) which adds a 'world' coordinate system
    and smooth, mouse controlled zoom (ctrl-RMB) and pan (ctrl-LMB).
    The framework for the application inherits from John Grayson's AppShell
    PMW megawidget, modified slightly. 

    Here's how it works:
    All CAD operations are initiated through a dispatch method, which after
    first initalizing things, and saving the name of the operation as self.op,
    then calls the method (whose name is saved in self.op). Within the
    operation method, the selection mode is set, determining what types of
    data (points or canvas items) are needed from the user and an appropriate
    message prompt is displayed at the bottom of the application window.
    The user then follows the instructions of the message prompt, and clicks
    the mouse on the screen, or enters data using the keyboard or calculator.
    Event handlers detect user input, save the data onto the appropriate
    stack (point_stack, float_stack, or object_stack) and then call the
    'self.op' method again. Some operations may allow items to be "box
    selected" or assembled into a list. If an operation allows a list of
    items to be selected, the RMB popup menu will include 2 additional
    buttons: "Start list" and "End list".
    If the operation wants to show a hypothetical result, such as a 'rubber
    line', the mouse_motion event passes a screen coordinate to the method as
    an argument. When all the needed data have been entered and stored in
    the appropriate stack, the method pops the data off the stacks and
    completes the operation. When the user wants to quit the current
    operation, he can click the MMB (which calls the end() method), or he
    can just click on another operation, (which causes the dispatch method
    to run again, which in turn calls the end() method as part of the
    initialization sequence).

    3 Coordinate systems:
    The tk Canvas has its own Coordinate System (CCS) with 0,0 in the top left
    corner and increasing Y values going down. In order to facilitate zooming
    and panning, the canvas is wrapped by 'Zooming', which introduces a World
    Coordinate System (WCS) which has the benefit of remaining invariant in
    size, but is still inverted, like the CCS. For CAD, it is conventional
    to work in an environment where positive Y values go up. Therefore,
    an Engineering Coordinate System (ECS) is introduced, which is an X-axis
    reflection of the WCS. The ECS has a 1:1 relation to the CAD  model
    (in millimeters). Wherever possible, calculations are done in ECS,
    converting to or from canvas units as needed. Working in the WCS is
    discouraged, because the negative Y-values and negative angles can cause
    a lot of confusion, especially when calculating angles.
    
    Keeping track of items on the canvas:
    Drawing entities of various types, such as construction lines, geometry
    lines, circles, etc are encapsulated in entity objects which save their
    types, coordinates, etc as attributes. These objects are stored as values
    in a dictionary, accessible by a unique key (integer) which has been
    assigned by the tk canvas. A single dictionary contains all the drawing
    entities in the current display.
    
    File save/load:
    For the purpose of being able to save and load the current display to file,
    these entity objects are disassembled and saved as individual dictionaries
    of exactly one key/value pair. The key is the entity type and the value is
    a tuple containing all the other attributes of the entity.
    When it comes time to reload the data, the original objects are first
    reassembled (the key determines the type of entity object to create and the
    tuple of attributes is supplied as the argument), then the new objects are
    submitted to type-specific generator methods which display them on the
    canvas and use the canvas generated handle to rebuild the dictionary of
    displayed entities. 

    Calculator:
    An RPN calculator can be launched by running many of the "Measure"
    functions. When measurements are made, values are sent to the x-register
    of the calculator. Also, if an operation is prompting the user to enter a
    float value, the buttons to the left of the calculator registers will send
    the associated value to the CAD operation."""
    #=======================================================================
    # Functions for converting between canvas CS and engineering CS
    #=======================================================================

    def ep2cp(self, pt):
        """Convert pt from ECS to CCS."""
        return self.canvas.world2canvas(pt[0], -pt[1])

    def cp2ep(self, pt):
        """Convert pt from CCS to ECS."""
        x, y = self.canvas.canvas2world(pt[0], pt[1])
        return (x, -y)

    #=======================================================================
    # File, View, Units and Measure commands
    #=======================================================================

    def printps(self):
        openfile = None
        ftypes = [('PostScript file', '*.ps'),
                  ('All files', '*')]
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

    def fileOpen(self):
        openfile = None
        ftypes = [('CADvas dwg', '*.pkl'),
                  ('All files', '*')]
        openfile = askopenfilename(filetypes=ftypes,
                                   defaultextension='.pkl')
        if openfile:
            infile = os.path.abspath(openfile)
            self.load(infile)

    def fileImport(self):
        openfile = None
        ftypes = [('DXF format', '*.dxf'),
                  ('All files', '*')]
        openfile = askopenfilename(filetypes=ftypes,
                                   defaultextension='.dxf')
        if openfile:
            infile = os.path.abspath(openfile)
            self.load(infile)

    def fileSave(self):
        openfile = self.filename
        if openfile:
            outfile = os.path.abspath(openfile)
            self.save(outfile)
        else:
            self.fileSaveas()

    def fileSaveas(self):
        ftypes = [('CADvas dwg', '*.pkl'),
                  ('All files', '*')]
        openfile = asksaveasfilename(filetypes=ftypes,
                                     defaultextension='.pkl')
        if openfile:
            self.filename = openfile
            outfile = os.path.abspath(openfile)
            self.save(outfile)

    def fileExport(self):
        ftypes = [('DXF format', '*.dxf'),
                  ('All files', '*')]
        openfile = asksaveasfilename(filetypes=ftypes,
                                     defaultextension='.dxf')
        if openfile:
            outfile = os.path.abspath(openfile)
            self.save(outfile)

    def save(self, file):

        drawlist = []
        for entity in self.curr.values():
            drawlist.append({entity.type: entity.get_attribs()})

        fext = os.path.splitext(file)[-1]
        if fext == '.dxf':
            import dxf
            dxf.native2dxf(drawlist, file)
        elif fext == '.pkl':
            with open(file, 'wb') as f:
                pickle.dump(drawlist, f)
            self.filename = file
        elif not fext:
            print("Please type entire filename, including extension.")
        else:
            print("Save files of type {fext} not supported.")

    def load(self, file):
        """Load CAD data from file.

        Data is saved/loaded as a list of dicts, one dict for each
        drawing entity, {key=entity_type: val=entity_attribs} """
        
        fext = os.path.splitext(file)[-1]
        if fext == '.dxf':
            import dxf
            drawlist = dxf.dxf2native(file)
        elif fext == '.pkl':
            with open(file, 'rb') as f:
                drawlist = pickle.load(f)
            self.filename = file
        else:
            print("Load files of type {fext} not supported.")
        for ent_dict in drawlist:
            if 'cl' in ent_dict:
                attribs = ent_dict['cl']
                e = entities.CL(attribs)
                self.cline_gen(e.coords)  # This method takes coords
            elif 'cc' in ent_dict:
                attribs = ent_dict['cc']
                e = entities.CC(attribs)
                self.cline_gen(e)
            elif 'gl' in ent_dict:
                attribs = ent_dict['gl']
                e = entities.GL(attribs)
                self.gline_gen(e)
            elif 'gc' in ent_dict:
                attribs = ent_dict['gc']
                e = entities.GC(attribs)
                self.gcirc_gen(e)
            elif 'ga' in ent_dict:
                attribs = ent_dict['ga']
                e = entities.GA(attribs)
                self.garc_gen(e)
            elif 'dl' in ent_dict:
                attribs = ent_dict['dl']
                e = entities.DL(attribs)
                self.dim_gen(e)
            elif 'tx' in ent_dict:
                attribs = ent_dict['tx']
                print(attribs)
                e = entities.TX(attribs)
                self.text_gen(e)
        self.view_fit()
        self.save_delta()  # undo/redo thing

    def close(self):
        self.quit()

    def view_fit(self):
        bbox = self.canvas.bbox('g', 'd', 't')
        if bbox:
            xsize, ysize = bbox[2]-bbox[0], bbox[3]-bbox[1]
            xc, yc = (bbox[2]+bbox[0])/2, (bbox[3]+bbox[1])/2
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            self.canvas.move_can(w/2-xc, h/2-yc)
            wm, hm = .9 * w, .9 * h
            xscale, yscale = wm/float(xsize), hm/float(ysize)
            if xscale > yscale:
                scale = yscale
            else:
                scale = xscale
            self.canvas.scale(w/2, h/2, scale, scale)
            self.regen()

    def regen(self, event=None):
        self.regen_all_cl()
        #self.regen_all_dims()
        self.regen_all_text()

    def set_units(self, units):
        if units in self.unit_dict.keys():
            self.units = units
            self.unitscale = self.unit_dict.get(units)
            self.unitsDisplay.configure(text="Units: %s" % self.units)
            self.regen_all_dims()

    def meas_dist(self, obj=None):
        """Measure distance between 2 points."""
        self.op = 'meas_dist'
        if not self.pt_stack:
            self.updateMessageBar('Pick 1st point for distance measurement.')
            self.set_sel_mode('pnt')
        elif len(self.pt_stack) == 1:
            self.updateMessageBar('Pick 2nd point for distance measurement.')
        elif len(self.pt_stack) > 1:
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            dist = p2p_dist(p1, p2)/self.unitscale
            self.updateMessageBar('%s %s'%(dist, self.units))
            self.launch_calc()
            self.calculator.putx(dist)

    def itemcoords(self, obj=None):
        """Print coordinates (in ECS) of selected element."""
        if not self.obj_stack:
            self.updateMessageBar('Pick element from drawing.')
            self.set_sel_mode('items')
        elif self.obj_stack:
            elem = self.obj_stack.pop()
            if 'g' in self.canvas.gettags(elem):
                x1, y1, x2, y2 = self.canvas.coords(elem)
                print(self.cp2ep((x1, y1)), self.cp2ep((x2, y2)))
            else:
                print("This works only for 'geometry type' elements")

    def itemlength(self, obj=None):
        """Print length (in current units) of selected line, circle, or arc."""
        if not self.obj_stack:
            self.updateMessageBar('Pick element from drawing.')
            self.set_sel_mode('items')
        elif self.obj_stack:
            elem = None
            for item in self.obj_stack.pop():
                if 'g' in self.canvas.gettags(item):
                    elem = self.curr[item]
            length = 0
            if elem:
                if elem.type is 'gl':
                    p1, p2 = elem.coords
                    length = p2p_dist(p1, p2) / self.unitscale
                elif elem.type is 'gc':
                    length = math.pi*2*elem.coords[1]/self.unitscale
                elif elem.type is 'cc':
                    length = math.pi*2*elem.coords[1]/self.unitscale
                elif elem.type is 'ga':
                    pc, r, a0, a1 = elem.coords
                    ang = float(self.canvas.itemcget(item, 'extent'))
                    length = math.pi*r*ang/180/self.unitscale
                if length:
                    self.launch_calc()
                    self.calculator.putx(length)


    #=======================================================================
    # GUI configuration
    #=======================================================================
 
    def createBase(self):
        self.toolbar = self.createcomponent('toolbar', (), None,
                  Frame, (self.interior(),), background="gray80")
        self.toolbar.pack(fill=X)

        self.canvas = self.createcomponent('canvas', (), None,
                  Zooming, (self.interior(),), background="black")
        self.canvas.pack(side=LEFT, expand=YES, fill=BOTH)
        self.canvas.panbindings()
        self.canvas.zoombindings()
        Widget.bind(self.canvas, "<Motion>", self.mouseMove)
        Widget.bind(self.canvas, "<Button-1>", self.lftClick)
        Widget.bind(self.canvas, "<Button-2>", self.midClick)
        Widget.bind(self.canvas, "<Button-3>", self.rgtClick)
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)
        self.root.bind("<Key>", self.setCC)
        self.root.bind("<KeyRelease>", self.setCC)
        self.root.bind("<Control-B1-ButtonRelease>", self.regen_all_cl)
        self.root.bind("<Control-B3-ButtonRelease>", self.regen)

    def createMenus(self):
        self.menuBar.deletemenuitems('File', 0)
        self.menuBar.addmenuitem('File', 'command', 'Print drawing',
                                 label='Print', command=self.printps)
        self.menuBar.addmenuitem('File', 'command', 'Open drawing',
                                 label='Open...', command=self.fileOpen)
        self.menuBar.addmenuitem('File', 'command', 'Save drawing',
                                 label='Save', command=self.fileSave)
        self.menuBar.addmenuitem('File', 'command', 'Save drawing',
                                 label='SaveAs...', command=self.fileSaveas)
        self.menuBar.addmenuitem('File', 'command', 'Import DXF',
                                 label='Import DXF', command=self.fileImport)
        self.menuBar.addmenuitem('File', 'command', 'Export DXF',
                                 label='Export DXF', command=self.fileExport)
        self.menuBar.addmenuitem('File', 'separator')
        self.menuBar.addmenuitem('File', 'command', 'Exit program',
                                 label='Exit', command=self.quit)
        self.menuBar.addmenu('Edit', 'Undo / Redo')
        self.menuBar.addmenuitem('Edit', 'command', 'Undo',
                                 label='Undo (Ctrl+Z)', command=self.undo)
        self.menuBar.addmenuitem('Edit', 'command', 'Redo',
                                 label='Redo (Ctrl+Y)', command=self.redo)
        self.menuBar.addmenuitem('Edit', 'command', 'Clear Redo',
                                 label='Clr Redo', command=self.clear_redo)
        self.menuBar.addmenuitem('Edit', 'command', 'Clear Undo',
                                 label='Clr Undo', command=self.clear_undo)
        self.menuBar.addmenu('View', 'View commands')
        self.menuBar.addmenuitem('View', 'command', 'Fit geometry to screen',
                                 label='Fit', command=self.view_fit)
        self.menuBar.addmenu('Units', 'Switch units')
        self.menuBar.addmenuitem('Units', 'command', 'Set units=mm',
                                 label='mm',
                                 command=lambda k='mm': self.set_units(k))
        self.menuBar.addmenuitem('Units', 'command', 'Set units=cm',
                                 label='cm',
                                 command=lambda k='cm': self.set_units(k))
        self.menuBar.addmenuitem('Units', 'command', 'Set units=inches',
                                 label='inches',
                                 command=lambda k='inches': self.set_units(k))
        self.menuBar.addmenuitem('Units', 'command', 'Set units=feet',
                                 label='feet',
                                 command=lambda k='feet': self.set_units(k))
        self.menuBar.addmenu('Measure', 'Measure')
        self.menuBar.addmenuitem('Measure', 'command', 'measure distance',
                                 label='pt-pt distance', command=self.meas_dist)
        self.menuBar.addmenuitem('Measure', 'command', 'print item coords',
                                 label='item coords',
                                 command=lambda k='itemcoords':self.dispatch(k))
        self.menuBar.addmenuitem('Measure', 'command', 'print item length',
                                 label='item length',
                                 command=lambda k='itemlength':self.dispatch(k))
        self.menuBar.addmenuitem('Measure', 'command', 'launch calculator',
                                 label='calculator',
                                 command=self.launch_calc)
        self.menuBar.addmenu('Dimension', 'Dimensions')
        self.menuBar.addmenuitem('Dimension', 'command', 'Horizontal dimension',
                                 label='Dim Horizontal',
                                 command=lambda k='dim_h':self.dispatch(k))
        self.menuBar.addmenuitem('Dimension', 'command', 'Vertical dimension',
                                 label='Dim Vertical',
                                 command=lambda k='dim_v':self.dispatch(k))
        self.menuBar.addmenuitem('Dimension', 'command', 'Parallel dimension',
                                 label='Dim Parallel',
                                 command=lambda k='dim_par':self.dispatch(k))
        self.menuBar.addmenu('Text', 'Text')
        self.menuBar.addmenuitem('Text', 'command', 'Enter text',
                                 label='Create text',
                                 command=lambda k='text_enter':self.dispatch(k))
        self.menuBar.addmenuitem('Text', 'command', 'Move text',
                                 label='Move text',
                                 command=lambda k='text_move':self.dispatch(k))
        self.menuBar.addmenuitem('Text', 'command', 'Edit Text',
                                 label='Edit text',
                                 command=self.txt_params)
        self.menuBar.addmenu('Delete', 'Delete drawing elements')
        self.menuBar.addmenuitem('Delete', 'command',
                                 'Delete individual element',
                                 label='Del Element',
                                 command=lambda k='del_el':self.dispatch(k))
        self.menuBar.addmenuitem('Delete', 'separator')
        self.menuBar.addmenuitem('Delete', 'command', 'Delete all construct',
                                 label='All Cons', command=self.del_all_c)
        self.menuBar.addmenuitem('Delete', 'command', 'Delete all geometry',
                                 label='All Geom', command=self.del_all_g)
        self.menuBar.addmenuitem('Delete', 'command', 'Delete all dimensions',
                                 label='All Dims', command=self.del_all_d)
        self.menuBar.addmenuitem('Delete', 'command', 'Delete all text',
                                 label='All Text', command=self.del_all_t)
        self.menuBar.addmenuitem('Delete', 'separator')
        self.menuBar.addmenuitem('Delete', 'command', 'Delete all',
                                 label='Delete All', command=self.del_all)
        self.menuBar.addmenu('Debug', 'Debug')
        self.menuBar.addmenuitem('Debug', 'command', 'Show self.op',
                                 label='Show self.op',
                                 command=self.show_op)
        self.menuBar.addmenuitem('Debug', 'command', 'Show Curr',
                                 label='Show Curr',
                                 command=lambda k='show_curr':self.dispatch(k))
        self.menuBar.addmenuitem('Debug', 'command', 'Show Prev',
                                 label='Show Prev',
                                 command=lambda k='show_prev':self.dispatch(k))
        self.menuBar.addmenuitem('Debug', 'command', 'Show Undo',
                                 label='Show Undo',
                                 command=lambda k='show_undo':self.dispatch(k))
        self.menuBar.addmenuitem('Debug', 'command', 'Show Redo',
                                 label='Show Redo',
                                 command=lambda k='show_redo':self.dispatch(k))
        self.menuBar.addmenuitem('Debug', 'command', 'Show ZoomScale',
                                 label='Show Zoom Scale',
                                 command=lambda k='show_zoomscale':self.dispatch(k))
        
    def dispatch(self, key):
        """Dispatch commands initiated by menubar & toolbar buttons."""
        self.end()
        self.set_sel_mode('pnt')
        self.op = key
        func = 'self.%s()' % self.op
        eval(func)
        self.entry.focus()

    def set_sel_mode(self, mode=''):
        '''Set selection mode and cursor style.
        Selection mode should be controlled by current operation
        in order to determine what is returned from screen picks.'''
        cursordict = {''    :   'top_left_arrow',
                      'pnt' :   'crosshair',
                      'items':  'right_ptr',
                      'list':   'right_ptr'}
        if mode in cursordict.keys():
            self.sel_mode = mode
            self.canvas.config(cursor=cursordict[mode])

    def createInterface(self):
        main.app_ui.createInterface(self)
        self.createMenus()
        self.createBase()
        self.createTools()
        self.canvas.move_can(60,420)    # Put 0,0 near lower left corner

    #=======================================================================
    # Debug Tools
    #=======================================================================

    def show_op(self):
        print(self.op)

    def show_curr(self):
        pprint.pprint(self.curr)
        self.end()

    def show_prev(self):
        pprint.pprint(self.prev)
        self.end()

    def show_undo(self):
        pprint.pprint(self.undo_stack)
        self.end()
        
    def show_redo(self):
        pprint.pprint(self.redo_stack)
        self.end()

    def show_zoomscale(self):
        zoom_scale = self.canvas.scl.x
        pprint.pprint(zoom_scale)
        self.end()

    #=======================================================================
    # Construction
    # construction lines (clines) are "infinite" length lines
    # described by the equation:            ax + by + c = 0
    # they are defined by coefficients:     (a, b, c)
    #
    # circles are defined by coordinates:   (pc, r)
    #=======================================================================

    def cline_gen(self, cline, rubber=0, regen=False):
        '''Generate clines from coords (a,b,c) in ECS (mm) values.'''
        
        # extend clines 500 canvas units beyond edge of canvas
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        toplft = self.cp2ep((-500, -500))
        botrgt = self.cp2ep((w+500, h+500))
        trimbox = (toplft[0], toplft[1], botrgt[0], botrgt[1])
        endpts = cline_box_intrsctn(cline, trimbox)
        if len(endpts) == 2:
            p1 = self.ep2cp(endpts[0])
            p2 = self.ep2cp(endpts[1])
            if rubber:
                if self.rubber:
                    self.canvas.coords(self.rubber, p1[0], p1[1], p2[0], p2[1])
                else:
                    self.rubber = self.canvas.create_line(p1[0], p1[1],
                                                          p2[0], p2[1],
                                                          fill=constrcolor,
                                                          tags='r')
            else:
                if self.rubber:
                    self.canvas.delete(self.rubber)
                    self.rubber = None
                handle = self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                                 fill=constrcolor, tags='c')
                self.canvas.tag_lower(handle)
                attribs = (cline, constrcolor)
                e = entities.CL(attribs)
                self.curr[handle] = e
                if not regen:
                    self.cl_list.append(cline)

    def regen_all_cl(self, event=None):
        """Delete existing clines, remove them from self.curr, and regenerate

        This needs to be done after pan or zoom because the "infinite" length
        clines are not really infinite, they just hang off the edge a bit. So
        when zooming out, new clines need to be generated so they extend over
        the full canvas. Also, when zooming in, some clines are completely off
        the canvas, so we need a way to keep them from getting lost."""
        
        cl_keylist = [k for k, v in self.curr.items() if v.type is 'cl']
        for handle in cl_keylist:
            self.canvas.delete(handle)
            del self.curr[handle]
        for cline in self.cl_list:
            self.cline_gen(cline, regen=True)

    def hcl(self, pnt=None):
        """Create horizontal construction line from one point or y value."""

        message = 'Pick pt or enter value for horizontal constr line'
        message += self.shift_key_advice
        self.updateMessageBar(message)
        proceed = 0
        if self.pt_stack:
            p = self.pt_stack.pop()
            proceed = 1
        elif self.float_stack:
            y = self.float_stack.pop()*self.unitscale
            p = (0, y)
            proceed = 1
        elif pnt:
            p = self.cp2ep(pnt)
            cline = angled_cline(p, 0)
            self.cline_gen(cline, rubber=1)
        if proceed:
            cline = angled_cline(p, 0)
            self.cline_gen(cline)

    def vcl(self, pnt=None):
        """Create vertical construction line from one point or x value."""

        message = 'Pick pt or enter value for vertical constr line'
        message += self.shift_key_advice
        self.updateMessageBar(message)
        proceed = 0
        if self.pt_stack:
            p = self.pt_stack.pop()
            proceed = 1
        elif self.float_stack:
            x = self.float_stack.pop()*self.unitscale
            p = (x, 0)
            proceed = 1
        elif pnt:
            p = self.cp2ep(pnt)
            cline = angled_cline(p, 90)
            self.cline_gen(cline, rubber=1)
        if proceed:
            cline = angled_cline(p, 90)
            self.cline_gen(cline)

    def hvcl(self, pnt=None):
        """Create a horizontal & vertical construction line pair at a point."""

        message = 'Pick pnt or enter coords for vertical & horizontal constr lines'
        message += self.shift_key_advice
        self.updateMessageBar(message)
        if self.pt_stack:
            p = self.pt_stack.pop()
            self.cline_gen(angled_cline(p, 0))
            self.cline_gen(angled_cline(p, 90))


    def clrefang(self, p3=None):
        """Create a construction line at an angle relative to a reference."""
        
        if not self.pt_stack:
            message = 'Specify point for new construction line'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif not self.float_stack:
            self.updateMessageBar('Enter offset angle in degrees')
        elif len(self.pt_stack) == 1:
            message = 'Pick first point on reference line'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif len(self.pt_stack) == 2:
            message = 'Pick second point on reference line'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif len(self.pt_stack) == 3:
            p3 = self.pt_stack.pop()
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            baseangle = (p2, p3)
            angoffset = self.float_stack.pop()
            ang = baseangle + angoffset
            cline = angled_cline(p1, ang)
            self.cline_gen(cline)

    def abcl(self, pnt=None):
        """Create an angular bisector construction line."""
        
        if not self.float_stack and not self.pt_stack:
            message = 'Enter bisector factor (Default=.5) or specify vertex'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif not self.pt_stack:
            message = 'Specify vertex point'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif len(self.pt_stack) == 1:
            self.updateMessageBar('Specify point on base line')
        elif len(self.pt_stack) == 2:
            self.updateMessageBar('Specify second point')
            if pnt:
                f = .5
                if self.float_stack:
                    f = self.float_stack[-1]
                p2 = self.cp2ep(pnt)
                p1 = self.pt_stack[-1]
                p0 = self.pt_stack[-2]
                cline = ang_bisector(p0, p1, p2, f)
                self.cline_gen(cline, rubber=1)
        elif len(self.pt_stack) == 3:
            f = .5
            if self.float_stack:
                f = self.float_stack[-1]
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            p0 = self.pt_stack.pop()
            cline = ang_bisector(p0, p1, p2, f)
            self.cline_gen(cline)

    def perpcl(self, pnt=None):
        """Create a perpendicular cline through a selected point."""
        
        if not self.obj_stack:
            self.updateMessageBar('Pick line to be perpendicular to')
            self.set_sel_mode('items')
        else:
            message = 'Select point for perpendicular construction'
            message += self.shift_key_advice
            self.updateMessageBar(message)
            self.set_sel_mode('pnt')
            obj = self.obj_stack[0]
            if not obj:
                return
            item = obj[0]
            baseline = (0,0,0)
            if self.canvas.type(item) == 'line':
                if 'c' in self.canvas.gettags(item):
                    baseline = self.curr[item].coords
                elif 'g' in self.canvas.gettags(item):
                    p1, p2 = self.curr[item].coords
                    baseline = cnvrt_2pts_to_coef(p1, p2)
            if self.pt_stack:
                p = self.pt_stack.pop()
                newline = perp_line(baseline, p)
                self.cline_gen(newline)
                self.obj_stack.pop()
            elif pnt:
                p = self.cp2ep(pnt)
                newline = perp_line(baseline, p)
                self.cline_gen(newline, rubber=1)

    def ccirc_gen(self, cc, tag='c'):
        """Create constr circle from a CC object. Save to self.curr."""

        coords, color = cc.get_attribs()
        handle = self.circ_draw(coords, color, tag=tag)
        self.curr[handle] = cc
        self.canvas.tag_lower(handle)

    def ccirc(self, p1=None):
        '''Create a construction circle from center point and
        perimeter point or radius.'''
        
        self.circ(p1=p1, constr=1)

    def cccirc(self, p1=None):
        '''Create a construction circle concentric to an existing circle,
        at a "relative" radius.'''
        
        if not self.obj_stack:
            self.set_sel_mode('items')
            self.updateMessageBar('Select existing circle')
        elif self.obj_stack and not (self.float_stack or self.pt_stack):
            item = self.obj_stack[0][0]
            self.coords = None
            if self.curr[item].type in ('cc', 'gc'):
                self.coords = self.curr[item].coords
            self.set_sel_mode('pnt')
            self.updateMessageBar(
                'Enter relative radius or specify point on new circle')
            if self.coords and p1:
                pc, r0 = self.coords
                ep = self.cp2ep(p1)
                r = p2p_dist(pc, ep)
                self.circ_builder((pc, r), rubber=1)
        elif self.coords and self.float_stack:
            pc, r0 = self.coords
            self.obj_stack.pop()
            r = self.float_stack.pop()*self.unitscale + r0
            self.circ_builder((pc, r), constr=1)
        elif self.coords and self.pt_stack:
            pc, r0 = self.coords
            self.obj_stack.pop()
            p = self.pt_stack.pop()
            r = p2p_dist(pc, p)
            self.circ_builder((pc, r), constr=1)

    """    def cc3p(self, p3=None):
        #Create a constr circle from 3 pts on circle.
        
        if not self.pt_stack:
            self.updateMessageBar('Pick first point on circle')
        elif len(self.pt_stack) == 1:
            self.updateMessageBar('Pick second point on circle')
        elif len(self.pt_stack) == 2:
            self.updateMessageBar('Pick third point on circle')
            if p3:
                p3 = self.cp2ep(p3)
                p2 = self.pt_stack[1]
                p1 = self.pt_stack[0]
                tuple = cr_from_3p(p1, p2, p3)
                if tuple:
                    pc, r = tuple
                    self.circ_builder((pc, r,), rubber=1)
        elif len(self.pt_stack) == 3:
            p3 = self.pt_stack.pop()
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            pc, r = cr_from_3p(p1, p2, p3)
            self.circ_builder((pc, r), constr=1)"""

    #=======================================================================
    # Geometry
    # geometry line parameters are stored in GL objects.
    # geometry lines are finite length segments between 2 pts: p1, p2
    # lines are defined by coordinates:         (p1, p2)
    #
    #=======================================================================

    def line_draw(self, coords, color, arrow=None, tag='g'):
        """Create and display line segment between two pts. Return ID.

        This is a low level method that accesses the canvas directly &
        returns tkid. The caller can save to self.curr if needed."""
        
        p1, p2 = coords
        xa, ya = self.ep2cp(p1)
        xb, yb = self.ep2cp(p2)
        tkid = self.canvas.create_line(xa, ya, xb, yb,
                                       fill=color, tags=tag, arrow=arrow)
        return tkid

    def gline_gen(self, gl):
        """Create line segment from gl object. Store {ID: obj} in self.curr.

        This provides access to line_gen using a gl object."""

        coords, color = gl.get_attribs()
        tkid = self.line_draw(coords, color)
        self.curr[tkid] = gl
        
    def line(self, p1=None):
        '''Create line segment between 2 points. Enable 'rubber line' mode'''
        
        rc = rubbercolor
        if not self.pt_stack:
            message = 'Pick start point of line or enter coords'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif self.pt_stack and p1:
            p0 = self.pt_stack[-1]
            x, y = self.ep2cp(p0)   # fixed first point (canvas coords)
            xr, yr = p1             # rubber point (canvas coords)
            x0, y0 = p0             # fixed first point (ECS)
            x1, y1 = self.cp2ep(p1) # rubber point (ECS)
            strcoords = "(%1.3f, %1.3f)" % ((x1-x0)/self.unitscale,
                                            (y1-y0)/self.unitscale)
            if self.rubber:
                self.canvas.coords(self.rubber, x, y, xr, yr)
            else:
                self.rubber = self.canvas.create_line(x, y, xr, yr,
                                                      fill=rc, tags='r')
            if self.rtext:
                self.canvas.delete(self.rtext)
            self.rtext = self.canvas.create_text(xr+20, yr-20,
                                                 text=strcoords,
                                                 fill=textcolor)
            self.updateMessageBar('Specify end point of line')
        elif len(self.pt_stack) > 1:
            p2 = self.pt_stack.pop()
            p1 = self.pt_stack.pop()
            coords = (p1, p2)
            attribs = (coords, geomcolor)
            e = entities.GL(attribs)
            self.gline_gen(e)
            if self.rubber:
                self.canvas.delete(self.rubber)
                self.rubber = None
            if self.rtext:
                self.canvas.delete(self.rtext)
                self.rtext = None

    def poly(self, p1=None):
        '''Create chain of line segments, enabling 'rubber line' mode.'''
        
        if not self.pt_stack:
            self.poly_start_pt = None
            message = 'Pick start point or enter coords'
            message += self.shift_key_advice
            self.updateMessageBar(message)
        elif self.pt_stack and p1:
            if not self.poly_start_pt:
                self.poly_start_pt = self.pt_stack[-1]
            self.line(p1)   # This will generate rubber line
            self.updateMessageBar('Pick next point or enter coords')
        elif len(self.pt_stack) > 1:
            lastpt = self.pt_stack[-1]
            self.line()     # This will pop 2 points off stack
            if not same_pt_p(self.poly_start_pt, lastpt):
                self.pt_stack.append(lastpt)
    
    def rect(self, p2=None):
        '''Generate a rectangle from 2 diagonally opposite corners.'''
        
        rc = rubbercolor
        if not self.pt_stack:
            self.updateMessageBar(
                'Pick first corner of rectangle or enter coords')
        elif len(self.pt_stack) == 1 and p2:
            self.updateMessageBar(
                'Pick opposite corner of rectangle or enter coords')
            p1 = self.pt_stack[0]
            x1, y1 = self.ep2cp(p1)
            x2, y2 = p2
            if self.rubber:
                self.canvas.coords(self.rubber, x1, y1, x2, y2)
            else:
                self.rubber = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                           outline=rc,
                                                           tags='r')
        elif len(self.pt_stack) > 1:
            x2, y2 = self.pt_stack.pop()
            x1, y1 = self.pt_stack.pop()
            a = (x1, y1)
            b = (x2, y1)
            c = (x2, y2)
            d = (x1, y2)
            sides = ((a, b), (b, c), (c, d), (d, a))
            for p in sides:
                coords = (p[0], p[1])
                attribs = (coords, geomcolor)
                e = entities.GL(attribs)
                self.gline_gen(e)
            if self.rubber:
                self.canvas.delete(self.rubber)
                self.rubber = None

    #=======================================================================
    # geometry circle parameters are stored in GC objects.
    # circles are defined by coordinates:       (pc, r)
    #=======================================================================

    def circ_draw(self, coords, color, tag):
        """Draw a circle on the canvas and return the tkid handle.

        This low level method accesses the canvas directly & returns tkid.
        The caller should save handle & entity_obj to self.curr if needed."""

        ctr, rad = coords
        x, y = self.ep2cp(ctr)
        r = self.canvas.w2c_dx(rad)
        handle = self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                         outline=color,
                                         tags=tag)
        return handle

    def gcirc_gen(self, gc, tag='g'):
        """Create geometry circle from a GC object. Save to self.curr."""

        coords, color = gc.get_attribs()
        handle = self.circ_draw(coords, color, tag=tag)
        self.curr[handle] = gc

    def circ_builder(self, coords, rubber=0, constr=0):
        """Create circle at center pc, radius r in engineering (mm) coords.

        Handle rubber circles, construction, and geom circles."""
        
        ctr, rad = coords       # ECS
        x, y = self.ep2cp(ctr)
        r = self.canvas.w2c_dx(rad)
        if rubber:
            color = rubbercolor
            tag = 'r'
            if self.rubber:
                self.canvas.coords(self.rubber, x-r, y-r, x+r, y+r)
            else:
                self.rubber = self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                                      outline=color,
                                                      tags=tag)
        else:
            if constr:  # Constr circle
                attribs = (coords, constrcolor)
                e = entities.CC(attribs)
                self.ccirc_gen(e)
            else:  # geom circle
                attribs = (coords, geomcolor)
                e = entities.GC(attribs)
                self.gcirc_gen(e)
            if self.rubber:
                self.canvas.delete(self.rubber)
                self.rubber = None
            
    def circ(self, p1=None, constr=0):
        '''Create a circle from center pnt and perimeter pnt or radius.'''
        
        finish = 0
        if not self.pt_stack:
            self.updateMessageBar('Pick center of circle or enter coords')
        elif len(self.pt_stack) == 1 and p1 and not self.float_stack:
            self.updateMessageBar('Specify point on circle or radius')
            pc = self.pt_stack[0]
            p1 = self.cp2ep(p1)
            r = p2p_dist(pc, p1)
            coords = (pc, r)
            self.circ_builder(coords, rubber=1)
        elif len(self.pt_stack) > 1:
            p1 = self.pt_stack.pop()
            pc = self.pt_stack.pop()
            r = p2p_dist(pc, p1)
            finish = 1
        elif self.pt_stack and self.float_stack:
            pc = self.pt_stack.pop()
            r = self.float_stack.pop()*self.unitscale
            finish = 1
        if finish:
            self.circ_builder((pc, r), constr=constr)

    #=======================================================================
    # geometry arc parameters are stored in GA objects
    # arcs are defined by coordinates:  (pc, r, a0, a1)
    # where:    pc = (x, y) coords of center point
    #           r = radius
    #           a0 = start angle in degrees
    #           a1 = end angle in degrees
    #=======================================================================

    def garc_gen(self, ga, tag='g'):
        """Create geometry arc from GA object (coords in ECS)

        pc  = arc center pt
        rad = radius of arc center in mm
        a0  = start angle in degrees measured CCW from 3 o'clock position
        a1  = end angle in degrees measured CCW from 3 o'clock position
        """
        coords, color = ga.get_attribs()
        pc, rad, a0, a1 = coords
        ext = a1-a0
        if ext<0:
            ext += 360
        x, y = self.ep2cp(pc)
        r = self.canvas.w2c_dx(rad)
        x1 = x-r
        y1 = y-r
        x2 = x+r
        y2 = y+r
        if tag is 'r':
            if self.rubber:
                self.canvas.coords(self.rubber, x1, y1, x2, y2,)
                self.canvas.itemconfig(self.rubber, start=a0, extent=ext)
            else:
                self.rubber = self.canvas.create_arc(x1, y1, x2, y2,
                                                     start=a0, extent=ext,
                                                     style='arc', tags=tag,
                                                     outline=color)
        else:
            handle = self.canvas.create_arc(x1, y1, x2, y2,
                                            start=a0, extent=ext, style='arc',
                                            outline=color, tags=tag)
            self.curr[handle] = ga


                
    
    #=======================================================================
    # Delete
    #=======================================================================

    def del_el(self, item_tuple=None):
        '''Delete individual elements.'''
        
        self.set_sel_mode('items')
        self.allow_list = 1
        self.updateMessageBar('Pick element(s) to delete.')
        if self.obj_stack:
            item_tuple = self.obj_stack.pop()
            for item in item_tuple:
                tags = self.canvas.gettags(item)
                if item in self.curr:
                    e = self.curr[item]
                    if e.type is 'cl':
                        self.cl_list.remove(e.coords)
                    del self.curr[item]
                    self.canvas.delete(item)
                else:
                    if 'd' in tags:
                        dgid = tags[1]
                        dim_items = self.canvas.find_withtag(dgid)
                        for each in dim_items:
                            self.canvas.delete(each)
                        del self.curr[dgid]

    #=======================================================================
    # Undo / Redo
    #=======================================================================

    """
    When drawing entities are created and displayed, their parameters are
    stored in objects that are specific to their 'type'. The objects which
    encapsulate them each have a .type attribute mirroring the type of the
    entity being encapsulated. The types are as follows:
    
    'cl'    construction line
    'cc'    construction circle
    'gl'    geometry line
    'gc'    geometry circle
    'ga'    geometry arc
    'dl'    linear dimension
    'tx'    text

    Information about all the entities currently in the drawing is kept in a
    dictionary named self.curr, whose values are the entity objects
    encapsulating each entity and whose keys are the canvas generated handles
    associated with each entity.
    In order to implement undo and redo, it is neccesary to detect whenever
    there is a change in self.curr. To do this, a copy of self.curr (named
    self.prev) is maintained. Whenever a CAD operation ends, the save_delta()
    method is called. This method first compares self.curr with self.prev to
    see if they are equal. If not, a set containing the values in self.curr is
    compared with a set containing the values in self.prev. The difference is
    loaded onto the undo_stack. The curr config is then copied to self.prev.
                             __________
                            |  Change  |
                            |_detected_|
                                 ||
                                 ||1
                                 \/          2
     ____________            __________    diff    ______________
    | redo stack |          |   Curr   |    -->   |  Undo stack  |
    |____________|          |__________|          |______________|
                                 ||
                                 ||3
                                 \/
                             __________
                            |   Prev   |
                            |__________|

    1. difference detected between curr and prev.
    2. diff (delta) pushed onto undo_stack.
    3. copy of curr saved to prev.
    
    
    The undo & redo buttons work as shown in the diagram below.

     ____________     2      __________ 3       1  ______________
    | redo stack |   <--    |   Curr   |    <--   |  Undo stack  |
    |____________|          |__________|          |______________|
                                 ||
                                 ||4
                                 \/
                             __________
                            |   Prev   |
                            |__________|

    For example, when the Undo button is clicked:
    1. undo_data is popped off the undo_stack.
    2. undo data is pushed onto the redo_stack.
    3. curr is updated with undo_data.
    4. copy of curr is save to prev.


     ____________ 1       3  __________      2     ______________
    | redo stack |   -->    |   Curr   |    -->   |  Undo stack  |
    |____________|          |__________|          |______________|
                                 ||
                                 ||4
                                 \/
                             __________
                            |   Prev   |
                            |__________|

    Similarly, if the Redo button is clicked:
    1. redo_data is popped off the redo_stack.
    2. redo data is pushed onto the undo_stack.
    3. curr is updated with redo_data.
    4. copy of curr is saved to prev.

    Typically, after clicking undo / redo buttons one or more times,
    the user will resume running CAD operations that create, modify or
    delete CAD data. Once CAD operations are resumed, the data on the
    redo stack is no longer relevant and is discarded. Thus, when the
    save_delta method runs, the redo stack is emptied.
    """

    def save_delta(self):
        """After a drawing change, save deltas on undo stack."""

        if self.curr.values() != self.prev.values():
            plus = set(self.curr.values()) - set(self.prev.values())
            minus = set(self.prev.values()) - set(self.curr.values())
            if plus or minus:  # Only save if something changed
                delta = {'+': plus, '-': minus}
                self.undo_stack.append(delta)
                self.prev = self.curr.copy()
                self.clear_redo()

    def undo(self, event=None):
        """Pop data off undo, push onto redo, update curr, copy to prev."""
        
        self.end()
        if self.undo_stack:
            undo_data = self.undo_stack.pop()
            self.redo_stack.append(undo_data)
            for item in undo_data['+']:
                self.rem_draw(item)
            for item in undo_data['-']:
                self.add_draw(item)
            self.prev = self.curr.copy()
        else:
            print("No Undo steps available.")

    def redo(self, event=None):
        """Pop data off redo, push onto undo, update curr, copy to prev."""

        self.end()
        if self.redo_stack:
            redo_data = self.redo_stack.pop()
            self.undo_stack.append(redo_data)
            for item in redo_data['+']:
                self.add_draw(item)
            for item in redo_data['-']:
                self.rem_draw(item)
            self.prev = self.curr.copy()
        else:
            print("No Redo steps available.")

    def add_draw(self, entity):
        """Add entity to current drawing."""

        if entity.type is 'cl':
            self.cline_gen(entity.coords)  # This one takes coords
        elif entity.type is 'cc':
            self.ccirc_gen(entity)
        elif entity.type is 'gl':
            self.gline_gen(entity)
        elif entity.type is 'gc':
            self.gcirc_gen(entity)
        elif entity.type is 'ga':
            self.garc_gen(entity)
        elif entity.type is 'dl':
            self.dim_gen(entity)
        elif entity.type is 'tx':
            self.text_gen(entity)
        

    def rem_draw(self, entity):
        """Remove entity from current drawing."""

        kvlist = list(self.curr.items())
        for k, v in kvlist:
            if v == entity:
                self.canvas.delete(k)
                del self.curr[k]

    def clear_redo(self):
        self.redo_stack.clear()

    def clear_undo(self):
        self.undo_stack.clear()

    #=======================================================================
    # Event handling
    #=======================================================================

    def end(self):
        '''End current operation'''
        
        if self.rubber:
            self.canvas.delete(self.rubber)
            self.rubber = None
        if self.rtext:
            self.canvas.delete(self.rtext)
            self.rtext = None
        if self.catch_pnt:
            self.canvas.delete(self.catch_pnt)
            self.catch_pnt = None
        if self.op:
            self.op = ''
        self.sel_box_crnr = None
        self.canvas.delete(self.sel_boxID)
        self.sel_boxID = None
        self.text = ''
        self.pt_stack = []
        self.float_stack = []
        self.obj_stack = []
        self.text_entry_enable = 0
        self.set_sel_mode('')
        self.allow_list = 0
        self.quitpopup()
        self.save_delta()
        self.updateMessageBar('CTRL-LMB to pan.  CTRL-RMB to zoom.')

    def enterfloat(self, str_value):
        """Receive string value (from calculator) and do the right thing."""
        
        if str_value:
            val = float(str_value)
            self.float_stack.append(val)
            func = 'self.%s()' % self.op
            eval(func)

    def keybrdEntry(self, event):
        """Store user entered values on stack.

        POINTS:
        points are stored in mm units in ECS on self.pt_stack.
        This is one of the places where unit scale is applied.

        FLOATS:
        floats are stored as unitless numbers on self.float_stack. Because a
        float value may be used for anything: radius, angle, x value, y value,
        whatever; it is not possible to know here how a float value will
        be used. It remains the responsibility of the using function to
        condition the float value appropriately by applying unitscale for
        distances, etc."""
        
        if self.op:
            text = self.entry.get()
            self.entry.delete(0, len(text))
            if self.text_entry_enable:
                self.text = text
            else:
                list = text.split(',')
                if len(list) == 1:
                    val = list[0]
                    self.float_stack.append(float(val))
                elif len(list) == 2 and self.sel_mode == 'pnt':
                    # user entered points are already in ECS units
                    x, y = list
                    x = float(x) * self.unitscale
                    y = float(y) * self.unitscale
                    self.pt_stack.append((x, y))
            func = 'self.%s()' % self.op
            eval(func)

    def lftClick(self, event):
        '''Place screen picks on appropriate stack, call method named by self.op.
        In "point" mode, put x,y coords of "catch point", if any, on point
        stack, otherwise put pointer x,y coords on stack.
        In "items" mode, put a tuple of selected items on "object stack".
        If first click does not find one or more items within its
        "catch radius", enter "box select mode" and look for objects that
        lie completely inside box defined by 1st and 2nd clicks.
        '''
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        cr = self.catch_radius
        if self.sel_mode == 'pnt':
            # convert screen coords to ECS units and put on pt_stack
            if self.catch_pnt:
                l, t, r, b = self.canvas.coords(self.catch_pnt)
                x = (r + l)/2
                y = (t + b)/2
            p = self.cp2ep((x, y))
            self.pt_stack.append(p)
            func = 'self.%s()' % self.op
            eval(func)
        elif self.sel_mode in ('items', 'list'):
            items = self.canvas.find_overlapping(x-cr, y-cr, x+cr, y+cr)
            if not items and not self.sel_box_crnr:
                self.sel_box_crnr = (x, y)
                return
            elif self.sel_box_crnr:
                x1, y1 = self.sel_box_crnr
                items = self.canvas.find_enclosed(x1, y1, x, y)
                self.sel_box_crnr = None
                self.canvas.delete(self.sel_boxID)
                self.sel_boxID = None
            if self.sel_mode == 'items':
                self.obj_stack.append(items)
                func = 'self.%s()' % self.op
                eval(func)
            elif self.sel_mode == 'list':
                if not self.obj_stack:
                    self.obj_stack.append([])
                for item in items:
                    if item not in self.obj_stack[-1]:
                        self.obj_stack[-1].append(item)

    def midClick(self, event):
        self.end()

    def rgtClick(self, event):
        '''Popup menu for view options.'''
        
        if self.popup:
            self.popup.destroy()
        self.popup = Toplevel()
        self.popup.overrideredirect(1)
        frame = Frame(self.popup)
        Button(frame, text='View Fit',
               command=lambda:(self.view_fit(), self.quitpopup())).pack()
        if self.allow_list:
            Button(frame, text='Start list',
                   command=lambda:(self.set_sel_mode('list'), self.quitpopup())).pack()
            Button(frame, text='End list',
                   command=lambda:(self.set_sel_mode('items'), eval('self.%s()' % self.op),
                                   self.quitpopup())).pack()
        frame.pack()
        size, x, y = self.winfo_toplevel().winfo_geometry().split('+')
        x = int(x)
        y = int(y)
        if self.allow_list:
            self.popup.geometry('60x90+%s+%s' % (x+event.x, y+event.y+30))
        else:
            self.popup.geometry('60x30+%s+%s' % (x+event.x, y+event.y+30))

    def quitpopup(self):
        if self.popup:
            self.popup.destroy()
            self.popup = None

    def setCC(self, event):
        '''Set center catch flag'''
        
        if event.type == '2' and event.keysym == 'Shift_L':
            self.catchCntr = True
        else:
            self.catchCntr = False