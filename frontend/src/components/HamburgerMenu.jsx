import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function HamburgerMenu({ setActivePersona, activePersona }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);

  // Initialize theme
  useEffect(() => {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDark(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.theme = 'light';
      setIsDark(false);
    } else {
      document.documentElement.classList.add('dark');
      localStorage.theme = 'dark';
      setIsDark(true);
    }
  };

  const handleAdminAccess = () => {
    setActivePersona('admin');
    setIsOpen(false);
  };

  const handleGoHome = () => {
    setActivePersona('landing');
    setIsOpen(false);
  };

  return (
    <>
      {/* Floating Hamburger Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed top-6 right-6 z-50 w-12 h-12 bg-white/80 dark:bg-stone-800/80 backdrop-blur-md rounded-full shadow-lg flex flex-col items-center justify-center gap-1.5 border border-stone-200 dark:border-stone-700 hover:scale-105 transition-transform"
      >
        <div className="w-5 h-0.5 bg-stone-800 dark:bg-white rounded-full"></div>
        <div className="w-5 h-0.5 bg-stone-800 dark:bg-white rounded-full"></div>
        <div className="w-5 h-0.5 bg-stone-800 dark:bg-white rounded-full"></div>
      </button>

      {/* Drawer Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm flex justify-end"
            onClick={() => setIsOpen(false)}
          >
            {/* Drawer */}
            <motion.div 
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="w-80 h-full bg-[#FAF9F6] dark:bg-stone-900 shadow-2xl flex flex-col p-8 border-l border-stone-200 dark:border-stone-800"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-12">
                <h2 className="text-2xl font-display font-black text-reserve-dark dark:text-reserve-light">Menu</h2>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="w-10 h-10 flex items-center justify-center rounded-full bg-stone-100 dark:bg-stone-800 text-stone-500 hover:text-stone-900 dark:hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="flex flex-col gap-6">
                {activePersona !== 'landing' && (
                  <button 
                    onClick={handleGoHome}
                    className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-stone-800 shadow-sm border border-stone-100 dark:border-stone-700 text-left font-semibold text-stone-800 dark:text-white hover:bg-stone-50 dark:hover:bg-stone-700 transition-colors"
                  >
                    <span>Back to Home</span>
                    <span>→</span>
                  </button>
                )}

                <div className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-stone-800 shadow-sm border border-stone-100 dark:border-stone-700">
                  <span className="font-semibold text-stone-800 dark:text-white">Theme</span>
                  <button 
                    onClick={toggleTheme}
                    className="relative w-14 h-8 rounded-full bg-stone-200 dark:bg-stone-600 transition-colors p-1"
                  >
                    <motion.div 
                      layout
                      className="w-6 h-6 rounded-full bg-white dark:bg-stone-900 shadow-md flex items-center justify-center text-xs"
                      style={{ marginLeft: isDark ? 'auto' : 0 }}
                    >
                      {isDark ? '🌙' : '☀️'}
                    </motion.div>
                  </button>
                </div>

                <div className="mt-8 border-t border-stone-200 dark:border-stone-800 pt-8">
                  <p className="text-xs font-bold text-stone-400 uppercase tracking-widest mb-4">Internal Tooling</p>
                  <button 
                    onClick={handleAdminAccess}
                    className="w-full flex items-center justify-center py-4 rounded-xl bg-stone-900 dark:bg-white text-white dark:text-stone-900 font-bold hover:scale-[1.02] transition-transform shadow-lg"
                  >
                    Admin Console 🔒
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
