#!/bin/python

import sys,random,os,math
import numpy as np
from functools import reduce
from itertools import groupby
from PIL import Image

### SETUP ###
# Constants
palettes = {'normal':
               {'bg':(255,255,255),
                'true-black':(0,0,0),
                'black':(10,10,10),
                'true-white':(255,255,255),
                'white':(255,255,255),
                'red':(240,0,0),
                'green':(0,240,0),
                'blue':(0,0,240),
                'cyan':(0,240,240),
                'yellow':(240,240,0),
                'magenta':(240,0,240)},
            'darkness':
               {'bg':(0,0,0),
                'true-black':(10,10,10),
                'black':(20,20,20),
                'true-white':(50,50,50),
                'white':(50,50,50),
                'red':(40,0,0),
                'green':(0,40),
                'blue':(0,0,40),
                'cyan':(0,40,40),
                'yellow':(40,40,0),
                'magenta':(40,0,40),},
            'day':
               {'bg':(210,240,255),
                'true-black':(0,0,0),
                'black':(10,10,10),
                'true-white':(255,255,255),
                'white':(255,255,255),
                'red':(230,0,0),
                 'green':(0,230),
                'blue':(0,0,230),
                'cyan':(0,230,230),
                'yellow':(230,230,0),
                'magenta':(230,0,23)},
            'night':
               {'bg':(45,45,90),
                'true-black':(0,0,0),
                'black':(10,10,10),
                'true-white':(255,255,255),
                'white':(230,230,230),
                'red':(190,0,0),
                'green':(0,190),
                'blue':(0,0,190),
                'cyan':(0,190,190),
                'yellow':(190,190,0),
                'magenta':(190,0,190)}}
# Variable defaults
panels       = []
balls        = {}
global_palette_name = 'normal'
global_panel_height = 445
comic_width  = 720
# Class declarations
class Panel:
    def __init__(self,index,height,palette_name):
        self.index        = index
        self.height       = height
        self.palette_name = palette_name
        self.balls = []
        self.pixels = Canvas(comic_width,height)
    def add_ball(self,ball):
        self.balls.append(ball)
class Ball:
    def __init__(self,country='Poland',dialogue='',face='normal',facing='right',
                 position='left',size='normal',template=None):
        if template != None:
            self = template
        self.country  = country
        self.dialogue = dialogue
        self.face     = face
        self.facing   = facing
        self.position = position
        self.size     = size
    def add_dialogue(dialogue):
        self.dialogue = dialogue
class Region:
    '''
    Store a region on the surface of a sphere bounded by circles on the
    surface of the sphere.
    '''
    def __init__(self,circles,points,color):
        '''
        :param circles: a list of circles on the surface of the sphere;
            each circle is a rank 2 tuple that looks like so:
            ((theta,phi),dist)
            where the plane that is cutting the circle is touching and
            perpendicular to the end of a line segment radiating from
            the center of the sphere that has polar angle theta,
            azimuthal angle phi, and a ratio to the radius of dist. If
            the dist is 0, then it will be treated as a great circle.
            Warning to physics students: this is _maths_ territory. The
            convention is the opposite of what you are used to.
        :type circles: tuple of (a tuple of two floats) and a float
        :param points: a tuple of coordinates for points that are in
            the region, with the (theta,phi) convention. Each point
            highlights an area that is maximally bounded by each
            circle. If there only needs to be one point, then a tuple
            of the two coordinates themselves will work, too.
        :type points: a tuple of tuples of two floats, or a tuple of two
            floats
        '''
        self.circles = circles
        if hasattr(points[0],'__float__'):
            self.points = (points,)
        else:
            self.points = points
        self.color = color
