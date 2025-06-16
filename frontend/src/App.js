import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import axios from 'axios';
import './App.css';

// Import components
import LandingPage from './components/LandingPage';
import EchoVerse from './components/EchoVerse';
import EgoCore from './components/EgoCore';
import UserProfile from './components/UserProfile';
import AIChat from './components/AIChat';
import SocialFeed from './components/SocialFeed';
import MonetizationHub from './components/MonetizationHub';
import VRExplorer from './components/VRExplorer';
import NavigationMenu from './components/NavigationMenu';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Global Context
const AppContext = createContext();

// Context Provider
const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [currentMode, setCurrentMode] = useState('echoverse');
  const [loading, setLoading] = useState(true);
  const [aiPersonality, setAiPersonality] = useState({});
  const [userInsights, setUserInsights] = useState([]);

  // Initialize user or create demo user
  useEffect(() => {
    initializeUser();
  }, []);

  const initializeUser = async () => {
    try {
      // Check for existing user in localStorage
      const savedUserId = localStorage.getItem('echoverse_user_id');
      if (savedUserId) {
        const response = await axios.get(`${API}/users/${savedUserId}`);
        setUser(response.data);
        setCurrentMode(response.data.current_mode);
      } else {
        // Create demo user
        await createDemoUser();
      }
    } catch (error) {
      console.error('Error initializing user:', error);
      await createDemoUser();
    } finally {
      setLoading(false);
    }
  };

  const createDemoUser = async () => {
    try {
      const demoUser = {
        username: `Explorer_${Math.random().toString(36).substr(2, 6)}`,
        email: `demo@echoverse.ai`
      };
      const response = await axios.post(`${API}/users`, demoUser);
      setUser(response.data);
      localStorage.setItem('echoverse_user_id', response.data.id);
    } catch (error) {
      console.error('Error creating demo user:', error);
    }
  };

  const switchMode = async (mode) => {
    if (!user) return;
    try {
      await axios.post(`${API}/users/${user.id}/mode`, null, { 
        params: { mode } 
      });
      setCurrentMode(mode);
      trackBehavior('mode_switch', { from: currentMode, to: mode });
    } catch (error) {
      console.error('Error switching mode:', error);
    }
  };

  const trackBehavior = async (eventType, eventData) => {
    if (!user) return;
    try {
      await axios.post(`${API}/behavior/track`, {
        user_id: user.id,
        event_type: eventType,
        event_data: eventData
      });
    } catch (error) {
      console.error('Error tracking behavior:', error);
    }
  };

  const updateUserJourney = async (step, responses) => {
    if (!user) return;
    try {
      await axios.post(`${API}/journey/${user.id}/step`, {
        step,
        responses
      });
      trackBehavior('journey_progress', { step, responses });
    } catch (error) {
      console.error('Error updating journey:', error);
    }
  };

  const getUserInsights = async () => {
    if (!user) return;
    try {
      const response = await axios.get(`${API}/analytics/${user.id}/insights`);
      setUserInsights(response.data);
    } catch (error) {
      console.error('Error getting insights:', error);
    }
  };

  const contextValue = {
    user,
    setUser,
    currentMode,
    setCurrentMode,
    switchMode,
    loading,
    trackBehavior,
    updateUserJourney,
    aiPersonality,
    setAiPersonality,
    userInsights,
    getUserInsights
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

// Mode Toggle Component
const ModeToggle = () => {
  const { currentMode, switchMode } = useApp();

  return (
    <div className="fixed top-4 right-4 z-50">
      <motion.div
        className="flex items-center space-x-2 bg-black/20 backdrop-blur-lg rounded-full p-2 border border-white/10"
        whileHover={{ scale: 1.05 }}
      >
        <button
          onClick={() => switchMode('echoverse')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
            currentMode === 'echoverse'
              ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
              : 'text-white/70 hover:text-white'
          }`}
        >
          🌌 Echo
        </button>
        <button
          onClick={() => switchMode('egocore')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
            currentMode === 'egocore'
              ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white'
              : 'text-white/70 hover:text-white'
          }`}
        >
          ⚡ Ego
        </button>
      </motion.div>
    </div>
  );
};

// Animated Background Component
const AnimatedBackground = ({ mode }) => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <AnimatePresence mode="wait">
        {mode === 'echoverse' ? (
          <motion.div
            key="echo-bg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
            className="absolute inset-0 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900"
          >
            {/* Floating particles */}
            {[...Array(50)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-white rounded-full opacity-30"
                animate={{
                  x: [0, 100, 0],
                  y: [0, -100, 0],
                  opacity: [0.3, 0.8, 0.3]
                }}
                transition={{
                  duration: Math.random() * 10 + 10,
                  repeat: Infinity,
                  ease: "linear"
                }}
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`
                }}
              />
            ))}
          </motion.div>
        ) : (
          <motion.div
            key="ego-bg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
            className="absolute inset-0 bg-gradient-to-br from-gray-900 via-red-900 to-black"
          >
            {/* Electric lines */}
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute h-px bg-gradient-to-r from-transparent via-red-500 to-transparent opacity-20"
                animate={{
                  scaleX: [0, 1, 0],
                  opacity: [0, 0.5, 0]
                }}
                transition={{
                  duration: Math.random() * 3 + 2,
                  repeat: Infinity,
                  delay: Math.random() * 2
                }}
                style={{
                  width: '200px',
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  transform: `rotate(${Math.random() * 360}deg)`
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Main App Component
function App() {
  const { loading, currentMode } = useApp();

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="App min-h-screen relative">
      <AnimatedBackground mode={currentMode} />
      <BrowserRouter>
        <NavigationMenu />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/echoverse" element={<EchoVerse />} />
          <Route path="/egocore" element={<EgoCore />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="/chat" element={<AIChat />} />
          <Route path="/social" element={<SocialFeed />} />
          <Route path="/premium" element={<MonetizationHub />} />
          <Route path="/vr" element={<VRExplorer />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster 
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)'
          }
        }}
      />
    </div>
  );
}

// Export wrapped App
export default function WrappedApp() {
  return (
    <AppProvider>
      <App />
    </AppProvider>
  );
}