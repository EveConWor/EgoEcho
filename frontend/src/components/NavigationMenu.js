import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../App';

const NavigationMenu = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, currentMode, switchMode } = useApp();
  const [isOpen, setIsOpen] = useState(false);

  const menuItems = [
    {
      id: 'home',
      label: 'Home',
      path: '/',
      icon: '🏠',
      description: 'Return to main dashboard'
    },
    {
      id: 'echoverse',
      label: 'EchoVerse',
      path: '/echoverse',
      icon: '🌌',
      description: 'Identity exploration journey',
      mode: 'echoverse'
    },
    {
      id: 'egocore',
      label: 'EgoCore',
      path: '/egocore',
      icon: '⚡',
      description: 'AI companion challenges',
      mode: 'egocore'
    },
    {
      id: 'chat',
      label: 'AI Chat',
      path: '/chat',
      icon: '💬',
      description: 'Conversation with AI'
    },
    {
      id: 'social',
      label: 'Community',
      path: '/social',
      icon: '🌐',
      description: 'Social feed and connections'
    },
    {
      id: 'vr',
      label: 'VR Explorer',
      path: '/vr',
      icon: '🥽',
      description: 'Virtual reality spaces'
    },
    {
      id: 'premium',
      label: 'Premium',
      path: '/premium',
      icon: '💎',
      description: 'Subscription and features'
    },
    {
      id: 'profile',
      label: 'Profile',
      path: '/profile',
      icon: '👤',
      description: 'User dashboard and settings'
    }
  ];

  const handleNavigation = (item) => {
    // Switch mode if needed
    if (item.mode && item.mode !== currentMode) {
      switchMode(item.mode);
    }
    
    navigate(item.path);
    setIsOpen(false);
  };

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const MenuButton = () => (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => setIsOpen(!isOpen)}
      className={`fixed top-4 left-4 z-50 w-12 h-12 rounded-full flex items-center justify-center glass transition-all ${
        isOpen 
          ? 'bg-white/20 backdrop-blur-lg' 
          : currentMode === 'echoverse' 
            ? 'bg-gradient-to-r from-purple-500/80 to-blue-500/80' 
            : 'bg-gradient-to-r from-red-500/80 to-orange-500/80'
      }`}
    >
      <motion.div
        animate={{ rotate: isOpen ? 45 : 0 }}
        transition={{ duration: 0.2 }}
      >
        {isOpen ? '✕' : '☰'}
      </motion.div>
    </motion.button>
  );

  const MenuItem = ({ item, index }) => (
    <motion.button
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ x: 5, backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
      onClick={() => handleNavigation(item)}
      className={`w-full flex items-center space-x-4 p-4 rounded-xl text-left transition-all ${
        isActive(item.path)
          ? currentMode === 'echoverse'
            ? 'bg-gradient-to-r from-purple-500/30 to-blue-500/30 border border-purple-500/50'
            : 'bg-gradient-to-r from-red-500/30 to-orange-500/30 border border-red-500/50'
          : 'hover:bg-white/10'
      }`}
    >
      <div className="text-2xl">{item.icon}</div>
      
      <div className="flex-1">
        <div className="text-white font-medium">{item.label}</div>
        <div className="text-white/60 text-sm">{item.description}</div>
      </div>
      
      {isActive(item.path) && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="w-2 h-2 bg-gradient-to-r from-purple-400 to-blue-400 rounded-full"
        />
      )}
    </motion.button>
  );

  const UserInfo = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="p-4 border-t border-white/10"
    >
      {user ? (
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold bg-gradient-to-r ${
            currentMode === 'echoverse' 
              ? 'from-purple-500 to-blue-500' 
              : 'from-red-500 to-orange-500'
          }`}>
            {user.username?.charAt(0).toUpperCase()}
          </div>
          
          <div className="flex-1">
            <div className="text-white font-medium">{user.username}</div>
            <div className={`text-sm ${
              currentMode === 'echoverse' ? 'text-purple-300' : 'text-red-300'
            }`}>
              {currentMode === 'echoverse' ? '🌌 EchoVerse' : '⚡ EgoCore'} Mode
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-xs text-white/60">Level</div>
            <div className="text-white font-bold">{user.level || 1}</div>
          </div>
        </div>
      ) : (
        <div className="text-center">
          <div className="text-white/60 mb-2">Welcome to</div>
          <div className="text-white font-bold">EchoVerse & EgoCore</div>
        </div>
      )}
    </motion.div>
  );

  const ModeToggle = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
      className="p-4 border-t border-white/10"
    >
      <div className="text-white/70 text-sm mb-3">Switch Mode</div>
      
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => {
            switchMode('echoverse');
            setIsOpen(false);
          }}
          className={`p-3 rounded-xl text-center transition-all ${
            currentMode === 'echoverse'
              ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
              : 'bg-white/10 text-white/70 hover:bg-white/20'
          }`}
        >
          <div className="text-lg mb-1">🌌</div>
          <div className="text-xs">Echo</div>
        </button>
        
        <button
          onClick={() => {
            switchMode('egocore');
            setIsOpen(false);
          }}
          className={`p-3 rounded-xl text-center transition-all ${
            currentMode === 'egocore'
              ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white'
              : 'bg-white/10 text-white/70 hover:bg-white/20'
          }`}
        >
          <div className="text-lg mb-1">⚡</div>
          <div className="text-xs">Ego</div>
        </button>
      </div>
    </motion.div>
  );

  const QuickStats = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7 }}
      className="p-4 border-t border-white/10"
    >
      <div className="text-white/70 text-sm mb-3">Quick Stats</div>
      
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-white font-bold">{user?.experience_points || 0}</div>
          <div className="text-xs text-white/60">XP</div>
        </div>
        
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-white font-bold">{user?.credits || 100}</div>
          <div className="text-xs text-white/60">Credits</div>
        </div>
        
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-white font-bold">{user?.streak_days || 0}</div>
          <div className="text-xs text-white/60">Streak</div>
        </div>
      </div>
    </motion.div>
  );

  return (
    <>
      <MenuButton />
      
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            />
            
            {/* Menu Panel */}
            <motion.div
              initial={{ x: '-100%', opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: '-100%', opacity: 0 }}
              transition={{ type: 'spring', damping: 20, stiffness: 300 }}
              className="fixed top-0 left-0 h-full w-80 bg-black/80 backdrop-blur-xl border-r border-white/10 z-50 overflow-y-auto"
            >
              {/* Header */}
              <div className="p-6 pt-20">
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center mb-6"
                >
                  <h2 className="text-2xl font-bold text-gradient mb-2">
                    Navigation
                  </h2>
                  <p className="text-white/60 text-sm">
                    Explore your digital identity journey
                  </p>
                </motion.div>
                
                {/* Menu Items */}
                <div className="space-y-2">
                  {menuItems.map((item, index) => (
                    <MenuItem key={item.id} item={item} index={index} />
                  ))}
                </div>
              </div>
              
              {/* User Info */}
              <UserInfo />
              
              {/* Mode Toggle */}
              <ModeToggle />
              
              {/* Quick Stats */}
              {user && <QuickStats />}
              
              {/* Footer */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="p-4 border-t border-white/10 text-center"
              >
                <div className="text-xs text-white/40">
                  EchoVerse & EgoCore v2.0
                </div>
                <div className="text-xs text-white/40">
                  Singularity Platform
                </div>
              </motion.div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default NavigationMenu;