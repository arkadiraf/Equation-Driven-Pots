import os
import glob
import math
import struct
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

# ==========================================
# 1. ADVANCED SPHERICAL DESIGN LIBRARY
# ==========================================

SPHERICAL_DESIGNS = {
    "Perfect Sphere": "R",
    "Dragon Egg (Diamond)": "R * (1 + 0.08 * cos(10*theta + 8*phi) + 0.08 * cos(10*theta - 8*phi))",
    "Twisted Hex Vortex": "R * (1 + 0.15 * cos(6 * (theta + phi*2)))",
    "Ribbed Art Deco": "R * (1 + 0.15 * pow(cos(8*theta), 4) * sin(phi))",
    "Equatorial Flare": "R * (1 + 0.4 * exp(-pow(phi-1.57, 2)*10))",
    "Cellular Organic": "R * (1 + 0.06 * (sin(8*theta)*cos(10*phi) + sin(11*theta)*cos(5*phi)))",
    "Pumpkin Lobes": "R * (1 + 0.15 * cos(8 * theta))",
    "Starfruit": "R * (1 + 0.25 * cos(5 * theta) * sin(phi))",
    "Hourglass Peanut": "R * (1 - 0.25 * sin(2 * phi))",
    "Coral Brain": "R * (1 + 0.08 * sin(10 * theta + 5*phi) * sin(8 * phi))",
    "Woven Basket": "R * (1 + 0.05 * sin(12 * theta) * cos(8 * phi))"
}

# ==========================================
# 2. CORE GEOMETRY GENERATOR
# ==========================================

def generate_spherical_mesh(equation, scale=10.0, resT=140, resP=80, outer_only=False):
    """
    Generates vertices and triangular faces for spherical r(theta, phi) equations.
    If outer_only is True, it skips the inner shell and stitching (used for fast preview generation).
    """
    baseR = 5.0
    wall = 0.35
    topCut = math.radians(25)
    botFlatten = math.radians(150)
    botCut = math.radians(175)
    
    # Safe math environment for python eval()
    env = {
        "pi": math.pi, "sin": math.sin, "cos": math.cos, 
        "pow": math.pow, "exp": math.exp, "min": min, 
        "max": max, "abs": abs, "sqrt": math.sqrt, "R": baseR
    }
    
    def eval_r(theta, phi):
        env.update({"theta": theta, "phi": phi})
        try: return float(eval(equation, {"__builtins__": {}}, env))
        except: return baseR

    oRings, iRings = [], []
    minZ = float('inf')
    flatBottomZ = baseR * math.cos(botFlatten)

    # Calculate coordinates
    for ip in range(resP + 1):
        phi = topCut + (botCut - topCut) * (ip / resP)
        oR, iR = [], []
        for it in range(resT):
            t = 2 * math.pi * it / resT
            rOut = eval_r(t, phi)
            rIn = max(0.1, rOut - wall)

            oX = rOut * math.sin(phi) * math.cos(t)
            oY = rOut * math.sin(phi) * math.sin(t)
            oZ = rOut * math.cos(phi)

            iX = rIn * math.sin(phi) * math.cos(t)
            iY = rIn * math.sin(phi) * math.sin(t)
            iZ = rIn * math.cos(phi)

            # Flatten the bottom at 150 degrees
            if phi >= botFlatten or oZ < flatBottomZ:
                oZ = flatBottomZ
                iZ = flatBottomZ + wall

            if oZ < minZ: minZ = oZ
            oR.append((oX, oY, oZ))
            if not outer_only: iR.append((iX, iY, iZ))
            
        oRings.append(oR)
        if not outer_only: iRings.append(iR)

    vertices, faces = [], []
    
    # Zero-Shift logic
    def add_v(pt):
        # Shift Z so bottom is perfectly at 0, map to standard coordinate space
        vertices.append((pt[0] * scale, pt[1] * scale, (pt[2] - minZ) * scale))
        return len(vertices) - 1

    oIdx, iIdx = [], []
    for ip in range(resP + 1):
        oIdx.append([add_v(pt) for pt in oRings[ip]])
        if not outer_only: iIdx.append([add_v(pt) for pt in iRings[ip]])

    # Stitch faces
    for it in range(resT):
        it1 = (it + 1) % resT
        for ip in range(resP):
            # Outer shell faces
            faces.extend([
                (oIdx[ip][it], oIdx[ip+1][it], oIdx[ip+1][it1]), 
                (oIdx[ip][it], oIdx[ip+1][it1], oIdx[ip][it1])
            ])
            # Inner shell faces
            if not outer_only:
                faces.extend([
                    (iIdx[ip][it], iIdx[ip][it1], iIdx[ip+1][it1]), 
                    (iIdx[ip][it], iIdx[ip+1][it1], iIdx[ip+1][it])
                ])
                
        # Top and bottom bridging
        if not outer_only:
            faces.extend([
                (oIdx[0][it], oIdx[0][it1], iIdx[0][it1]), 
                (oIdx[0][it], iIdx[0][it1], iIdx[0][it]),
                (oIdx[resP][it], iIdx[resP][it], iIdx[resP][it1]), 
                (oIdx[resP][it], iIdx[resP][it1], oIdx[resP][it1])
            ])
            
    return vertices, faces

