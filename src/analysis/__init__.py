

import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import glob
from pathlib import Path

def load_images_from_directory(directory):
    """
    Load all TIFF images from a directory and sort them by date
    Returns a dictionary with dates as keys and loaded images as values
    """
    images = {}
    
    # Find all tiff files in the directory
    tiff_files = glob.glob(os.path.join(directory, "*.tif")) + glob.glob(os.path.join(directory, "*.tiff"))
    
    if not tiff_files:
        print(f"No TIFF files found in {directory}")
        return images
    
    print(f"Found {len(tiff_files)} TIFF files")
    
    for tiff_file in tiff_files:

        # Extract date from filename - assuming date is in the filename
        # This pattern extraction needs to be adjusted based on your actual filename format
        filename = Path(tiff_file).stem
        
        # Try to find date in filename (adjust the format as needed)
        try:
            # Attempt to extract date from the filename
            # Common formats: YYYY-MM-DD, YYYYMMDD, YYYY_MM_DD
            # This is a simplified approach - adjust based on your actual naming convention
            parts = filename.split('_')
            for part in parts:
                if len(part) == 8 and part.isdigit():  # YYYYMMDD format
                    date_str = part
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    break
                elif len(part) == 10 and part.count('-') == 2:  # YYYY-MM-DD format
                    date_str = part
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    break
            else:
                # If no date found in parts, use the file creation time
                date_obj = datetime.fromtimestamp(os.path.getctime(tiff_file))
                print(f"Could not extract date from filename {filename}, using file creation time instead")
        except Exception as e:
            print(f"Error extracting date from {filename}: {e}")
            # Fallback to file creation time if date extraction fails
            date_obj = datetime.fromtimestamp(os.path.getctime(tiff_file))
        
        date_str = date_obj.strftime('%Y-%m-%d')
        
        # Load the image using rasterio
        try:
            with rasterio.open(tiff_file) as src:
                # Read the image data
                image_data = src.read()
                
                # Store metadata for later use
                metadata = {
                    'transform': src.transform,
                    'crs': src.crs,
                    'bounds': src.bounds,
                    'width': src.width,
                    'height': src.height,
                    'count': src.count,  # Number of bands
                    'file_path': tiff_file
                }
                
                # Store both the image data and metadata
                images[date_str] = {
                    'data': image_data,
                    'metadata': metadata
                }
                
                print(f"Loaded image for date {date_str} with shape {image_data.shape}")
        except Exception as e:
            print(f"Error loading {tiff_file}: {e}")
    
    return images

def compare_images(image_dict):
    """
    Compare loaded images to detect changes over time
    """
    if len(image_dict) < 2:
        print("Need at least two images to compare")
        return
    
    # Sort dates
    dates = sorted(image_dict.keys())
    
    # Initialize results dictionary
    results = {}
    
    # Compare each image with the next one in chronological order
    for i in range(len(dates) - 1):
        date1 = dates[i]
        date2 = dates[i + 1]
        
        image1 = image_dict[date1]['data']
        image2 = image_dict[date2]['data']
        
        # Check if images have the same dimensions
        if image1.shape != image2.shape:
            print(f"Warning: Images for {date1} and {date2} have different shapes")
            print(f"Shape of {date1}: {image1.shape}")
            print(f"Shape of {date2}: {image2.shape}")
            continue
        
        # Calculate simple difference
        difference = image2.astype(float) - image1.astype(float)
        
        # Calculate absolute difference
        abs_difference = np.abs(difference)
        
        # Calculate percentage change
        # Avoid division by zero
        epsilon = 1e-10  # Small value to avoid division by zero
        percentage_change = (difference / (image1.astype(float) + epsilon)) * 100
        
        # Calculate total change metrics
        total_difference = np.sum(abs_difference)
        mean_difference = np.mean(abs_difference)
        max_difference = np.max(abs_difference)
        
        # Store results
        results[f"{date1}_to_{date2}"] = {
            'difference': difference,
            'abs_difference': abs_difference,
            'percentage_change': percentage_change,
            'total_difference': total_difference,
            'mean_difference': mean_difference,
            'max_difference': max_difference,
            'date1': date1,
            'date2': date2
        }
        
        print(f"Comparison from {date1} to {date2}:")
        print(f"  Total absolute change: {total_difference}")
        print(f"  Mean absolute change: {mean_difference}")
        print(f"  Maximum absolute change: {max_difference}")
    
    return results

