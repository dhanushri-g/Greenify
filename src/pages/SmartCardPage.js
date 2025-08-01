import React, { useState } from 'react';
import { Download, Share2, Edit3, CreditCard, QrCode, Printer } from 'lucide-react';
import SmartWasteCard from '../components/SmartWasteCard';

const SmartCardPage = () => {
  const [userInfo, setUserInfo] = useState({
    accountNo: 'GRN-091423',
    userName: 'Chinmay H.',
    validTill: '31-Dec-2025',
    status: 'Moderate',
    points: 1250,
    level: 'Eco Warrior'
  });

  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState(userInfo);

  const handleEdit = () => {
    setIsEditing(true);
    setEditForm(userInfo);
  };

  const handleSave = () => {
    setUserInfo(editForm);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditForm(userInfo);
    setIsEditing(false);
  };

  const handleDownload = () => {
    // In a real app, this would generate a PDF or image
    alert('Card download feature would be implemented here!');
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'My Greenify Smart Waste Card',
        text: `Check out my Greenify Smart Waste Card! Account: ${userInfo.accountNo}`,
        url: window.location.href
      });
    } else {
      // Fallback for browsers that don't support Web Share API
      navigator.clipboard.writeText(window.location.href);
      alert('Card link copied to clipboard!');
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="smart-card-page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">
            <CreditCard size={40} />
            Smart Waste Card
          </h1>
          <p className="page-subtitle">
            Your digital identity for smart waste management and eco-rewards
          </p>
        </div>

        <div className="card-actions">
          <button className="btn btn-primary" onClick={handleEdit}>
            <Edit3 size={20} />
            Edit Card
          </button>
          <button className="btn btn-secondary" onClick={handleDownload}>
            <Download size={20} />
            Download
          </button>
          <button className="btn btn-outline" onClick={handleShare}>
            <Share2 size={20} />
            Share
          </button>
          <button className="btn btn-ghost" onClick={handlePrint}>
            <Printer size={20} />
            Print
          </button>
        </div>

        {isEditing && (
          <div className="edit-modal">
            <div className="edit-modal-content">
              <h3>Edit Card Information</h3>
              <div className="edit-form">
                <div className="form-group">
                  <label className="form-label">Account Number</label>
                  <input
                    type="text"
                    className="form-input"
                    value={editForm.accountNo}
                    onChange={(e) => setEditForm({...editForm, accountNo: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">User Name</label>
                  <input
                    type="text"
                    className="form-input"
                    value={editForm.userName}
                    onChange={(e) => setEditForm({...editForm, userName: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Valid Till</label>
                  <input
                    type="text"
                    className="form-input"
                    value={editForm.validTill}
                    onChange={(e) => setEditForm({...editForm, validTill: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Status</label>
                  <select
                    className="form-select"
                    value={editForm.status}
                    onChange={(e) => setEditForm({...editForm, status: e.target.value})}
                  >
                    <option value="Excellent">Excellent</option>
                    <option value="Good">Good</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Poor">Poor</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Eco Points</label>
                  <input
                    type="number"
                    className="form-input"
                    value={editForm.points}
                    onChange={(e) => setEditForm({...editForm, points: parseInt(e.target.value)})}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Level</label>
                  <select
                    className="form-select"
                    value={editForm.level}
                    onChange={(e) => setEditForm({...editForm, level: e.target.value})}
                  >
                    <option value="Eco Beginner">Eco Beginner</option>
                    <option value="Eco Enthusiast">Eco Enthusiast</option>
                    <option value="Eco Warrior">Eco Warrior</option>
                    <option value="Eco Champion">Eco Champion</option>
                    <option value="Eco Master">Eco Master</option>
                  </select>
                </div>
              </div>
              <div className="edit-actions">
                <button className="btn btn-primary" onClick={handleSave}>
                  Save Changes
                </button>
                <button className="btn btn-outline" onClick={handleCancel}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="card-display">
          <SmartWasteCard userInfo={userInfo} />
        </div>

        <div className="card-info-section">
          <div className="info-cards">
            <div className="info-card">
              <QrCode size={24} />
              <h3>Digital Identity</h3>
              <p>Your unique digital identity for waste management services and eco-rewards tracking.</p>
            </div>
            <div className="info-card">
              <CreditCard size={24} />
              <h3>Smart Features</h3>
              <p>Barcode scanning, points tracking, status monitoring, and reward redemption.</p>
            </div>
            <div className="info-card">
              <Share2 size={24} />
              <h3>Easy Sharing</h3>
              <p>Share your eco achievements and inspire others to join the green movement.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartCardPage;
