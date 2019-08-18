import pygame, OpenGL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

verticies= (
	(1, -1, -1),
	(1, 1, -1),
	(-1, 1, -1),
	(-1, -1, -1),
	(1, -1, 1),
	(1, 1, 1),
	(-1, -1, 1),
	(-1, 1, 1)
)

edges = (
	(0,1),
	(0,3),
	(0,4),
	(2,1),
	(2,3),
	(2,7),
	(6,3),
	(6,4),
	(6,7),
	(5,1),
	(5,4),
	(5,7)
)

surfaces = (
	(0,1,2,3),
	(3,2,7,6),
	(6,7,5,4),
	(4,5,1,0),
	(1,5,7,2),
	(4,0,3,6)
)

colors = (
	(1,0,0),
	(0,1,0),
	(0,0,1),
	(0,1,0),
	(1,1,1),
	(0,1,1),
	(1,0,0),
	(0,1,0),
	(0,0,1),
	(1,0,0),
	(1,1,1),
	(0,1,1),
)

def Cube():
	glBegin(GL_LINES)
	for edge in edges:
		for vertex in edge:
			glVertex3fv(verticies[vertex])
	glEnd()

def main():
	pygame.init()
	
	display = (800,600)
	aspectRatio = float(display[0])/display[1]
	fov = 45
	
	pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
	# setting up perspective, FOV, display ratio, drawing distances
	gluPerspective(fov, aspectRatio, 0.1, 50.0)
	# moving our camera by -5 along Z axis
	glTranslatef(0.0,0.0, -5)
	
	while True:		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					quit()
				if event.key == pygame.K_LEFT:
					 glRotatef(5, 0, 1, 0)
				if event.key == pygame.K_RIGHT:
					glRotatef(5, 0, -1, 0)

				if event.key == pygame.K_UP:
					glRotatef(5, 1, 0, 0)
				if event.key == pygame.K_DOWN:
					glRotatef(5, -1, 0, 0)

				if event.key == pygame.K_q:
					glRotatef(5, 0, 0, 1)
				if event.key == pygame.K_e:
					glRotatef(5, 0, 0, -1)
		
		# glRotatef(1, 1, 0, 0)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		Cube()
		pygame.display.flip()
		

		pygame.time.wait(10)
		
main()