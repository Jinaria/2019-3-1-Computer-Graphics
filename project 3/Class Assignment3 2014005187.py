import glfw
import numpy as np
from numpy import linalg as la
from OpenGL.GL import *
from OpenGL.GLU import *
import copy

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
up = np.array([0, 1, 0])


# drop global variable
gHierarchy = None
gMotion = None
gOffset = None
gFirstOffset = []
gSecondOffset = []
gRotation = None
gFirstRotation = []
gSecondRotation = []
angleOrder = []
oldt = 0
frameTime = 0.
numOfFrames = 0
currentFrame = 0

def initVar():
    global gHierarchy, gMotion, gOffset, gFirstOffset, gSecondOffset, gRotation, gFirstRotation, gSecondRotation, currentFrame
    global oldt, numOfFrames, angleOrder
    gHierarchy = None
    gMotion = None
    gOffset = None
    gFirstOffset = []
    gSecondOffset = []
    gRotation = None
    gFirstRotation = []
    gSecondRotation = []
    currentFrame = 0
    oldt = 0
    numOfFrames = 0
    angleOrder = []

def drop_callback(window, paths):
    global gHierarchy, gMotion, gOffset, gFirstOffset, gSecondOffset, gRotation, gFirstRotation, gSecondRotation
    global frameTime, numOfFrames, angleOrder
    objData = None
    cnt = 0
    snum = 0
    FPS = 0.
    initVar()
    if paths[0][-4:] == ".bvh":
        jointName = []
        componentNum = 0
        with open(paths[0], 'r') as f:
            objData = f.read()
        objData = objData.split('\n')
        for i in objData:
            objData[cnt] = i.split()
            if objData[cnt]:
                if objData[cnt][0] == "ROOT" or objData[cnt][0] == "JOINT":
                    jointName.append(objData[cnt][1])
                    componentNum += 1
                elif objData[cnt][0] == "OFFSET":
                    gFirstOffset.append([float(k) for k in objData[cnt][1:]])
                    gFirstRotation.append([0, 0, 0])
                elif objData[cnt][0] == "CHANNELS" and objData[cnt][1] == "6":
                    temp = []
                    for k in objData[cnt][-3:]:
                        if k[0] == "X" or k[0] == "x":
                            temp.append(0)
                        elif k[0] == "Y" or k[0] == "y":
                            temp.append(1)
                        elif k[0] == "Z" or k[0] == "z":
                            temp.append(2)
                    angleOrder.append(temp)
                elif objData[cnt][0] == "CHANNELS" and objData[cnt][1] == "3":
                    temp = []
                    for k in objData[cnt][-3:]:
                        if k[0] == "X" or k[0] == "x":
                            temp.append(0)
                        elif k[0] == "Y" or k[0] == "y":
                            temp.append(1)
                        elif k[0] == "Z" or k[0] == "z":
                            temp.append(2)
                    angleOrder.append(temp)
            if i == "MOTION":
                snum = cnt
                break
            cnt += 1
        
        
        gHierarchy = objData[:snum]
        gMotion = objData[snum:]
        cnt = 3
        numOfFrames = float(gMotion[1].split()[-1])
        frameTime = float(gMotion[2].split()[-1])
        FPS = int(1 / frameTime)
        for i in gMotion[3:]:
            gMotion[cnt] = [float(k) for k in i.split()]
            gMotion[cnt] = [gMotion[cnt][i:i+3] for i in range(0, len(gMotion[cnt]), 3)]
            cnt += 1
        gMotion = gMotion[3:]
        gFirstOffset = np.array(gFirstOffset)
        gSecondOffset = copy.deepcopy(gFirstOffset)
        gSecondOffset[0] = gMotion[0][0]
        gSecondRotation = gMotion[0][1:]
        gOffset = gFirstOffset
        gRotation = gFirstRotation
        
        print("file name: " + paths[0])
        print("number of frames: " + str(numOfFrames))
        print("FPS: " + str(FPS))
        print("number of joints: " + str(componentNum))
        print("list of all joint names: ")
        print(jointName)

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
    global gOffset, gFirstOffset, gSecondOffset, gRotation, gFirstRotation, gSecondRotation, gMotion
    global currentFrame
    if action == glfw.PRESS:
        if key == glfw.KEY_SPACE:
            pass
            if gOffset is gFirstOffset:
                gSecondOffset[0] = gMotion[0][0]
                gSecondRotation = gMotion[0][1:]
                gOffset = gSecondOffset
                gRotation = gSecondRotation
                currentFrame = 0
            elif gOffset is gSecondOffset:
                gOffset = gFirstOffset
                gRotation = gFirstRotation
            

def drawLines(direction, position):
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
        drawLines(0, i - 5)
        drawLines(1, i - 5)

