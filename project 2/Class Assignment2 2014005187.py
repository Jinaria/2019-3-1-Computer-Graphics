import glfw
import numpy as np
from numpy import linalg as la
from OpenGL.GL import *
from OpenGL.GLU import *

# camera global variable
gButton = -1
gAct = -1
flag = False
gCur = [0, 0]
targetPoint = np.array([0., 0., 0., 1])
gAzimuth = 45
gElevation = 36.264 
dist = 15.0
w = None
u = None
v = None

# drop global variable
gVarr = None
gNarr = None
gIarr = None
gPolygonMode = GL_LINE
shadeFlag = True
firstShading = None
secondShading = None
firstVertex = None
secondVertex = None

def initVar():
    global gVarr, gIarr, gNarr, firstShading, secondShading, firstVertex, secondVertex, shadeFlag
    gVarr = None
    gIarr = None
    gNarr = None
    firstShading = None
    secondShading = None
    firstVertex = None
    secondVertex = None
    # shadeFlag = True


def drop_callback(window, paths):
    global gVarr, gIarr, gNarr, firstShading, secondShading, firstVertex, secondVertex, shadeFlag
    varr = None
    narr = None
    initVar()
    if paths[0][-4:] == ".obj":
        with open(paths[0], 'r') as f:
            while True:
                data = f.readline()
                if not data:
                    break
                data = data.split()
                # print(data)
                if not data:
                    continue
                if data[0] is 'v':
                    d = [0., 0., 0., 0.]
                    for i in range(1, 4):
                        d[i] = float(data[i])
                    if varr is None:
                        varr = np.array([d[1:]], 'float32')
                    else:
                        varr = np.concatenate((varr, np.array([d[1:]])), axis = 0)
                elif data[0] == "vn":
                    d = [0., 0., 0., 0.]
                    for i in range(1, 4):
                        d[i] = float(data[i])
                    if narr is None:
                        narr = np.array([d[1:]], 'float32')
                    else:
                        narr = np.concatenate((narr, np.array([d[1:]])), axis = 0)
                elif data[0] is 'f':
                    for i in range(1, 4):
                        data[i] = data[i].split('/')
                    if gIarr is None:
                        gIarr = np.array([data[1:4]])
                    else:
                        gIarr = np.concatenate((gIarr, np.array([data[1:4]])), axis = 0)
        vnlist = np.array([[0., 0., 0.]])
        secondVertex = varr
        for i in range(len(varr) - 1):
            vnlist = np.concatenate((vnlist, np.array([[0., 0., 0.]])), axis = 0)
        tiarr = None
        for t in gIarr:
            a = []
            for k in range(3):
                a.append(int(t[k][0]) - 1)
                vnlist[int(t[k][0]) - 1] += narr[int(t[k][2]) - 1]
                if gNarr is None:
                    gNarr = np.array([narr[int(t[k][2]) - 1]])
                else:
                    gNarr = np.concatenate((gNarr, np.array([narr[int(t[k][2]) - 1]])), axis = 0)
                if gVarr is None:
                    gVarr = np.array([varr[int(t[k][0]) - 1]])
                else:
                    gVarr = np.concatenate((gVarr, np.array([varr[int(t[k][0]) - 1]])), axis = 0)
            if tiarr is None:
                tiarr = np.array([a])
            else:
                tiarr = np.concatenate((tiarr, np.array([a])), axis = 0)
        firstVertex = gVarr
        
        for i in range(len(vnlist)):
            vnlist[i] = vnlist[i] / np.sqrt(np.dot(vnlist[i], vnlist[i]))
        firstShading = gNarr
        secondShading = vnlist
        gIarr = tiarr
        print("file name : " + paths[0])
        print("total num of faces : " + str(len(gIarr)))
        if not shadeFlag:
            gNarr = secondShading
            gVarr = secondVertex
    else:
        print("file is not obj")


