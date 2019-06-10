import glfw
import numpy as numpy
from numpy import linalg as la
from OpenGL.GL import *
from OpenGL.GLU import *
import time

oldt = 0

def drawLine(v):
    glBegin(GL_LINES)
    glVertex2f(0, 0)
    glVertex2fv(v)
    glEnd()

def render():
    global oldt
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    # glVertex2f(0, 0)

    glPushMatrix()
    drawLine((1, 0.))
    glTranslatef(1, 0., 0)
    glRotatef(45, 0, 0, 1)
    glPushMatrix()
    drawLine((-1, 0.))
    glPopMatrix()
    glPopMatrix()
    newt = glfw.get_time()
    FPS = 10
    if newt - oldt >= 1 / FPS:
        oldt = newt
        print(oldt)
    # print(newt)
    

def main():
    if not glfw.init():
        return
    window = glfw.create_window(1000, 1000, "classAssignment2", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
    main()