import os
from PIL import Image, ImageSequence
from pygifsicle import optimize

# ==========================================
# USER CONFIGURATION
# ==========================================

input_file = "input.gif"
output_file = "output.gif"

# --- STRATEGY 1: FRAME SKIPPING (Best for huge weight reduction) ---
# 1 = Original FPS (No skip)
# 2 = Keep 1 every 2 frames (50% weight reduction, half FPS)
# 3 = Keep 1 every 3 frames
skip_factor = 3

# --- STRATEGY 2: RESIZING ---
# 1.0 = Original Size
# 0.75 = 75% of original size
scale_factor = 0.74

# --- STRATEGY 3: GIFSICLE OPTIMIZATION ---
use_gifsicle = False      # Requires gifsicle installed/exe present
lossy_level = 30          # 0 to 200. Higher = lighter weight but more noise.
reduce_colors = False     # Set False to keep YOUR original colors perfectly.

# ==========================================
# MAIN SCRIPT
# ==========================================

def process_gif():
    try:
        print(f"Processing: {input_file}...")
        original_size = os.path.getsize(input_file)

        with Image.open(input_file) as im:
            # 1. Extract and Filter Frames
            frames = [f.copy() for f in ImageSequence.Iterator(im)]
            selected_frames = frames[::skip_factor]
            
            # 2. Resize Frames
            final_frames = []
            for frame in selected_frames:
                if scale_factor != 1.0:
                    new_w = int(frame.width * scale_factor)
                    new_h = int(frame.height * scale_factor)
                    frame = frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
                final_frames.append(frame)

            # 3. Calculate new duration to match original speed
            # If we skip frames, the remaining ones must last longer
            orig_duration = im.info.get('duration', 100)
            new_duration = orig_duration * skip_factor

            # 4. Save Initial Pass (Pillow)
            print("Saving manipulated frames...")
            final_frames[0].save(
                output_file,
                save_all=True,
                append_images=final_frames[1:],
                optimize=False, # Let Gifsicle handle optimization later
                duration=new_duration,
                loop=0,
                disposal=2
            )

        # 5. Gifsicle Pass (Compression)
        if use_gifsicle:
            print("Running Gifsicle optimization...")
            
            # Build options list
            opts = ["--optimize=3"] # Max optimization level
            if lossy_level > 0:
                opts.append(f"--lossy={lossy_level}")
            
            # Only reduce colors if explicitly requested
            colors_param = 256 if not reduce_colors else 128
            
            optimize(output_file, colors=colors_param, options=opts)

        # --- REPORT ---
        final_size = os.path.getsize(output_file)
        reduction = ((original_size - final_size) / original_size) * 100
        
        print("\n" + "="*30)
        print(f"Original: {original_size/1024:.2f} KB")
        print(f"Final:    {final_size/1024:.2f} KB")
        print(f"Reduced:  {reduction:.2f}%")
        print("="*30)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_gif()