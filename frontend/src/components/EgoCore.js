import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import axios from 'axios';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const challengeTypes = [
  {
    id: 'growth',
    title: 'Growth Challenge',
    icon: '🚀',
    description: 'Push your boundaries and expand your capabilities',
    color: 'from-red-500 to-orange-500'
  },
  {
    id: 'reflection',
    title: 'Deep Reflection',
    icon: '🔥',
    description: 'Confront difficult truths about yourself',
    color: 'from-orange-500 to-yellow-500'
  },
  {
    id: 'action',
    title: 'Action Challenge',
    icon: '⚡',
    description: 'Turn insights into concrete actions',
    color: 'from-red-600 to-pink-500'
  }
];

const EgoCore = () => {
  const navigate = useNavigate();
  const { user, trackBehavior, getUserInsights, userInsights } = useApp();
  const [aiPersonality, setAiPersonality] = useState({
    energy: 0.8,
    directness: 0.7,
    challenge: 0.6
  });
  const [currentChallenge, setCurrentChallenge] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [aiResponse, setAiResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [personalizedPrompt, setPersonalizedPrompt] = useState('');

  useEffect(() => {
    trackBehavior('egocore_enter', { timestamp: new Date().toISOString() });
    fetchPersonalizedPrompt();
    getUserInsights();
  }, []);

  const fetchPersonalizedPrompt = async () => {
    if (!user) return;
    try {
      const response = await axios.get(`${API}/journey/${user.id}/prompts`, {
        params: { mode: 'egocore' }
      });
      setPersonalizedPrompt(response.data.prompt);
    } catch (error) {
      console.error('Error fetching prompt:', error);
    }
  };

  const handleChallengeSelect = (challenge) => {
    setCurrentChallenge(challenge);
    trackBehavior('challenge_selected', { challenge_type: challenge.id });
  };

  const handleAIInteraction = async () => {
    if (!userInput.trim() || !user) return;

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/ai/chat?user_id=${user.id}`, {
        message: userInput,
        mode: 'egocore',
        context: {
          current_challenge: currentChallenge?.id,
          personality_state: aiPersonality
        }
      });

      setAiResponse(response.data);
      setUserInput('');
      
      // Update AI personality based on interaction
      setAiPersonality(prev => ({
        energy: Math.min(1, prev.energy + 0.1),
        directness: response.data.personality_traits.directness || prev.directness,
        challenge: response.data.personality_traits.challenge || prev.challenge
      }));

      trackBehavior('ai_interaction', { 
        user_message: userInput,
        ai_response_tone: response.data.emotion_tone,
        challenge_context: currentChallenge?.id
      });

    } catch (error) {
      console.error('Error in AI interaction:', error);
      toast.error('AI temporarily unavailable. Try again!');
    } finally {
      setIsLoading(false);
    }
  };

  const PersonalityBar = ({ label, value, color }) => (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-white/70">{label}</span>
        <span className="text-white/90">{Math.round(value * 100)}%</span>
      </div>
      <div className="w-full bg-white/10 rounded-full h-2">
        <motion.div
          className={`bg-gradient-to-r ${color} h-2 rounded-full`}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 0.8 }}
        />
      </div>
    </div>
  );

  return (
    <div className="min-h-screen text-white p-6">
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl md:text-6xl font-bold text-gradient-ego mb-4">
          ⚡ EgoCore
        </h1>
        <p className="text-white/70 text-lg">
          Your AI companion for relentless growth
        </p>
      </motion.div>

      <div className="max-w-6xl mx-auto grid lg:grid-cols-3 gap-8">
        
        {/* AI Personality Panel */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-dark rounded-2xl p-6"
        >
          <h3 className="text-xl font-bold mb-4 text-gradient-ego">AI Personality State</h3>
          
          <PersonalityBar 
            label="Energy Level"
            value={aiPersonality.energy}
            color="from-red-500 to-orange-500"
          />
          <PersonalityBar 
            label="Directness"
            value={aiPersonality.directness}
            color="from-orange-500 to-yellow-500"
          />
          <PersonalityBar 
            label="Challenge Mode"
            value={aiPersonality.challenge}
            color="from-red-600 to-pink-500"
          />

          {/* User Insights */}
          {userInsights.insights && userInsights.insights.length > 0 && (
            <div className="mt-6">
              <h4 className="text-lg font-semibold mb-3 text-red-400">Your Insights</h4>
              <div className="space-y-2">
                {userInsights.insights.slice(0, 3).map((insight, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.2 }}
                    className="text-sm text-white/80 bg-red-500/10 rounded-lg p-3 border border-red-500/20"
                  >
                    {insight}
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Main Interaction Area */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 space-y-6"
        >
          
          {/* Personalized Prompt */}
          {personalizedPrompt && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-dark rounded-2xl p-6 border border-red-500/30"
            >
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-2xl">🎯</span>
                <h3 className="text-lg font-semibold text-red-400">Your Challenge Today</h3>
              </div>
              <p className="text-white/90 text-lg italic">{personalizedPrompt}</p>
            </motion.div>
          )}

          {/* Challenge Selection */}
          {!currentChallenge && (
            <div className="grid md:grid-cols-3 gap-4">
              {challengeTypes.map((challenge, index) => (
                <motion.div
                  key={challenge.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  whileTap={{ scale: 0.95 }}
                  className="glass-dark rounded-xl p-6 cursor-pointer border border-white/10 hover:border-red-500/30 transition-all"
                  onClick={() => handleChallengeSelect(challenge)}
                >
                  <div className="text-4xl mb-3">{challenge.icon}</div>
                  <h3 className="text-lg font-bold mb-2 text-gradient-ego">
                    {challenge.title}
                  </h3>
                  <p className="text-white/70 text-sm">
                    {challenge.description}
                  </p>
                </motion.div>
              ))}
            </div>
          )}

          {/* AI Interaction Area */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-dark rounded-2xl p-6"
          >
            {currentChallenge && (
              <div className="mb-4 p-4 bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-lg border border-red-500/30">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-2xl">{currentChallenge.icon}</span>
                  <span className="font-semibold text-red-400">{currentChallenge.title}</span>
                </div>
                <p className="text-white/80 text-sm">{currentChallenge.description}</p>
              </div>
            )}

            {/* AI Response */}
            <AnimatePresence>
              {aiResponse && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="mb-6 p-4 bg-gradient-to-r from-gray-800 to-gray-700 rounded-lg border border-red-500/20"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-8 h-8 bg-gradient-to-r from-red-500 to-orange-500 rounded-full flex items-center justify-center text-sm font-bold">
                      AI
                    </div>
                    <span className="text-red-400 font-medium text-sm">
                      Tone: {aiResponse.emotion_tone}
                    </span>
                  </div>
                  <p className="text-white/90 mb-3">{aiResponse.response}</p>
                  
                  {aiResponse.suggestions && aiResponse.suggestions.length > 0 && (
                    <div className="border-t border-white/10 pt-3">
                      <div className="text-sm text-white/60 mb-2">Suggestions:</div>
                      <div className="flex flex-wrap gap-2">
                        {aiResponse.suggestions.map((suggestion, index) => (
                          <span
                            key={index}
                            className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded-full border border-red-500/30"
                          >
                            {suggestion}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Input Area */}
            <div className="space-y-4">
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Share your thoughts, challenges, or ask for guidance..."
                className="form-input w-full h-32 resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    handleAIInteraction();
                  }
                }}
              />
              
              <div className="flex justify-between items-center">
                <div className="text-xs text-white/50">
                  Ctrl + Enter to send
                </div>
                <button
                  onClick={handleAIInteraction}
                  disabled={!userInput.trim() || isLoading}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Processing...</span>
                    </div>
                  ) : (
                    'Send Challenge'
                  )}
                </button>
              </div>
            </div>
          </motion.div>

          {/* Actions */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setCurrentChallenge(null)}
              className="btn-secondary"
            >
              New Challenge
            </button>
            <button
              onClick={() => navigate('/')}
              className="btn-secondary"
            >
              ← Home
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default EgoCore;