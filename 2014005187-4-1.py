import glfw
import numpy as np
from OpenGL.GL import *

new_M = np.identity(3)
g_M = np.identity(3)

def render(T):
	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()
	# draw coordinate
	glBegin(GL_LINES)
	glColor3ub(255, 0, 0)
	glVertex2fv(np.array([0., 0.]))
	glVertex2fv(np.array([1., 0.]))
	glColor3ub(0, 255, 0)		
	glVertex2fv(np.array([0., 0.]))
	glVertex2fv(np.array([0., 1.]))
	glEnd()
	# draw triangle
	glBegin(GL_TRIANGLES)
	glColor3ub(255, 255, 255)
	glVertex2fv((T @ np.array([.0, .5, 1.]))[:-1])
	glVertex2fv((T @ np.array([.0, .0, 1.]))[:-1])
	glVertex2fv((T @ np.array([.5, .0, 1.]))[:-1])
	glEnd()

def key_callback(window, key, scancode, action, mods):
	global new_M
	global g_M

	if action is not glfw.PRESS:
		return

	if key == glfw.KEY_Q:
		new_M = np.array([[1., 0., -0.1],
						  [0., 1., 0.  ],
						  [0., 0., 1.  ]])
		g_M = new_M @ g_M
	elif key == glfw.KEY_E:
		new_M = np.array([[1., 0., 0.1],
						  [0., 1., 0. ],
						  [0., 0., 1. ]])
		g_M = new_M @ g_M
	elif key == glfw.KEY_A:
		new_M = np.array([[np.cos(np.radians(10)), -np.sin(np.radians(10)), 0.],
						  [np.sin(np.radians(10)), np.cos(np.radians(10)),  0.],
						  [0.,                     0.,                       1.]])
		g_M = g_M @ new_M	
	elif key == glfw.KEY_D:
		new_M = np.array([[np.cos(np.radians(-10)), -np.sin(np.radians(-10)), 0.],
						  [np.sin(np.radians(-10)), np.cos(np.radians(-10)),  0.],
						  [0.,                      0.,                        1.]])
		g_M = g_M @ new_M
	elif key == glfw.KEY_1:
		new_M = g_M = np.identity(3);
	else:
		new_M = np.identity(3)

def main():
	global new_M
	global g_M
	if not glfw.init():
		return
	window = glfw.create_window(480, 480, "2014005187-4-1", None, None)
	if not window:
		glfw.terminate()
		return
	glfw.set_key_callback(window, key_callback)
	glfw.make_context_current(window)
	while not glfw.window_should_close(window):
		glfw.poll_events()
		render(g_M)
		glfw.swap_buffers(window)
	glfw.terminate()

if __name__ == "__main__":
	main()