def cursor_callback(window, xpos, ypos):
    global gButton, gAct, flag, gCur
    global gAzimuth, gElevation, targetPoint
    if gAct == glfw.PRESS:
        if gButton == glfw.MOUSE_BUTTON_RIGHT:
            if flag:
                movX = gCur[0] - xpos
                movY = gCur[1] - ypos
                gCur = [xpos, ypos]
                if gElevation > 90 and gElevation < 270:
                    movX *= -1
                    movY *= -1
                targetPoint[0] = targetPoint[0] + u[0] * movX * 0.01 - v[0] * movY * 0.01
                targetPoint[1] = targetPoint[1] - v[1] * movY * 0.01
                targetPoint[2] = targetPoint[2] + u[2] * movX * 0.01 - v[2] * movY * 0.01
            else:
                flag = True
                gCur = [xpos, ypos]
                
        elif gButton == glfw.MOUSE_BUTTON_LEFT:
            if flag:
                movX = gCur[0] - xpos
                movY = gCur[1] - ypos
                gCur = [xpos, ypos]
                if gElevation > 90 and gElevation < 270:
                    movX *= -1
                gAzimuth = (gAzimuth + movX * 0.2) % 360
                gElevation = (gElevation - movY * 0.2) % 360
                
            else:
                flag = True
                gCur = [xpos, ypos]

def button_callback(window, button, action, mode):
    global gButton, gAct, flag
    if action == glfw.PRESS:
        gButton = button
        gAct = action
    elif action == glfw.RELEASE:
        if button == glfw.MOUSE_BUTTON_LEFT or button == glfw.MOUSE_BUTTON_RIGHT:
            gButton = -1
            gAct = -1
            flag = False

def scroll_callback(window, xoffset, yoffset):
    global dist
    dist = dist - yoffset * dist * 0.08

def key_callback(window, key, scancode, action, mods):
    global gPolygonMode, shadeFlag, gVarr, gNarr, firstShading, secondShading, firstVertex, secondVertex
    if action == glfw.PRESS:
        if key == glfw.KEY_Z:
            if gPolygonMode == GL_LINE:
                gPolygonMode = GL_FILL
            else:
                gPolygonMode = GL_LINE
        if key == glfw.KEY_S:
            if shadeFlag:
                shadeFlag = False
                gNarr = secondShading
                gVarr = secondVertex
            else:
                shadeFlag = True
                gNarr = firstShading
                gVarr = firstVertex


def drawFrame():
	glBegin(GL_LINES)
	glColor3ub(255, 0, 0)
	glVertex3fv(np.array([0., 0., 0.]))
	glVertex3fv(np.array([5., 0., 0.]))
	glColor3ub(0, 255, 0)
	glVertex3fv(np.array([0., 0., 0.]))
	glVertex3fv(np.array([0., 5., 0.]))
	glColor3ub(0, 0, 255)
	glVertex3fv(np.array([0., 0., 0.]))
	glVertex3fv(np.array([0., 0., 5.]))
	glEnd()

def drawLine(direction, position):
    glBegin(GL_LINES)
    if direction == 1:
        glVertex3f(-5., 0., position) 
        glVertex3f(5., 0., position)
    else:
        glVertex3f(position, 0., -5.)
        glVertex3f(position, 0., 5.)
    glEnd()

def drawPlane():
    glColor3ub(255, 255, 255)
    for i in range(11):
        drawLine(0, i - 5)
        drawLine(1, i - 5)

def drawCube():
    glBegin(GL_QUADS)
    glVertex3f(1., 1., -1.)
    glVertex3f(-1., 1., -1.)
    glVertex3f(-1., 1., 1.)
    glVertex3f(1., 1., 1.)  

    glVertex3f(1., -1., 1.)
    glVertex3f(-1., -1., 1.)
    glVertex3f(-1., -1., -1.)
    glVertex3f(1., -1., -1.)

    glVertex3f(1., 1., 1.)
    glVertex3f(-1., 1., 1.)
    glVertex3f(-1., -1., 1.)
    glVertex3f(1., -1., 1.)

    glVertex3f(1., -1., -1.)
    glVertex3f(-1., -1., -1.)
    glVertex3f(-1., 1., -1.)
    glVertex3f(1., 1., -1.)

    glVertex3f(-1., 1., 1.)
    glVertex3f(-1., 1., -1.)
    glVertex3f(-1., -1., -1.)
    glVertex3f(-1., -1., 1.)

    glVertex3f(1., 1., -1.)
    glVertex3f(1., 1., 1.)
    glVertex3f(1., -1., 1.)
    glVertex3f(1., -1., -1.)

    glEnd()

