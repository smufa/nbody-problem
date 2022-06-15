#version 330

in vec2 square;
in float teem;

out vec4 color;

void main() {
    float dist = length(vec2(0.5, 0.5) - square.xy);
    if (dist > 0.5) {
        discard;
    }
    color = vec4(teem,1,1,1);
}
