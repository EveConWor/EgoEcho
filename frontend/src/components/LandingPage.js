import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, currentMode } = useApp();
  const [currentText, setCurrentText] = useState(0);

  const heroTexts = [
    "Discover Your Digital Identity",
    "Explore the Depths of Self",
    "Create Your Personal Mythology",
    "Unlock Your Infinite Potential"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentText((prev) => (prev + 1) % heroTexts.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleEnterExperience = () => {
    if (currentMode === 'echoverse') {
      navigate('/echoverse');
    } else {
      navigate('/egocore');
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center text-white relative overflow-hidden">
      
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="text-center z-10 max-w-4xl mx-auto px-6"
      >
        {/* Logo/Brand */}
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="mb-8"
        >
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-3xl font-bold mb-4">
            ∞
          </div>
        </motion.div>

        {/* Animated Hero Text */}
        <motion.h1
          key={currentText}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.8 }}
          className="text-5xl md:text-7xl font-bold mb-6 text-gradient"
        >
          {heroTexts[currentText]}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="text-xl md:text-2xl mb-8 text-white/80 leading-relaxed"
        >
          Welcome to the intersection of identity and technology. 
          Experience dual paths of self-discovery through EchoVerse and EgoCore.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <button
            onClick={handleEnterExperience}
            className="btn-primary text-lg px-8 py-4 hover:scale-105 transition-transform"
          >
            Enter Experience
          </button>
          <button
            onClick={() => navigate('/profile')}
            className="btn-secondary text-lg px-8 py-4"
          >
            View Profile
          </button>
        </motion.div>

        {/* User Info */}
        {user && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5, duration: 0.8 }}
            className="mt-8 text-white/60"
          >
            Welcome back, <span className="text-purple-400 font-semibold">{user.username}</span>
          </motion.div>
        )}
      </motion.div>

      {/* Feature Cards */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 1 }}
        className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto px-6 mt-16"
      >
        {/* EchoVerse Card */}
        <motion.div
          whileHover={{ scale: 1.05, y: -5 }}
          className="card cursor-pointer"
          onClick={() => navigate('/echoverse')}
        >
          <div className="text-4xl mb-4">🌌</div>
          <h3 className="text-2xl font-bold mb-3 text-gradient">EchoVerse</h3>
          <p className="text-white/70 mb-4">
            Journey through contemplative identity exploration. Discover your essence, 
            mindscape, aesthetic, and personal narrative through guided reflection.
          </p>
          <div className="flex items-center text-purple-400 font-medium">
            Explore Identity →
          </div>
        </motion.div>

        {/* EgoCore Card */}
        <motion.div
          whileHover={{ scale: 1.05, y: -5 }}
          className="card cursor-pointer"
          onClick={() => navigate('/egocore')}
        >
          <div className="text-4xl mb-4">⚡</div>
          <h3 className="text-2xl font-bold mb-3 text-gradient-ego">EgoCore</h3>
          <p className="text-white/70 mb-4">
            Engage with your AI companion for dynamic growth challenges. 
            Experience behavioral insights, personalized motivation, and continuous evolution.
          </p>
          <div className="flex items-center text-red-400 font-medium">
            Meet Your AI →
          </div>
        </motion.div>
      </motion.div>

      {/* Stats/Info Bar */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2, duration: 1 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <div className="flex items-center space-x-8 text-white/50 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>AI System Active</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span>Singularity Mode</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
            <span>Phase 1 Active</span>
          </div>
        </div>
      </motion.div>

      {/* Floating Elements */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white/10 rounded-full"
            animate={{
              x: [0, 100, -100, 0],
              y: [0, -100, 100, 0],
              opacity: [0.1, 0.5, 0.1]
            }}
            transition={{
              duration: Math.random() * 20 + 10,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default LandingPage;