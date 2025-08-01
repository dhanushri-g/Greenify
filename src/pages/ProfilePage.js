// ProfilePage.jsx
import React, { useEffect, useState } from "react";
import {
  Camera, Edit3, User, Mail, FileText, Image, Sparkles,
  Award, TrendingUp, Calendar, MapPin, Phone, Globe,
  Settings, Bell, Eye, Shield, Download, Trash2,
  Star, Target, Zap, Heart, Share2, Copy, Check
} from 'lucide-react';

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [isFirstTime, setIsFirstTime] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [form, setForm] = useState({
    name: "",
    email: "",
    bio: "",
    profilePic: "",
    phone: "",
    location: "",
    website: "",
    interests: [],
  });

  // Enhanced user stats with dynamic data
  const [userStats, setUserStats] = useState({
    itemsScanned: 127,
    itemsRecycled: 89,
    co2Saved: 45.2,
    dayStreak: 15,
    totalPoints: 2450,
    level: 'Eco Champion',
    rank: 'Gold',
    joinDate: new Date().toISOString().split('T')[0]
  });

  // Achievements data
  const achievements = [
    { id: 1, name: 'First Scan', icon: '🎯', earned: true, description: 'Completed your first waste scan' },
    { id: 2, name: 'Eco Warrior', icon: '🌱', earned: true, description: 'Recycled 50+ items' },
    { id: 3, name: 'Streak Master', icon: '🔥', earned: true, description: '7-day scanning streak' },
    { id: 4, name: 'Planet Saver', icon: '🌍', earned: false, description: 'Save 100kg of CO₂' },
    { id: 5, name: 'Community Leader', icon: '👑', earned: false, description: 'Help 10 other users' },
    { id: 6, name: 'Perfectionist', icon: '⭐', earned: false, description: '100% accuracy for 30 days' }
  ];

  // Recent activity data
  const recentActivity = [
    { id: 1, action: 'Scanned plastic bottle', time: '2 hours ago', type: 'scan', icon: '♻️' },
    { id: 2, action: 'Earned Eco Warrior badge', time: '1 day ago', type: 'achievement', icon: '🏆' },
    { id: 3, action: 'Completed daily challenge', time: '2 days ago', type: 'challenge', icon: '🎯' },
    { id: 4, action: 'Shared recycling tip', time: '3 days ago', type: 'social', icon: '💡' },
    { id: 5, action: 'Reached 15-day streak', time: '4 days ago', type: 'milestone', icon: '🔥' }
  ];

  // Load profile from localStorage on first load
  useEffect(() => {
    try {
      const storedProfile = localStorage.getItem("userProfile");
      if (storedProfile) {
        const parsedProfile = JSON.parse(storedProfile);
        setProfile(parsedProfile);
        setIsFirstTime(false);
      } else {
        setIsFirstTime(true);
      }
    } catch (error) {
      console.error("Error loading profile:", error);
      setIsFirstTime(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleInterestToggle = (interest) => {
    const currentInterests = form.interests || [];
    const updatedInterests = currentInterests.includes(interest)
      ? currentInterests.filter(i => i !== interest)
      : [...currentInterests, interest];
    setForm({ ...form, interests: updatedInterests });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const completeProfile = {
      ...form,
      joinDate: profile?.joinDate || new Date().toISOString().split('T')[0],
      ...userStats
    };
    localStorage.setItem("userProfile", JSON.stringify(completeProfile));
    setProfile(completeProfile);
    setIsFirstTime(false);
  };

  const copyProfileLink = () => {
    navigator.clipboard.writeText(window.location.href);
    // You could add a toast notification here
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading your profile...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        {isFirstTime ? (
          <div className="first-time-setup">
            <div className="setup-header">
              <div className="welcome-animation">
                <Sparkles className="welcome-icon floating" />
                <div className="sparkle-effects">
                  <div className="sparkle sparkle-1">✨</div>
                  <div className="sparkle sparkle-2">⭐</div>
                  <div className="sparkle sparkle-3">💫</div>
                </div>
              </div>
              <h2 className="setup-title">Welcome to Smart Waste! 🌱</h2>
              <p className="setup-subtitle">Let's create your eco-profile and start your sustainability journey</p>
              <div className="setup-progress">
                <div className="progress-dots">
                  <div className="dot active"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="setup-form">
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">
                    <User size={16} />
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    placeholder="Enter your full name"
                    className="form-input"
                    value={form.name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Mail size={16} />
                    Email Address *
                  </label>
                  <input
                    type="email"
                    name="email"
                    placeholder="Enter your email"
                    className="form-input"
                    value={form.email}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">
                    <Phone size={16} />
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    placeholder="Your phone number"
                    className="form-input"
                    value={form.phone}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <MapPin size={16} />
                    Location
                  </label>
                  <input
                    type="text"
                    name="location"
                    placeholder="City, Country"
                    className="form-input"
                    value={form.location}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <Image size={16} />
                  Profile Picture URL
                </label>
                <input
                  type="url"
                  name="profilePic"
                  placeholder="https://example.com/your-photo.jpg"
                  className="form-input"
                  value={form.profilePic}
                  onChange={handleChange}
                />
                {form.profilePic && (
                  <div className="image-preview">
                    <img src={form.profilePic} alt="Preview" onError={(e) => e.target.style.display = 'none'} />
                  </div>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">
                  <Globe size={16} />
                  Website/Portfolio
                </label>
                <input
                  type="url"
                  name="website"
                  placeholder="https://your-website.com"
                  className="form-input"
                  value={form.website}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <FileText size={16} />
                  About You
                </label>
                <textarea
                  name="bio"
                  placeholder="Tell us about your sustainability journey, interests, and goals..."
                  className="form-textarea"
                  value={form.bio}
                  onChange={handleChange}
                  rows="4"
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <Heart size={16} />
                  Interests & Goals
                </label>
                <div className="interests-grid">
                  {['Recycling', 'Zero Waste', 'Composting', 'Renewable Energy', 'Sustainable Fashion', 'Green Technology', 'Climate Action', 'Eco Education'].map(interest => (
                    <button
                      key={interest}
                      type="button"
                      className={`interest-tag ${(form.interests || []).includes(interest) ? 'selected' : ''}`}
                      onClick={() => handleInterestToggle(interest)}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                className="submit-btn enhanced"
              >
                <Sparkles size={16} />
                Create My Eco Profile
                <div className="btn-shine"></div>
              </button>
            </form>
          </div>
        ) : (
          <div className="profile-display">
            {/* Enhanced Profile Header */}
            <div className="profile-header-enhanced">
              <div className="profile-cover">
                <div className="cover-gradient"></div>
                <div className="profile-level-badge">
                  <Star size={16} />
                  {userStats.level}
                </div>
              </div>

              <div className="profile-main-info">
                <div className="profile-avatar-section">
                  {profile?.profilePic ? (
                    <img
                      src={profile.profilePic}
                      alt="Profile"
                      className="profile-avatar enhanced"
                    />
                  ) : (
                    <div className="profile-avatar-placeholder enhanced">
                      <User size={48} />
                    </div>
                  )}
                  <div className="avatar-status online"></div>
                  <button className="avatar-edit-btn enhanced">
                    <Camera size={16} />
                  </button>
                </div>

                <div className="profile-info-enhanced">
                  <div className="name-section">
                    <h2 className="profile-name enhanced">{profile?.name || 'Eco Warrior'}</h2>
                    <div className="profile-badges">
                      <span className="rank-badge">{userStats.rank}</span>
                      <span className="points-badge">{userStats.totalPoints} pts</span>
                    </div>
                  </div>

                  <div className="profile-meta">
                    <div className="meta-item">
                      <Mail size={14} />
                      <span>{profile?.email || 'No email'}</span>
                    </div>
                    {profile?.location && (
                      <div className="meta-item">
                        <MapPin size={14} />
                        <span>{profile.location}</span>
                      </div>
                    )}
                    {profile?.phone && (
                      <div className="meta-item">
                        <Phone size={14} />
                        <span>{profile.phone}</span>
                      </div>
                    )}
                    <div className="meta-item">
                      <Calendar size={14} />
                      <span>Joined {new Date(userStats.joinDate).toLocaleDateString()}</span>
                    </div>
                  </div>

                  {profile?.bio && (
                    <p className="profile-bio enhanced">{profile.bio}</p>
                  )}

                  {profile?.interests && profile.interests.length > 0 && (
                    <div className="profile-interests">
                      {profile.interests.map(interest => (
                        <span key={interest} className="interest-chip">{interest}</span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="profile-actions-enhanced">
                  <button
                    onClick={() => {
                      if (profile) {
                        setForm(profile);
                        setIsFirstTime(true);
                      }
                    }}
                    className="action-btn primary"
                  >
                    <Edit3 size={16} />
                    Edit Profile
                  </button>

                  <button
                    onClick={copyProfileLink}
                    className="action-btn secondary"
                  >
                    <Share2 size={16} />
                    Share
                  </button>

                  <button
                    onClick={() => setShowSettings(true)}
                    className="action-btn secondary"
                  >
                    <Settings size={16} />
                    Settings
                  </button>
                </div>
              </div>
            </div>

            {/* Enhanced Stats Section */}
            <div className="stats-section-enhanced">
              <h3 className="section-title">
                <TrendingUp size={20} />
                Your Impact Dashboard
              </h3>
              <div className="stats-grid-enhanced">
                <div className="stat-card enhanced primary">
                  <div className="stat-icon-wrapper">
                    <Target size={24} />
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{userStats.itemsScanned}</div>
                    <div className="stat-label">Items Scanned</div>
                    <div className="stat-trend">+12 this week</div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress-bar" style={{width: '78%'}}></div>
                  </div>
                </div>

                <div className="stat-card enhanced success">
                  <div className="stat-icon-wrapper">
                    <Zap size={24} />
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{userStats.itemsRecycled}</div>
                    <div className="stat-label">Items Recycled</div>
                    <div className="stat-trend">+8 this week</div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress-bar" style={{width: '65%'}}></div>
                  </div>
                </div>

                <div className="stat-card enhanced eco">
                  <div className="stat-icon-wrapper">
                    <Globe size={24} />
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{userStats.co2Saved}kg</div>
                    <div className="stat-label">CO₂ Saved</div>
                    <div className="stat-trend">+2.1kg this week</div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress-bar" style={{width: '45%'}}></div>
                  </div>
                </div>

                <div className="stat-card enhanced fire">
                  <div className="stat-icon-wrapper">
                    <Award size={24} />
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{userStats.dayStreak}</div>
                    <div className="stat-label">Day Streak</div>
                    <div className="stat-trend">Keep it up!</div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress-bar" style={{width: '88%'}}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tabbed Content Section */}
            <div className="profile-tabs-section">
              <div className="tabs-header">
                <button
                  className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  <TrendingUp size={16} />
                  Overview
                </button>
                <button
                  className={`tab-btn ${activeTab === 'achievements' ? 'active' : ''}`}
                  onClick={() => setActiveTab('achievements')}
                >
                  <Award size={16} />
                  Achievements
                </button>
                <button
                  className={`tab-btn ${activeTab === 'activity' ? 'active' : ''}`}
                  onClick={() => setActiveTab('activity')}
                >
                  <Zap size={16} />
                  Activity
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'overview' && (
                  <div className="overview-tab">
                    <div className="overview-grid">
                      <div className="overview-card">
                        <h4>Weekly Goal Progress</h4>
                        <div className="goal-progress">
                          <div className="goal-item">
                            <span>Scans</span>
                            <div className="progress-container">
                              <div className="progress-bar" style={{width: '70%'}}></div>
                              <span>14/20</span>
                            </div>
                          </div>
                          <div className="goal-item">
                            <span>Recycling</span>
                            <div className="progress-container">
                              <div className="progress-bar" style={{width: '85%'}}></div>
                              <span>17/20</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="overview-card">
                        <h4>Environmental Impact</h4>
                        <div className="impact-metrics">
                          <div className="impact-item">
                            <div className="impact-icon">🌳</div>
                            <div>
                              <div className="impact-value">12</div>
                              <div className="impact-label">Trees Saved</div>
                            </div>
                          </div>
                          <div className="impact-item">
                            <div className="impact-icon">💧</div>
                            <div>
                              <div className="impact-value">2,340L</div>
                              <div className="impact-label">Water Saved</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'achievements' && (
                  <div className="achievements-tab">
                    <div className="achievements-header">
                      <h4>Your Eco Achievements</h4>
                      <div className="achievement-progress">
                        <span>{achievements.filter(a => a.earned).length}/{achievements.length} Unlocked</span>
                      </div>
                    </div>
                    <div className="achievements-grid">
                      {achievements.map(achievement => (
                        <div
                          key={achievement.id}
                          className={`achievement-card ${achievement.earned ? 'earned' : 'locked'}`}
                        >
                          <div className="achievement-icon">{achievement.icon}</div>
                          <h5 className="achievement-name">{achievement.name}</h5>
                          <p className="achievement-description">{achievement.description}</p>
                          {achievement.earned && (
                            <div className="earned-badge">
                              <Check size={16} />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'activity' && (
                  <div className="activity-tab">
                    <div className="activity-header">
                      <h4>Recent Activity</h4>
                      <button className="view-all-btn">View All</button>
                    </div>
                    <div className="activity-timeline">
                      {recentActivity.map(activity => (
                        <div key={activity.id} className="activity-item">
                          <div className={`activity-icon ${activity.type}`}>
                            {activity.icon}
                          </div>
                          <div className="activity-content">
                            <p className="activity-action">{activity.action}</p>
                            <span className="activity-time">{activity.time}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Settings Modal */}
        {showSettings && (
          <div className="modal-overlay enhanced" onClick={() => setShowSettings(false)}>
            <div className="settings-modal enhanced" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Profile Settings</h3>
                <button className="modal-close" onClick={() => setShowSettings(false)}>
                  <Trash2 size={20} />
                </button>
              </div>
              <div className="settings-content">
                <div className="setting-section">
                  <h4>Privacy & Notifications</h4>
                  <div className="setting-item">
                    <div className="setting-info">
                      <Bell size={16} />
                      <div>
                        <strong>Push Notifications</strong>
                        <p>Get notified about achievements and goals</p>
                      </div>
                    </div>
                    <label className="toggle-switch">
                      <input type="checkbox" defaultChecked />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                  <div className="setting-item">
                    <div className="setting-info">
                      <Eye size={16} />
                      <div>
                        <strong>Public Profile</strong>
                        <p>Make your profile visible to other users</p>
                      </div>
                    </div>
                    <label className="toggle-switch">
                      <input type="checkbox" />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div className="setting-section">
                  <h4>Account Actions</h4>
                  <button className="setting-button">
                    <Download size={16} />
                    Export My Data
                  </button>
                  <button
                    className="setting-button danger"
                    onClick={() => {
                      localStorage.removeItem("userProfile");
                      window.location.reload();
                    }}
                  >
                    <Trash2 size={16} />
                    Reset All Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;
