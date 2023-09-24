from PIL import Image, ImageDraw
import os
import math


def radial_offset(image_size:int, xy:tuple, padding:int=16) -> tuple:
    radius = (image_size / 2)
    r = xy[1] / 255 * radius
    theta = xy[0] / 255 * 2*math.pi
    x = radius + math.sin(theta) * (r - padding*2)
    y = radius + math.cos(theta) * (r - padding*2)
    return x, y


def normal_offset(image_size:int, xy:tuple, padding:int=16) -> tuple:
    remap = lambda v, OldMin, OldMax, NewMin, NewMax: (((v - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    new_min = 0 + padding
    new_max = image_size - padding*2
    x = remap(xy[0], 0, 255, new_min, new_max)
    y = remap(xy[1], 0, 255, new_min, new_max)
    return x, y


def image_list(folder:str) -> list:
    """Create a list to store the image data for each image"""
    images = []
    for root, dirs, files in os.walk(folder):
        directory = [os.path.join(root, name) for name in files]
        for image_path in directory:
            # Skip non-image files
            if not image_path.endswith('.png') or image_path.endswith('.jpg'): continue
            image = Image.open(image_path)

            # Skip images that are not 16x16
            if image.size != (16, 16): continue
            
            # Skip images that have a transparent pixel
            if 0 in list(zip(*list(zip(*image.convert('RGBA').getcolors()))[1]))[-1]: continue
            
            # Convert to HSV 
            image_rgba = image.convert('RGBA').getcolors()
            image_hsv = image.convert('HSV').getcolors()
            hsv = []
            rgba = []
            if "debug" in image_path: continue

            
            rgba = [color[1] for color in image_rgba for i in range(color[0])]
            hsv = [color[1] for color in image_hsv for i in range(color[0])]
                    
            average_rgba = tuple(int(sum(color)/len(color)) for color in list(zip(*rgba)))
            average_hsv = tuple(int(sum(color)/len(color)) for color in list(zip(*hsv)))
                
            # for color in image_hsv:
            #     # print("--",color[0])
            #     if color[1] == (0, 0, 0): continue
                
            #     for i in range(color[0]): hsv.append(color[1])   # Amount of similar pixels matter
            #     # hsv.append(color[1])                           # Amount of similar pixels don't matter
            average_hsv = tuple(int(sum(color)/len(color)) for color in list(zip(*hsv)))
            images.append((average_hsv, image_path, average_rgba))
    return images

def make_image(folder:str, output:str, image_size:str = 1024, sort_type:int = 0, step:int = 0, replace = True):
    """Sort type: \n
    0 = hue & saturation \n
    1 = saturation & value \n
    2 = hue & value"""
    
    if not os.path.exists(folder): 
        print(f"ERROR: Folder '{folder}' does not exist")
        input()
        assert False
    
    images = image_list(folder)
            
    # Create a new image to hold the sorted images
    if replace:
        image_result = Image.new('RGBA', (image_size, image_size), color=0)
        print('Creating image..')
        
    # Look for existing image, if it exists, open it, if not, create a new one
    else:
        try: 
            image_result = Image.open(os.path.join('', output))
            print("Opening existing image")
        except:
            image_result = Image.new('RGBA', (image_size, image_size), color=0)
            print('Creating new image')
    
    if sort_type == 'hs':
        draw = ImageDraw.Draw(image_result)
        draw.ellipse((0,0,image_size,image_size), fill=(50,50,50))
    else:
        draw = ImageDraw.Draw(image_result)
        draw.rectangle((0,0,image_size,image_size), fill=(50,50,50))
    
    for image_data in images:
        file_image = Image.new('RGBA', (16, 16), image_data[0]) #avarage color
        file_image = Image.open(image_data[1]) #original image
        
        # Skip empty image data
        if not image_data[0]: continue
        
        hue = image_data[0][0]
        saturation = image_data[0][1]
        value = image_data[0][2]
        
        
        def set_xy():
            stepxy = lambda a, b: (int(step * round(a/step)), int(step * round(b/step)))
            if sort_type == 'hs':
                return stepxy(*radial_offset(image_size, (hue, saturation)))
            elif sort_type == 'sv':
                return stepxy(*normal_offset(image_size, (saturation, value)))
            elif sort_type == 'hv':
                return stepxy(*normal_offset(image_size, (hue, value)))
        
        image_result.paste(file_image, set_xy())

    # Save the result image
    image_result.save(output)
    print(f" - Done")

def make_image_flat(folder:str, output:str):
    if not os.path.exists(folder): 
        print(f"ERROR: Folder '{folder}' does not exist")
        input()
        assert False
        
    images = image_list(folder)
    image_avarage = Image.new('RGBA', (16*len(images), 16), color=0)
    image_original = Image.new('RGBA', (16*len(images), 16), color=0)
    
    for i, image in enumerate(images):
        image_avarage.paste(image[2],(i*16, 0, i*16+16, 16))
        image_original.paste(Image.open(image[1]), (i*16, 0))
        
    image_avarage.save(output.replace('.png', '_avarage.png'))
    image_original.save(output.replace('.png', '_original.png'))
    print('Done')
    input()


def valid_input(text, default):
    # Show default value if it exists
    suffix = f" (default {default})" if default else ""
    # User input
    var = input(f" - {text}{suffix}: ")
    # Use default if no input
    if not var: 
        print(f"Using default value: {default}")
        var = default
    # Return folder if it exists
    if os.path.isdir(var): 
        return var
    # Try to convert str to int to correct type
    if type(default) == int: 
        try: return int(var)
        except: pass
    # Try again if input is invalid
    if type(var) != type(default):
        print(f"ERROR: Invalid input: '{var}'\n")
        return valid_input(text, default)
    return var

print("\n")
mode = valid_input("Mode (0 - Palette, 1 - Flat)", 0)

    
if mode == 0:
    folder = valid_input("Folder name", "./")
    image_size = valid_input("Output image size", 1024)
    stepsize = valid_input("Step size", 1)

    make_image(folder=folder, output='./sorted_hs.png', image_size=image_size, sort_type='hs', step=stepsize, replace=True)
    make_image(folder=folder, output='./sorted_sv.png', image_size=image_size, sort_type='sv', step=stepsize, replace=True)
    make_image(folder=folder, output='./sorted_hv.png', image_size=image_size, sort_type='hv', step=stepsize, replace=True)

elif mode == 1:
    folder = valid_input("Folder name", "./")
    make_image_flat(folder, './sorted_flat.png')
    
else:
    print("ERROR: Invalid mode (Use 0 or 1))\n")
    mode = valid_input("Mode (0 - Palette, 1 - Flat)", 0)