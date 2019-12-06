import glfw
import numpy as np
from numpy import linalg as la
from OpenGL.GL import *
from OpenGL.GLU import *

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

def drawLizard(factor):
    t = glfw.get_time() * factor # move speed adjust
    glColor3ub(255, 255, 0)

    #front body base
    glPushMatrix()
    glTranslatef(0, 1., 2)
    glRotatef(10 * np.sin(t), 0, 1, 0)

    #front body draw
    glPushMatrix()
    glScalef(1., 0.7, 1.6)
    drawSphere()
    # drawCube()
    glPopMatrix()
    
    glColor3ub(255, 0, 0)
    # head base
    glPushMatrix()
    glTranslatef(0., 0.3, 1.4)
    glRotatef(-10 * np.sin(t), 0, 1, 0)
    glTranslatef(0., 0., 1.)

    # head draw
    glPushMatrix()
    glScalef(0.8, 0.6, 1.)
    drawSphere()
    glPopMatrix() # head draw pop

    glPopMatrix() # head base pop

    glColor3ub(255, 0, 0)
    #left arm base
    glPushMatrix()
    glTranslatef(0.5, 0., 1.)
    glRotatef(90 + 30 * np.sin(t), 0, 1, 0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0., .8)
    
    #left arm draw
    glPushMatrix()
    glScalef(0.23, 0.23, 0.7)
    drawSphere()
    glPopMatrix()

    glColor3ub(0, 0, 255)
    #left low arm base
    glPushMatrix()
    
    glTranslatef(0., 0., 0.7)
    glRotatef(-20, 1, 0, 0)
    glRotatef(-90 - 30 * np.sin(t), 0,1,0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0., 0.6)
    
    #left low arm draw
    glPushMatrix()
    glScalef(0.2, 0.2, 0.6)
    drawSphere()
    glPopMatrix()

    glColor3ub(0, 255, 255)
    #left hand base
    glPushMatrix()
    glTranslatef(0., 0., 0.6)
    glRotatef(-20, 1, 0, 0)

    #left hand draw
    glPushMatrix()
    glScalef(0.3, 0.1, 0.3)
    drawCube()
    glPopMatrix()

    glPopMatrix() #left hand base pop
    glPopMatrix() #left low arm base pop
    glPopMatrix() #left arm base pop

    glColor3ub(255, 0, 0)
    #right arm base
    glPushMatrix()
    glTranslatef(-0.5, 0., 1.)
    glRotatef(-90 + 30 * np.sin(t), 0, 1, 0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0., .8)

    #right arm draw
    glPushMatrix()
    glScalef(0.23, 0.23, 0.7)
    drawSphere()
    glPopMatrix()

    glColor3ub(0, 0, 255)
    #right low arm base
    glPushMatrix()
    
    glTranslatef(0., 0., 0.7)
    glRotatef(-20, 1, 0, 0)
    glRotatef(90 - 30 * np.sin(t), 0, 1, 0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0., 0.6)
    
    #right low arm draw
    glPushMatrix()
    glScalef(0.2, 0.2, 0.6)
    drawSphere()
    glPopMatrix()

    glColor3ub(0, 255, 255)
    #right hand base
    glPushMatrix()
    glTranslatef(0., 0., 0.6)
    glRotatef(-20, 1, 0, 0)

    #right hand draw
    glPushMatrix()
    glScalef(0.3, 0.1, 0.3)
    drawCube()
    glPopMatrix()

    glPopMatrix() # right hand base pop
    glPopMatrix() # right low arm base pop
    glPopMatrix() # right arm base pop

    glColor3ub(255, 0, 0)
    # back body base
    glPushMatrix()
    glTranslatef(0., 0., -1.4)
    glRotatef(-20 * np.sin(t), 0, 1, 0)
    glTranslatef(0., 0., -1.6)

    # back body draw
    glPushMatrix()
    glScalef(1.0, 0.7, 1.6)
    drawSphere()
    # drawCube()
    glPopMatrix()

    glColor3ub(0, 0, 255)
    # left leg base
    glPushMatrix()
    glTranslatef(0.5, 0., -1.0)
    glRotatef(90 - 30 * np.sin(t), 0, 1, 0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0., .8)

    # left leg draw
    glPushMatrix()
    glScalef(0.23, 0.23, 0.7)
    drawSphere()
    glPopMatrix()

    glColor3ub(0, 255, 255)
    #left low leg base
    glPushMatrix()
    glTranslatef(0., 0., 0.7)
    glRotatef(-20, 1, 0, 0)
    glRotatef(90 + 30 * np.sin(t), 0, 1, 0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0, 0.6)

    #left low leg draw
    glPushMatrix()
    glScalef(0.2, 0.2, 0.6)
    drawSphere()
    glPopMatrix()

    glColor3ub(255, 0, 255)
    #left leg foot base
    glPushMatrix()
    glTranslatef(0., 0., 0.6)
    glRotatef(-20, 1, 0, 0)

    #left leg foot draw
    glPushMatrix()
    glScalef(0.3, 0.1, 0.3)
    drawCube()
    glPopMatrix()

    glPopMatrix()
    glPopMatrix()
    glPopMatrix()

    glColor3ub(0, 0, 255)
    # right leg base
    glPushMatrix()
    glTranslatef(-0.5, 0., -1.0)
    glRotatef(-90 - 30 * np.sin(t), 0, 1, 0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0., .8)

    # right leg draw
    glPushMatrix()
    glScalef(0.23, 0.23, 0.7)
    drawSphere()
    glPopMatrix()

    glColor3ub(0, 255, 255)
    #right low leg base
    glPushMatrix()
    
    glTranslatef(0., 0., 0.7)
    glRotatef(-20, 1, 0, 0)
    glRotatef(-90 + 30 * np.sin(t), 0, 1, 0)
    glRotatef(20, 1, 0, 0)
    glTranslatef(0., 0., 0.6)

    #right low leg draw
    glPushMatrix()
    glScalef(0.2, 0.2, 0.6)
    drawSphere()
    glPopMatrix()

    glColor3ub(255, 0, 255)
    #right leg foot base
    glPushMatrix()
    glTranslatef(0., 0., 0.6)
    glRotatef(-20, 1, 0, 0)

    #right leg foot draw
    glPushMatrix()
    glScalef(0.3, 0.1, 0.3)
    drawCube()
    glPopMatrix()

    glPopMatrix()
    glPopMatrix()
    glPopMatrix()

    glColor3ub(0, 0, 255)
    # tail 1 base
    glPushMatrix()
    glTranslatef(0, 0, -1.6)
    glRotatef(-10 * np.sin(t), 0,1,0)
    glTranslatef(0, 0, -0.8)

    # tail 1 draw
    glPushMatrix()
    glScalef(0.8, 0.6, 0.8)
    # drawCube()
    drawSphere()
    glPopMatrix() #tail 1 draw pop

    glColor3ub(0, 255, 255)
    # tail 2 base
    glPushMatrix()
    glTranslatef(0, 0, -0.8)
    glRotatef(-10 * np.sin(t), 0,1,0)
    glTranslatef(0, 0, -0.8)

    #tail 2 draw
    glPushMatrix()
    glScalef(0.6, 0.4, 0.8)
    drawSphere()
    glPopMatrix() #tail 2 draw pop

    glColor3ub(255, 0, 255)
    #tail 3 base
    glPushMatrix()
    glTranslatef(0, 0, -0.8)
    glRotatef(-10 * np.sin(t), 0,1,0)
    glTranslatef(0, 0, -0.8)

    #tail 3 draw
    glPushMatrix()
    glScalef(0.4, 0.2, 0.8)
    drawSphere()
    glPopMatrix() #tail 3 draw pop

    glPopMatrix() #tail 3 base pop
    glPopMatrix() #tail 2 base pop
    glPopMatrix() #tail 1 base pop
    glPopMatrix() #back body baes pop
    glPopMatrix() #frond body base pop


def render():
    global targetPoint, gAzimuth, gElevation, dist
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity( )
    gluPerspective(45, 1, 1, 1000)
    
    cameraWork()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity( )

    drawPlane()
    drawLizard(6)
    
    
    
    
def main():
    if not glfw.init():
        return
    window = glfw.create_window(1000, 1000, "classAssignment1", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glfw.make_context_current(window)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        # func
        # glClear(GL_COLOR_BUFFER_BIT)
        render()
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
    main()