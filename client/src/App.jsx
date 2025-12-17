import React, { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { FaPlay } from 'react-icons/fa';
import './App.css';

import Visualizer from './components/Visualizer';

import { CommandController } from './utils/CommandController';

function App() {
  const [editorCode, setEditorCode] = useState('# Define an array to visualize it\narr = [1, 2, 3, 4, 5]\n\n# Print check\nprint("Hello visualizer")\nprint(arr)');
  const [visualData, setVisualData] = useState(null);

  // Terminal Output
  const [terminalOutput, setTerminalOutput] = useState([]);
  const [userInput, setUserInput] = useState('');

  // Resizable Divider State
  const [leftWidth, setLeftWidth] = useState(50);
  const isDragging = useRef(false);

  const startDrag = () => {
    isDragging.current = true;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  const onDrag = (e) => {
    if (!isDragging.current) return;
    const newWidth = (e.clientX / window.innerWidth) * 100;
    // Limit width between 20% and 80%
    if (newWidth > 20 && newWidth < 80) {
      setLeftWidth(newWidth);
    }
  };

  const stopDrag = () => {
    isDragging.current = false;
    document.body.style.cursor = 'default';
    document.body.style.userSelect = 'auto';
  };

  useEffect(() => {
    window.addEventListener('mousemove', onDrag);
    window.addEventListener('mouseup', stopDrag);
    return () => {
      window.removeEventListener('mousemove', onDrag);
      window.removeEventListener('mouseup', stopDrag);
    };
  }, []);

  // Real-time Parsing Effect
  useEffect(() => {
    // USE COMMAND CONTROLLER (Async)
    const fetchData = async () => {
      const { structures, hasLoop, loopTarget, loopIterator, loopDependencies } = await CommandController.parse(editorCode);

      if (structures.length > 0) {
        setVisualData({ structures, hasLoop, loopTarget, loopIterator, loopDependencies });
      } else {
        setVisualData(null);
      }
    };
    fetchData();
  }, [editorCode]);

  const handleRun = async () => {
    // 1. Get latest parsed data via Controller
    const { structures, hasLoop, loopTarget, loopIterator, loopDependencies } = await CommandController.parse(editorCode);

    // 2. Simulated Print Logic
    const newLogs = [];
    const printRegex = /print\s*\((.*?)\)/g;
    let printMatch;

    while ((printMatch = printRegex.exec(editorCode)) !== null) {
      const content = printMatch[1].trim();

      if ((content.startsWith('"') && content.endsWith('"')) ||
        (content.startsWith("'") && content.endsWith("'"))) {
        newLogs.push(content.slice(1, -1));
      } else {
        const foundStruct = structures.find(s => s.name === content);
        if (foundStruct) {
          if (foundStruct.type === 'set') {
            newLogs.push(`{${foundStruct.data.join(', ')}}`);
          } else if (foundStruct.type === 'dictionary') {
            const dictStr = foundStruct.data.map(e => `'${e.key}': ${e.value}`).join(', ');
            newLogs.push(`{${dictStr}}`);
          } else {
            newLogs.push(`[${foundStruct.data.join(', ')}]`);
          }
        } else {
          newLogs.push(`NameError: name '${content}' is not defined (or not supported)`);
        }
      }
    }
    setTerminalOutput(newLogs);

    // 3. Trigger Animation
    // We update visualData with a 'lastRun' timestamp to signal start
    setVisualData({ structures, hasLoop, loopTarget, loopIterator, loopDependencies, lastRun: Date.now() });
  };

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
  };

  const handleInputKeyDown = (e) => {
    if (e.key === 'Enter') {
      // For now, just clear input. Logic can be added later.
      setUserInput('');
    }
  };

  return (
    <div className="app-container" style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>

      {/* LEFT: Visualization Panel */}
      <div style={{ width: `${leftWidth}%`, position: 'relative', overflow: 'hidden' }}>
        <Visualizer visualData={visualData} />
      </div>

      {/* MIDDLE: Resizable Divider */}
      <div
        onMouseDown={startDrag}
        style={{
          width: '5px',
          backgroundColor: '#333',
          cursor: 'col-resize',
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {/* Grip handle visual */}
        <div style={{ width: '1px', height: '20px', backgroundColor: '#666' }}></div>
      </div>

      {/* RIGHT: Editor & Terminal Panel */}
      <div style={{ width: `${100 - leftWidth}%`, display: 'flex', flexDirection: 'column' }}>

        {/* Top: Editor Toolbar */}
        <div className="sidebar" style={{ flex: 2, display: 'flex', flexDirection: 'column', borderBottom: '1px solid #333' }}>
          <div className="actions" style={{ padding: '10px', borderBottom: '1px solid #333', display: 'flex', gap: '10', justifyContent: 'flex-end' }}>
            <button onClick={handleRun} style={{ display: 'flex', alignItems: 'center', gap: '5px', backgroundColor: '#4caf50', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}>
              <FaPlay size={12} /> Run
            </button>
          </div>

          <div className="content" style={{ flex: 1, overflow: 'hidden' }}>
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={editorCode}
              onChange={(value) => setEditorCode(value)}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
              }}
            />
          </div>
        </div>

        {/* Bottom: Terminal */}
        <div style={{ flex: 1, backgroundColor: '#0f0f0f', color: '#ccc', fontFamily: 'monospace', padding: '10px', display: 'flex', flexDirection: 'column', minHeight: '150px' }}>
          <div style={{ borderBottom: '1px solid #333', marginBottom: '5px', paddingBottom: '5px', fontSize: '12px', color: '#666', textTransform: 'uppercase' }}>
            Terminal Output
          </div>
          <div style={{ overflowY: 'auto', flex: 1, marginBottom: '10px' }}>
            {terminalOutput.length === 0 ? (
              <span style={{ color: '#444', fontStyle: 'italic' }}>Run code to see output...</span>
            ) : (
              terminalOutput.map((line, i) => (
                <div key={i} style={{ lineHeight: '1.4' }}>{line}</div>
              ))
            )}
          </div>

          {/* Input Area */}
          <div style={{ display: 'flex', alignItems: 'center', borderTop: '1px solid #333', paddingTop: '5px' }}>
            <span style={{ color: '#4caf50', marginRight: '8px' }}>&gt;</span>
            <input
              type="text"
              value={userInput}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              placeholder="Enter command..."
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                color: 'white',
                fontFamily: 'monospace',
                flex: 1,
                outline: 'none'
              }}
            />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