class Canvas:
    def __init__(self,width,height):
        self.width  = width
        self.height = height
        self.pixels = None # gets initialized later
    def init_pixels(self,bg_color):
        self.pixels = np.tile(np.array(bg_color),
                              (self.height,self.width))
    def get_pixel(self,x,y):
        if 0 <= x and x < self.width and 0 <= y and y < len(self.pixels):
            assert hasattr(x,'__int__') # I fucking swear this was the
            assert hasattr(y,'__int__') # most embarrassing shit ever.
            return (self.pixels[y][3*x],
                    self.pixels[y][3*x+1],
                    self.pixels[y][3*x+2])
        else:
            return (-2,-2,-2) # (-1,-1,-1) would mean transparency
    def is_color(self,x,y,color):
        if 0 <= x and x < self.width and 0 <= y and y < self.height:
            return np.array(color) == self.get_pixel(x,y)
        else:
            return False
    def pencil(self,x,y,color):
        if 0 <= x and x < self.width and 0 <= y and y < self.height:
            assert hasattr(x,'__int__') # I fucking swear this was the
            assert hasattr(y,'__int__') # most embarrassing shit ever.
            self.pixels[y][3*x]   = color[0]
            self.pixels[y][3*x+1] = color[1]
            self.pixels[y][3*x+2] = color[2]
    def paint(self,x,y,color,size=1):
        if size == 1:
            self.pencil(x,y,color)
        elif size == 2:
            self.pencil(x,y-1,color)
            self.pencil(x-1,y,color)
            self.paint(x,y,color,1)
            self.pencil(x+1,y,color)
            self.pencil(x,y+1,color)
        elif size == 3:
            self.pencil(x-1,y-1,color)
            self.pencil(x+1,y-1,color)
            self.paint(x,y,color,2)
            self.pencil(x-1,y+1,color)
            self.pencil(x+1,y+1,color)
        elif size == 4:
            self.pencil(x,y-2,color)
            self.pencil(x-2,y,color)
            self.paint(x,y,color,3)
            self.pencil(x+2,y,color)
            self.pencil(x,y+2,color)
        elif size == 5:
            self.pencil(x-1,y-2,color)
            self.pencil(x+1,y-2,color)
            self.pencil(x-2,y-1,color)
            self.pencil(x+2,y-1,color)
            self.paint(x,y,color,4)
            self.pencil(x-2,y+1,color)
            self.pencil(x+2,y+1,color)
            self.pencil(x-1,y+2,color)
            self.pencil(x+1,y+2,color)
        elif size == 6:
            self.pencil(x,y-3,color)
            self.pencil(x-2,y-2,color)
            self.pencil(x+2,y-2,color)
            self.pencil(x-3,y,color)
            self.paint(x,y,color,5)
            self.pencil(x+3,y,color)
            self.pencil(x-2,y+2,color)
            self.pencil(x+2,y+2,color)
            self.pencil(x,y+3,color)
        elif size == 7 or size == 8:
            self.pencil(x-2,y-3,color)
            self.pencil(x-1,y-3,color)
            self.pencil(x+1,y-3,color)
            self.pencil(x+2,y-3,color)
            self.pencil(x-3,y-2,color)
            self.pencil(x+3,y-2,color)
            self.pencil(x-3,y-1,color)
            self.pencil(x+3,y-1,color)
            self.paint(x,y,color,6)
            self.pencil(x-3,y+1,color)
            self.pencil(x+3,y+1,color)
            self.pencil(x-3,y+2,color)
            self.pencil(x+3,y+2,color)
            self.pencil(x-2,y+3,color)
            self.pencil(x-1,y+3,color)
            self.pencil(x+1,y+3,color)
            self.pencil(x+2,y+3,color)
        elif size == 9:
            self.pencil(x-1,y-4,color)
            self.pencil(x,y-4,color)
            self.pencil(x+1,y-4,color)
            self.pencil(x-3,y-3,color)
            self.pencil(x+3,y-3,color)
            self.pencil(x-4,y-1,color)
            self.pencil(x+4,y-1,color)
            self.pencil(x-4,y,color)
            self.paint(x,y,color,8)
            self.pencil(x+4,y,color)
            self.pencil(x-4,y+1,color)
            self.pencil(x+4,y+1,color)
            self.pencil(x-3,y+3,color)
            self.pencil(x+3,y+3,color)
            self.pencil(x-1,y+4,color)
            self.pencil(x,y+4,color)
            self.pencil(x+1,y+4,color)
        elif size == 10:
            self.pencil(x-2,y-4,color)
            self.pencil(x+2,y-4,color)
            self.pencil(x-4,y-2,color)
            self.pencil(x+4,y-2,color)
            self.paint(x,y,color,9)
            self.pencil(x-4,y+2,color)
            self.pencil(x+4,y+2,color)
            self.pencil(x-2,y+4,color)
            self.pencil(x+2,y+4,color)
        elif size > 10:
            self.paint(x,y,color,10)
    def ellipse(self,x,y,vert_len,horiz_len,color=(0,0,0),rotation=0,
            fixed_brush_size=None,depth_func=None):
        '''
        Draws a wobbly ellipse according to the parameters.
        :param x: x coordinate of center of ellipse
        :type x: non-negative int
        :param y: y coordinate of center of ellipse (origin at top)
        :type y: non-negative int
        :param vert_len: length of axis of ellipse pointing at the
            angle indicated by rotation
        :type vert_len: non-negative float
        :param horiz_len: length of axis of ellipse pointing
            perpendicular to the vertical axis
        :type horiz_len: non-negative float
        :param color: the color with which to draw the ellipse
        :type color: tuple of integers between 0 and 255
        :param rotation: amount of radians to rotate the ellipse by
        :type rotation: float
        :param fixed_brush_size: brush size to use; if not specified,
            size will be made proportional to ellipse size
        :type fixed_brush_size: positive integer
        :param depth_func: parameters of function to check whether the
            ellipse is in the front of the ball or not. It consists of
            an amplitude and an offset, applied to a cosine. The
            method checks whether the resulting function is above 0 or
            not. The amplitude comes first, then the (vertical)
            offset.
        :type depth_func: tuple of two floats
        '''
        x_values = [] # each value is a tuple:
        y_values = [] # (phase, frequency, amplitude)
        x_values.append((0,
                         1,
                         horiz_len+horiz_len*0.1*random.random()))
        y_values.append((-1.570796,
                         1,
                         vert_len+vert_len*0.1*random.random()))
        # Generate the amplitudes for the random deviations:
        x_amount_to_append = random.randrange(8,12)
        y_amount_to_append = random.randrange(8,12)
        freqs = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        for index in range(x_amount_to_append-1):
            rand_freq = random.choice(freqs)
            x_values.append((
                random.random()*6.28319,
                rand_freq,
                random.choice((-1,1))*\
                              (((vert_len+horiz_len)**0.82)*\
                              (0.1*random.random()+0.08)/\
                              (rand_freq**1.45))))
        for index in range(y_amount_to_append-1):
            rand_freq = random.choice(freqs)
            y_values.append((
                random.random()*6.28319,
                rand_freq,
                random.choice((-1,1))*\
                              (((vert_len+horiz_len)**0.82)*\
                              (0.1*random.random()+0.08)/\
                              (rand_freq**1.45))))
        # Determine brush size:
        if fixed_brush_size != None:
            brush_size = fixed_brush_size
        else:
            brush_size = int(math.sqrt(vert_len+horiz_len)/3)
        # Draw it:
        increment = 1.5/(3*(vert_len+horiz_len)-\
                math.sqrt((3*vert_len+horiz_len)*\
                (vert_len+3*horiz_len))) # So we don't waste time
        if depth_func == None:
            t = 0
            if rotation == 0:
                while t < 6.28319:
                    self.paint(
                        int(x+reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    x_values])),
                        int(y+reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    y_values])),
                            color,
                            brush_size)
                    t += increment
            else:
                while t < 6.28319:
                    x_pos = reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    x_values])
                    y_pos = reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    y_values])
                    self.paint(
                            int(x+math.cos(rotation)*x_pos-\
                                    math.sin(rotation)*y_pos),
                            int(y+math.sin(rotation)*x_pos+\
                                    math.cos(rotation)*y_pos),
                            color,
                            brush_size)
                    t += increment
        else:
            phase = math.acos(-float(depth_func[1])/depth_func[0])
            end   = 6.283185-phase
            t     = phase
            if rotation == 0:
                while t < end:
                    self.paint(
                        int(x+reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    x_values])),
                        int(y+reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    y_values])),
                            color,
                            brush_size)
                    t += increment
            else:
                while t < end:
                    x_pos = reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    x_values])
                    y_pos = reduce(
                            lambda a,b:a+b,
                            [amp*math.cos(freq*t+phase) for phase,freq,amp in\
                                    y_values])
                    self.paint(
                            int(x+math.cos(rotation)*x_pos-\
                                    math.sin(rotation)*y_pos),
                            int(y+math.sin(rotation)*x_pos+\
                                    math.cos(rotation)*y_pos),
                            color,
                            brush_size)
                    t += increment
    def flood_fill(self,x,y,color):
        '''
        Exactly like MS Paint bucket fill, down to the inefficiency.
        '''
        original_color = self.get_pixel(x,y)
        if color == original_color:
            return
        stack = [(x,y)]
        while len(stack) > 0:
            pos = stack.pop()
            if self.get_pixel(*pos) != original_color:
                continue
            self.pencil(*(pos+(color,)))
            stack.append((pos[0],pos[1]-1))
            stack.append((pos[0]-1,pos[1]))
            stack.append((pos[0]+1,pos[1]))
            stack.append((pos[0],pos[1]+1))
    def composite(self,other_canvas,x,y):
        '''
        Blit another canvas onto the surface of this one, x and y
        specifying the top left corner.
        '''
        for y_i in range(other_canvas.height):
            for x_i in range(other_canvas.width):
                color = other_canvas.get_pixel(x_i,y_i)
                if color != -1:
                    self.pencil(x+x_i,y+y_i,color,1)
    def render_sphere(self,ball,regions,stickers):
        '''
        Draw a sphere (i.e. a countryball) with the specified sections
        of it (regions) colored in the appropriate way. e.g. Polan
        would have one region, for the top red part (because the ball
        starts out white). France would have two surfaces, Germany
        three. The regions are each Region objects, which define a
        section of the surface of a sphere, bounded by cross-sections
        of the sphere.
        :param ball: the countryball to draw
        :type ball: Ball object
        :param regions: a list of regions to draw
        :type regions: a tuple of Regions
        :param stickers: a list of tuples that contain a (theta,phi)
            coordinate and a Canvas respectively to slap on the sphere
            at like a sticker.
        :type stickers: a tuple of tuples of (a tuple of two floats)
            and a Canvas
        '''
        # Determine what angle to rotate the ball to:
        if ball.facing == 'right':
            theta = 0.261799  #  pi/3
            phi   = -0.261799 # -pi/12
        elif ball.facing == 'left':
            theta = -0.261799 # -pi/3
            phi   = -0.261799 # -pi/12
        if ball.size == 'normal':
            R = 110.
        # Break circles down into ellipses to draw. Specifically,
        # self.ellipse() queries in the forms of tuples; note that
        # since this function includes a specialized version of
        # self.ellipse(), these will never get passed into it. However,
        # the goal is that if these tuples were *passed into
        # self.ellipse(), they should be able to go through just fine.
        ellipse_queries = []
        for region in regions:
            for circle in region.circles:
                # The fucking math here took horribly long to find out
                c_theta,c_phi = circle[0][0]+theta,circle[0][1]+phi
                r             = R*circle[1]
                st,ct         = math.sin(c_theta),math.cos(c_theta)
                sp,cp         = math.sin(c_phi),math.cos(c_phi)
                x   = r*cp*st
                y   = r*sp
                Mx  = R*math.cos(c_phi+math.acos(r/R))*st
                My  = R*math.sin(c_phi+math.acos(r/R))
                mx  = R*cp*math.sin(c_theta+math.acos(r/R))
                my  = R*sp
                M   = math.sqrt((Mx-x)**2+(My-y)**2)
                m   = math.sqrt((mx-x)**2+(my-y)**2)
                rot = 1.5707963-math.atan2(My-y,Mx-x)
                ellipse_queries.append((
                    x+360,       # x
                    y+300,       # y
                    M,           # vert axis
                    m,           # horiz axis
                    (0,255,255), # color
                    rot,         # rotation
                    1,           # brush_size
                    None))       # depth_func
            self.ellipse(*ellipse_queries[0])