def drawCube(point):
    global up
    p = np.array(point)
    p1 = np.cross(p, up)
    p1 = (p1 / np.sqrt(np.dot(p1, p1))) * 0.02
    p2 = np.cross(p1, p)
    p2 = (p2 / np.sqrt(np.dot(p2, p2))) * 0.02
    p3 = p1 * -1
    p4 = p2 * -1
    p5 = p1 + p
    p6 = p2 + p
    p7 = p3 + p
    p8 = p4 + p

    glBegin(GL_QUADS)
    glVertex3fv(p1)
    glVertex3fv(p2)
    glVertex3fv(p3)
    glVertex3fv(p4)

    glVertex3fv(p8)
    glVertex3fv(p7)
    glVertex3fv(p6)
    glVertex3fv(p5)

    glVertex3fv(p4)
    glVertex3fv(p8)
    glVertex3fv(p5)
    glVertex3fv(p1)
    
    glVertex3fv(p2)
    glVertex3fv(p6)
    glVertex3fv(p7)
    glVertex3fv(p3)


    glVertex3fv(p3)
    glVertex3fv(p7)
    glVertex3fv(p8)
    glVertex3fv(p4)    

    glVertex3fv(p1)
    glVertex3fv(p5)
    glVertex3fv(p6)
    glVertex3fv(p2)


    glEnd()

# def drawCube():
#     glBegin(GL_QUADS)
#     glVertex3f(1., 1., 0.)
#     glVertex3f(-1., 1., 0.)
#     glVertex3f(-1., 1., 2.)
#     glVertex3f(1., 1., 2.)  

#     glVertex3f(1., -1., 2.)
#     glVertex3f(-1., -1., 2.)
#     glVertex3f(-1., -1., 0.)
#     glVertex3f(1., -1., 0.)

#     glVertex3f(1., 1., 2.)
#     glVertex3f(-1., 1., 2.)
#     glVertex3f(-1., -1., 2.)
#     glVertex3f(1., -1., 2.)

#     glVertex3f(1., -1., 0.)
#     glVertex3f(-1., -1., 0.)
#     glVertex3f(-1., 1., 0.)
#     glVertex3f(1., 1., 0.)

#     glVertex3f(-1., 1., 2.)
#     glVertex3f(-1., 1., 0.)
#     glVertex3f(-1., -1., 0.)
#     glVertex3f(-1., -1., 2.)

#     glVertex3f(1., 1., 0.)
#     glVertex3f(1., 1., 2.)
#     glVertex3f(1., -1., 2.)
#     glVertex3f(1., -1., 0.)

#     glEnd()

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

def drawLine(v):
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3fv(v)
    glEnd()

def animate():
    global gOffset, gFirstOffset, gSecondOffset, gRotation, gFirstRotation, gSecondRotation
    global frameTime, oldt, currentFrame, numOfFrames
    if gOffset is gFirstOffset:
        pass
    elif gOffset is gSecondOffset:
        # newt = glfw.get_time()
        # if newt - oldt > frameTime:
        currentFrame += 1
        if currentFrame >= numOfFrames:
            currentFrame = 0
        gSecondOffset[0] = gMotion[currentFrame][0]
        gRotation = gMotion[currentFrame][1:]
        # oldt = newt

def rotate(angle, num):
    global angleOrder
    cnt = 0
    for i in angleOrder[num]:
        glRotatef(angle[cnt], 1 if i == 0 else 0, 1 if i == 1 else 0, 1 if i == 2 else 0)
        cnt += 1
    # print(angleOrder)

def drawDrop():
    global gHierarchy, gMotion, gOffset, gRotation
    if gHierarchy is None:
        pass
    else: 
        tcnt = 0
        rcnt = 0
        a = 0
        for line in gHierarchy:
            if line[0] == '{':
                glPushMatrix()
            elif line[0] == '}':
                glPopMatrix()
            elif line[0] == "ROOT":
                a = 0
            elif line[0] == "JOINT":
                a = 1
            elif line[0] == "End":
                a = 2
            elif line[0] == "OFFSET":
                if a == 0:
                    glTranslatef(gOffset[tcnt][0], gOffset[tcnt][1], gOffset[tcnt][2])
                    rotate(gRotation[rcnt], rcnt)
                    rcnt += 1
                elif a == 1:
                    # drawLine(gOffset[tcnt])
                    drawCube(gOffset[tcnt])
                    glTranslatef(gOffset[tcnt][0], gOffset[tcnt][1], gOffset[tcnt][2])
                    rotate(gRotation[rcnt], rcnt)
                    rcnt += 1
                elif a == 2:
                    # drawLine(gOffset[tcnt])
                    drawCube(gOffset[tcnt])
                tcnt += 1
            
        

                

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
    global targetPoint, gAzimuth, gElevation, dist
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 1000)
    
    cameraWork()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity( )
    drawPlane()
 
    # lighting system
    lightingSystem()
    # glColor3ub(255, 255, 255)
    animate()
    drawDrop()
    # drawCube([2, 3, 4])

    
def main():
    if not glfw.init():
        return
    window = glfw.create_window(1000, 1000, "classAssignment3", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
    main()