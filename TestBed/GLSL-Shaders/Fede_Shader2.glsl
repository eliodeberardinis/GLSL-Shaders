#version 430 core

uniform vec2 resolution;
uniform float globalTime;

#define PI 3.1415926535897931

void main()
{
	vec2 uv = gl_FragCoord.xy / resolution.xy;
    vec3 uvz = vec3(gl_FragCoord.xy / resolution.xy * 2.0 - vec2(1.0, 1.0), 0.0);
    uvz.z =  uvz.x*resolution.x/resolution.y;
	vec4 sans = texture2D(iChannel0, uv);
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    if (sans.w == 1.0) 
    	gl_FragColor = sans;
    else {        
        gl_FragColor.z=(uvz.x*uvz.x+uvz.y*uvz.y)*(abs(uvz.x)*abs(uvz.y))/2.0;
        //fragColor.z=max(uvz.x*uvz.x, uvz.y*uvz.y)/3.0;
	}
}