### READ FILE ###
if sys.argv[0] == './polandball.py':
    filename = sys.argv[1]
elif sys.argv[0] in ('python','python3'):
    filename = sys.argv[2]
if os.path.isfile(filename):
    if filename[-4:] == '.pbc':
        source = open(filename)
    else:
        print('Source file must have extension .pbc.')
        sys.exit()
else:
    print('Sorry, that file was not found.')
    sys.exit()
mode = 'global' # can be 'global' or 'panel'
for line_number,line in enumerate(source,1):
    line = line[:line.find('//')] # truncate newline and comment
    tokens = line.split() # TODO: replace this with an actual lexer
    # Parse and execute the statement
    if tokens == []:
        pass
    elif tokens == ['}'] and mode == 'panel':
        mode = 'global'
    elif len(tokens) >= 2:
        if tokens[1] == ':' and mode == 'panel':
            panels[-1].add_ball(
                    balls[tokens[0]].add_dialogue(' '.join(tokens[2:])))
            # TODO: add ability to change attrs, use lexer
        elif tokens[0].isdigit() and tokens[1] == '{' and mode == 'global':
            mode = 'panel'
            panel_height = global_panel_height
            palette_name = global_palette_name
            panels.append(Panel(int(tokens[0]),panel_height,palette_name))
        elif len(tokens) == 3:
            if tokens[0].isalpha() and tokens[1] == '=' and tokens[2].isalnum():
                varname = tokens[0]
                value = tokens[2]
                if varname == 'pheight' and value.isdigit():
                    if mode == 'global':
                        global_panel_height = int(value)
                    elif mode == 'panel':
                        panels[-1].height = int(value)
                elif varname == 'palette' and value.isalpha():
                    if mode == 'global':
                        global_palette_name = value
                    elif mode == 'panel':
                        panels[-1].palette_name = value
                elif varname == 'width' and value.isdigit():
                    comic_width = int(value)
        elif len(tokens) >= 4:
            if tokens[0] == 'ball' and tokens[1].isalnum() and\
                    tokens[2] == '=' and tokens[3].isalpha():
                if len(tokens) == 4:
                    balls[tokens[1]] = Ball(country=tokens[3])
                elif tokens.find('(') < tokens.find(')') and\
                        tokens.find('(') != -1:
                    face     = 'normal'
                    facing   = 'right'
                    position = 'left'
                    for assignment in groupby(tokens[tokens.find('(')+1,
                                                     tokens.find(')')],
                                              lambda x:x==','):
                        if len(assignment) == 3:
                            if assignment[0].isalpha() and\
                                    assignment[1] == '=' and\
                                    assignment[2].isalpha():
                                varname = assignment[0]
                                value   = assignment[2]
                                if varname == 'face':
                                    face = value
                                elif varname == 'facing':
                                    facing = value
                                elif varname == 'position':
                                    position = value
                                else:
                                    print("Line "+str(line_number)+\
                                          ": no attribute \""+varname+"\".")
                                    sys.exit()
                            else:
                                print("Line "+str(line_number)+\
                                      ": syntax error.")
                                sys.exit()
                        else:
                            print("Line "+str(line_number)+": syntax error.")
                            sys.exit()
                    balls[tokens[1]] = Ball(country=tokens[3],
                                            face=face,
                                            facing=facing,
                                            position=position)
                else:
                    print("Line "+str(line_number)+": syntax error.")
                    sys.exit()
            else:
                print("Line "+str(line_number)+": syntax error.")
                sys.exit()
        else:
            print("Line "+str(line_number)+": syntax error.")
            sys.exit()
    else:
        print("Line "+str(line_number)+": syntax error.")
        sys.exit()
