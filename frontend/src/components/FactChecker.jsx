import React from 'react';

const FactChecker = ({ claims }) => {
    if (!claims || claims.length === 0) return null;

    const getStatusStyle = (status) => {
        switch (status) {
            case 'Verified':
                return { bg: '#e8f5e9', text: '#2e7d32', border: '#c8e6c9' };
            case 'Contradicted':
                return { bg: '#ffebee', text: '#c62828', border: '#ffcdd2' };
            default: // Unverified or Error
                return { bg: '#fff3e0', text: '#ef6c00', border: '#ffe0b2' };
        }
    };

    return (
        <div style={{ background: '#ffffff', padding: '20px', borderRadius: '8px', border: '1px solid #dee2e6', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
            <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Automated Fact-Check</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '15px' }}>
                {claims.map((item, index) => {
                    const styles = getStatusStyle(item.status);
                    
                    return (
                        <div key={index} style={{ padding: '15px', borderRadius: '6px', backgroundColor: styles.bg, border: `1px solid ${styles.border}` }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                                <strong style={{ fontSize: '15px', flex: 1 }}>"{item.claim}"</strong>
                                <span style={{ 
                                    marginLeft: '15px', 
                                    padding: '4px 8px', 
                                    borderRadius: '12px', 
                                    fontSize: '12px', 
                                    fontWeight: 'bold',
                                    backgroundColor: styles.text,
                                    color: 'white'
                                }}>
                                    {item.status}
                                </span>
                            </div>
                            <p style={{ margin: 0, fontSize: '14px', color: '#555' }}>
                                <strong>AI Analysis:</strong> {item.reason}
                            </p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default FactChecker;