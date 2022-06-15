import arcade
from arcade.gl import BufferDescription
from array import array
import random
import time
import math

class Window(arcade.Window):
    def __init__(self):
        # Initializing window
        super().__init__(1920, 1080,
                       "N-body sim",
                       gl_version=(4, 3),
                       fullscreen=True)
        # Number of bodies
        self.N = 3000
        # Generate structures
        self.starting_points = array('f', self.gen_galaxies())

        # GPU things
        # - create buffers for data
        self.points_buffer1 = self.ctx.buffer(data=self.starting_points)
        self.points_buffer2 = self.ctx.buffer(data=self.starting_points)
        # - define vertex names
        self.vao1 = self.ctx.geometry([BufferDescription(self.points_buffer1, '4f 4x4 4f', ['in_vert', 'mass'])], mode=self.ctx.POINTS)
        self.vao2 = self.ctx.geometry([BufferDescription(self.points_buffer2, '4f 4x4 4f', ['in_vert', 'mass'])], mode=self.ctx.POINTS)
        # - open shader files
        vertex_src = open('shaders/vertex.glsl').read()
        geometry_src = open('shaders/geometry.glsl').read()
        fragment_src = open('shaders/fragment.glsl').read()
        compute_src = open('shaders/compute.glsl').read()
        # - set shaders
        self.program = self.ctx.program(
            vertex_shader=vertex_src,
            geometry_shader=geometry_src,
            fragment_shader=fragment_src,
        )
        # - compute shader setup
        self.compute_shader = self.ctx.compute_shader(source=compute_src)

    def on_draw(self):
        self.clear()
        self.ctx.enable(self.ctx.BLEND)
        self.points_buffer1.bind_to_storage_buffer(binding=0)
        self.points_buffer2.bind_to_storage_buffer(binding=1)

        #self.compute_shader['timeStep'] = 0.0
        # Compute shader things
        self.compute_shader.run(group_x=256, group_y=1)
        # Draw
        self.vao2.render(self.program)
        # Swap buffers
        self.points_buffer1, self.points_buffer2 = self.points_buffer2, self.points_buffer1
        self.vao1, self.vao2 = self.vao2, self.vao1
    ##DELETE
    def gen_random(self):
        radius = 1.0
        for i in range(self.N):
            yield random.random() * 1920
            yield random.random() * 1080
            yield random.random() * 1080
            yield radius

            yield random.random() - 0.5
            yield random.random() - 0.5
            yield random.random() - 0.5
            yield 0.0

            yield 1.0
            yield 0.0
            yield 0.0
            yield 0.0
    def gen_galaxies(self):
        for i in range(self.N):
            size = 2 + random.random()
            star_rad = 400
            angle = random.random() * math.pi * 2
            angle2 = random.random() * math.pi * 2
            distance = random.random() * star_rad

            if i % 2 == 0:
                yield distance * math.cos(angle) - star_rad + 800
            else:
                yield distance * math.cos(angle) + star_rad+ 1120
            yield distance * math.sin(angle) + 1080 / 2
            yield distance * math.sin(angle2)
            yield size/1.5

            if i % 2 == 0:
                yield math.cos(angle + math.pi / 2) * distance / 100 + 2
            else:
                yield math.cos(angle + math.pi / 2) * distance / 100 - 2
            yield math.sin(angle + math.pi / 2) * distance / 100
            yield math.sin(angle2 + math.pi / 2) * distance / 100
            yield 0.0

            yield size 
            if i % 2 == 0:
                yield 1.0
            else:
                yield 0.0 
            yield 0.0  
            yield 0.0  

if __name__=='__main__':
    app = Window()
    arcade.run()
