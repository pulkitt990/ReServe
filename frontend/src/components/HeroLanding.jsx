import React, { useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, Float, Sparkles, ContactShadows, OrbitControls } from '@react-three/drei';
import { motion } from 'framer-motion';
import * as THREE from 'three';
import ScratchReveal from './ScratchReveal';

const START_TIME = 4 * 3600; 
const DURATION = 60; 

const CountdownRing = ({ startTimeRef, onReset }) => {
  const materialRef = useRef();
  const groupRef = useRef();
  const [hovered, setHover] = useState(false);

  useFrame(() => {
    const elapsed = (Date.now() - startTimeRef.current) / 1000;
    let timeRatio = 1.0 - (elapsed / DURATION);
    if (timeRatio < 0) timeRatio = 0;

    if (materialRef.current) {
      materialRef.current.uniforms.uTimeRatio.value = timeRatio;
      const targetColor = new THREE.Color(
        timeRatio > 0.5 ? '#1B4332' : 
        timeRatio > 0.25 ? '#E8A33D' : 
        '#DC2626'
      );
      materialRef.current.uniforms.uColor.value.lerp(targetColor, 0.1);
    }

    if (groupRef.current) {
      groupRef.current.rotation.z -= 0.002;
      const targetScale = hovered ? 1.05 : 1;
      groupRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.15);
    }
  });

  return (
    <group 
      ref={groupRef} 
      rotation={[Math.PI / 6, 0, 0]}
      onPointerOver={() => { document.body.style.cursor = 'grab'; setHover(true); }}
      onPointerOut={() => { document.body.style.cursor = 'auto'; setHover(false); }}
      onPointerDown={() => { document.body.style.cursor = 'grabbing'; }}
      onPointerUp={() => { document.body.style.cursor = 'grab'; }}
      onClick={(e) => {
        e.stopPropagation();
        onReset();
      }}
    >
      <mesh>
        <torusGeometry args={[3.2, 0.35, 64, 128]} />
        <meshPhysicalMaterial color="#0A1A14" metalness={0.9} roughness={0.1} clearcoat={1.0} clearcoatRoughness={0.05} />
      </mesh>
      
      <mesh>
        <torusGeometry args={[3.2, 0.1, 32, 128]} />
        <shaderMaterial
          ref={materialRef}
          args={[{
            uniforms: { uTimeRatio: { value: 1.0 }, uColor: { value: new THREE.Color('#1B4332') } },
            vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
            fragmentShader: `uniform float uTimeRatio; uniform vec3 uColor; varying vec2 vUv; void main() { if (vUv.x > uTimeRatio) discard; gl_FragColor = vec4(uColor * 1.5, 1.0); }`,
            transparent: true, side: THREE.DoubleSide
          }]}
        />
      </mesh>

      <Sparkles count={hovered ? 150 : 80} scale={10} size={hovered ? 5 : 3} speed={0.4} opacity={0.4} color="#E8A33D" />
    </group>
  );
};

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const SloganWord = ({ text, isLight }) => {
  const slogan3DShadow = `1px 1px 0px #d6d3d1, 2px 2px 0px #d6d3d1, 3px 3px 0px #d6d3d1, 4px 4px 0px #d6d3d1, 5px 5px 15px rgba(0,0,0,0.15)`;
  const slogan3DShadowHover = `1px 1px 0px #d6d3d1, 2px 2px 0px #d6d3d1, 3px 3px 0px #d6d3d1, 4px 4px 0px #d6d3d1, 5px 5px 0px #d6d3d1, 6px 6px 0px #d6d3d1, 7px 7px 25px rgba(0,0,0,0.2)`;

  return (
    <motion.span 
      className={`inline-block mr-[0.2em] origin-center ${isLight ? 'font-light text-stone-400 dark:text-stone-500 italic' : 'font-black text-[#1B4332] dark:text-[#52B788]'}`}
      style={{ textShadow: isLight ? 'none' : slogan3DShadow }}
      whileHover={{ scale: 1.15, y: -8, textShadow: isLight ? 'none' : slogan3DShadowHover, color: isLight ? '#a8a29e' : '#2D6A4F' }}
      whileTap={{ scale: 0.95, y: 0 }}
      transition={{ type: 'spring', stiffness: 400, damping: 15 }}
    >
      {text}
    </motion.span>
  );
};

