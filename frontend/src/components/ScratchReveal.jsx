import React, { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ScratchReveal() {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isFullyRevealed, setIsFullyRevealed] = useState(false);
  const holdTimeoutRef = useRef(null);
  const [holdProgress, setHoldProgress] = useState(0);

  useEffect(() => {
    if (isFullyRevealed) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const container = containerRef.current;

    const resizeCanvas = () => {
      canvas.width = container.offsetWidth;
      canvas.height = container.offsetHeight;
      
      ctx.fillStyle = '#0A1A14'; 
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = 'rgba(255,255,255,0.02)';
      for (let i = 0; i < 5000; i++) {
        ctx.beginPath();
        ctx.arc(Math.random() * canvas.width, Math.random() * canvas.height, Math.random() * 2, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    return () => window.removeEventListener('resize', resizeCanvas);
  }, [isFullyRevealed]);

  const startHold = () => {
    let elapsed = 0;
    setHoldProgress(0);
    holdTimeoutRef.current = setInterval(() => {
      elapsed += 100;
      setHoldProgress(elapsed / 5000); 
      if (elapsed >= 5000) { 
        setIsFullyRevealed(true);
        clearInterval(holdTimeoutRef.current);
      }
    }, 100);
  };

  const clearHold = () => {
    if (holdTimeoutRef.current) {
      clearInterval(holdTimeoutRef.current);
      holdTimeoutRef.current = null;
    }
    setHoldProgress(0);
  };

  const scratch = (x, y) => {
    if (isFullyRevealed) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    ctx.globalCompositeOperation = 'destination-out';
    
    // Low opacity fill to create a "fade/eraser" effect 
    // It requires multiple passes over the same area to fully reveal the text
    ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
    
    // Decreased brush size by 50%
    const baseRadius = 60; 
    
    for (let i = 0; i < 60; i++) {
      const offsetX = (Math.random() - 0.5) * baseRadius * 1.2;
      const offsetY = (Math.random() - 0.5) * baseRadius * 1.2;
      const particleRadius = Math.random() * baseRadius * 0.4;
      
      ctx.beginPath();
      ctx.arc(x + offsetX, y + offsetY, particleRadius, 0, Math.PI * 2);
      ctx.fill();
    }
  };

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    if (e.touches && e.touches.length > 0) {
      return {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top
      };
    }
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  };

  const handlePointerDown = (e) => {
    if (isFullyRevealed) return;
    setIsDrawing(true);
    startHold();
    const { x, y } = getCoordinates(e);
    scratch(x, y);
  };

  const handlePointerMove = (e) => {
    if (!isDrawing || isFullyRevealed) return;
    const { x, y } = getCoordinates(e);
    scratch(x, y);
  };

  const handlePointerUp = () => {
    setIsDrawing(false);
    clearHold();
  };

  return (
    <div 
      ref={containerRef} 
      className="relative w-full h-screen flex items-center justify-center overflow-hidden bg-[#FAF9F6] dark:bg-stone-900"
      style={{ touchAction: 'none' }}
    >
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none select-none">
        <h1 className="text-[5rem] sm:text-[8rem] lg:text-[12rem] font-display font-black text-reserve-dark dark:text-reserve-light tracking-tighter opacity-90 drop-shadow-lg">
          ReServe
        </h1>
        <p className="text-xl sm:text-2xl text-stone-500 font-light italic tracking-widest uppercase mt-4">
          DevOps Edition
        </p>
      </div>

      <AnimatePresence>
        {!isFullyRevealed && (
          <motion.canvas
            ref={canvasRef}
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
            className="absolute inset-0 z-10 cursor-crosshair touch-none"
            onMouseDown={handlePointerDown}
            onMouseMove={handlePointerMove}
            onMouseUp={handlePointerUp}
            onMouseLeave={handlePointerUp}
            onTouchStart={handlePointerDown}
            onTouchMove={handlePointerMove}
            onTouchEnd={handlePointerUp}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {!isFullyRevealed && (
          <motion.div 
            initial={{ opacity: 0.6 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20 pointer-events-none flex flex-col items-center mix-blend-difference text-white"
          >
            <span className="animate-pulse font-bold tracking-widest text-sm uppercase mb-4">
              Scratch or Hold for 5s to reveal
            </span>
            
            {holdProgress > 0 && (
              <div className="w-32 h-1 bg-white/20 rounded-full overflow-hidden mb-2">
                <motion.div 
                  className="h-full bg-white"
                  style={{ width: `${holdProgress * 100}%` }}
                />
              </div>
            )}
            
            <div className="w-px h-12 bg-gradient-to-b from-white to-transparent" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
