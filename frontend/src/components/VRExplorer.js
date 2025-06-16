import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import axios from 'axios';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VRExplorer = () => {
  const navigate = useNavigate();
  const { user, currentMode, trackBehavior } = useApp();
  const [virtualSpaces, setVirtualSpaces] = useState([]);
  const [userAvatar, setUserAvatar] = useState(null);
  const [currentSpace, setCurrentSpace] = useState(null);
  const [isInVR, setIsInVR] = useState(false);
  const [vrSupported, setVrSupported] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('spaces');
  const vrSceneRef = useRef(null);

  const environmentTypes = {
    cosmic: {
      name: 'Cosmic Reflection',
      description: 'Vast starfield with floating crystals for deep contemplation',
      icon: '🌌',
      color: 'from-purple-600 to-blue-600'
    },
    minimal: {
      name: 'Minimal Void',
      description: 'Clean, minimalist space for pure thought',
      icon: '⬜',
      color: 'from-gray-600 to-gray-800'
    },
    nature: {
      name: 'Digital Forest',
      description: 'Serene digital nature for grounded exploration',
      icon: '🌲',
      color: 'from-green-600 to-emerald-600'
    },
    abstract: {
      name: 'Abstract Mindscape',
      description: 'Surreal environment representing the unconscious',
      icon: '🎨',
      color: 'from-pink-600 to-purple-600'
    }
  };

  useEffect(() => {
    if (user) {
      checkVRSupport();
      loadVirtualSpaces();
      loadUserAvatar();
      trackBehavior('vr_explorer_view', { timestamp: new Date().toISOString() });
    }
  }, [user]);

  const checkVRSupport = () => {
    if ('xr' in navigator) {
      navigator.xr.isSessionSupported('immersive-vr').then((supported) => {
        setVrSupported(supported);
      }).catch(() => {
        setVrSupported(false);
      });
    } else {
      setVrSupported(false);
    }
  };

  const loadVirtualSpaces = async () => {
    try {
      // Demo spaces - in production this would fetch from API
      const demoSpaces = [
        {
          id: '1',
          name: 'Cosmic Reflection Chamber',
          description: 'A vast cosmic space for deep self-reflection',
          environment_type: 'cosmic',
          creator_id: 'system',
          current_participants: ['demo1', 'demo2'],
          max_participants: 10,
          is_public: true,
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Minimalist Focus Zone',
          description: 'Pure white space for focused meditation',
          environment_type: 'minimal',
          creator_id: 'system',
          current_participants: ['demo3'],
          max_participants: 5,
          is_public: true,
          created_at: new Date().toISOString()
        },
        {
          id: '3',
          name: 'Digital Zen Garden',
          description: 'Virtual nature space for peaceful contemplation',
          environment_type: 'nature',
          creator_id: user?.id || 'system',
          current_participants: [],
          max_participants: 8,
          is_public: true,
          created_at: new Date().toISOString()
        }
      ];
      
      setVirtualSpaces(demoSpaces);
    } catch (error) {
      console.error('Error loading virtual spaces:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserAvatar = async () => {
    if (!user) return;

    try {
      // Demo avatar - in production this would fetch from API
      const demoAvatar = {
        id: '1',
        user_id: user.id,
        name: `${user.username} Avatar`,
        appearance: {
          head: {
            type: currentMode === 'echoverse' ? 'sphere' : 'crystal',
            material: currentMode === 'echoverse' ? 'cosmic_glass' : 'sharp_crystal',
            color: currentMode === 'echoverse' ? '#667eea' : '#ff6b6b',
            effects: currentMode === 'echoverse' ? ['gentle_glow'] : ['intense_glow']
          },
          body: {
            type: currentMode === 'echoverse' ? 'energy_form' : 'crystalline',
            material: currentMode === 'echoverse' ? 'flowing_energy' : 'angular_crystal',
            color: currentMode === 'echoverse' ? '#764ba2' : '#feca57'
          }
        },
        is_default: true
      };

      setUserAvatar(demoAvatar);
    } catch (error) {
      console.error('Error loading avatar:', error);
    }
  };

  const createVirtualSpace = async (environmentType, name, description) => {
    if (!user) return;

    try {
      const response = await axios.post(`${API}/xr/spaces`, {
        creator_id: user.id,
        environment_type: environmentType,
        name,
        custom_settings: { description }
      });

      const newSpace = response.data;
      setVirtualSpaces([newSpace, ...virtualSpaces]);
      toast.success('Virtual space created!');
      
      trackBehavior('vr_space_created', { environment_type: environmentType });
      
    } catch (error) {
      console.error('Error creating space:', error);
      toast.error('Failed to create virtual space');
    }
  };

  const joinVirtualSpace = async (spaceId) => {
    if (!user) return;

    try {
      setCurrentSpace(spaceId);
      
      // Simulate joining VR space
      toast.success('Entering virtual space...');
      setIsInVR(true);
      
      trackBehavior('vr_space_joined', { space_id: spaceId });
      
      // Simulate VR session duration
      setTimeout(() => {
        exitVR();
      }, 30000); // Auto-exit after 30 seconds for demo
      
    } catch (error) {
      console.error('Error joining space:', error);
      toast.error('Failed to enter virtual space');
    }
  };

  const exitVR = () => {
    setIsInVR(false);
    setCurrentSpace(null);
    toast.success('Exited virtual space');
    
    trackBehavior('vr_space_exited', { 
      space_id: currentSpace,
      session_duration: 30 // Demo duration
    });
  };

  const startVRSession = async () => {
    if (!vrSupported) {
      toast.error('VR not supported in this browser');
      return;
    }

    try {
      // Request VR session
      const session = await navigator.xr.requestSession('immersive-vr');
      setIsInVR(true);
      
      // Initialize VR scene (simplified for demo)
      initializeVRScene(session);
      
    } catch (error) {
      console.error('VR session error:', error);
      toast.error('Could not start VR session');
    }
  };

  const initializeVRScene = (session) => {
    // In a real implementation, this would set up the WebXR scene
    // with Three.js or A-Frame based on the space configuration
    console.log('VR Session started:', session);
    
    // Simulate VR experience
    setTimeout(() => {
      session.end();
      setIsInVR(false);
    }, 60000); // 1 minute demo session
  };

  const SpaceCard = ({ space }) => {
    const env = environmentTypes[space.environment_type];
    const occupancy = space.current_participants.length;
    const maxOccupancy = space.max_participants;
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.02, y: -5 }}
        className="glass rounded-2xl p-6 cursor-pointer"
        onClick={() => joinVirtualSpace(space.id)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 bg-gradient-to-r ${env.color} rounded-xl flex items-center justify-center text-2xl`}>
              {env.icon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">{space.name}</h3>
              <p className="text-white/60 text-sm">{env.name}</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-sm text-white/60">Occupancy</div>
            <div className="text-white font-medium">{occupancy}/{maxOccupancy}</div>
          </div>
        </div>

        <p className="text-white/70 mb-4">{space.description}</p>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${occupancy > 0 ? 'bg-green-400' : 'bg-gray-400'}`} />
            <span className="text-sm text-white/60">
              {occupancy > 0 ? `${occupancy} people inside` : 'Empty'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {space.is_public && (
              <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs">
                Public
              </span>
            )}
            <span className="text-purple-400 font-medium">Enter →</span>
          </div>
        </div>
      </motion.div>
    );
  };

  const AvatarCustomizer = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6"
    >
      <h3 className="text-xl font-semibold text-white mb-4">Avatar Customizer</h3>
      
      {userAvatar ? (
        <div className="space-y-6">
          {/* Avatar Preview */}
          <div className="text-center">
            <div className={`w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-r ${
              currentMode === 'echoverse' ? 'from-purple-500 to-blue-500' : 'from-red-500 to-orange-500'
            } flex items-center justify-center text-3xl relative overflow-hidden`}>
              <div className="absolute inset-0 bg-white/10 backdrop-blur-sm" />
              <span className="relative z-10">
                {currentMode === 'echoverse' ? '🌌' : '⚡'}
              </span>
            </div>
            <h4 className="text-white font-medium">{userAvatar.name}</h4>
            <p className="text-white/60 text-sm">
              {currentMode === 'echoverse' ? 'Cosmic Being' : 'Energy Crystal'}
            </p>
          </div>

          {/* Customization Options */}
          <div className="space-y-4">
            <div>
              <label className="block text-white/70 text-sm mb-2">Head Type</label>
              <select className="form-input w-full">
                <option value="sphere">Sphere</option>
                <option value="crystal">Crystal</option>
                <option value="geometric">Geometric</option>
              </select>
            </div>

            <div>
              <label className="block text-white/70 text-sm mb-2">Body Style</label>
              <select className="form-input w-full">
                <option value="energy_form">Energy Form</option>
                <option value="crystalline">Crystalline</option>
                <option value="wireframe">Wireframe</option>
              </select>
            </div>

            <div>
              <label className="block text-white/70 text-sm mb-2">Color Theme</label>
              <div className="grid grid-cols-5 gap-2">
                {['#667eea', '#ff6b6b', '#feca57', '#48cab3', '#fd79a8'].map((color, index) => (
                  <button
                    key={index}
                    className="w-full h-8 rounded-lg border-2 border-white/20 hover:border-white/50 transition-colors"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>
          </div>

          <button className="w-full btn-primary">
            Save Avatar
          </button>
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">👤</div>
          <p className="text-white/60 mb-4">Loading avatar...</p>
        </div>
      )}
    </motion.div>
  );

  const CreateSpaceModal = ({ isOpen, onClose }) => (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-6"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="glass rounded-2xl p-6 max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-xl font-semibold text-white mb-4">Create Virtual Space</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-white/70 text-sm mb-2">Environment Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(environmentTypes).map(([key, env]) => (
                    <button
                      key={key}
                      className="p-3 glass-dark rounded-lg hover:bg-white/10 transition-colors text-center"
                    >
                      <div className="text-2xl mb-1">{env.icon}</div>
                      <div className="text-sm text-white">{env.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-white/70 text-sm mb-2">Space Name</label>
                <input
                  type="text"
                  className="form-input w-full"
                  placeholder="My Reflection Space"
                />
              </div>

              <div>
                <label className="block text-white/70 text-sm mb-2">Description</label>
                <textarea
                  className="form-input w-full h-20 resize-none"
                  placeholder="Describe your virtual space..."
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button onClick={onClose} className="flex-1 btn-secondary">
                Cancel
              </button>
              <button className="flex-1 btn-primary">
                Create Space
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );

  const [showCreateModal, setShowCreateModal] = useState(false);

  const tabs = [
    { id: 'spaces', label: 'Virtual Spaces', icon: '🌐' },
    { id: 'avatar', label: 'Avatar', icon: '👤' },
    { id: 'experiences', label: 'Experiences', icon: '✨' }
  ];

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        <div className="text-center">
          <div className="text-6xl mb-4">🥽</div>
          <h2 className="text-2xl font-bold mb-2">Enter Virtual Reality</h2>
          <p className="text-white/70 mb-6">Sign in to explore virtual identity spaces</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Get Started
          </button>
        </div>
      </div>
    );
  }

  if (isInVR) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
        <div className="text-center text-white">
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-8xl mb-8"
          >
            🥽
          </motion.div>
          <h2 className="text-3xl font-bold mb-4">You're in VR!</h2>
          <p className="text-white/70 mb-8">Experiencing virtual reality...</p>
          
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-4 text-sm text-white/60">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>Connected to virtual space</span>
            </div>
            
            <div className="flex items-center justify-center space-x-4 text-sm text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
              <span>Avatar active</span>
            </div>
          </div>
          
          <button
            onClick={exitVR}
            className="mt-8 btn-secondary"
          >
            Exit VR
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen text-white p-6">
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto mb-8"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-gradient mb-2">VR Explorer</h1>
            <p className="text-white/70">Explore identity in virtual reality spaces</p>
          </div>
          
          <div className="flex items-center space-x-4">
            {vrSupported && (
              <div className="flex items-center space-x-2 glass rounded-xl px-4 py-2">
                <div className="w-2 h-2 bg-green-400 rounded-full" />
                <span className="text-sm">VR Ready</span>
              </div>
            )}
            
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              Create Space
            </button>
            
            <button onClick={() => navigate('/')} className="btn-secondary">
              ← Home
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 bg-black/20 rounded-xl p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Content */}
      <div className="max-w-6xl mx-auto">
        <AnimatePresence mode="wait">
          {activeTab === 'spaces' && (
            <motion.div
              key="spaces"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {virtualSpaces.map((space) => (
                    <SpaceCard key={space.id} space={space} />
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'avatar' && (
            <motion.div
              key="avatar"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-md mx-auto"
            >
              <AvatarCustomizer />
            </motion.div>
          )}

          {activeTab === 'experiences' && (
            <motion.div
              key="experiences"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-12"
            >
              <div className="text-6xl mb-4">✨</div>
              <h3 className="text-xl font-semibold mb-2">Shared Experiences</h3>
              <p className="text-white/60 mb-6">
                Join guided meditations, rituals, and challenges in VR
              </p>
              <button className="btn-primary">Coming Soon</button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <CreateSpaceModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
};

export default VRExplorer;