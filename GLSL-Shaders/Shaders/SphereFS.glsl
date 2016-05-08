// Raytraced plane and sphere with fake ambient occlusion

#version 430 core

uniform vec2 resolution;
uniform float globalTime;

vec4 sph1 = vec4(0.0, 1.0, 0.0, 1.0);
vec3 light = normalize(vec3(0.57703));

float intersectSphere(in vec3 ro, in vec3 rd, in vec4 sph) {
    vec3 oc = ro - sph.xyz;
    float b = 2.0 * dot(oc, rd);
    float c = dot(oc, oc) - sph.w * sph.w;
    float h = b * b - 4.0 * c;

    if (h < 0.0) {
        return -1.0;
    }

    float t = (-b - sqrt(h)) / 2.0;
    return t;
}

vec3 normalSphere(in vec3 p, in vec4 sph) {
    return (p - sph.xyz) / sph.w;
}

float intersectPlane(in vec3 ro, in vec3 rd) {
    return -ro.y / rd.y;
}

vec3 normalPlane(in vec3 p) {
    return vec3(0.0, 1.0, 0.0);
}

float intersect(in vec3 ro, in vec3 rd, out float resT) {
    resT = 1000.0;
    float id = -1.0;
    float tSphere = intersectSphere(ro, rd, sph1);
    float tPlane = intersectPlane(ro, rd);

    if (tSphere > 0.0) {
        id = 1.0;
        resT = tSphere;
    }

    if (tPlane > 0.0 && tPlane < resT) {
        id = 2.0;
        resT = tPlane;
    }

    return id;
}

void main() {

    vec2 uv = gl_FragCoord.xy / resolution.xy;

    sph1.x = -0.5 * cos(globalTime);
    sph1.z = 0.5 * sin(globalTime);

    // ray
    vec3 ro = vec3(0.0, 1.0, 3.0);
    vec3 rd = normalize(vec3((-1.0 + 2.0 * uv) * vec2(resolution.x / resolution.y, 1.0), -1.0));

    float t;
    float id = intersect(ro, rd, t);

    vec3 color = vec3(0.01);
    if (id == 1.0) {
        vec3 p = ro + t * rd;
        vec3 n = normalSphere(p, sph1);

        float ao = 0.5 + 0.5 * n.y;
        float dif = clamp(dot(n, light), 0.0, 1.0);

        color = vec3(0.9, 0.8, 0.6) * dif * ao + vec3(0.1, 0.2, 0.4) * ao;

    } else if (id == 2.0) {
        vec3 p = ro + t * rd;
        vec3 n = normalPlane(p);

        float amb = smoothstep(0.0, 2.0 * sph1.w, length(p.xz - sph1.xz));

        color = vec3(amb * 0.7);
    }

    color = sqrt(color);

    gl_FragColor = vec4(color, 1.0);
}
