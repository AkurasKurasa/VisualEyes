import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Box } from '@react-three/drei';
import * as THREE from 'three';
import { FaPlay, FaPause, FaRedo } from 'react-icons/fa';

const ArrayElement = ({ position, value, index, isHighlighted }) => {
    const mesh = useRef();
    const group = useRef();
    const animationStartTime = useRef(null);

    useFrame((state) => {
        if (!group.current) return;

        // Bounce animation logic
        if (isHighlighted) {
            const now = state.clock.getElapsedTime();

            // Initialize start time if we just started highlighting
            if (animationStartTime.current === null) {
                animationStartTime.current = now;
            }

            const elapsed = now - animationStartTime.current;
            const duration = 0.5; // Swipe/Bounce duration in seconds

            if (elapsed < duration) {
                // Smooth single bounce (sin wave 0 -> 1 -> 0)
                const bounceHeight = 0.8;
                // pi * elapsed / duration maps 0..duration to 0..pi
                const yOffset = Math.sin((elapsed / duration) * Math.PI) * bounceHeight;
                group.current.position.y = position[1] + yOffset;
            } else {
                // Animation finished
                group.current.position.y = position[1];
            }
        } else {
            // Reset state when not highlighted
            animationStartTime.current = null;
            group.current.position.y = position[1];
        }
    });

    return (
        <group position={position} ref={group}>
            {/* The 2D Square representing the array index */}
            <Box args={[1, 1, 0.1]} ref={mesh}>
                <meshBasicMaterial color={isHighlighted ? "#ff9800" : "#4caf50"} />
                {/* Border outline effect */}
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(1, 1, 0.1)]} />
                    <lineBasicMaterial color="black" linewidth={2} />
                </lineSegments>
            </Box>

            {/* Index Label above */}
            <Text
                position={[0, 0.8, 0.1]}
                fontSize={0.3}
                color={isHighlighted ? "#ff9800" : "white"}
                anchorX="center"
                anchorY="middle"
            >
                {index}
            </Text>

            {/* Value Label centered */}
            <Text
                position={[0, 0, 0.11]}
                fontSize={0.5}
                color="black"
                anchorX="center"
                anchorY="middle"
            >
                {value}
            </Text>
        </group>
    );
};

const SetElement = ({ position, value, isHighlighted }) => {
    const group = useRef();
    const animationStartTime = useRef(null);

    useFrame((state) => {
        if (!group.current) return;

        // Bounce animation logic
        if (isHighlighted) {
            const now = state.clock.getElapsedTime();
            if (animationStartTime.current === null) {
                animationStartTime.current = now;
            }
            const elapsed = now - animationStartTime.current;
            const duration = 0.5;

            if (elapsed < duration) {
                // Smooth single bounce
                const bounceHeight = 0.8;
                const yOffset = Math.sin((elapsed / duration) * Math.PI) * bounceHeight;
                group.current.position.y = position[1] + yOffset;
            } else {
                group.current.position.y = position[1];
            }
        } else {
            animationStartTime.current = null;
            group.current.position.y = position[1];
        }
    });

    return (
        <group position={position} ref={group}>
            {/* Circular Token using Cylinder */}
            <mesh rotation={[Math.PI / 2, 0, 0]}>
                <cylinderGeometry args={[0.5, 0.5, 0.1, 32]} />
                <meshBasicMaterial color={isHighlighted ? "#ff4081" : "#9c27b0"} />
                {/* Border outline */}
                <lineSegments>
                    <edgesGeometry args={[new THREE.CylinderGeometry(0.5, 0.5, 0.1, 32)]} />
                    <lineBasicMaterial color="black" linewidth={2} />
                </lineSegments>
            </mesh>

            {/* Value Label centered */}
            <Text
                position={[0, 0, 0.11]}
                fontSize={0.4}
                color="white"
                anchorX="center"
                anchorY="middle"
            >
                {value}
            </Text>
        </group>
    );
};

