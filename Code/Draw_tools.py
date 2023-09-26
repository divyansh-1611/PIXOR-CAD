import math
import pickle
import os
from   tkinter import *
from   tkinter.filedialog import *
import entities


geomcolor = 'white'     # color of geometry entities
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