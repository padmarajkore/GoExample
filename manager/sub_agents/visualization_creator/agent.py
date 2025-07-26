from google.adk.agents import Agent
import json
import re
from typing import Dict, List, Any, Optional

def validate_concept(concept: str) -> dict:
    """Validate and categorize the educational concept."""
    if not concept or len(concept.strip()) < 2:
        return {"valid": False, "error": "Concept must be at least 2 characters long"}
    
    # Define concept categories for better visualization selection
    categories = {
        "science": ["atom", "molecule", "dna", "cell", "planet", "solar system", "gravity", "wave", "electron"],
        "math": ["function", "geometry", "graph", "equation", "calculus", "statistics", "probability"],
        "geography": ["earth", "mountain", "volcano", "continent", "ocean", "climate"],
        "biology": ["heart", "brain", "ecosystem", "photosynthesis", "evolution"],
        "physics": ["force", "energy", "magnetism", "electricity", "quantum", "particle"],
        "chemistry": ["reaction", "bond", "periodic table", "compound", "solution"]
    }
    
    concept_lower = concept.lower()
    detected_category = "general"
    
    for category, keywords in categories.items():
        if any(keyword in concept_lower for keyword in keywords):
            detected_category = category
            break
    
    return {
        "valid": True, 
        "concept": concept.strip(), 
        "category": detected_category,
        "complexity": "basic" if len(concept.split()) <= 2 else "advanced"
    }

def generate_3d_template(concept_data: dict) -> str:
    """Generate appropriate 3D visualization template based on concept category."""
    concept = concept_data["concept"]
    category = concept_data["category"]
    
    # Base HTML structure with Three.js
    base_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Visualization: {concept}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Arial', sans-serif;
            overflow: hidden;
        }}
        #container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        #info {{
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            z-index: 100;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border-radius: 10px;
            max-width: 300px;
        }}
        #controls {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 100;
        }}
        .control-btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .control-btn:hover {{
            background: rgba(255,255,255,0.4);
        }}
        #loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 24px;
            z-index: 200;
        }}
    </style>
