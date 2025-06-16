import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import axios from 'axios';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SocialFeed = () => {
  const navigate = useNavigate();
  const { user, currentMode, trackBehavior } = useApp();
  const [posts, setPosts] = useState([]);
  const [users, setUsers] = useState({});
  const [loading, setLoading] = useState(true);
  const [newPostContent, setNewPostContent] = useState('');
  const [isPosting, setIsPosting] = useState(false);
  const [selectedTab, setSelectedTab] = useState('feed');

  useEffect(() => {
    if (user) {
      loadSocialFeed();
      trackBehavior('social_feed_view', { timestamp: new Date().toISOString() });
    }
  }, [user]);

  const loadSocialFeed = async () => {
    if (!user) return;
    
    try {
      const response = await axios.get(`${API}/social/feed`, {
        params: { user_id: user.id, limit: 20 }
      });
      
      setPosts(response.data.posts || []);
      setUsers(response.data.users || {});
    } catch (error) {
      console.error('Error loading social feed:', error);
      toast.error('Failed to load social feed');
    } finally {
      setLoading(false);
    }
  };

  const createPost = async () => {
    if (!newPostContent.trim() || !user || isPosting) return;

    setIsPosting(true);
    try {
      const response = await axios.post(`${API}/social/posts`, {
        user_id: user.id,
        content: newPostContent,
        content_type: 'text'
      });

      // Add new post to beginning of feed
      const newPost = {
        ...response.data,
        like_count: 0,
        comment_count: 0,
        user_liked: false
      };
      
      setPosts([newPost, ...posts]);
      setNewPostContent('');
      toast.success('Post created!');
      
      trackBehavior('post_created', { content_length: newPostContent.length });
      
    } catch (error) {
      console.error('Error creating post:', error);
      toast.error('Failed to create post');
    } finally {
      setIsPosting(false);
    }
  };

  const likePost = async (postId) => {
    if (!user) return;

    try {
      const response = await axios.post(`${API}/social/posts/${postId}/like`, {
        user_id: user.id
      });

      // Update post in state
      setPosts(posts.map(post => {
        if (post.id === postId) {
          const liked = response.data.liked;
          return {
            ...post,
            user_liked: liked,
            like_count: liked ? post.like_count + 1 : post.like_count - 1
          };
        }
        return post;
      }));

      trackBehavior('post_liked', { post_id: postId, action: response.data.liked ? 'like' : 'unlike' });
      
    } catch (error) {
      console.error('Error liking post:', error);
      toast.error('Failed to like post');
    }
  };

  const PostCard = ({ post }) => {
    const postUser = users[post.user_id];
    if (!postUser) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6 mb-4"
      >
        {/* User Info */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
            {postUser.username?.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="text-white font-medium">{postUser.display_name || postUser.username}</div>
            <div className="text-white/60 text-sm">
              {new Date(post.created_at).toLocaleDateString()}
            </div>
          </div>
          
          {/* Mode indicator */}
          <div className={`ml-auto px-2 py-1 rounded-full text-xs ${
            postUser.current_mode === 'echoverse' 
              ? 'bg-purple-500/20 text-purple-300' 
              : 'bg-red-500/20 text-red-300'
          }`}>
            {postUser.current_mode === 'echoverse' ? '🌌' : '⚡'}
          </div>
        </div>

        {/* Content */}
        <div className="text-white/90 mb-4 leading-relaxed">
          {post.content}
        </div>

        {/* Content Type Badge */}
        {post.content_type !== 'text' && (
          <div className="mb-4">
            <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm">
              {post.content_type}
            </span>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center space-x-6 pt-3 border-t border-white/10">
          <button
            onClick={() => likePost(post.id)}
            className={`flex items-center space-x-2 text-sm transition-colors ${
              post.user_liked 
                ? 'text-red-400 hover:text-red-300' 
                : 'text-white/60 hover:text-red-400'
            }`}
          >
            <span>{post.user_liked ? '❤️' : '🤍'}</span>
            <span>{post.like_count}</span>
          </button>
          
          <button className="flex items-center space-x-2 text-white/60 hover:text-blue-400 text-sm transition-colors">
            <span>💬</span>
            <span>{post.comment_count}</span>
          </button>
          
          <button className="flex items-center space-x-2 text-white/60 hover:text-green-400 text-sm transition-colors">
            <span>🔄</span>
            <span>{post.shares || 0}</span>
          </button>
        </div>
      </motion.div>
    );
  };

  const CreatePostCard = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6 mb-6"
    >
      <div className="flex items-start space-x-3">
        <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
          {user?.username?.charAt(0).toUpperCase()}
        </div>
        
        <div className="flex-1">
          <textarea
            value={newPostContent}
            onChange={(e) => setNewPostContent(e.target.value)}
            placeholder={currentMode === 'echoverse' 
              ? "Share a reflection on your journey..." 
              : "What challenge are you tackling today?"}
            className="form-input w-full h-24 resize-none mb-3"
            maxLength={500}
          />
          
          <div className="flex items-center justify-between">
            <div className="text-xs text-white/50">
              {newPostContent.length}/500 characters
            </div>
            
            <button
              onClick={createPost}
              disabled={!newPostContent.trim() || isPosting}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPosting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Posting...</span>
                </div>
              ) : (
                'Share'
              )}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );

  const CommunityStats = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass rounded-2xl p-6"
    >
      <h3 className="text-lg font-semibold text-white mb-4">Community Pulse</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-white/70">Active Members</span>
          <span className="text-white font-medium">1,247</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-white/70">Posts Today</span>
          <span className="text-white font-medium">89</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-white/70">Challenges Active</span>
          <span className="text-white font-medium">12</span>
        </div>
        
        <div className="pt-4 border-t border-white/10">
          <div className="text-sm text-white/70 mb-2">Mode Distribution</div>
          <div className="flex space-x-2">
            <div className="flex-1 bg-purple-500/20 rounded-full h-2">
              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '60%' }}></div>
            </div>
            <div className="text-xs text-white/60">60% 🌌</div>
          </div>
          <div className="flex space-x-2 mt-1">
            <div className="flex-1 bg-red-500/20 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: '40%' }}></div>
            </div>
            <div className="text-xs text-white/60">40% ⚡</div>
          </div>
        </div>
      </div>
    </motion.div>
  );

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        <div className="text-center">
          <div className="text-6xl mb-4">🌐</div>
          <h2 className="text-2xl font-bold mb-2">Join the Community</h2>
          <p className="text-white/70 mb-6">Connect with others on their identity journey</p>
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
            <h1 className="text-4xl font-bold text-gradient mb-2">Social Feed</h1>
            <p className="text-white/70">Connect with the community on their journey</p>
          </div>
          
          <button
            onClick={() => navigate('/')}
            className="btn-secondary"
          >
            ← Home
          </button>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-6 bg-black/20 rounded-xl p-1">
          {[
            { id: 'feed', label: 'Feed', icon: '📰' },
            { id: 'discover', label: 'Discover', icon: '🔍' },
            { id: 'challenges', label: 'Challenges', icon: '🏆' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                selectedTab === tab.id
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
        <div className="grid lg:grid-cols-4 gap-8">
          
          {/* Main Feed */}
          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              {selectedTab === 'feed' && (
                <motion.div
                  key="feed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <CreatePostCard />
                  
                  {loading ? (
                    <div className="flex justify-center py-12">
                      <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : posts.length > 0 ? (
                    posts.map((post) => (
                      <PostCard key={post.id} post={post} />
                    ))
                  ) : (
                    <div className="text-center py-12">
                      <div className="text-6xl mb-4">📝</div>
                      <h3 className="text-xl font-semibold mb-2 text-white/80">No posts yet</h3>
                      <p className="text-white/60 mb-6">
                        Be the first to share something with the community!
                      </p>
                    </div>
                  )}
                </motion.div>
              )}

              {selectedTab === 'discover' && (
                <motion.div
                  key="discover"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="text-center py-12"
                >
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold mb-2">Discover New Connections</h3>
                  <p className="text-white/60 mb-6">Find others on similar journeys</p>
                  <button className="btn-primary">Coming Soon</button>
                </motion.div>
              )}

              {selectedTab === 'challenges' && (
                <motion.div
                  key="challenges"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="text-center py-12"
                >
                  <div className="text-6xl mb-4">🏆</div>
                  <h3 className="text-xl font-semibold mb-2">Community Challenges</h3>
                  <p className="text-white/60 mb-6">Join growth challenges with others</p>
                  <button className="btn-primary">Coming Soon</button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <CommunityStats />
            
            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
              
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/echoverse')}
                  className="w-full btn-secondary text-left p-3"
                >
                  <div className="flex items-center space-x-2">
                    <span>🌌</span>
                    <span>Continue Journey</span>
                  </div>
                </button>
                
                <button
                  onClick={() => navigate('/egocore')}
                  className="w-full btn-secondary text-left p-3"
                >
                  <div className="flex items-center space-x-2">
                    <span>⚡</span>
                    <span>Take Challenge</span>
                  </div>
                </button>
                
                <button
                  onClick={() => navigate('/chat')}
                  className="w-full btn-secondary text-left p-3"
                >
                  <div className="flex items-center space-x-2">
                    <span>💬</span>
                    <span>Chat with AI</span>
                  </div>
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocialFeed;