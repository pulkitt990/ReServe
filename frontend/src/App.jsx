import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import DonorDashboard from './components/DonorDashboard';
import NGODashboard from './components/NGODashboard';
import AdminDashboard from './components/AdminDashboard';
import HeroLanding from './components/HeroLanding';
import HamburgerMenu from './components/HamburgerMenu';

const PageWrapper = ({ children, setActivePersona, persona }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.4, ease: "easeOut" }}
    className="w-full min-h-screen pt-24 px-6 md:px-12 max-w-7xl mx-auto pb-24"
  >
    {persona && persona !== 'landing' && (
      <button 
        onClick={() => setActivePersona('landing')}
        className="mb-8 flex items-center text-sm font-bold text-stone-500 hover:text-stone-800 transition-colors bg-white/50 px-4 py-2 rounded-full border border-stone-200 w-max cursor-pointer z-50 relative"
      >
        <span className="mr-2">←</span> Back to Home Screen
      </button>
    )}
    {children}
  </motion.div>
);

function App() {
  const [activePersona, setActivePersonaState] = useState('landing');
  const [hasVisitedDashboard, setHasVisitedDashboard] = useState(false);
  const [listings, setListings] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const setActivePersona = (persona) => {
    if (persona !== 'landing') {
      setHasVisitedDashboard(true);
    }
    setActivePersonaState(persona);
  };

  const fetchListings = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/listings/');
      const data = await res.json();
      setListings(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const fetchForecasts = async () => {
    try {
      const res = await fetch('/api/v1/forecasting/donor/1');
      const data = await res.json();
      if (Array.isArray(data)) setForecasts(data);
      else setForecasts([]);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (activePersona !== 'landing') {
      fetchListings();
      if (activePersona === 'donor') {
        fetchForecasts();
      }
    }
  }, [activePersona]);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const formatCountdown = (minutes) => {
    if (minutes < 0) return { text: "Expired", urgent: false };
    if (minutes < 60) return { text: `${Math.round(minutes)}m left`, urgent: true };
    const h = Math.floor(minutes / 60);
    const m = Math.round(minutes % 60);
    return { text: `${h}h ${m}m`, urgent: false };
  };

  return (
    <div className="min-h-screen bg-reserve-surface dark:bg-stone-900 font-sans transition-colors duration-500 overflow-x-hidden">
      
      <HamburgerMenu activePersona={activePersona} setActivePersona={setActivePersona} />

      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-6 left-1/2 -translate-x-1/2 z-[100] bg-reserve-dark text-white px-6 py-3 rounded-full shadow-2xl font-semibold text-sm flex items-center gap-2"
          >
            <span className="w-2 h-2 rounded-full bg-reserve-light animate-pulse" />
            {notification}
          </motion.div>
        )}
      </AnimatePresence>

      <main className="w-full relative">
        <AnimatePresence mode="wait">
          {activePersona === 'landing' && (
            <motion.div
              key="landing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
              className="w-full"
            >
              <HeroLanding setActivePersona={setActivePersona} skipReveal={hasVisitedDashboard} />
            </motion.div>
          )}
          {activePersona === 'donor' && (
            <PageWrapper key="donor" persona="donor" setActivePersona={setActivePersona}>
              <div className="mb-8">
                <h2 className="text-4xl font-display font-black text-reserve-dark dark:text-reserve-light">Donor Console</h2>
                <p className="text-stone-500 mt-2">Manage your surplus and predictive models.</p>
              </div>
              <DonorDashboard 
                forecasts={forecasts} 
                fetchForecasts={fetchForecasts} 
                setNotification={setNotification} 
                listings={listings} 
                loading={loading} 
                setShowCreateModal={setShowCreateModal} 
                formatCountdown={formatCountdown} 
              />
            </PageWrapper>
          )}
          {activePersona === 'ngo' && (
            <PageWrapper key="ngo" persona="ngo" setActivePersona={setActivePersona}>
              <div className="mb-8">
                <h2 className="text-4xl font-display font-black text-reserve-dark dark:text-reserve-light">NGO Dispatch</h2>
                <p className="text-stone-500 mt-2">Review intelligent allocations and claim surplus.</p>
              </div>
              <NGODashboard 
                listings={listings} 
                loading={loading} 
                setNotification={setNotification} 
                fetchListings={fetchListings} 
                formatCountdown={formatCountdown} 
              />
            </PageWrapper>
          )}
          {activePersona === 'admin' && (
            <PageWrapper key="admin" persona="admin" setActivePersona={setActivePersona}>
              <div className="mb-8">
                <h2 className="text-4xl font-display font-black text-reserve-dark dark:text-reserve-light">Admin Telemetry</h2>
                <p className="text-stone-500 mt-2">Platform-wide metrics and engine health.</p>
              </div>
              <AdminDashboard 
                listings={listings} 
                loading={loading} 
              />
            </PageWrapper>
          )}
        </AnimatePresence>
      </main>

    </div>
  );
}

export default App;
