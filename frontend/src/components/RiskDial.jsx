// RiskDial.jsx - Milestone 4: Risk Score Visualization Component
/**
 * Circular gauge component for displaying injury risk scores
 * Shows risk level with visual indicators
 */

import React from 'react';
import './RiskDial.css';

const RiskDial = ({ value = 0, size = 'large', label = 'Risk Score' }) => {
  // Normalize value to 0-100
  const normalizedValue = Math.max(0, Math.min(100, value));
  
  // Determine risk level
  const getRiskLevel = (score) => {
    if (score < 40) return { level: 'Low', color: '#27ae60', icon: '✓' };
    if (score < 70) return { level: 'Moderate', color: '#f39c12', icon: '⚠' };
    if (score < 85) return { level: 'High', color: '#e74c3c', icon: '!' };
    return { level: 'Critical', color: '#c0392b', icon: '✕' };
  };
  
  const risk = getRiskLevel(normalizedValue);
  
  // Calculate rotation for needle
  const rotation = (normalizedValue / 100) * 180 - 90;
  
  // Size dimensions
  const sizeMap = {
    small: 120,
    medium: 180,
    large: 240
  };
  
  const diameter = sizeMap[size] || sizeMap.large;
  const radius = diameter / 2;
  const strokeWidth = diameter / 20;
  
  return (
    <div className={`risk-dial-container ${size}`}>
      <div className="risk-dial-wrapper">
        <svg
          className="risk-dial-svg"
          viewBox={`0 0 ${diameter} ${diameter}`}
          width={diameter}
          height={diameter}
        >
          {/* Background circle */}
          <circle
            cx={radius}
            cy={radius}
            r={radius - strokeWidth / 2}
            fill="none"
            stroke="#ecf0f1"
            strokeWidth={strokeWidth}
          />
          
          {/* Risk gradient segments */}
          <defs>
            <linearGradient id="lowRiskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#27ae60" />
              <stop offset="100%" stopColor="#2ecc71" />
            </linearGradient>
            <linearGradient id="moderateRiskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f39c12" />
              <stop offset="100%" stopColor="#f1c40f" />
            </linearGradient>
            <linearGradient id="highRiskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#e74c3c" />
              <stop offset="100%" stopColor="#e67e22" />
            </linearGradient>
            <linearGradient id="criticalRiskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#c0392b" />
              <stop offset="100%" stopColor="#e74c3c" />
            </linearGradient>
          </defs>
          
          {/* Low Risk segment (0-40%) */}
          <path
            d={describeArc(radius, radius, radius - strokeWidth / 2, 180, 252)}
            fill="none"
            stroke="url(#lowRiskGradient)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          
          {/* Moderate Risk segment (40-70%) */}
          <path
            d={describeArc(radius, radius, radius - strokeWidth / 2, 252, 306)}
            fill="none"
            stroke="url(#moderateRiskGradient)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          
          {/* High Risk segment (70-85%) */}
          <path
            d={describeArc(radius, radius, radius - strokeWidth / 2, 306, 333)}
            fill="none"
            stroke="url(#highRiskGradient)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          
          {/* Critical Risk segment (85-100%) */}
          <path
            d={describeArc(radius, radius, radius - strokeWidth / 2, 333, 360)}
            fill="none"
            stroke="url(#criticalRiskGradient)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          
          {/* Progress arc showing current value */}
          <path
            d={describeArc(radius, radius, radius - strokeWidth / 2, 180, 180 + normalizedValue * 1.8)}
            fill="none"
            stroke={risk.color}
            strokeWidth={strokeWidth * 1.2}
            strokeLinecap="round"
            opacity="0.8"
          />
          
          {/* Needle/Pointer */}
          <g transform={`translate(${radius}, ${radius}) rotate(${rotation})`}>
            <line
              x1="0"
              y1="0"
              x2="0"
              y2={-(radius - strokeWidth * 2)}
              stroke={risk.color}
              strokeWidth={strokeWidth * 0.6}
              strokeLinecap="round"
            />
            <circle
              cx="0"
              cy="0"
              r={strokeWidth}
              fill={risk.color}
            />
          </g>
          
          {/* Center circle */}
          <circle
            cx={radius}
            cy={radius}
            r={strokeWidth * 1.5}
            fill="white"
            stroke={risk.color}
            strokeWidth={strokeWidth * 0.4}
          />
          
          {/* Labels for segments */}
          <text
            x={radius - 50}
            y="25"
            fontSize={diameter / 16}
            fontWeight="bold"
            fill="#27ae60"
            textAnchor="middle"
          >
            Low
          </text>
          <text
            x={radius + 50}
            y="35"
            fontSize={diameter / 16}
            fontWeight="bold"
            fill="#f39c12"
            textAnchor="middle"
          >
            Moderate
          </text>
          <text
            x={radius + 60}
            y={diameter - 20}
            fontSize={diameter / 16}
            fontWeight="bold"
            fill="#e74c3c"
            textAnchor="middle"
          >
            High
          </text>
          <text
            x={radius - 50}
            y={diameter - 20}
            fontSize={diameter / 16}
            fontWeight="bold"
            fill="#c0392b"
            textAnchor="middle"
          >
            Critical
          </text>
        </svg>
        
        {/* Value display */}
        <div className="risk-dial-display">
          <div className="risk-value">{normalizedValue.toFixed(0)}</div>
          <div className="risk-label">{label}</div>
          <div className={`risk-level ${risk.level.toLowerCase()}`}>
            <span className="risk-icon">{risk.icon}</span>
            <span className="risk-text">{risk.level}</span>
          </div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="risk-dial-legend">
        <div className="legend-item">
          <span className="legend-color low"></span>
          <span className="legend-label">Low: 0-40</span>
        </div>
        <div className="legend-item">
          <span className="legend-color moderate"></span>
          <span className="legend-label">Moderate: 40-70</span>
        </div>
        <div className="legend-item">
          <span className="legend-color high"></span>
          <span className="legend-label">High: 70-85</span>
        </div>
        <div className="legend-item">
          <span className="legend-color critical"></span>
          <span className="legend-label">Critical: 85-100</span>
        </div>
      </div>
    </div>
  );
};

/**
 * Utility function to describe SVG arc path
 * Used for creating the circular gauge segments
 */
function describeArc(x, y, radius, startAngle, endAngle) {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArc = endAngle - startAngle <= 180 ? "0" : "1";
  
  return [
    "M", start.x, start.y,
    "A", radius, radius, 0, largeArc, 0, end.x, end.y
  ].join(" ");
}

/**
 * Convert polar coordinates to cartesian
 */
function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians)
  };
}

export default RiskDial;
