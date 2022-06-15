#version 430
layout (points) in;
layout (triangle_strip, max_vertices=4) out;

//kaaaaj je to
uniform Projection {
    uniform mat4 matrix;
} projection;

in vec2 vert_pos[];
in float vert_rad[];
in float team[];

out vec2 square;
out float teem;

void main() {
    vec2 center = vert_pos[0];
    vec2 rad = vec2(vert_rad[0]);

    gl_Position = projection.matrix * vec4(vec2(-rad.x, rad.y) + center, 0.0, 1.0);
    square = vec2(0,1);
    teem = team[0];
    EmitVertex();

    gl_Position = projection.matrix * vec4(vec2(-rad.x, -rad.y) + center, 0.0, 1.0);
    square = vec2(0,0);
    teem = team[0];
    EmitVertex();

    gl_Position = projection.matrix * vec4(vec2(rad.x, rad.y) + center, 0.0, 1.0);
    square = vec2(1,1);
    teem = team[0];
    EmitVertex();

    gl_Position = projection.matrix * vec4(vec2(rad.x, -rad.y) + center, 0.0, 1.0);
    square = vec2(1,0);
    teem = team[0];
    EmitVertex();
    EndPrimitive();
}
