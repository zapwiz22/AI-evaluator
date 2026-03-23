import React from 'react';

const MetricsGauge = ({ label, percentage, isDanger }) => {
    // If it's a "danger" metric (like plagiarism), high numbers are red. 
    // Otherwise, standard colors.
    const getColor = (val) => {
        if (val < 20) return '#4caf50'; // Green
        if (val < 60) return '#ff9800'; // Orange
        return '#f44336'; // Red
    };

    const barColor = isDanger ? getColor(percentage) : '#2196f3';

    return (
        <div style={{ marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <strong>{label}</strong>
                <span>{percentage}%</span>
            </div>
            <div style={{ width: '100%', backgroundColor: '#e0e0e0', borderRadius: '4px', height: '10px' }}>
                <div 
                    style={{ 
                        width: `${percentage}%`, 
                        backgroundColor: barColor, 
                        height: '100%', 
                        borderRadius: '4px',
                        transition: 'width 1s ease-in-out'
                    }} 
                />
            </div>
        </div>
    );
};

export default MetricsGauge;