export default function HeroLanding({ setActivePersona, skipReveal }) {
  const timeTextRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  useEffect(() => {
    let animationFrameId;
    const tick = () => {
      const elapsed = (Date.now() - startTimeRef.current) / 1000;
      let timeRatio = 1.0 - (elapsed / DURATION);
      if (timeRatio < 0) timeRatio = 0;
      
      const currentSeconds = Math.max(0, START_TIME * timeRatio);
      
      if (timeTextRef.current) {
        timeTextRef.current.innerText = formatTime(currentSeconds);
        const color = timeRatio > 0.5 ? '#1B4332' : timeRatio > 0.25 ? '#E8A33D' : '#DC2626';
        timeTextRef.current.style.color = color;
      }
      animationFrameId = requestAnimationFrame(tick);
    };

    animationFrameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  const handleReset = () => {
    startTimeRef.current = Date.now();
    if (timeTextRef.current) {
      timeTextRef.current.animate([{ transform: 'scale(1.15)' }, { transform: 'scale(1)' }], { duration: 400, easing: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)' });
    }
  };

  return (
    <div className="w-full bg-[#FAF9F6] dark:bg-stone-900 font-sans selection:bg-[#1B4332] selection:text-white transition-colors duration-500">
      
      {/* Stage 1: The Scratch Reveal */}
      {!skipReveal && <ScratchReveal />}

      {/* Stage 2: The 3D Hero */}
      <div className="relative w-full min-h-screen flex flex-col md:flex-row items-center justify-between px-8 md:px-24 py-24 md:py-0">
        
        <div className="z-10 w-full md:w-[55%] flex flex-col justify-center cursor-default pb-12 md:pb-0">
          <h1 className="text-[3.5rem] sm:text-[4.5rem] lg:text-[6.5rem] tracking-tight text-stone-900 leading-[1.05] font-display mb-6">
            <div className="mb-2">
              <SloganWord text="Race" /><SloganWord text="against" /><br /><SloganWord text="the" /><SloganWord text="clock," />
            </div>
            <div>
              <SloganWord text="never" isLight /><SloganWord text="against" isLight /><br /><SloganWord text="the" isLight /><SloganWord text="dumpster." isLight />
            </div>
          </h1>
          <p className="mt-6 text-lg md:text-xl text-stone-500 dark:text-stone-400 max-w-md leading-relaxed font-medium">
            Intelligent surplus forecasting and predictive rescue matching. We turn perishable liabilities into immediate impact.
          </p>
        </div>

        <div className="relative z-20 w-[400px] h-[400px] sm:w-[550px] sm:h-[550px] md:w-[750px] md:h-[750px] flex items-center justify-center shrink-0 mt-12 md:mt-0">
          <div className="absolute inset-0 z-0 drop-shadow-2xl">
            <Canvas camera={{ position: [0, 0, 15], fov: 45 }} dpr={[1, 2]}>
              <ambientLight intensity={1.5} color="#ffffff" />
              <directionalLight position={[10, 20, 10]} intensity={3} />
              <directionalLight position={[-10, -10, -10]} intensity={1.5} color="#E8A33D" />
              <Environment preset="city" />
              <Float speed={2} rotationIntensity={0.2} floatIntensity={0.3}>
                <CountdownRing startTimeRef={startTimeRef} onReset={handleReset} />
              </Float>
              <ContactShadows position={[0, -4.0, 0]} opacity={0.4} scale={15} blur={2.5} far={10} color="#0A1A14" />
              <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={1.0} makeDefault />
            </Canvas>
          </div>

          <div className="z-10 absolute inset-0 flex flex-col items-center justify-center pointer-events-none pt-2">
            <span ref={timeTextRef} className="text-5xl sm:text-6xl lg:text-7xl font-black tabular-nums tracking-tighter drop-shadow-md" style={{ color: '#1B4332' }}>
              04:00:00
            </span>
          </div>
        </div>
      </div>

      {/* Stage 3: Persona Selection Gateway */}
      <div className="w-full flex flex-col items-center justify-start px-6 pb-32 pt-8 z-30 relative -mt-12 md:-mt-24">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl md:text-6xl font-display font-black text-stone-900 dark:text-white mb-6">Who are you?</h2>
          <p className="text-stone-500 dark:text-stone-400 text-xl max-w-2xl mx-auto">Select your persona to enter the ReServe dashboard experience.</p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-10 w-full max-w-5xl">
          {/* Donor Card */}
          <motion.button 
            onClick={() => setActivePersona('donor')}
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            whileHover={{ y: -15, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="group relative overflow-hidden bg-stone-50 dark:bg-stone-800 p-12 rounded-[2.5rem] shadow-2xl text-left border border-stone-200 dark:border-stone-700"
          >
            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="text-9xl">🏪</span>
            </div>
            <div className="relative z-10">
              <span className="inline-block py-2 px-4 rounded-full bg-reserve-dark/10 dark:bg-reserve-light/10 text-reserve-dark dark:text-reserve-light font-bold text-sm uppercase tracking-widest mb-6">
                Kitchen / Bakery
              </span>
              <h3 className="text-4xl font-black text-stone-900 dark:text-white mb-4">I am a Donor</h3>
              <p className="text-stone-500 dark:text-stone-400 text-lg leading-relaxed max-w-sm">
                Post surplus food before it perishes. Use our ML models to predict your upcoming waste and save money.
              </p>
              <div className="mt-10 flex items-center text-reserve-dark dark:text-reserve-light font-bold">
                Enter Dashboard <span className="ml-2 group-hover:translate-x-2 transition-transform">→</span>
              </div>
            </div>
          </motion.button>

          {/* NGO Card */}
          <motion.button 
            onClick={() => setActivePersona('ngo')}
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            whileHover={{ y: -15, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="group relative overflow-hidden bg-stone-50 dark:bg-stone-800 p-12 rounded-[2.5rem] shadow-2xl text-left border border-stone-200 dark:border-stone-700"
          >
            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="text-9xl">🤝</span>
            </div>
            <div className="relative z-10">
              <span className="inline-block py-2 px-4 rounded-full bg-reserve-urgency/10 text-reserve-urgency font-bold text-sm uppercase tracking-widest mb-6">
                NGO / Shelter
              </span>
              <h3 className="text-4xl font-black text-stone-900 dark:text-white mb-4">I am an NGO</h3>
              <p className="text-stone-500 dark:text-stone-400 text-lg leading-relaxed max-w-sm">
                Rescue food instantly. Let our allocation engine match you with the best available surplus based on distance and capacity.
              </p>
              <div className="mt-10 flex items-center text-reserve-urgency font-bold">
                Enter Dashboard <span className="ml-2 group-hover:translate-x-2 transition-transform">→</span>
              </div>
            </div>
          </motion.button>
        </div>
      </div>

    </div>
  );
}
