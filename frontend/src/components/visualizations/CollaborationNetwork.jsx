import React, { useEffect, useRef } from 'react';

const CollaborationNetwork = ({ data }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.nodes || !data.links) return;

    const svg = svgRef.current;
    const width = svg.clientWidth || 600;
    const height = svg.clientHeight || 400;

    // Clear previous content
    svg.innerHTML = '';

    // Create SVG group for zoom/pan
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    svg.appendChild(g);

    // Simple force simulation using basic calculations
    const nodes = data.nodes.map(d => ({ ...d, x: Math.random() * width, y: Math.random() * height }));
    const links = data.links.map(d => ({ ...d }));

    // Simple physics simulation
    const simulation = () => {
      for (let i = 0; i < 50; i++) {
        // Apply forces
        nodes.forEach(node => {
          let fx = 0, fy = 0;
          
          // Centering force
          fx += (width / 2 - node.x) * 0.01;
          fy += (height / 2 - node.y) * 0.01;
          
          // Repulsion from other nodes
          nodes.forEach(other => {
            if (other !== node) {
              const dx = node.x - other.x;
              const dy = node.y - other.y;
              const distance = Math.sqrt(dx * dx + dy * dy) || 1;
              const force = 100 / (distance * distance);
              fx += dx * force;
              fy += dy * force;
            }
          });
          
          // Link forces
          links.forEach(link => {
            if (link.source === node.id) {
              const target = nodes.find(n => n.id === link.target);
              if (target) {
                const dx = target.x - node.x;
                const dy = target.y - node.y;
                fx += dx * 0.1;
                fy += dy * 0.1;
              }
            }
            if (link.target === node.id) {
              const source = nodes.find(n => n.id === link.source);
              if (source) {
                const dx = source.x - node.x;
                const dy = source.y - node.y;
                fx += dx * 0.1;
                fy += dy * 0.1;
              }
            }
          });
          
          node.x += fx * 0.5;
          node.y += fy * 0.5;
          
          // Keep nodes in bounds
          node.x = Math.max(20, Math.min(width - 20, node.x));
          node.y = Math.max(20, Math.min(height - 20, node.y));
        });
      }
    };

    simulation();

    // Draw links
    links.forEach(link => {
      const source = nodes.find(n => n.id === link.source);
      const target = nodes.find(n => n.id === link.target);
      
      if (source && target) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', source.x);
        line.setAttribute('y1', source.y);
        line.setAttribute('x2', target.x);
        line.setAttribute('y2', target.y);
        line.setAttribute('stroke', '#94a3b8');
        line.setAttribute('stroke-width', Math.sqrt(link.weight || 1));
        line.setAttribute('opacity', '0.6');
        g.appendChild(line);
      }
    });

    // Draw nodes
    nodes.forEach(node => {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', node.x);
      circle.setAttribute('cy', node.y);
      circle.setAttribute('r', Math.sqrt((node.publications || 1) * 3));
      circle.setAttribute('fill', node.id === 'main' ? '#3b82f6' : '#64748b');
      circle.setAttribute('stroke', '#ffffff');
      circle.setAttribute('stroke-width', '2');
      circle.setAttribute('opacity', '0.8');
      
      // Add hover effect
      circle.style.cursor = 'pointer';
      circle.addEventListener('mouseenter', () => {
        circle.setAttribute('opacity', '1');
        circle.setAttribute('stroke-width', '3');
      });
      circle.addEventListener('mouseleave', () => {
        circle.setAttribute('opacity', '0.8');
        circle.setAttribute('stroke-width', '2');
      });
      
      g.appendChild(circle);

      // Add label
      if (node.name) {
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + Math.sqrt((node.publications || 1) * 3) + 15);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '10');
        text.setAttribute('fill', '#374151');
        text.textContent = node.name.length > 15 ? node.name.substring(0, 15) + '...' : node.name;
        g.appendChild(text);
      }
    });

  }, [data]);

  // Default empty state
  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-muted-foreground">
        <div className="text-center">
          <div className="text-lg font-medium mb-2">Нет данных для отображения</div>
          <div className="text-sm">Сеть сотрудничества будет показана здесь</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-96 border rounded-lg bg-gray-50/50">
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        style={{ minHeight: '300px' }}
        viewBox="0 0 600 400"
        preserveAspectRatio="xMidYMid meet"
      />
    </div>
  );
};

export default CollaborationNetwork;
