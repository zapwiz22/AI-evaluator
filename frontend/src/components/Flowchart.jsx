import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
});

const Flowchart = ({ chartCode }) => {
  const containerRef = useRef(null);
  const renderIdRef = useRef(`mermaid-chart-${Math.random().toString(36).slice(2)}`);

  useEffect(() => {
    if (chartCode && containerRef.current) {
      // Clear previous chart
      containerRef.current.innerHTML = '';
      // Render new chart
      mermaid.render(renderIdRef.current, chartCode).then((result) => {
        containerRef.current.innerHTML = result.svg;
      }).catch(err => {
        console.error("Mermaid syntax error:", err);
        containerRef.current.innerHTML = '<p style="color:red;">Error rendering flowchart. AI generated invalid syntax.</p>';
      });
    }
  }, [chartCode]);

  return <div ref={containerRef} className="mermaid-container" />;
};

export default Flowchart;