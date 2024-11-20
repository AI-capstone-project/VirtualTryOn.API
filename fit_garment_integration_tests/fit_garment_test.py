import os
import shutil
from PIL import Image
from fit_garment.fitting import pd_update

# Define paths
garment_image_path = '.examples/garment/garment1.jpg'
model_image_path = '.examples/model/model1.jpg'
output_folder = './output'

# Ensure the output folder is empty
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder)

# Load images
garment_image = Image.open(garment_image_path)
model_image = Image.open(model_image_path)

# Perform the fitting
result_image = pd_update(model_image, garment_image, 20)

# Save the result
result_image_path = os.path.join(output_folder, 'result.jpg')
result_image.save(result_image_path)

print(f"Result image saved to {result_image_path}")