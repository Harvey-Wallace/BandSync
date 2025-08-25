#!/usr/bin/env python3
"""Simple script to create a basic favicon.ico file"""

# Create a minimal ICO file manually
# This is a simple 16x16 favicon with a blue background and white "B"
ico_data = bytes([
    # ICO Header
    0x00, 0x00,  # Reserved
    0x01, 0x00,  # Type (1 = ICO)
    0x01, 0x00,  # Number of images
    
    # Image Directory Entry
    0x10,        # Width (16)
    0x10,        # Height (16)
    0x00,        # Color count (0 = 256+)
    0x00,        # Reserved
    0x01, 0x00,  # Planes
    0x20, 0x00,  # Bits per pixel (32)
    0x00, 0x04, 0x00, 0x00,  # Size of image data (1024 bytes)
    0x16, 0x00, 0x00, 0x00,  # Offset to image data
])

# Create a simple 16x16 RGBA bitmap (blue background, white B in center)
bitmap_data = bytearray(1024)  # 16x16x4 bytes (RGBA)

# Fill with blue background
for i in range(0, 1024, 4):
    bitmap_data[i] = 0xFF      # Blue
    bitmap_data[i+1] = 0x7B    # Green  
    bitmap_data[i+2] = 0x00    # Red
    bitmap_data[i+3] = 0xFF    # Alpha

# Draw a simple "B" shape (white pixels)
b_pixels = [
    # Simple B pattern (row, col)
    (4, 4), (4, 5), (4, 6), (4, 7), (4, 8),  # Top horizontal
    (5, 4), (5, 8),                           # Sides
    (6, 4), (6, 5), (6, 6), (6, 7),          # Middle horizontal
    (7, 4), (7, 8),                           # Sides
    (8, 4), (8, 8),                           # Sides
    (9, 4), (9, 5), (9, 6), (9, 7),          # Middle horizontal
    (10, 4), (10, 8),                         # Sides
    (11, 4), (11, 5), (11, 6), (11, 7), (11, 8) # Bottom horizontal
]

for row, col in b_pixels:
    if 0 <= row < 16 and 0 <= col < 16:
        idx = (row * 16 + col) * 4
        bitmap_data[idx] = 0xFF     # White Blue
        bitmap_data[idx+1] = 0xFF   # White Green
        bitmap_data[idx+2] = 0xFF   # White Red  
        bitmap_data[idx+3] = 0xFF   # White Alpha

# Write the ICO file
with open('favicon.ico', 'wb') as f:
    f.write(ico_data)
    f.write(bitmap_data)

print("favicon.ico created successfully!")
