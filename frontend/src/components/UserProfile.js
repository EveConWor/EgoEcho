import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserProfile = () => {
  const navigate = useNavigate();
  const { user, currentMode, getUserInsights, userInsights, trackBehavior } = useApp();
  const [activeTab, setActiveTab] = useState('overview');
  const [userStats, setUserStats] = useState({});
  const [journeyProgress, setJourneyProgress] = useState({});

  useEffect(() => {
    if (user) {
      fetchUserData();
      getUserInsights();
      trackBehavior('profile_view', { tab: activeTab });
    }
  }, [user, activeTab]);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${API}/users/${user.id}`);
      setJourneyProgress(response.data.journey_progress || {});
      
      // Calculate stats
      const completedSteps = Object.keys(response.data.journey_progress || {}).length;
      const totalSteps = 4; // essence, mindscape, aesthetic, narrative
      
      setUserStats({
        journeyCompletion: Math.round((completedSteps / totalSteps) * 100),
        completedSteps,
        totalSteps,
        joinDate: new Date(response.data.created_at).toLocaleDateString(),
        currentMode: response.data.current_mode
      });
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const journeySteps = [
    { id: 'essence', title: 'Essence', icon: '🔮', color: 'from-purple-500 to-pink-500' },
    { id: 'mindscape', title: 'Mindscape', icon: '🧠', color: 'from-blue-500 to-purple-500' },
    { id: 'aesthetic', title: 'Aesthetic', icon: '🎨', color: 'from-green-500 to-blue-500' },
    { id: 'narrative', title: 'Narrative', icon: '📜', color: 'from-orange-500 to-red-500' }
  ];

  const StatCard = ({ title, value, subtitle, icon, color = 'from-purple-500 to-blue-500' }) => (
    <motion.div
      whileHover={{ scale: 1.05, y: -5 }}
      className="glass rounded-xl p-6 text-center"
    >
      <div className={`text-3xl mb-2 w-12 h-12 mx-auto rounded-full bg-gradient-to-r ${color} flex items-center justify-center`}>
        {icon}
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-lg text-white/90 mb-1">{title}</div>
      {subtitle && <div className="text-sm text-white/60">{subtitle}</div>}
    </motion.div>
  );

  const JourneyStepCard = ({ step, progress }) => {
    const isCompleted = progress && Object.keys(progress).length > 0;
    const responseCount = progress ? Object.keys(progress).length : 0;
    
    return (
      <motion.div
        whileHover={{ scale: 1.02 }}
        className={`glass rounded-xl p-6 border-2 transition-all ${
          isCompleted ? 'border-green-500/50 bg-green-500/10' : 'border-white/10'
        }`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`text-2xl w-10 h-10 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center`}>
              {step.icon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">{step.title}</h3>
              <div className="text-sm text-white/60">
                {isCompleted ? `${responseCount} responses` : 'Not started'}
              </div>
            </div>
          </div>
          
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
            isCompleted 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
              : 'bg-white/10 text-white/60 border border-white/20'
          }`}>
            {isCompleted ? 'Complete' : 'Pending'}
          </div>
        </div>
        
        {isCompleted && progress && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="border-t border-white/10 pt-4"
          >
            <div className="text-sm text-white/80">
              <div className="font-medium mb-2">Recent Responses:</div>
              {Object.entries(progress).slice(0, 2).map(([key, value], index) => (
                <div key={index} className="mb-2 p-2 bg-black/20 rounded text-xs">
                  {typeof value === 'string' ? value.substring(0, 100) + (value.length > 100 ? '...' : '') : JSON.stringify(value)}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>
    );
  };

  const tabs = [
    { id: 'overview', title: 'Overview', icon: '📊' },
    { id: 'journey', title: 'Journey', icon: '🗺️' },
    { id: 'insights', title: 'AI Insights', icon: '🧠' },
    { id: 'settings', title: 'Settings', icon: '⚙️' }
  ];

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        <div className="text-center">
          <div className="text-6xl mb-4">🤖</div>
          <h2 className="text-2xl font-bold mb-2">No User Found</h2>
          <p className="text-white/70 mb-6">Please return to home to initialize your profile.</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Go Home
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
            <h1 className="text-4xl font-bold text-gradient mb-2">Profile Dashboard</h1>
            <p className="text-white/70">Track your digital identity journey</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={`px-4 py-2 rounded-full text-sm font-medium ${
              currentMode === 'echoverse'
                ? 'bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-purple-300 border border-purple-500/30'
                : 'bg-gradient-to-r from-red-500/20 to-orange-500/20 text-red-300 border border-red-500/30'
            }`}>
              {currentMode === 'echoverse' ? '🌌 EchoVerse' : '⚡ EgoCore'} Mode
            </div>
            
            <button
              onClick={() => navigate('/')}
              className="btn-secondary"
            >
              ← Home
            </button>
          </div>
        </div>

        {/* User Info */}
        <div className="glass rounded-2xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-2xl font-bold">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{user.username}</h2>
                <p className="text-white/70">Joined {userStats.joinDate}</p>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-2xl font-bold text-gradient">
                {userStats.journeyCompletion}%
              </div>
              <div className="text-sm text-white/70">Journey Complete</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-8 bg-black/20 rounded-xl p-1">
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
              <span>{tab.title}</span>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Tab Content */}
      <div className="max-w-6xl mx-auto">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="grid md:grid-cols-4 gap-6 mb-8">
                <StatCard
                  title="Journey Steps"
                  value={`${userStats.completedSteps}/${userStats.totalSteps}`}
                  subtitle="Completed"
                  icon="🗺️"
                  color="from-purple-500 to-blue-500"
                />
                <StatCard
                  title="Completion"
                  value={`${userStats.journeyCompletion}%`}
                  subtitle="Overall Progress"
                  icon="📈"
                  color="from-green-500 to-teal-500"
                />
                <StatCard
                  title="AI Interactions"
                  value="Active"
                  subtitle="Learning Mode"
                  icon="🤖"
                  color="from-blue-500 to-purple-500"
                />
                <StatCard
                  title="Insights"
                  value={userInsights.insights?.length || 0}
                  subtitle="Generated"
                  icon="💡"
                  color="from-orange-500 to-red-500"
                />
              </div>

              {/* Quick Actions */}
              <div className="glass rounded-2xl p-6">
                <h3 className="text-xl font-semibold mb-4 text-gradient">Quick Actions</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  <button
                    onClick={() => navigate('/echoverse')}
                    className="btn-secondary text-left p-4"
                  >
                    <div className="text-2xl mb-2">🌌</div>
                    <div className="font-medium">Continue EchoVerse</div>
                    <div className="text-sm text-white/60">Identity exploration</div>
                  </button>
                  <button
                    onClick={() => navigate('/egocore')}
                    className="btn-secondary text-left p-4"
                  >
                    <div className="text-2xl mb-2">⚡</div>
                    <div className="font-medium">Challenge in EgoCore</div>
                    <div className="text-sm text-white/60">AI companion</div>
                  </button>
                  <button
                    onClick={() => navigate('/chat')}
                    className="btn-secondary text-left p-4"
                  >
                    <div className="text-2xl mb-2">💬</div>
                    <div className="font-medium">Chat with AI</div>
                    <div className="text-sm text-white/60">Free conversation</div>
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'journey' && (
            <motion.div
              key="journey"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="space-y-6">
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold mb-4 text-gradient">Journey Progress</h3>
                  <div className="w-full bg-white/10 rounded-full h-3 mb-6">
                    <motion.div
                      className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full"
                      animate={{ width: `${userStats.journeyCompletion}%` }}
                      transition={{ duration: 1 }}
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {journeySteps.map((step) => (
                    <JourneyStepCard
                      key={step.id}
                      step={step}
                      progress={journeyProgress[step.id]}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'insights' && (
            <motion.div
              key="insights"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="glass rounded-2xl p-6">
                <h3 className="text-xl font-semibold mb-6 text-gradient">AI-Generated Insights</h3>
                
                {userInsights.insights && userInsights.insights.length > 0 ? (
                  <div className="space-y-4">
                    {userInsights.insights.map((insight, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg p-4 border border-purple-500/20"
                      >
                        <div className="flex items-start space-x-3">
                          <div className="text-2xl">🧠</div>
                          <div className="flex-1">
                            <p className="text-white/90">{insight}</p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">🔮</div>
                    <h4 className="text-xl font-semibold mb-2 text-white/80">No Insights Yet</h4>
                    <p className="text-white/60 mb-6">
                      Continue your journey to unlock AI-generated insights about your identity and growth patterns.
                    </p>
                    <button
                      onClick={() => navigate('/echoverse')}
                      className="btn-primary"
                    >
                      Start Journey
                    </button>
                  </div>
                )}

                {userInsights.suggestions && userInsights.suggestions.length > 0 && (
                  <div className="mt-8 pt-6 border-t border-white/10">
                    <h4 className="text-lg font-semibold mb-4 text-white/90">Suggestions for Growth</h4>
                    <div className="flex flex-wrap gap-2">
                      {userInsights.suggestions.map((suggestion, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-orange-500/20 text-orange-300 rounded-full text-sm border border-orange-500/30"
                        >
                          {suggestion}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'settings' && (
            <motion.div
              key="settings"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="glass rounded-2xl p-6">
                <h3 className="text-xl font-semibold mb-6 text-gradient">Settings</h3>
                
                <div className="space-y-6">
                  <div>
                    <h4 className="text-lg font-medium mb-3 text-white/90">Account Information</h4>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-white/70 mb-2">Username</label>
                        <input
                          type="text"
                          value={user.username}
                          disabled
                          className="form-input w-full opacity-60"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-white/70 mb-2">Email</label>
                        <input
                          type="email"
                          value={user.email || 'Not provided'}
                          disabled
                          className="form-input w-full opacity-60"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-white/10 pt-6">
                    <h4 className="text-lg font-medium mb-3 text-white/90">Preferences</h4>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white/90">Default Mode</div>
                          <div className="text-sm text-white/60">
                            Currently: {currentMode === 'echoverse' ? 'EchoVerse' : 'EgoCore'}
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button className="btn-secondary text-sm">
                            Change
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-white/10 pt-6">
                    <h4 className="text-lg font-medium mb-3 text-red-400">Danger Zone</h4>
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                      <div className="text-red-300 mb-2">Reset Journey Progress</div>
                      <div className="text-sm text-red-200/70 mb-4">
                        This will permanently delete all your journey responses and start fresh.
                      </div>
                      <button className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        Reset Progress
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default UserProfile;