const DictionaryElement = ({ position, k, v, isHighlighted }) => {
    const group = useRef();

    // Optional bounce animation could go here

    return (
        <group position={position} ref={group}>
            {/* KEY Box (Orange/Yellow) */}
            <mesh position={[0, 0.6, 0]}>
                <boxGeometry args={[1.4, 0.8, 0.1]} />
                <meshBasicMaterial color="#ffc107" />
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(1.4, 0.8, 0.1)]} />
                    <lineBasicMaterial color="black" linewidth={2} />
                </lineSegments>
            </mesh>
            <Text position={[0, 0.6, 0.11]} fontSize={0.35} color="black" anchorX="center" anchorY="middle">
                {k}
            </Text>

            {/* VALUE Box (Green) */}
            <mesh position={[0, -0.4, 0]}>
                <boxGeometry args={[1.4, 0.8, 0.1]} />
                <meshBasicMaterial color={isHighlighted ? "#ff9800" : "#4caf50"} />
                <lineSegments>
                    <edgesGeometry args={[new THREE.BoxGeometry(1.4, 0.8, 0.1)]} />
                    <lineBasicMaterial color="black" linewidth={2} />
                </lineSegments>
            </mesh>
            <Text position={[0, -0.4, 0.11]} fontSize={0.4} color="black" anchorX="center" anchorY="middle">
                {v}
            </Text>
        </group>
    );
};

const DraggableStructure = ({ structure, highlightIndex, initialY, overrideValue, indexHighlights = [] }) => {
    const { name, data, type } = structure; // type is 'array' or 'set' or 'variable' or 'dictionary'
    const { viewport } = useThree();

    // Use the overridden value if provided (for animation), otherwise original data
    const displayValue = overrideValue !== undefined ? overrideValue : data;

    const [position, setPosition] = useState([0, 0, 0]);

    useEffect(() => {
        // Center the structure initially but apply Y offset
        // Variables don't have length, so center them simpler
        const len = type === 'variable' ? 1 : data.length;
        const initialX = -((len * 1.5) / 2) + 0.75;
        setPosition([initialX, initialY, 0]);
    }, [data.length, type, initialY]);

    const [isDragging, setIsDragging] = useState(false);
    const dragOffset = useRef([0, 0]);

    const getPointerWorldPos = (e) => {
        return {
            x: (e.pointer.x * viewport.width) / 2,
            y: (e.pointer.y * viewport.height) / 2
        };
    };

    const onDown = (e) => {
        e.stopPropagation();
        e.target.setPointerCapture(e.pointerId);
        setIsDragging(true);
        const ptr = getPointerWorldPos(e);
        dragOffset.current = [ptr.x - position[0], ptr.y - position[1]];
    };

    const onMove = (e) => {
        if (!isDragging) return;
        const ptr = getPointerWorldPos(e);
        setPosition([ptr.x - dragOffset.current[0], ptr.y - dragOffset.current[1], 0]);
    };

    const onUp = (e) => {
        setIsDragging(false);
        e.target.releasePointerCapture(e.pointerId);
    };

    const isSet = type === 'set';
    const isVar = type === 'variable';
    const isDict = type === 'dictionary';

    if (isVar) {
        return (
            <>
                <group
                    position={position}
                    onPointerDown={onDown}
                    onPointerMove={onMove}
                    onPointerUp={onUp}
                >
                    {/* Variable Card */}
                    <mesh position={[0, 0, -0.1]}>
                        <planeGeometry args={[4, 1.5]} />
                        <meshBasicMaterial color="#2196f3" transparent opacity={0.3} />
                        <lineSegments>
                            <edgesGeometry args={[new THREE.PlaneGeometry(4, 1.5)]} />
                            <lineBasicMaterial color="#2196f3" linewidth={2} />
                        </lineSegments>
                    </mesh>

                    <Text
                        position={[0, 0, 0]}
                        fontSize={0.6}
                        color="white"
                        anchorX="center"
                        anchorY="middle"
                    >
                        {name} = {displayValue}
                    </Text>
                </group>
                <OrbitControls enableRotate={false} enablePan={!isDragging} />
            </>
        )
    }

    return (
        <>
            <group
                position={position}
                onPointerDown={onDown}
                onPointerMove={onMove}
                onPointerUp={onUp}
            >
                {/* Invisible hit box for easier dragging */}
                <mesh visible={false}>
                    <planeGeometry args={[data.length * 1.5 + 4, 4]} />
                </mesh>

                <Text
                    position={[-1.5, 0, 0]}
                    fontSize={0.8}
                    color="white"
                    anchorX="right"
                    anchorY="middle"
                >
                    {name} = {isSet ? "{" : isDict ? "{" : "["}
                </Text>

                {data.map((value, index) => {
                    const xPos = index * 1.6; // Slightly wider spacing
                    const isIndexHighlighted = indexHighlights.includes(index);
                    const isLoopHighlighted = highlightIndex === index;
                    const isHighlighted = isIndexHighlighted || isLoopHighlighted;

                    if (isDict) {
                        return (
                            <DictionaryElement
                                key={index}
                                position={[xPos, 0, 0]}
                                k={value.key}
                                v={value.value}
                                isHighlighted={isHighlighted}
                            />
                        );
                    }
                    return isSet ? (
                        <SetElement
                            key={index}
                            position={[xPos, 0, 0]}
                            value={value}
                            isHighlighted={isHighlighted}
                        />
                    ) : (
                        <ArrayElement
                            key={index}
                            position={[xPos, 0, 0]}
                            value={value}
                            index={index}
                            isHighlighted={isHighlighted}
                        />
                    );
                })}

                <Text
                    position={[(data.length * 1.6) - 0.5, 0, 0]} // Adjusted closing bracket position
                    fontSize={0.8}
                    color="white"
                    anchorX="left"
                    anchorY="middle"
                >
                    {isSet ? "}" : isDict ? "}" : "]"}
                </Text>
            </group>
            <OrbitControls enableRotate={false} enablePan={!isDragging} />
        </>
    );
};

