from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import http.server
import socketserver
import threading
import os
import random
from PIL import Image, ImageGrab
import requests
from urllib.parse import urlparse
import argparse
import shutil
from resource_server import run_server as run_resource_server
from io import BytesIO

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Take a specified number of screenshots of a webpage with randomized content.")
parser.add_argument('--count', type=int, default=1, help='Number of screenshots to take.')
parser.add_argument('--clear-screenshots', action='store_true', help='If set, clears the screenshots folder before generating new ones.')
args = parser.parse_args()

# --- Server Setup ---
PORT = 8000
web_dir = os.path.dirname(os.path.abspath(__file__))

# --- Folder Cleanup ---
screenshots_dir = os.path.join(web_dir, 'screenshots')
temp_dir = os.path.join(web_dir, 'temp')

if args.clear_screenshots:
    if os.path.exists(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    os.makedirs(screenshots_dir)
    print(f"Cleared and recreated '{{screenshots_dir}}'")
else:
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"Created '{{screenshots_dir}}'")

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)
print(f"Cleared and recreated '{{temp_dir}}'")

server_thread = threading.Thread(target=run_resource_server, args=(PORT, web_dir))
server_thread.daemon = True
server_thread.start()
print("Resource server thread started.")

url = f"http://localhost:{PORT}/index.html"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-web-security")
driver = webdriver.Chrome(options=chrome_options)