# ==========================================
# 3. EXPORT & VISUALIZATION UTILITIES
# ==========================================

def calculate_normal(v1, v2, v3):
    u = [v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2]]
    v = [v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2]]
    n = [u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0]]
    length = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
    if length == 0: return (0,0,0)
    return (n[0]/length, n[1]/length, n[2]/length)

def export_binary_stl(filename, vertices, faces):
    with open(filename, 'wb') as f:
        f.write(bytes(80)) # 80-byte empty header
        f.write(struct.pack('<I', len(faces))) # Number of triangles
        for face in faces:
            v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            nx, ny, nz = calculate_normal(v1, v2, v3)
            f.write(struct.pack('<12fH', nx, ny, nz, *v1, *v2, *v3, 0))

def generate_matplotlib_preview(filename, name, vertices, faces):
    """Renders the aesthetic Matplotlib plot using Poly3DCollection."""
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Format vertices for Poly3DCollection
    poly3d = [[vertices[idx] for idx in face] for face in faces]
    
    # Aesthetic styling (Tan fill, Saddlebrown edges)
    collection = Poly3DCollection(poly3d, facecolors='tan', edgecolors='saddlebrown', alpha=0.8, linewidths=0.2)
    ax.add_collection3d(collection)
    
    # Format the scene
    ax.set_title(name, fontsize=14, pad=10, fontweight='bold', color='#2c3e50')
    
    # Calculate bounds dynamically
    verts_array = np.array(vertices)
    max_range = np.array([verts_array[:,0].max()-verts_array[:,0].min(), 
                          verts_array[:,1].max()-verts_array[:,1].min(), 
                          verts_array[:,2].max()-verts_array[:,2].min()]).max() / 2.0

    mid_x = (verts_array[:,0].max()+verts_array[:,0].min()) * 0.5
    mid_y = (verts_array[:,1].max()+verts_array[:,1].min()) * 0.5
    mid_z = (verts_array[:,2].max()+verts_array[:,2].min()) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    ax.set_box_aspect([1, 1, 1]) # Ensure it doesn't look stretched

    ax.axis('off') # Hide grid lines for clean presentation
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#f4f7f6')
    plt.close()

def create_image_grid(image_folder="images", output_file="spherical_design_summary.jpg", cols=3):
    image_paths = sorted(glob.glob(os.path.join(image_folder, "*.jpg")))
    if not image_paths: return
    
    rows = math.ceil(len(image_paths) / cols)
    first_image = Image.open(image_paths[0])
    tile_w, tile_h = first_image.size
    
    grid_img = Image.new('RGB', (cols * tile_w, rows * tile_h), (244, 247, 246))
    
    for i, path in enumerate(image_paths):
        img = Image.open(path)
        col, row = i % cols, i // cols
        grid_img.paste(img, (col * tile_w, row * tile_h))
        
    grid_img.save(output_file, quality=90)
    print(f"\n[+] Created grid summary: {output_file}")

# ==========================================
# 4. MAIN BATCH PROCESS
# ==========================================

if __name__ == "__main__":
    os.makedirs("3dModels", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    print(f"--- Processing {len(SPHERICAL_DESIGNS)} Spherical Designs ---")
    
    for name, eq in SPHERICAL_DESIGNS.items():
        safe_name = name.replace(" ", "_").replace("/", "").replace("(", "").replace(")", "")
        print(f"Generating [{name}]...")
        
        # 1. High-Res STL Export
        high_verts, high_faces = generate_spherical_mesh(eq, resT=140, resP=80, outer_only=False)
        export_binary_stl(f"3dModels/{safe_name}.stl", high_verts, high_faces)
        
        # 2. Lower-Res Preview Export (outer shell only to save plotting time)
        low_verts, low_faces = generate_spherical_mesh(eq, resT=60, resP=40, outer_only=True)
        generate_matplotlib_preview(f"images/{safe_name}.jpg", name, low_verts, low_faces)
        
    # 3. Create Final Arrangement
    print("\nStitching preview grid...")
    create_image_grid(cols=3)
    
    print("Batch processing complete! Check the /3dModels and /images folders.")