def drawSphere(numLats = 12, numLongs = 12):
    for i in range(0, numLats + 1):
        lat0 = np.pi * (-.5 + float(float(i - 1) / float(numLats)))
        z0 = np.sin(lat0)
        zr0 = np.cos(lat0)

        lat1 = np.pi * (-.5 + float(float(i) / float(numLats)))
        z1 = np.sin(lat1)
        zr1 = np.cos(lat1)

        glBegin(GL_QUAD_STRIP)

        for j in range(0, numLongs + 1):
            lng = 2 * np.pi * float(float(j - 1) / float(numLongs))
            x = np.cos(lng)
            y = np.sin(lng)
            glVertex3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr1, y * zr1, z1)

        glEnd()

def drawDrop():
    global gIarr, gVarr, gNarr, shadeFlag
    if gIarr is None:
        pass
    else:
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_DOUBLE, 3 * gNarr.itemsize, gNarr)
        glVertexPointer(3, GL_DOUBLE, 3 * gVarr.itemsize, gVarr)
        if shadeFlag:
            glDrawArrays(GL_TRIANGLES, 0, int(gVarr.size/3))
        else:
            glDrawElements(GL_TRIANGLES, gIarr.size, GL_UNSIGNED_INT, gIarr)
            

def setWUV(eye, at, up):
    global w, u, v

    w = (eye - at) / np.sqrt(np.dot(at - eye, at - eye))
    u = np.cross(up, w)
    u = u / np.sqrt(np.dot(u, u))
    v = np.cross(w, u)

def cameraWork():
    global gElevation, gAzimuth, targetPoint

    x = dist * np.cos(np.radians(gElevation)) * np.sin(np.radians(gAzimuth)) + targetPoint[0]
    y = dist * np.sin(np.radians(gElevation)) + targetPoint[1]
    z = dist * np.cos(np.radians(gElevation)) * np.cos(np.radians(gAzimuth)) + targetPoint[2]
    cam = np.array([x, y, z])
    up = np.array([0., 1., 0.])# * np.cos(np.radians(tElevation))
    setWUV(cam, targetPoint[:3], up)

    glRotatef(gElevation, 1., 0., 0.)
    glRotatef(-gAzimuth, 0., 1., 0.)
    glTranslatef(-targetPoint[0] - x, -targetPoint[1] - y, -targetPoint[2] - z)

def lightingSystem():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)

    glEnable(GL_RESCALE_NORMAL)

    #light position
    glPushMatrix()
    t0 = glfw.get_time()
    t1 = t0 + np.radians(120)
    t2 = t1 + np.radians(120)

    lightPos0 = (np.sin(t0) * 8., 8., np.cos(t0) * 8, 1.)
    lightPos1 = (np.sin(t1) * 8., 8., np.cos(t1) * 8, 1.)
    lightPos2 = (np.sin(t2) * 8., 8., np.cos(t2) * 8, 1.)
    
    # lightPos2 = ()
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos1)
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos2)
    glPopMatrix()

    # light intensity for each color channel
    lightColor0 = (1., 0., 0., 1.)
    lightColor1 = (0., 0., 1., 1.)
    lightColor2 = (0., 1., 0., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor0)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, lightColor2)
    glLightfv(GL_LIGHT2, GL_SPECULAR, lightColor2)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor) 

    # material reflectance for each color channel
    objectColor = (1., 1., 1., 1.)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterial(GL_FRONT, GL_SPECULAR, specularObjectColor)


def render():
    global targetPoint, gAzimuth, gElevation, dist, gPolygonMode
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, gPolygonMode)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity( )
    gluPerspective(45, 1, 1, 1000)
    
    cameraWork()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity( )
    drawPlane()
 
    # lighting system
    lightingSystem()

    drawDrop()
    # drawLizard(6)

    
def main():
    if not glfw.init():
        return
    window = glfw.create_window(1000, 1000, "classAssignment2", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
    main()