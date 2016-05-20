
#version 430 core

uniform vec2 resolution;
uniform float globalTime;

void main()
{
	vec2 uv = gl_FragCoord.xy / resolution.xy;
	gl_FragColor = vec4(uv,0.5+0.5*sin(globalTime),1.0);
}
