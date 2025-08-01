import React from 'react';
import { Recycle, User, Calendar, BarChart3, Shield } from 'lucide-react';

const SmartWasteCard = ({ userInfo = {} }) => {
  const {
    accountNo = 'GRN-091423',
    userName = 'Chinmay H.',
    validTill = '31-Dec-2025',
    status = 'Moderate',
    points = 1250,
    level = 'Eco Warrior'
  } = userInfo;

  const generateBarcode = (data) => {
    return `https://barcode.tec-it.com/barcode.ashx?data=${data}&code=Code128&dpi=96&width=200&height=50`;
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'excellent': return '#22c55e';
      case 'good': return '#3b82f6';
      case 'moderate': return '#f59e0b';
      case 'poor': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="smart-card-container">
      {/* Front Card - Green */}
      <div className="smart-card smart-card-front">
        <div className="card-logo">
          <Recycle size={32} />
        </div>
        
        <div className="card-header">
          <div className="greenify-logo">
            <h2 className="greenify-title">GREENIFY</h2>
            <p className="greenify-subtitle">Smart Waste Management</p>
          </div>
        </div>
        
        <div className="card-info">
          <div className="info-row">
            <span className="info-label">Account No:</span>
            <span className="info-value">{accountNo}</span>
          </div>
          <div className="info-row">
            <span className="info-label">User:</span>
            <span className="info-value">{userName}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Valid Till:</span>
            <span className="info-value">{validTill}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Level:</span>
            <span className="info-value">{level}</span>
          </div>
        </div>
        
        <div className="card-status" style={{ backgroundColor: getStatusColor(status) }}>
          <BarChart3 size={16} />
          <span>Waste Collection Status: {status}</span>
        </div>
        
        <div className="card-points">
          <Shield size={16} />
          <span>{points} Eco Points</span>
        </div>
      </div>

      {/* Back Card - White */}
      <div className="smart-card smart-card-back">
        <div className="card-logo">
          <Recycle size={32} />
        </div>
        
        <div className="card-header">
          <div className="greenify-logo">
            <h2 className="greenify-title-dark">GREENIFY</h2>
            <p className="greenify-subtitle-dark">Smart Waste Management</p>
          </div>
        </div>

        <div className="barcode-section">
          <img 
            src={generateBarcode(accountNo)} 
            alt="Account Barcode"
            className="barcode-image"
          />
          <p className="barcode-text">{accountNo}</p>
        </div>
        
        <div className="card-features">
          <div className="feature-item">
            <User size={16} />
            <span>Digital Identity</span>
          </div>
          <div className="feature-item">
            <Calendar size={16} />
            <span>Valid Until {validTill}</span>
          </div>
          <div className="feature-item">
            <Shield size={16} />
            <span>Verified Member</span>
          </div>
        </div>
        
        <div className="card-signature">
          <p>Authorised Signature</p>
          <div className="signature-line"></div>
        </div>
      </div>
    </div>
  );
};

export default SmartWasteCard;