</head>
<body>
    <div id="loading">Loading 3D Visualization...</div>
    <div id="container">
        <div id="info">
            <h2>{concept}</h2>
            <p>Interactive 3D educational visualization</p>
            <p><strong>Category:</strong> {category.title()}</p>
            <p><strong>Controls:</strong> Mouse to rotate, scroll to zoom</p>
        </div>
        <div id="controls">
            <button class="control-btn" onclick="resetView()">Reset View</button>
            <button class="control-btn" onclick="toggleAnimation()">Toggle Animation</button>
            <button class="control-btn" onclick="toggleInfo()">Toggle Info</button>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Global variables
        let scene, camera, renderer, controls;
        let animationActive = true;
        let mainObject;
        
        // Initialize the 3D scene
        function init() {{
            // Scene setup
            scene = new THREE.Scene();
            scene.fog = new THREE.Fog(0x050505, 2000, 3500);
            
            // Camera setup
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 0, 5);
            
            // Renderer setup
            renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            document.getElementById('container').appendChild(renderer.domElement);
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(10, 10, 5);
            directionalLight.castShadow = true;
            scene.add(directionalLight);
            
            // Create concept-specific visualization
            createVisualization();
            
            // Mouse controls
            setupControls();
            
            // Start animation
            animate();
            
            // Hide loading
            document.getElementById('loading').style.display = 'none';
        }}
        
        function createVisualization() {{
            {get_category_specific_code(category, concept)}
        }}
        
        function setupControls() {{
            let isDragging = false;
            let previousMousePosition = {{ x: 0, y: 0 }};
            
            renderer.domElement.addEventListener('mousedown', function(e) {{
                isDragging = true;
            }});
            
            renderer.domElement.addEventListener('mousemove', function(e) {{
                if (isDragging) {{
                    const deltaMove = {{
                        x: e.offsetX - previousMousePosition.x,
                        y: e.offsetY - previousMousePosition.y
                    }};
                    
                    if (mainObject) {{
                        mainObject.rotation.y += deltaMove.x * 0.01;
                        mainObject.rotation.x += deltaMove.y * 0.01;
                    }}
                }}
                
                previousMousePosition = {{ x: e.offsetX, y: e.offsetY }};
            }});
            
            renderer.domElement.addEventListener('mouseup', function(e) {{
                isDragging = false;
            }});
            
            // Zoom with mouse wheel
            renderer.domElement.addEventListener('wheel', function(e) {{
                e.preventDefault();
                camera.position.z += e.deltaY * 0.01;
                camera.position.z = Math.max(2, Math.min(20, camera.position.z));
            }});
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            
            if (animationActive && mainObject) {{
                mainObject.rotation.y += 0.005;
            }}
            
            renderer.render(scene, camera);
        }}
        
        // Control functions
        function resetView() {{
            camera.position.set(0, 0, 5);
            if (mainObject) {{
                mainObject.rotation.set(0, 0, 0);
            }}
        }}
        
        function toggleAnimation() {{
            animationActive = !animationActive;
        }}
        
        function toggleInfo() {{
            const info = document.getElementById('info');
            info.style.display = info.style.display === 'none' ? 'block' : 'none';
        }}
        
        // Handle window resize
        window.addEventListener('resize', function() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        // Initialize when page loads
        window.addEventListener('load', init);
    </script>
</body>
</html>'''
    
    return base_template

def get_category_specific_code(category: str, concept: str) -> str:
    """Generate category-specific 3D visualization code."""
    
    category_code = {
        "science": '''
            // Create atomic structure or molecular model
            const group = new THREE.Group();
            
            // Central nucleus
            const nucleusGeometry = new THREE.SphereGeometry(0.3, 32, 32);
            const nucleusMaterial = new THREE.MeshLambertMaterial({ color: 0xff4444 });
            const nucleus = new THREE.Mesh(nucleusGeometry, nucleusMaterial);
            group.add(nucleus);
            
            // Electron orbits and electrons
            for (let i = 0; i < 3; i++) {
                // Orbit ring
                const orbitGeometry = new THREE.RingGeometry(1 + i * 0.8, 1.02 + i * 0.8, 64);
                const orbitMaterial = new THREE.MeshBasicMaterial({ 
                    color: 0x4488ff, 
                    transparent: true, 
                    opacity: 0.3,
                    side: THREE.DoubleSide 
                });
                const orbit = new THREE.Mesh(orbitGeometry, orbitMaterial);
                orbit.rotation.x = Math.PI / 2;
                orbit.rotation.z = i * Math.PI / 6;
                group.add(orbit);
                
                // Electron
                const electronGeometry = new THREE.SphereGeometry(0.1, 16, 16);
                const electronMaterial = new THREE.MeshLambertMaterial({ color: 0x44ff44 });
                const electron = new THREE.Mesh(electronGeometry, electronMaterial);
                const radius = 1 + i * 0.8;
                electron.position.set(radius, 0, 0);
                
                // Animate electron orbit
                const electronOrbit = new THREE.Group();
                electronOrbit.add(electron);
                electronOrbit.rotation.x = Math.PI / 2;
                electronOrbit.rotation.z = i * Math.PI / 6;
                group.add(electronOrbit);
                
                // Store reference for animation
                electron.userData = { orbitGroup: electronOrbit, speed: 0.02 + i * 0.01 };
            }
            
            mainObject = group;
            scene.add(mainObject);
        ''',
        
        "math": '''
            // Create mathematical visualization (function graph or geometric shape)
            const group = new THREE.Group();
            
            // Create a 3D function surface
            const geometry = new THREE.ParametricGeometry((u, v, target) => {
                const x = (u - 0.5) * 4;
                const z = (v - 0.5) * 4;
                const y = Math.sin(x) * Math.cos(z) * 0.5;
                target.set(x, y, z);
            }, 50, 50);
            
            const material = new THREE.MeshLambertMaterial({ 
                color: 0x44aa88,
                wireframe: false,
                transparent: true,
                opacity: 0.8
            });
            
            const surface = new THREE.Mesh(geometry, material);
            group.add(surface);
            
            // Add coordinate axes
            const axesHelper = new THREE.AxesHelper(3);
            group.add(axesHelper);
            
            // Add grid
            const gridHelper = new THREE.GridHelper(6, 20, 0x444444, 0x444444);
            gridHelper.position.y = -1;
            group.add(gridHelper);
            
            mainObject = group;
            scene.add(mainObject);
        ''',
        
        "biology": '''
            // Create biological structure (cell, DNA helix, etc.)
            const group = new THREE.Group();
            
            // DNA Double Helix
            const helixGroup = new THREE.Group();
            
            for (let i = 0; i < 100; i++) {
                const angle = i * 0.3;
                const y = i * 0.05 - 2.5;
                
                // First strand
                const sphere1 = new THREE.Mesh(
                    new THREE.SphereGeometry(0.08, 8, 8),
                    new THREE.MeshLambertMaterial({ color: 0xff6b6b })
                );
                sphere1.position.set(
                    Math.cos(angle) * 0.8,
                    y,
                    Math.sin(angle) * 0.8
                );
                helixGroup.add(sphere1);
                
                // Second strand
                const sphere2 = new THREE.Mesh(
                    new THREE.SphereGeometry(0.08, 8, 8),
                    new THREE.MeshLambertMaterial({ color: 0x4ecdc4 })
                );
                sphere2.position.set(
                    Math.cos(angle + Math.PI) * 0.8,
                    y,
                    Math.sin(angle + Math.PI) * 0.8
                );
                helixGroup.add(sphere2);
                
                // Base pairs (every 10th)
                if (i % 10 === 0) {
                    const basePair = new THREE.Mesh(
                        new THREE.CylinderGeometry(0.02, 0.02, 1.6),
                        new THREE.MeshLambertMaterial({ color: 0xffe66d })
                    );
                    basePair.position.set(0, y, 0);
                    basePair.rotation.z = angle;
                    helixGroup.add(basePair);
                }
            }
            
            group.add(helixGroup);
            mainObject = group;
            scene.add(mainObject);
        ''',
        
        "default": '''
            // Generic 3D visualization
            const group = new THREE.Group();
            
            // Create an interesting geometric composition
            const geometries = [
                new THREE.BoxGeometry(1, 1, 1),
                new THREE.SphereGeometry(0.7, 32, 32),
                new THREE.ConeGeometry(0.6, 1.2, 8),
                new THREE.CylinderGeometry(0.5, 0.5, 1, 8)
            ];
            
            const colors = [0xff6b6b, 0x4ecdc4, 0x45b7d1, 0xf39c12, 0x9b59b6];
            
            for (let i = 0; i < 4; i++) {
                const material = new THREE.MeshLambertMaterial({ 
                    color: colors[i],
                    transparent: true,
                    opacity: 0.8
                });
                const mesh = new THREE.Mesh(geometries[i], material);
                
                // Position in a circle
                const angle = (i / 4) * Math.PI * 2;
                mesh.position.set(
                    Math.cos(angle) * 2,
                    Math.sin(i) * 0.5,
                    Math.sin(angle) * 2
                );
                
                group.add(mesh);
            }
            
            // Add connecting lines
            const lineGeometry = new THREE.BufferGeometry();
            const positions = [];
            for (let i = 0; i < 4; i++) {
                const angle1 = (i / 4) * Math.PI * 2;
                const angle2 = ((i + 1) % 4 / 4) * Math.PI * 2;
                positions.push(
                    Math.cos(angle1) * 2, Math.sin(i) * 0.5, Math.sin(angle1) * 2,
                    Math.cos(angle2) * 2, Math.sin(i + 1) * 0.5, Math.sin(angle2) * 2
                );
            }
            lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            
            const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, opacity: 0.6, transparent: true });
            const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
            group.add(lines);
            
            mainObject = group;
            scene.add(mainObject);
        '''
    }
    
    return category_code.get(category, category_code["default"])

def create_advanced_visualization_html(concept: str, options: Optional[Dict[str, Any]] = None) -> dict:
    """Generate an advanced 3D HTML visualization with enhanced features."""
    try:
        # Validate the concept
        validation = validate_concept(concept)
        if not validation["valid"]:
            return {"status": "error", "message": validation["error"]}
        
        # Set default options
        if options is None:
            options = {}
        
        options.setdefault("include_controls", True)
        options.setdefault("include_info", True)
        options.setdefault("animation", True)
        options.setdefault("responsive", True)
        
        # Generate the HTML
        html_content = generate_3d_template(validation)
        
        return {
            "status": "success",
            "concept": validation["concept"],
            "category": validation["category"],
            "html": html_content,
            "features": [
                "Interactive 3D visualization",
                "Mouse controls (rotate, zoom)",
                "Animation controls",
                "Responsive design",
                "Educational information panel",
                f"Category-specific visualization ({validation['category']})"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate visualization: {str(e)}"
        }

def get_concept_suggestions(category: Optional[str] = None) -> dict:
    """Provide suggestions for educational concepts that work well with 3D visualization."""
    suggestions = {
        "science": [
            "Atomic Structure", "Molecular Bonds", "Solar System", "DNA Helix", 
            "Wave Propagation", "Electromagnetic Field", "Crystal Lattice"
        ],
        "math": [
            "3D Functions", "Geometric Transformations", "Calculus Surfaces", 
            "Statistical Distributions", "Fractal Patterns", "Vector Fields"
        ],
        "biology": [
            "Cell Structure", "Protein Folding", "Neural Networks", "Heart Anatomy", 
            "Photosynthesis Process", "Ecosystem Food Web"
        ],
        "physics": [
            "Particle Interactions", "Magnetic Fields", "Gravity Wells", 
            "Quantum States", "Energy Levels", "Force Diagrams"
        ],
        "chemistry": [
            "Chemical Reactions", "Periodic Table", "Molecular Geometry", 
            "Phase Transitions", "Catalysis Process", "Electron Orbitals"
        ]
    }
    
    if category and category in suggestions:
        return {"suggestions": suggestions[category], "category": category}
    else:
        all_suggestions = []
        for cat_suggestions in suggestions.values():
            all_suggestions.extend(cat_suggestions)
        return {"suggestions": all_suggestions[:15], "category": "all"}

# Enhanced ADK Agent
visualization_creator = Agent(
    name="advanced_visualization_creator",
    model="gemini-2.5-pro",
    description="""
    Advanced agent that generates interactive 3D HTML visualizations for educational concepts.
    Specializes in creating engaging, scientifically accurate visualizations across multiple domains
    including science, mathematics, biology, physics, and chemistry.
    """,
    instruction="""
    You are an advanced educational visualization agent that creates comprehensive, interactive 3D HTML visualizations.

    Key capabilities:
    1. Generate complete, working HTML files with Three.js 3D visualizations
    2. Adapt visualization style based on educational concept category
    3. Include interactive controls (rotation, zoom, animation toggle)
    4. Provide educational context and information panels
    5. Ensure responsive design for various screen sizes
    6. Implement proper lighting, materials, and visual effects

    Guidelines:
    - Always output complete, functional HTML code
    - Include educational information about the concept
    - Make visualizations scientifically accurate when possible
    - Add interactive elements to enhance learning
    - Use appropriate colors and styling for the educational context
    - Include loading states and error handling
    - Optimize for performance and smooth animations

    Output format: Provide only the complete HTML code without any additional text or explanations.
    The HTML should be ready to save and open in any modern web browser.
    """,
    tools=[
        create_advanced_visualization_html,
        validate_concept,
        get_concept_suggestions
    ],
)