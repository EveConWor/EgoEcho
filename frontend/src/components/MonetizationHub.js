import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import axios from 'axios';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MonetizationHub = () => {
  const navigate = useNavigate();
  const { user, trackBehavior } = useApp();
  const [currentTier, setCurrentTier] = useState('free');
  const [credits, setCredits] = useState(0);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('plans');
  const [featureAccess, setFeatureAccess] = useState({});
  const [transactions, setTransactions] = useState([]);

  const subscriptionPlans = {
    free: {
      name: 'Explorer',
      price: 0,
      period: 'Forever',
      description: 'Perfect for getting started',
      features: [
        '10 daily AI interactions',
        '4 journey steps',
        '3 challenge participations',
        '50 social connections',
        'Basic insights',
        'Community access'
      ],
      color: 'from-gray-500 to-gray-600',
      popular: false
    },
    pro: {
      name: 'Discoverer',
      price: 9.99,
      period: 'month',
      description: 'Unlock your full potential',
      features: [
        '100 daily AI interactions',
        'Unlimited journey exploration',
        'Unlimited challenges',
        '500 social connections',
        'Advanced insights & analytics',
        'Premium challenges',
        'Custom avatars',
        '3 VR spaces access'
      ],
      color: 'from-purple-500 to-blue-500',
      popular: true
    },
    elite: {
      name: 'Visionary',
      price: 29.99,
      period: 'month',
      description: 'The ultimate growth experience',
      features: [
        'Unlimited AI interactions',
        'Unlimited everything',
        'Priority AI responses',
        'Unlimited VR spaces',
        'White-label options',
        'API access',
        'Priority support',
        'Beta features access'
      ],
      color: 'from-orange-500 to-red-500',
      popular: false
    }
  };

  const premiumFeatures = [
    {
      id: 'custom_avatar',
      name: 'Custom Avatar Creator',
      description: 'Design unique avatars for VR experiences',
      cost: 50,
      icon: '🎭'
    },
    {
      id: 'premium_challenge',
      name: 'Premium Challenge Pack',
      description: 'Access to exclusive growth challenges',
      cost: 25,
      icon: '🏆'
    },
    {
      id: 'advanced_insight',
      name: 'Advanced AI Insights',
      description: 'Deep behavioral analysis and predictions',
      cost: 30,
      icon: '🧠'
    },
    {
      id: 'vr_space_access',
      name: 'VR Space Creator',
      description: 'Create custom virtual reality spaces',
      cost: 100,
      icon: '🌐'
    }
  ];

  useEffect(() => {
    if (user) {
      setCurrentTier(user.subscription_tier || 'free');
      setCredits(user.credits || 0);
      loadFeatureAccess();
      loadTransactionHistory();
      trackBehavior('monetization_hub_view', { timestamp: new Date().toISOString() });
    }
  }, [user]);

  const loadFeatureAccess = async () => {
    if (!user) return;

    try {
      const features = ['daily_ai_interactions', 'journey_steps', 'challenge_participation', 'social_connections'];
      const accessData = {};

      for (const feature of features) {
        const response = await axios.get(`${API}/monetization/access/${user.id}/${feature}`);
        accessData[feature] = response.data;
      }

      setFeatureAccess(accessData);
    } catch (error) {
      console.error('Error loading feature access:', error);
    }
  };

  const loadTransactionHistory = async () => {
    if (!user) return;

    try {
      const response = await axios.get(`${API}/monetization/transactions/${user.id}`);
      setTransactions(response.data.slice(0, 10)); // Show last 10 transactions
    } catch (error) {
      console.error('Error loading transactions:', error);
    }
  };

  const handleSubscribe = async (tier) => {
    if (!user || isProcessing) return;

    setIsProcessing(true);
    setSelectedPlan(tier);

    try {
      const response = await axios.post(`${API}/monetization/subscribe`, {
        user_id: user.id,
        tier,
        payment_method_id: 'demo_payment_method'
      });

      if (response.data.error) {
        toast.error(response.data.error);
      } else {
        toast.success(`Successfully subscribed to ${subscriptionPlans[tier].name}!`);
        setCurrentTier(tier);
        trackBehavior('subscription_created', { tier, amount: subscriptionPlans[tier].price });
        
        // Reload feature access
        setTimeout(loadFeatureAccess, 1000);
      }
    } catch (error) {
      console.error('Error subscribing:', error);
      toast.error('Subscription failed. Please try again.');
    } finally {
      setIsProcessing(false);
      setSelectedPlan(null);
    }
  };

  const purchaseCredits = async (amount) => {
    if (!user || isProcessing) return;

    setIsProcessing(true);

    try {
      const response = await axios.post(`${API}/monetization/credits/purchase`, {
        user_id: user.id,
        amount,
        payment_method_id: 'demo_payment_method'
      });

      if (response.data.error) {
        toast.error(response.data.error);
      } else {
        toast.success(`Successfully purchased ${amount} credits!`);
        setCredits(credits + amount);
        trackBehavior('credits_purchased', { amount, price: amount });
        loadTransactionHistory();
      }
    } catch (error) {
      console.error('Error purchasing credits:', error);
      toast.error('Credit purchase failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const unlockFeature = async (featureId) => {
    if (!user || isProcessing) return;

    const feature = premiumFeatures.find(f => f.id === featureId);
    if (!feature) return;

    if (credits < feature.cost) {
      toast.error(`Insufficient credits. Need ${feature.cost}, have ${credits}.`);
      return;
    }

    setIsProcessing(true);

    try {
      const response = await axios.post(`${API}/monetization/features/unlock`, {
        user_id: user.id,
        feature_id: featureId,
        payment_method: 'credits'
      });

      if (response.data.error) {
        toast.error(response.data.error);
      } else {
        toast.success(`${feature.name} unlocked!`);
        setCredits(response.data.remaining_credits);
        trackBehavior('feature_unlocked', { feature_id: featureId, cost: feature.cost });
        loadTransactionHistory();
      }
    } catch (error) {
      console.error('Error unlocking feature:', error);
      toast.error('Feature unlock failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const PlanCard = ({ planKey, plan }) => {
    const isCurrentPlan = currentTier === planKey;
    const isUpgrade = currentTier === 'free' && planKey !== 'free';
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`relative glass rounded-2xl p-6 ${plan.popular ? 'ring-2 ring-purple-500' : ''}`}
      >
        {plan.popular && (
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
              Most Popular
            </div>
          </div>
        )}

        <div className="text-center mb-6">
          <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
          <div className="text-3xl font-bold text-gradient mb-2">
            ${plan.price}
            {plan.price > 0 && <span className="text-lg text-white/60">/{plan.period}</span>}
          </div>
          <p className="text-white/70">{plan.description}</p>
        </div>

        <div className="space-y-3 mb-8">
          {plan.features.map((feature, index) => (
            <div key={index} className="flex items-center space-x-2">
              <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">✓</span>
              </div>
              <span className="text-white/90">{feature}</span>
            </div>
          ))}
        </div>

        <button
          onClick={() => handleSubscribe(planKey)}
          disabled={isCurrentPlan || isProcessing || selectedPlan === planKey}
          className={`w-full py-3 rounded-xl font-medium transition-all ${
            isCurrentPlan
              ? 'bg-green-500/20 text-green-400 cursor-default'
              : isUpgrade
              ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-600 hover:to-blue-600'
              : 'bg-white/10 text-white hover:bg-white/20'
          } ${isProcessing && selectedPlan === planKey ? 'opacity-50' : ''}`}
        >
          {isProcessing && selectedPlan === planKey ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Processing...</span>
            </div>
          ) : isCurrentPlan ? (
            'Current Plan'
          ) : (
            `${isUpgrade ? 'Upgrade to' : 'Switch to'} ${plan.name}`
          )}
        </button>
      </motion.div>
    );
  };

  const FeatureCard = ({ feature }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-6"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="text-2xl mb-2">{feature.icon}</div>
          <h3 className="text-lg font-semibold text-white mb-2">{feature.name}</h3>
          <p className="text-white/70 text-sm">{feature.description}</p>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-gradient">{feature.cost}</div>
          <div className="text-sm text-white/60">credits</div>
        </div>
      </div>

      <button
        onClick={() => unlockFeature(feature.id)}
        disabled={credits < feature.cost || isProcessing}
        className="w-full btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {credits < feature.cost ? 'Insufficient Credits' : 'Unlock Feature'}
      </button>
    </motion.div>
  );

  const tabs = [
    { id: 'plans', label: 'Subscription Plans', icon: '💎' },
    { id: 'credits', label: 'Credits', icon: '💰' },
    { id: 'features', label: 'Premium Features', icon: '✨' },
    { id: 'usage', label: 'Usage & Billing', icon: '📊' }
  ];

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        <div className="text-center">
          <div className="text-6xl mb-4">💎</div>
          <h2 className="text-2xl font-bold mb-2">Unlock Premium Features</h2>
          <p className="text-white/70 mb-6">Sign in to access subscription plans</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Get Started
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
            <h1 className="text-4xl font-bold text-gradient mb-2">Premium Hub</h1>
            <p className="text-white/70">Unlock your full potential with premium features</p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Credits Display */}
            <div className="glass rounded-xl px-4 py-2">
              <div className="flex items-center space-x-2">
                <span className="text-yellow-400">💰</span>
                <span className="font-semibold">{credits} credits</span>
              </div>
            </div>
            
            <button onClick={() => navigate('/')} className="btn-secondary">
              ← Home
            </button>
          </div>
        </div>

        {/* Current Plan Banner */}
        <div className={`glass rounded-2xl p-6 mb-6 bg-gradient-to-r ${subscriptionPlans[currentTier].color}/20`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white mb-1">
                Current Plan: {subscriptionPlans[currentTier].name}
              </h2>
              <p className="text-white/70">
                {currentTier === 'free' 
                  ? 'You\'re on the free plan. Upgrade to unlock more features!'
                  : `You have access to all ${subscriptionPlans[currentTier].name} features.`
                }
              </p>
            </div>
            {currentTier !== 'elite' && (
              <button
                onClick={() => setActiveTab('plans')}
                className="btn-primary"
              >
                Upgrade Now
              </button>
            )}
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
          {activeTab === 'plans' && (
            <motion.div
              key="plans"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="grid md:grid-cols-3 gap-8">
                {Object.entries(subscriptionPlans).map(([key, plan]) => (
                  <PlanCard key={key} planKey={key} plan={plan} />
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'credits' && (
            <motion.div
              key="credits"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="grid md:grid-cols-2 gap-8">
                {/* Purchase Credits */}
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Purchase Credits</h3>
                  <p className="text-white/70 mb-6">
                    Credits can be used to unlock premium features and content.
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { amount: 100, price: 1, bonus: 0 },
                      { amount: 500, price: 4, bonus: 50 },
                      { amount: 1000, price: 8, bonus: 200 },
                      { amount: 2500, price: 18, bonus: 750 }
                    ].map((package_, index) => (
                      <button
                        key={index}
                        onClick={() => purchaseCredits(package_.amount + package_.bonus)}
                        disabled={isProcessing}
                        className="glass-dark rounded-xl p-4 hover:bg-white/10 transition-all text-center"
                      >
                        <div className="text-lg font-bold text-gradient">
                          {package_.amount + package_.bonus}
                        </div>
                        <div className="text-sm text-white/70">${package_.price}</div>
                        {package_.bonus > 0 && (
                          <div className="text-xs text-green-400">+{package_.bonus} bonus!</div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Credit Balance */}
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Credit Balance</h3>
                  
                  <div className="text-center mb-6">
                    <div className="text-4xl font-bold text-gradient mb-2">{credits}</div>
                    <div className="text-white/70">Available Credits</div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/70">Earned from activities</span>
                      <span className="text-green-400">+150</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-white/70">Purchased</span>
                      <span className="text-blue-400">+{Math.max(0, credits - 150)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-white/70">Spent on features</span>
                      <span className="text-red-400">-25</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'features' && (
            <motion.div
              key="features"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="grid md:grid-cols-2 gap-6">
                {premiumFeatures.map((feature) => (
                  <FeatureCard key={feature.id} feature={feature} />
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'usage' && (
            <motion.div
              key="usage"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="grid md:grid-cols-2 gap-8">
                {/* Feature Usage */}
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Feature Usage</h3>
                  
                  <div className="space-y-4">
                    {Object.entries(featureAccess).map(([feature, data]) => (
                      <div key={feature} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-white/70 capitalize">
                            {feature.replace(/_/g, ' ')}
                          </span>
                          <span className="text-white">
                            {typeof data.limit === 'number' 
                              ? `${data.usage || 0}/${data.limit}`
                              : data.limit || 'Unlimited'
                            }
                          </span>
                        </div>
                        {typeof data.limit === 'number' && (
                          <div className="w-full bg-white/10 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                              style={{ 
                                width: `${Math.min(100, ((data.usage || 0) / data.limit) * 100)}%` 
                              }}
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Transactions */}
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Recent Transactions</h3>
                  
                  {transactions.length > 0 ? (
                    <div className="space-y-3">
                      {transactions.map((transaction, index) => (
                        <div key={index} className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <div>
                            <div className="text-white font-medium">
                              {transaction.transaction_type === 'credits' ? 'Credits Purchase' :
                               transaction.transaction_type === 'subscription' ? 'Subscription' :
                               'Premium Feature'}
                            </div>
                            <div className="text-white/60 text-sm">
                              {new Date(transaction.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          <div className={`font-medium ${
                            transaction.status === 'completed' ? 'text-green-400' :
                            transaction.status === 'pending' ? 'text-yellow-400' :
                            'text-red-400'
                          }`}>
                            ${transaction.amount.toFixed(2)}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-2">📊</div>
                      <p className="text-white/60">No transactions yet</p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default MonetizationHub;