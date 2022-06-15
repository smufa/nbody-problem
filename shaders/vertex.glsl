#version 430

in vec4 in_vert;
in vec4 mass;

out vec2 vert_pos;
out float vert_rad;
out float team;

void main() {
    vert_pos = in_vert.xy;
    vert_rad = in_vert.w;
    team = mass.y;
}
