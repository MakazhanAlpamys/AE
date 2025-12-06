import React from 'react';

interface LogoProps {
    className?: string;
}

const Logo: React.FC<LogoProps> = ({ className = '' }) => {
    return (
        <div className={`logo-container ${className}`} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="logoGradient" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stopColor="var(--primary)" />
                        <stop offset="100%" stopColor="var(--secondary)" />
                    </linearGradient>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Outer Hexagon */}
                <path
                    d="M20 2 L37.32 12 V32 L20 42 L2.68 32 V12 Z"
                    stroke="url(#logoGradient)"
                    strokeWidth="2.5"
                    fill="none"
                    transform="scale(0.85) translate(3.5, -1)"
                    filter="url(#glow)"
                />

                {/* Inner Circuit Lines */}
                <path
                    d="M20 10 V18 M20 22 V30 M12 24 L16 20 M28 24 L24 20"
                    stroke="var(--text-primary)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    opacity="0.8"
                />

                {/* Center Dot */}
                <circle cx="20" cy="20" r="3" fill="var(--primary)" filter="url(#glow)" />
            </svg>

            <div className="logo-text" style={{ display: 'flex', flexDirection: 'column', lineHeight: '1' }}>
                <span style={{
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    letterSpacing: '-0.03em',
                    background: 'linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                }}>
                    IntegrityOS
                </span>
                <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 600,
                    color: 'var(--primary)',
                    letterSpacing: '0.15em',
                    textTransform: 'uppercase',
                    marginTop: '2px'
                }}>
                    System
                </span>
            </div>
        </div>
    );
};

export default Logo;