source.close()

### MAKE AND SAVE COMIC ###
if len(panels) == 0:
    print('Error: no panels. No output file produced.')
    sys.exit()
if os.path.isfile(filename[:-4]+'.png'):
    os.remove(filename[:-4]+'.png')
panel_amount = len(panels)
count = 0
while len(panels) > 0:
    print('Creating Panel '+str(panel_amount-len(panels)+1)+'...')
    panel = panels[0]
    # Get the palette:
    palette = palettes[panel.palette_name]
    # Mutate the palette:
    for color in palette:
        new_color = []
        for value in palette[color]:
            if value in (0,255):
                new_color.append(value)
            else:
                new_value = value+int(value*(0.2*random.random()-0.01))
                if new_value < 0:
                    new_value = 0
                elif new_value > 255:
                    new_value = 255
                new_color.append(new_value)
        palette[color] = tuple(new_color)
    # Draw the panel:
    panel.pixels.init_pixels(palette['bg'])
    panel.pixels.ellipse(360,300,110,110,palette['true-black'])
    panel.pixels.ellipse(330,290,25,16,palette['true-black'])
    panel.pixels.ellipse(390,290,25,16,palette['true-black'])
    panel.pixels.flood_fill(360,300,palette['red'])
    panel.pixels.flood_fill(330,290,palette['true-white'])
    panel.pixels.flood_fill(390,290,palette['true-white'])
    panel.pixels.render_sphere(Ball(facing='right',size='normal'),(Region(
            (((0.,1.57079),0.),),
            [[],[],[]],
            ''
        ),),'')
    # Save the panel:
    if os.path.isfile(filename[:-4]+'.png'):
        comic_png = Image.open(filename[:-4]+'.png')
        panel_png = Image.fromarray(np.uint8(np.reshape(panel.pixels.pixels,
                                                        (panel.pixels.height,
                                                         panel.pixels.width,
                                                         3))))
        final_width,final_height = comic_png.size
        final_height += panel_png.size[1]
        final_png = Image.new('RGB',(final_width,final_height))
        final_png.paste(comic_png,(0,0))
        final_png.paste(panel_png,(0,comic_png.size[1]))
        final_png.save(filename[:-4]+'.png')
    else:
        panel_png = Image.fromarray(
                np.uint8(
                    np.reshape(
                        panel.pixels.pixels,
                        (panel.pixels.height,
                         panel.pixels.width,
                         3)))).save(filename[:-4]+'.png')
    del panels[0]
    count += 1
