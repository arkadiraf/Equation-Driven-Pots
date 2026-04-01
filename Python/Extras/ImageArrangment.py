import os
import glob
import math
from PIL import Image

def create_image_grid(image_folder="images", output_file="design_summary.jpg", cols=3):
    """
    Combines all JPG images in a folder into one large grid.
    """
    # 1. Gather all JPG files
    # We sort them to keep them in order of design name
    image_paths = sorted(glob.glob(os.path.join(image_folder, "*.jpg")))
    
    if not image_paths:
        print(f"Error: No .jpg files found in '{image_folder}' folder.")
        return

    num_images = len(image_paths)
    rows = math.ceil(num_images / cols)
    print(f"Found {num_images} images. Creating a {cols}x{rows} grid...")

    # 2. Get dimensions from the first image
    first_image = Image.open(image_paths[0])
    w, h = first_image.size
    
    # We can downscale the tiles slightly so the final image 
    # isn't too massive to open (e.g., 50% scale)
    scale = 0.5
    tile_w, tile_h = int(w * scale), int(h * scale)

    # 3. Create a blank white canvas for the grid
    grid_w = cols * tile_w
    grid_h = rows * tile_h
    grid_img = Image.new('RGB', (grid_w, grid_h), (255, 255, 255))

    # 4. Loop through images and paste into the grid
    for i, path in enumerate(image_paths):
        img = Image.open(path)
        
        # Resize to fit the tile
        img = img.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        
        # Calculate position (x, y)
        col = i % cols
        row = i // cols
        x_pos = col * tile_w
        y_pos = row * tile_h
        
        grid_img.paste(img, (x_pos, y_pos))

    # 5. Save the final image
    grid_img.save(output_file, quality=90)
    print(f"Summary image saved successfully as '{output_file}'")

if __name__ == "__main__":
    # You can change the folder name or column count here
    create_image_grid(image_folder="images", output_file="pot_designs_3xn_grid.jpg", cols=3)