def process_and_capture(gif_urls, image_urls=[]):
    background_urls = [
        "https://sunflower-land.com/assets/farm.b4df88b0.gif",
        "https://sunflower-land.com/assets/collectibles.bbad8a57.gif",
        "https://sunflower-land.com/assets/fishing.ce5e875b.gif"
    ]
    
    with open('content.html', 'r', encoding='utf-8') as f:
        str_div_html = f.read().replace('`', '\\`')

    # --- Main Loop for Capturing Screenshots ---
    for i in range(args.count):
        print(f"\n--- Starting capture {i + 1} of {args.count} ---")

        # Select a background URL, rotating every 5 captures
        current_background_url = background_urls[(i // 5) % len(background_urls)]
        print(f"Using background: {current_background_url}")

        # 1. Clear previous content and inject fresh HTML
        driver.execute_script("document.body.innerHTML = '';")
        driver.execute_script(f"document.body.innerHTML += `{str_div_html}`;")
        print("Injected fresh HTML content.")

        # 2. Convert GIFs (including processing the GIF)
        for url_item in gif_urls:
            try:
                response = requests.get(url_item, stream=True)
                response.raise_for_status()
                # Ensure raw stream is decoded if needed and open the image
                response.raw.decode_content = True
                with Image.open(response.raw) as img:
                    num_frames = img.n_frames
                    random_frame = 0
                    img.seek(random_frame)
                    
                    frame_filename = urlparse(url_item).path.split('/')[-1].replace('.gif', f'_frame{random_frame}.png')
                    frame_path = os.path.join(temp_dir, frame_filename)
                    img.save(frame_path, 'PNG')
                    image_urls.append(f'temp/{frame_filename}')
            except Exception as e:
                print(f"Could not process GIF, using original URL: {e}")
                image_urls.append(url_item)

        random.shuffle(image_urls)
        image_urls_js = str(image_urls).replace("'", '"')

        # 3. Apply transforms, replace images, add noise, and set random background
        # Use a plain string and safe placeholders to avoid Python f-string brace parsing errors
        combined_script = """
        // --- Set Body Background ---
        const mainDiv = document.querySelector('body > div');
        if (mainDiv) {
            mainDiv.style.backgroundImage = `url('<<<BACKGROUND>>>')`;
            mainDiv.style.backgroundSize = 'cover';
            mainDiv.style.backgroundPosition = 'center';
            mainDiv.style.backgroundRepeat = 'no-repeat';
        }

        // --- Set Random Background Color for panel ---
        const r = Math.floor(Math.random() * 256);
        const g = Math.floor(Math.random() * 256);
        const b = Math.floor(Math.random() * 256);
        const randomColor = `rgba(${r}, ${g}, ${b}, 0.8)`; // Added 0.8 alpha for transparency
        
        const addNoiseToBackground = (element, color) => {
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const rect = element.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
            
            // Base background color
            ctx.fillStyle = color;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const numObjects = Math.floor(Math.random() * 150) + 50; // Create 50 to 200 objects

            for (let i = 0; i < numObjects; i++) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                
                // Make color slightly darker/lighter and semi-transparent
                const r_obj = Math.floor(Math.random() * 50);
                const g_obj = Math.floor(Math.random() * 50);
                const b_obj = Math.floor(Math.random() * 50);
                const alpha = Math.random() * 0.3 + 0.1; // 0.1 to 0.4 opacity
                const objectColor = `rgba(${r_obj}, ${g_obj}, ${b_obj}, ${alpha})`;
                ctx.fillStyle = objectColor;

                // Randomly draw a circle (spot) or a rectangle (rock)
                if (Math.random() > 0.5) {
                    // Draw a spot
                    const radius = Math.random() * 6 + 2; // Radius between 2 and 8
                    ctx.beginPath();
                    ctx.arc(x, y, radius, 0, Math.PI * 2);
                    ctx.fill();
                } else {
                    // Draw a small rock-like rectangle
                    const width = Math.random() * 12 + 3; // Width between 3 and 15
                    const height = Math.random() * 12 + 3; // Height between 3 and 15
                    ctx.fillRect(x, y, width, height);
                }
            }
            element.style.backgroundImage = `url(${canvas.toDataURL()})`;
            element.style.backgroundColor = 'transparent'; // Ensure element background is transparent
        };

        const outerPanel = document.querySelector('#mainbackGround');
        if (outerPanel) {
            // Make the parent border semi-transparent too
            if(outerPanel.parentElement) {
                outerPanel.parentElement.style.backgroundColor = 'rgba(194, 133, 105, 0.8)';
            }
            addNoiseToBackground(outerPanel, randomColor);
            const innerPanel = outerPanel.querySelector('div');
            if (innerPanel) {
                addNoiseToBackground(innerPanel, randomColor);
            }
        }

        const p1 = .99, p2 = .99, p3 = .99, er = 0, eg = 0, eb = 0;
        const addNoise = (lt, kt=.4) => {
            if (!lt || !lt.complete || lt.src.startsWith("data:image/png;base64") || !lt.naturalWidth || !lt.naturalHeight)
                return;
            const St = document.createElement("canvas");
            const Dt = St.getContext("2d");
            St.width = lt.naturalWidth;
            St.height = lt.naturalHeight;
            Dt.drawImage(lt, 0, 0);
            const zt = Dt.getImageData(0, 0, lt.naturalWidth, lt.naturalHeight);
            for (let Ht = 0, Wt = zt.data.length; Ht < Wt; Ht += 4) {
                const Kt = .93 + Math.random() * kt;
                const Zt = .93 + Math.random() * kt;
                const na = .93 + Math.random() * kt;
                zt.data[Ht] = zt.data[Ht] * p1 * Kt + er;
                zt.data[Ht + 1] = zt.data[Ht + 1] * p2 * Zt + eg;
                zt.data[Ht + 2] = zt.data[Ht + 2] * p3 * na + eb;
            }
            Dt.putImageData(zt, 0, 0);
            const Ut = St.toDataURL();
            lt.src = Ut;
            return Ut;
        };

        function applyRandomTransform(item) {
            const skewX = Math.random() * 10 - 5;
            const skewY = Math.random() * 10 - 5;
            const rotateX = Math.random() * 50 - 25;
            const rotateY = Math.random() * 50 - 25;
            const scaleX = (Math.random()*0.4 + 0.6);
            const scaleY = (Math.random()*0.4 + 0.6);
            item.style.transform = `perspective(9cm) skew(${skewX}deg, ${skewY}deg) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scaleX(${scaleX}) scaleY(${scaleY})`;
        }

        const items = document.querySelectorAll('.group');
        const numItems = items.length;
        const images = <<<IMAGES>>>;
        
        if (numItems >= 3) {
            const chosenIndices = new Set();
            while (chosenIndices.size < 3) {
                const randomIndex = Math.floor(Math.random() * numItems);
                chosenIndices.add(randomIndex);
            }
            
            let imageIndex = 0;
            chosenIndices.forEach(index => {
                const item = items[index];
                const img = item.querySelector('img');
                if (img) {
                    applyRandomTransform(img);
                    img.src = images[imageIndex % images.length];
                    imageIndex++;
                }
            });
            console.log('Successfully transformed and replaced 3 random images.');

            // --- Exchange images among unchosen items ---
            const allIndices = Array.from(Array(numItems).keys());
            const unchosenIndices = allIndices.filter(index => !chosenIndices.has(index));
            const unchosenImages = unchosenIndices.map(index => items[index].querySelector('img')).filter(img => img);

            if (unchosenImages.length > 1) {
                const unchosenImageSrcs = unchosenImages.map(img => img.src);
                unchosenImageSrcs.push('assets/iguana.png'); // Add iguana to the shuffle pool

                // Shuffle the image sources
                for (let i = unchosenImageSrcs.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [unchosenImageSrcs[i], unchosenImageSrcs[j]] = [unchosenImageSrcs[j], unchosenImageSrcs[i]];
                }

                // Reassign the shuffled sources
                unchosenImages.forEach((img, i) => {
                    img.src = unchosenImageSrcs[i % unchosenImageSrcs.length];
                });
                console.log('Successfully exchanged images among unchosen items, including the iguana.');
            }
        }

        // --- Apply noise to all images ---
        const allImages = document.querySelectorAll('.group img');
        allImages.forEach(img => {
            // Ensure image is loaded before applying noise
            if (img.complete) {
                addNoise(img);
            } else {
                img.onload = () => addNoise(img);
            }
        });
        console.log('Applied noise to all images.');
        """
        # Inject the dynamic values safely (placeholders used above)
        combined_script = combined_script.replace("<<<BACKGROUND>>>", current_background_url).replace("<<<IMAGES>>>", image_urls_js)
        driver.execute_script(combined_script)
        
        # 4. Wait for images to load and noise to be applied
        print("Waiting 3 seconds for images to load and noise to be applied...")
        time.sleep(3)

        # 5. Take a screenshot of a random area using Selenium's method
        browser_size = driver.get_window_size()
        
        # Define boundaries
        win_width, win_height = browser_size['width'], browser_size['height']
        
        # Define minimum size for the screenshot (e.g., 30% of the window)
        min_width = int(win_width * 0.3)
        min_height = int(win_height * 0.3)
        
        # Get random width and height
        random_width = random.randint(min_width, win_width)
        random_height = random.randint(min_height, win_height)
        
        # Get random position, ensuring the screenshot is within the window
        random_x = random.randint(0, win_width - random_width)
        random_y = random.randint(0, win_height - random_height)
        
        # Take a screenshot of the viewport
        png = driver.get_screenshot_as_png()
        
        # Open the screenshot with Pillow and crop it
        img = Image.open(BytesIO(png))
        
        # Define the bounding box for cropping
        # The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
        bbox = (random_x, random_y, random_x + random_width, random_y + random_height)
        cropped_img = img.crop(bbox)
        
        # Find the next available screenshot number
        existing_files = os.listdir(screenshots_dir)
        screenshot_num = 0
        while f'screenshot_{screenshot_num}.png' in existing_files:
            screenshot_num += 1
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{screenshot_num}.png')
        cropped_img.save(screenshot_path)
        print(f"Screenshot of area {bbox} saved to {screenshot_path}")

try:
    print(f"Opening page: {url}")
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Page has completely loaded.")

    gif_urls = [
        "https://sunflower-land.com/game-assets/npcs/goblin_chef_doing.gif",
        "https://sunflower-land.com/game-assets/npcs/goblin_chef.gif",
        "https://sunflower-land.com/game-assets/npcs/goblin.gif",
        "https://sunflower-land.com/game-assets/npcs/suspicious_goblin.gif",
        "https://sunflower-land.com/game-assets/npcs/skeleton_walk.gif",
        # "https://sunflower-land.com/game-assets/npcs/synced.gif",
        "https://sunflower-land.com/game-assets/npcs/goblin_carry.gif",
        "https://sunflower-land.com/game-assets/npcs/pirate_goblin.gif",
        "https://sunflower-land.com/game-assets/npcs/goblin_snorkling.gif",
        "https://sunflower-land.com/game-assets/npcs/goblin_digger.gif"
    ]

    image_urls = [
        # "https://sunflower-land.com/game-assets/decorations/treasure_chest.png",
        "https://sunflower-land.com/game-assets/npcs/skeleton3.png",
        "https://sunflower-land.com/game-assets/npcs/goblin_head.png"
    ]
    process_and_capture(gif_urls, image_urls)

finally:
    # Clean up and close the browser
    print("\nAll captures complete. Closing the browser.")
    driver.quit()
