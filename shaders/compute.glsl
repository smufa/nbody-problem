#version 430
layout(local_size_x=256, local_size_y=1) in;

//uniform float timeStep;
struct Body {
    vec4 position;
    vec4 velocity;
    vec4 mass;
};

layout(std430, binding=0) buffer in_bodies {
    Body bodies[];
} In;

layout(std430, binding=1) buffer out_bodies {
    Body bodies[];
} Out;

void main() {
    int index = int(gl_GlobalInvocationID.x);
    Body current = In.bodies[index];
    vec3 accel = vec3(0.0, 0.0, 0.0);
    for (int i = 0; i < In.bodies.length(); i++) {
       //if (i == index) {
       //    continue;
       //}
       Body j = In.bodies[i];
       float min_dist = 1;
       float temp = max(distance(j.position.xyz, current.position.xyz), min_dist);
       temp = temp * temp * temp;
       temp =  j.mass.x / temp;
       accel += (j.position.xyz - current.position.xyz) * temp;
    }
    float timeStep = 1;
    current.velocity.xyz += accel * timeStep;
    current.position.xyz += current.velocity.xyz * timeStep;
    Out.bodies[index] = current;
}