def visualize_changes(results, output_dir=None):
    """
    Visualize the detected changes
    """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for period, data in results.items():
        date1 = data['date1']
        date2 = data['date2']
        
        # Create a figure with subplots for different visualizations
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Plot difference
        im1 = axes[0].imshow(data['difference'][0], cmap='RdBu', vmin=-500, vmax=500)
        axes[0].set_title(f'Raw Difference ({date1} to {date2})')
        plt.colorbar(im1, ax=axes[0], label='Pixel value difference')
        
        # Plot absolute difference
        im2 = axes[1].imshow(data['abs_difference'][0], cmap='hot', vmin=0, vmax=500)
        axes[1].set_title(f'Absolute Difference ({date1} to {date2})')
        plt.colorbar(im2, ax=axes[1], label='Absolute pixel value difference')
        
        # Plot thresholded difference to highlight significant changes
        # Threshold at 10% of the maximum difference
        threshold = 0.1 * data['max_difference']
        thresholded = np.copy(data['abs_difference'][0])
        thresholded[thresholded < threshold] = 0
        
        im3 = axes[2].imshow(thresholded, cmap='hot', vmin=0, vmax=data['max_difference'])
        axes[2].set_title(f'Significant Changes ({date1} to {date2})')
        plt.colorbar(im3, ax=axes[2], label='Changes above threshold')
        
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(os.path.join(output_dir, f"change_{date1}_to_{date2}.png"), dpi=300)
            print(f"Saved visualization to {os.path.join(output_dir, f'change_{date1}_to_{date2}.png')}")
        
        plt.show()

def estimate_volume_changes(results, pixel_area=100):  # pixel_area in square meters (10m x 10m for Sentinel-2)
    """
    Estimate the volume of material removed/added based on pixel value differences
    This is a simplified approach and would need calibration for actual volume estimates
    """
    volume_estimates = {}
    
    for period, data in results.items():
        difference = data['difference']
        
        # Assuming pixel values correspond to elevation changes in meters
        # This is a major assumption and would need calibration with ground truth data
        # Negative values indicate material removal, positive values indicate material addition
        
        # Calculate volume change per pixel (pixel area × height change)
        volume_change_per_pixel = difference * pixel_area
        
        # Sum up all negative changes (material removed)
        material_removed = -np.sum(volume_change_per_pixel[volume_change_per_pixel < 0])
        
        # Sum up all positive changes (material added)
        material_added = np.sum(volume_change_per_pixel[volume_change_per_pixel > 0])
        
        # Net change
        net_change = material_added - material_removed
        
        volume_estimates[period] = {
            'material_removed_m3': material_removed,
            'material_added_m3': material_added,
            'net_change_m3': net_change
        }
        
        print(f"Volume estimation for {period}:")
        print(f"  Material removed: {material_removed:.2f} m³")
        print(f"  Material added: {material_added:.2f} m³")
        print(f"  Net change: {net_change:.2f} m³")
    
    return volume_estimates

def main():
    # Path to your satellite images
    data_dir = "/Users/user/Desktop/satellite-inference/data/raw"
    
    # Create output directory for visualizations
    output_dir = "/Users/user/Desktop/satellite-inference/results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load images
    print("Loading images...")
    images = load_images_from_directory(data_dir)
    
    if len(images) < 2:
        print("Need at least two images for comparison")
        return
    
    # Compare images
    print("\nComparing images...")
    results = compare_images(images)
    
    # Visualize changes
    print("\nVisualizing changes...")
    visualize_changes(results, output_dir)
    
    # Estimate volume changes
    # Note: This is highly simplified and would need calibration
    print("\nEstimating volume changes...")
    volume_estimates = estimate_volume_changes(results)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()

