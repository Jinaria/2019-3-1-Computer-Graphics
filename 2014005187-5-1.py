import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

def render(M):
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

	glColor3ub(255, 255, 255)

	# draw point p
	glBegin(GL_POINTS)
	# your implementation
	glVertex2fv((M @ np.array([.5, 0., 1.]))[:2])
	glEnd()

	# draw vector v
	glBegin(GL_LINES)
	# your implementation
	glVertex2fv(np.array([0., 0., 0.])[:2])
	glVertex2fv((M @ np.array([.5, 0., 0.]))[:2])
	glEnd()

def main():
	if not glfw.init():
		return
	window = glfw.create_window(480, 480, "2014005187-5-1", None, None)
	if not window:
		glfw.terminate()
		return
	
	glfw.make_context_current(window)
	while not glfw.window_should_close(window):
		glfw.poll_events()
		t = glfw.get_time()
		R = np.array([[np.cos(t), -np.sin(t), 0.],
					  [np.sin(t), np.cos(t),  0.],
					  [0., 		  0., 		  1.]])
		T = np.identity(3)
		T[0, 2] = 0.5
		render(R @ T)
		glfw.swap_buffers(window)
	glfw.terminate()

if __name__ == "__main__":
	main()