const Visualizer = ({ visualData, onIterationChange }) => {
    const [highlightIndex, setHighlightIndex] = useState(-1);
    const [isLooping, setIsLooping] = useState(false);

    // Use a ref for onIterationChange to avoid stale closures in setInterval
    const onIterationChangeRef = useRef(onIterationChange);
    useEffect(() => {
        onIterationChangeRef.current = onIterationChange;
    }, [onIterationChange]);

    // Identify which structure to loop over
    let loopTargetStructure = null;
    if (visualData?.loopTarget) {
        // If a target variable is specified (e.g. "for x in arr"), strictly look for it.
        loopTargetStructure = visualData.structures?.find(s => s.name === visualData.loopTarget);
    } else {
        // If no target identified (e.g. "while" loop), default to the first structure.
        loopTargetStructure = visualData?.structures?.[0];
    }

    // Variable Overrides for Loop Animation
    const [variableOverrides, setVariableOverrides] = useState({});

    // Index Highlighting State
    const [indexHighlights, setIndexHighlights] = useState({});

    // Process index operations only when Run is pressed (lastRun exists)
    useEffect(() => {
        if (visualData?.lastRun && visualData?.indexOperations && visualData.indexOperations.length > 0) {
            const highlights = {};
            visualData.indexOperations.forEach(op => {
                if (!highlights[op.varName]) {
                    highlights[op.varName] = [];
                }
                highlights[op.varName] = [...highlights[op.varName], ...op.indices];
            });
            setIndexHighlights(highlights);
        } else if (!visualData?.lastRun) {
            // Clear highlights when not running
            setIndexHighlights({});
        }
    }, [visualData?.indexOperations, visualData?.lastRun]);

    useEffect(() => {
        let interval;
        if (isLooping && loopTargetStructure) {
            interval = setInterval(() => {
                setHighlightIndex((prev) => {
                    const next = prev + 1;
                    if (next >= loopTargetStructure.data.length) {
                        // Loop finished
                        setIsLooping(false);
                        setVariableOverrides({});
                        return -1;
                    }

                    // Update the iterator variable value
                    if (visualData.loopIterator) {
                        const currentVal = loopTargetStructure.data[next];

                        console.log(`Loop iteration ${next}: currentVal = ${currentVal}`);

                        setVariableOverrides(prevOverrides => {
                            const newOverrides = { ...prevOverrides };

                            // 1. Update Iterator
                            newOverrides[visualData.loopIterator] = currentVal;

                            // 2. Update Dependencies
                            if (visualData.loopDependencies && Array.isArray(visualData.loopDependencies)) {
                                visualData.loopDependencies.forEach(dep => {
                                    // dep can be object { name, formula } or legacy string
                                    const depName = typeof dep === 'object' ? dep.name : dep;
                                    const formula = typeof dep === 'object' ? dep.formula : null;

                                    if (formula) {
                                        // Evaluate formula: replace vars with values from scope
                                        try {
                                            // Build Scope: Current Overrides + Base Structure Data
                                            const scope = { _index: next };
                                            visualData.structures.forEach(s => scope[s.name] = s.data); // Base data
                                            Object.assign(scope, newOverrides); // Apply current animation overrides (e.g. i=10)

                                            // Skip if iterator is undefined
                                            if (scope[visualData.loopIterator] === undefined) {
                                                console.warn(`Skipping formula evaluation: ${visualData.loopIterator} is undefined`);
                                                return;
                                            }

                                            // Create function with scope keys as args
                                            const keys = Object.keys(scope);
                                            const values = Object.values(scope);

                                            // Debug logging
                                            console.log(`Evaluating formula: ${formula}`);
                                            console.log('Scope:', scope);

                                            // Use a specific 'Math' context if needed or just global JS math
                                            // Python 'i + 3' works in JS. 
                                            // Python 'i ** 2' works in JS (ES7).
                                            // Python 'pow(i, 2)' -> works if we alias Math.pow? For now support operators.
                                            const func = new Function(...keys, `return ${formula}`);
                                            const result = func(...values);

                                            console.log(`Result: ${result}`);
                                            newOverrides[depName] = result;
                                        } catch (e) {
                                            console.warn("Formula eval failed", e);
                                            // Fallback to simple assignment if possible or ignore
                                        }
                                    } else {
                                        // Direct assignment fallback
                                        newOverrides[depName] = currentVal;
                                    }
                                });
                            }
                            return newOverrides;
                        });
                    }

                    if (onIterationChangeRef.current) {
                        onIterationChangeRef.current(next);
                    }
                    return next;
                });
            }, 800); // 800ms delay between steps
        } else {
            clearInterval(interval);
        }
        return () => clearInterval(interval);
    }, [isLooping, loopTargetStructure, visualData]); // Added visualData to dependency array to ensure fresh access

    // Handle reset when new data comes in
    useEffect(() => {
        setIsLooping(false);
        setHighlightIndex(-1);
        setVariableOverrides({});

        // Clear index highlights unless this is a Run trigger
        if (!visualData?.lastRun) {
            setIndexHighlights({});
        }

        // If lastRun timestamp exists and hasLoop is true, start loop animation
        if (visualData?.lastRun && visualData?.hasLoop) {
            // Start from -1 so first increment goes to 0
            setHighlightIndex(-1);
            setIsLooping(true);
        }
    }, [visualData]);


    const handlePlay = () => {
        if (!visualData) return;
        setHighlightIndex(-1);
        setVariableOverrides({});
        setIsLooping(true);
    };

    const handlePause = () => {
        setIsLooping(false);
    };

    const handleReset = () => {
        setIsLooping(false);
        setHighlightIndex(-1);
        setVariableOverrides({});
    };


    if (!visualData || !visualData.structures) {
        return (
            <div style={{ width: '100%', height: '100%', backgroundColor: '#111', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#333' }}>
                {/* Blank state */}
            </div>
        );
    }

    const { structures, hasLoop } = visualData;

    const startingY = 2;
    const structureSpacing = 3;

    return (
        <div style={{ width: '100%', height: '100%', backgroundColor: '#111', position: 'relative' }}>
            <Canvas orthographic camera={{ zoom: 50, position: [0, 0, 100] }}>
                <ambientLight intensity={1} />
                {visualData.structures.map((structure, idx) => {
                    // Check if we have an override for this structure in the current iteration
                    let override = undefined;
                    if (highlightIndex >= 0 && visualData.iterationState && visualData.iterationState[highlightIndex]) {
                        const state = visualData.iterationState[highlightIndex];
                        if (state[structure.name] !== undefined) {
                            override = state[structure.name];
                        }
                    }

                    return (
                        <DraggableStructure
                            key={`${structure.name}-${idx}`}
                            structure={structure}
                            highlightIndex={highlightIndex}
                            initialY={startingY - (idx * structureSpacing)}
                            overrideValue={override}
                            indexHighlights={indexHighlights[structure.name] || []}
                        />
                    );
                })}
            </Canvas>

            <div style={{ position: 'absolute', bottom: 10, left: 10, color: '#aaa', fontSize: '0.8rem' }}>
                Scroll to Zoom • Pan to Move • Drag Array to Reposition
            </div>

            {/* Looping Controls - Only show if loop detected */}
            {hasLoop && (
                <div style={{
                    position: 'absolute',
                    bottom: 20,
                    right: 20,
                    display: 'flex',
                    gap: '10px',
                    backgroundColor: 'rgba(0,0,0,0.5)',
                    padding: '10px',
                    borderRadius: '8px'
                }}>
                    {!isLooping ? (
                        <button onClick={handlePlay} style={controlBtnStyle} title="Start Loop">
                            <FaPlay size={16} />
                        </button>
                    ) : (
                        <button onClick={handlePause} style={controlBtnStyle} title="Pause">
                            <FaPause size={16} />
                        </button>
                    )}
                    <button onClick={handleReset} style={controlBtnStyle} title="Reset">
                        <FaRedo size={16} />
                    </button>
                </div>
            )}
        </div>
    );
};

const controlBtnStyle = {
    background: 'none',
    border: 'none',
    color: 'white',
    cursor: 'pointer',
    padding: '5px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'color 0.2s',
};

export default Visualizer;
