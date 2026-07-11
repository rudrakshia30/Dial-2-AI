import { useEffect, useState, useRef } from 'react';
import { apiFetch } from '../lib/api';

export default function GraphVisualizer({ onSelectNode, selectedNodeId }) {
  const [data, setData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [draggedNode, setDraggedNode] = useState(null);
  
  const containerRef = useRef(null);
  const simulationRef = useRef(null);
  const nodesRef = useRef([]);
  const linksRef = useRef([]);

  const width = 800;
  const height = 500;

  // Colors based on theme
  const NODE_COLORS = {
    Person: '#22d3ee',   // Cyan
    City: '#fb923c',     // Orange
    Topic: '#a78bfa',    // Purple
  };

  const LINK_COLORS = {
    LIVES_IN: 'rgba(251, 146, 60, 0.25)',
    INTERESTED_IN: 'rgba(167, 139, 250, 0.25)',
  };

  useEffect(() => {
    // Fetch live graph layout data from backend
    apiFetch('/api/neo4j/graph')
      .then((res) => {
        // Initialize positions randomly near the center
        const nodes = res.nodes.map((node) => ({
          ...node,
          x: width / 2 + (Math.random() - 0.5) * 200,
          y: height / 2 + (Math.random() - 0.5) * 200,
          vx: 0,
          vy: 0,
        }));
        
        // Map link sources and targets to actual node objects
        const links = res.links.map((link) => {
          const sourceNode = nodes.find((n) => n.id === link.source);
          const targetNode = nodes.find((n) => n.id === link.target);
          return {
            ...link,
            sourceNode,
            targetNode,
          };
        }).filter(l => l.sourceNode && l.targetNode);

        nodesRef.current = nodes;
        linksRef.current = links;
        setData({ nodes, links });
      })
      .catch((err) => console.error("Error loading graph data:", err))
      .finally(() => setLoading(false));

    // Force simulation loop
    const step = () => {
      const nodes = nodesRef.current;
      const links = linksRef.current;

      if (nodes.length === 0) {
        simulationRef.current = requestAnimationFrame(step);
        return;
      }

      const chargeStrength = -500; // Repulsion force
      const linkStrength = 0.06;   // Link pull force
      const gravityStrength = 0.04; // Center pull force
      const damping = 0.83;        // Velocity friction

      // 1. Repulsion between all nodes (N-Body Charge)
      for (let i = 0; i < nodes.length; i++) {
        const n1 = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const n2 = nodes[j];
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const distSq = dx * dx + dy * dy + 0.1;
          const dist = Math.sqrt(distSq);

          if (dist < 300) {
            const force = chargeStrength / distSq;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            if (n1 !== draggedNode) {
              n1.vx += fx;
              n1.vy += fy;
            }
            if (n2 !== draggedNode) {
              n2.vx -= fx;
              n2.vy -= fy;
            }
          }
        }
      }

      // 2. Link attraction
      for (let i = 0; i < links.length; i++) {
        const link = links[i];
        const n1 = link.sourceNode;
        const n2 = link.targetNode;

        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.1;

        // Desired length is around 90px
        const targetLen = 100;
        const force = (dist - targetLen) * linkStrength;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        if (n1 !== draggedNode) {
          n1.vx += fx;
          n1.vy += fy;
        }
        if (n2 !== draggedNode) {
          n2.vx -= fx;
          n2.vy -= fy;
        }
      }

      // 3. Gravity pulling to center & Update Positions
      const cx = width / 2;
      const cy = height / 2;
      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        if (node === draggedNode) continue;

        const dx = cx - node.x;
        const dy = cy - node.y;

        node.vx += dx * gravityStrength;
        node.vy += dy * gravityStrength;

        // Apply velocities
        node.x += node.vx;
        node.y += node.vy;

        // Apply friction
        node.vx *= damping;
        node.vy *= damping;

        // Boundary constraints
        node.x = Math.max(20, Math.min(width - 20, node.x));
        node.y = Math.max(20, Math.min(height - 20, node.y));
      }

      // Force state update to re-render SVG
      setData({ nodes: [...nodes], links: [...links] });
      simulationRef.current = requestAnimationFrame(step);
    };

    simulationRef.current = requestAnimationFrame(step);

    return () => {
      if (simulationRef.current) {
        cancelAnimationFrame(simulationRef.current);
      }
    };
  }, [draggedNode]);

  // Dragging event handlers
  const handleMouseDown = (e, node) => {
    setDraggedNode(node);
    if (onSelectNode) {
      onSelectNode(node);
    }
  };

  const handleMouseMove = (e) => {
    if (!draggedNode || !containerRef.current) return;
    const svgRect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - svgRect.left;
    const mouseY = e.clientY - svgRect.top;

    draggedNode.x = mouseX;
    draggedNode.y = mouseY;
    draggedNode.vx = 0;
    draggedNode.vy = 0;
  };

  const handleMouseUp = () => {
    setDraggedNode(null);
  };

  if (loading) {
    return (
      <div className="h-96 w-full flex items-center justify-center text-gray-400 text-sm glass-card border border-white/5">
        Rendering Graph Network...
      </div>
    );
  }

  return (
    <div className="relative glass-card border border-white/5 overflow-hidden w-full flex flex-col items-center">
      <div className="absolute top-4 left-4 z-10 flex flex-wrap gap-4 text-xs bg-gray-950/80 backdrop-blur-xl border border-white/5 px-3 py-2 rounded-xl">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: NODE_COLORS.Person }} />
          <span className="text-gray-300">Callers (Person)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: NODE_COLORS.City }} />
          <span className="text-gray-300">Cities (City)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: NODE_COLORS.Topic }} />
          <span className="text-gray-300">Interests (Topic)</span>
        </div>
      </div>

      <svg
        ref={containerRef}
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="cursor-grab active:cursor-grabbing select-none"
      >
        {/* Render links */}
        {data.links.map((link, idx) => (
          <line
            key={`link-${idx}`}
            x1={link.sourceNode.x}
            y1={link.sourceNode.y}
            x2={link.targetNode.x}
            y2={link.targetNode.y}
            stroke={LINK_COLORS[link.type] || 'rgba(255,255,255,0.08)'}
            strokeWidth={1.5}
            strokeDasharray={link.type === 'LIVES_IN' ? '3,3' : 'none'}
          />
        ))}

        {/* Render nodes */}
        {data.nodes.map((node) => (
          <g
            key={`node-${node.id}`}
            transform={`translate(${node.x}, ${node.y})`}
            onMouseDown={(e) => handleMouseDown(e, node)}
          >
            {selectedNodeId === node.id && (
              <circle
                r={node.type === 'Person' ? 15 : 13}
                fill="none"
                stroke={NODE_COLORS[node.type]}
                strokeWidth={1.5}
                className="animate-ping"
                style={{ opacity: 0.8 }}
              />
            )}
            <circle
              r={node.type === 'Person' ? 9 : 7}
              fill={NODE_COLORS[node.type] || '#fff'}
              className="transition-transform duration-200 hover:scale-125 cursor-pointer"
              style={{
                filter: `drop-shadow(0 0 4px ${NODE_COLORS[node.type]}40)`,
                stroke: selectedNodeId === node.id ? '#fff' : 'none',
                strokeWidth: selectedNodeId === node.id ? 1.5 : 0,
              }}
            />
            <text
              y={-14}
              textAnchor="middle"
              className="text-[10px] fill-gray-300 font-semibold pointer-events-none select-none bg-gray-900/50"
            >
              {node.name.length > 14 ? node.name.substring(0, 12) + '..' : node.name}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
