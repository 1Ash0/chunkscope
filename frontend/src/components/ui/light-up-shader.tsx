"use client"

import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

const InteractiveStarfieldShader = () => {
    const containerRef = useRef<HTMLDivElement>(null);
    const materialRef = useRef<THREE.ShaderMaterial>();

    // React state to control shader uniforms
    const [hasActive, setHasActive] = useState(false);
    const [hasUpcoming, setHasUpcoming] = useState(false);
    const [dimmingDisabled, setDimmingDisabled] = useState(false);

    // Update shader uniforms when state changes
    useEffect(() => {
        if (materialRef.current) {
            materialRef.current.uniforms.hasActiveReminders.value = hasActive;
        }
    }, [hasActive]);

    useEffect(() => {
        if (materialRef.current) {
            materialRef.current.uniforms.hasUpcomingReminders.value = hasUpcoming;
        }
    }, [hasUpcoming]);

    useEffect(() => {
        if (materialRef.current) {
            materialRef.current.uniforms.disableCenterDimming.value = dimmingDisabled;
        }
    }, [dimmingDisabled]);


    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        // 1) Renderer + Scene + Camera + Clock
        let renderer: THREE.WebGLRenderer;
        try {
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);
        } catch (err) {
            console.error('WebGL not supported', err);
            container.innerHTML = '<p style="color:white;text-align:center;">Sorry, WebGL isn’t available.</p>';
            return;
        }

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        const clock = new THREE.Clock();

        // 2) Shaders
        const vertexShader = `
      varying vec2 vTextureCoord;
      void main() {
        vTextureCoord = uv;
        gl_Position = vec4(position, 1.0);
      }
    `;

        const fragmentShader = `
      precision mediump float;
      uniform vec2 iResolution;
      uniform float iTime;
      uniform bool hasActiveReminders;
      uniform bool hasUpcomingReminders;
      uniform bool disableCenterDimming;
      varying vec2 vTextureCoord;

      void mainImage(out vec4 O, in vec2 fragCoord) {
        O = vec4(0.0, 0.0, 0.0, 1.0);
        
        // Configuration for horizontal streaks
        vec2 b = vec2(0.5, 0.003); // Wide x, narrow y for horizontal streaks
        vec2 p;
        mat2 R = mat2(1.0, 0.0, 0.0, 1.0);
        
        // Calculate distance from center for dimming the center
        vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
        float dist = length(uv);
        
        // Center glow effect (Horizontal Beam)
        float beam = 0.001 / abs(uv.y) * smoothstep(0.8, 0.0, abs(uv.x));
        O.rgb += beam * vec3(1.0, 0.9, 0.7);

        // Core Black Hole Mask
        float centerDim = disableCenterDimming ? 1.0 : smoothstep(0.1, 0.3, dist);
        
        // Particles Loop
        for(int i = 0; i < 40; i++) {
          float fi = float(i) + 1.0;
          
          // Rotation for variation
          float angle = fi * 137.5; // Golden angle
          float c = cos(angle);
          float s = sin(angle);
          R = mat2(c, -s, s, c);
          
          // Motion logic - horizontal focus
          vec2 coord = fragCoord / iResolution.y * (fi * 0.05 + 0.1) + vec2(iTime * (0.5 + fi * 0.1), 0.0);
          vec2 frac_coord = fract(coord) - 0.5;
          p = R * frac_coord;
          
          vec2 clamped_p = clamp(p, -b, b);
          float len = length(clamped_p - p);
          
          if (len > 0.0) {
            // Color variations based on fi and reminder states
            vec3 col = 0.5 + 0.5 * cos(fi + vec3(0, 2, 4));
            
            if (hasActiveReminders) col = mix(col, vec3(0.0, 0.5, 1.0), 0.7);
            if (hasUpcomingReminders) col = mix(col, vec3(1.0, 0.5, 0.0), 0.7);
            
            vec4 star = 1e-3 / len * vec4(col, 1.0);
            O += star;
          }
        }
        
        // Post-processing
        O.rgb *= centerDim; // Apply black hole dimming
        O.rgb = pow(O.rgb, vec3(0.8)); // Gamma correction for pop
        O.a = 1.0;
      }

      void main() {
        vec4 color;
        mainImage(color, vTextureCoord * iResolution);
        gl_FragColor = color;
      }
    `;

        // 3) Material, Geometry, Mesh
        const uniforms = {
            iTime: { value: 0 },
            iResolution: { value: new THREE.Vector2() },
            hasActiveReminders: { value: hasActive },
            hasUpcomingReminders: { value: hasUpcoming },
            disableCenterDimming: { value: dimmingDisabled }
        };
        const material = new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms });
        materialRef.current = material;
        const geometry = new THREE.PlaneGeometry(2, 2);
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // 4) Resize Handler
        const onResize = () => {
            const w = container.clientWidth;
            const h = container.clientHeight;
            renderer.setSize(w, h);
            uniforms.iResolution.value.set(w, h);
        };

        window.addEventListener('resize', onResize);
        onResize();

        // 5) Animation Loop
        renderer.setAnimationLoop(() => {
            uniforms.iTime.value = clock.getElapsedTime();
            renderer.render(scene, camera);
        });

        // 6) Cleanup
        return () => {
            window.removeEventListener('resize', onResize);
            renderer.setAnimationLoop(null);
            const canvas = renderer.domElement;
            if (canvas && canvas.parentNode) {
                canvas.parentNode.removeChild(canvas);
            }
            material.dispose();
            geometry.dispose();
            renderer.dispose();
        };
    }, []);

    const buttonStyle = "px-6 py-3 rounded-xl font-bold transition-all duration-300 backdrop-blur-md border border-white/10 text-white shadow-lg whitespace-nowrap";

    return (
        <div className="fixed inset-0 w-full h-full -z-10 bg-black">
            <div ref={containerRef} className="w-full h-full" />

            {/* Control Panel */}
            <div className="fixed bottom-12 left-1/2 -translate-x-1/2 z-50 flex flex-wrap justify-center gap-4 p-4 bg-white/5 backdrop-blur-2xl rounded-3xl border border-white/10 shadow-2xl scale-90 md:scale-100">
                <button
                    onClick={() => setHasActive(!hasActive)}
                    className={`${buttonStyle} ${hasActive ? 'bg-blue-600/60 border-blue-400/50' : 'bg-black/40 hover:bg-white/10'}`}
                >
                    Active Reminders
                </button>
                <button
                    onClick={() => setHasUpcoming(!hasUpcoming)}
                    className={`${buttonStyle} ${hasUpcoming ? 'bg-orange-600/60 border-orange-400/50' : 'bg-black/40 hover:bg-white/10'}`}
                >
                    Upcoming Reminders
                </button>
                <button
                    onClick={() => setDimmingDisabled(!dimmingDisabled)}
                    className={`${buttonStyle} ${dimmingDisabled ? 'bg-red-600/60 border-red-400/50' : 'bg-black/40 hover:bg-white/10'}`}
                >
                    Disable Dimming
                </button>
            </div>
        </div>
    );
};

export default InteractiveStarfieldShader;
