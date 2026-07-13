import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import GraphVisualizer from '../components/GraphVisualizer';
import { apiFetch } from '../lib/api';

export default function KnowledgeGraph() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [matchingNodes, setMatchingNodes] = useState([]);
  const [graphData, setGraphData] = useState({ nodes: [] });

  useEffect(() => {
    // Load node names for search autocompletion
    apiFetch('/api/neo4j/graph')
      .then((res) => setGraphData(res))
      .catch((err) => console.error("Error loading graph lookup:", err));
  }, []);

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.trim().length >= 2) {
      const matches = graphData.nodes.filter(
        (n) => n.name.toLowerCase().includes(query.toLowerCase())
      );
      setMatchingNodes(matches);
    } else {
      setMatchingNodes([]);
    }
  };

  const selectMatchedNode = (node) => {
    setSelectedNode(node);
    setSearchQuery(node.name);
    setMatchingNodes([]);
  };

  return (
    <>
      <style jsx global>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(18px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .glass-card {
          background: rgba(17, 24, 39, 0.6);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 1rem;
        }
      `}</style>

      <div className="flex min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
        <Sidebar />

        <main className="flex-1 ml-0 lg:ml-64 p-4 pt-16 lg:pt-8 lg:p-8 overflow-y-auto" style={{ animation: 'fadeInUp 0.5s ease-out' }}>
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight">
                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  Knowledge Graph
                </span>
              </h1>
              <p className="text-gray-400 mt-1 text-sm">Explore live caller-topic relationship maps on Neo4j AuraDB</p>
            </div>

            {/* Node Search Bar */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search node name..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="pl-4 pr-10 py-2.5 w-64 rounded-xl bg-gray-800/60 backdrop-blur border border-white/10 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 transition"
              />
              <svg className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>

              {/* AutocompleteDropdown */}
              {matchingNodes.length > 0 && (
                <div className="absolute top-full right-0 w-full mt-2 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden z-20 max-h-48 overflow-y-auto">
                  {matchingNodes.map((node) => (
                    <button
                      key={node.id}
                      onClick={() => selectMatchedNode(node)}
                      className="w-full text-left px-4 py-2 text-xs hover:bg-white/5 border-b border-white/5 last:border-0 transition"
                    >
                      <span className="font-semibold text-gray-200">{node.name}</span>
                      <span className="ml-2 text-gray-500 font-mono">({node.type})</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
            {/* The Graph Visualizer */}
            <div className="xl:col-span-3">
              <GraphVisualizer
                onSelectNode={(node) => setSelectedNode(node)}
                selectedNodeId={selectedNode?.id}
              />
            </div>

            {/* Node detail side panel */}
            <div className="glass-card p-6 flex flex-col justify-between h-[500px]">
              {selectedNode ? (
                <div className="space-y-6 overflow-y-auto">
                  <div>
                    <span className="text-[10px] font-bold bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/20 uppercase tracking-widest">
                      Node Properties
                    </span>
                    <h2 className="text-xl font-bold text-white mt-2 break-all">{selectedNode.name}</h2>
                    <p className="text-xs text-gray-400 mt-1 font-mono uppercase">Label: {selectedNode.type}</p>
                  </div>

                  <div className="space-y-3">
                    <div className="text-xs p-3 rounded-lg bg-gray-800/40 border border-white/[0.02]">
                      <p className="text-gray-500 font-semibold mb-1">Node Identifier</p>
                      <p className="text-gray-200 font-mono break-all">{selectedNode.id}</p>
                    </div>

                    <div className="text-xs p-3 rounded-lg bg-gray-800/40 border border-white/[0.02]">
                      <p className="text-gray-500 font-semibold mb-1">AuraDB Cypher Traversal</p>
                      <pre className="text-emerald-400 font-mono overflow-x-auto whitespace-pre-wrap">
                        {selectedNode.type === 'Person'
                          ? `MATCH (p:Person {phone: "${selectedNode.id}"})\nRETURN p`
                          : selectedNode.type === 'City'
                            ? `MATCH (c:City {name: "${selectedNode.name}"})<-[:LIVES_IN]-(p:Person)\nRETURN p.name`
                            : `MATCH (t:Topic {name: "${selectedNode.name}"})<-[:INTERESTED_IN]-(p:Person)\nRETURN p.name`}
                      </pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-4">
                  <svg className="w-12 h-12 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 15l-6 6m0 0l-6-6m6 6V9a6 6 0 0112 0v3" />
                  </svg>
                  <p className="text-sm font-semibold text-gray-300">No node selected</p>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                    Click on any node circle inside the network map to inspect its properties and traversals.
                  </p>
                </div>
              )}

              {selectedNode && (
                <button
                  onClick={() => setSelectedNode(null)}
                  className="w-full py-2 bg-gray-800/50 hover:bg-gray-800 border border-white/5 rounded-xl text-xs font-semibold tracking-wide text-gray-400 hover:text-white transition"
                >
                  Clear Selection
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
