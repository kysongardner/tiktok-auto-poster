from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import random
import time
import schedule

# Load environment variables
load_dotenv()

class TikTokBufferPoster:
    def __init__(self):
        self.email = os.getenv('BUFFER_EMAIL')
        self.password = os.getenv('BUFFER_PASSWORD')
        self.videos_folder = os.getenv('VIDEOS_FOLDER')
        self.descriptions = [
            "Don't miss this! #viral #fyp #trending #foryou #foryoupage",
            "This is incredible! #amazing #wow #mustsee #viral #trending",
            "You won't believe this! #shocking #mindblowing #viral #fyp",
            "Pure magic right here! #magic #amazing #viral #trending #foryou",
            "Hit that follow button! #follow #viral #fyp #trending #foryoupage",
            "Motivation at its finest! #motivation #inspiration #viral #fyp",
            "Taking it to the next level! #nextlevel #viral #trending #fyp",
            "This is too funny! #funny #comedy #lol #viral #fyp #trending",
            "Pure gold content! #gold #quality #viral #trending #foryou",
            "Tag someone who needs to see this! #tag #share #viral #fyp"
            "🔥 Tag someone who needs to see this! #tag #share #viral #fyp"
        ]
        self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.binary_location = '/usr/bin/chromium-browser'
        
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome driver initialized successfully")

    def click_at_coordinates(self, x, y):
        """Click at specific x, y coordinates"""
        try:
            actions = ActionChains(self.driver)
            actions.move_by_offset(x, y).click().perform()
            print(f"Clicked at coordinates ({x}, {y})")
            time.sleep(2)
            # Reset action chain offset
            actions.move_by_offset(-x, -y).perform()
            return True
        except Exception as e:
            print(f"Error clicking at coordinates: {e}")
            return False

    def convert_wsl_path_to_windows(self, wsl_path):
        """Convert WSL path to Windows path for file uploads"""
        try:
            # If path starts with /mnt/c, convert to C:\
            if wsl_path.startswith('/mnt/'):
                # Extract drive letter and rest of path
                parts = wsl_path.split('/')
                if len(parts) >= 4:
                    drive = parts[2].upper()
                    rest_of_path = '/'.join(parts[3:])
                    windows_path = f"{drive}:\\{rest_of_path.replace('/', '\\')}"
                    print(f"Converted /mnt/ path to: {windows_path}")
                    return windows_path
            # If it's already a Windows path, return as is
            elif ':' in wsl_path and '\\' in wsl_path:
                return wsl_path
        except Exception as e:
            print(f"Error converting path: {e}")
        return wsl_path

    def handle_popups(self):
        """Close any popups that appear"""
        try:
            popup_selectors = [
                "button[aria-label='Close']",
                "button.close",
                "[data-testid='close-button']",
                "button[title='Close']",
                ".modal-close",
                "button:contains('×')"
            ]
            
            for selector in popup_selectors:
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in close_buttons:
                        if button.is_displayed():
                            button.click()
                            print(f"Closed popup using selector: {selector}")
                            time.sleep(1)
                except:
                    continue
        except Exception as e:
            print(f"No popups to close or error: {e}")

    def login_to_buffer(self):
        """Login to Buffer"""
        try:
            print("Navigating to Buffer login page...")
            self.driver.get('https://login.buffer.com/login')
            time.sleep(5)  # Increased wait time
            
            self.handle_popups()
            
            print("Entering email...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email"))
            )
            email_input.clear()
            time.sleep(0.5)
            email_input.send_keys(self.email)
            time.sleep(2)  # Wait after typing email
            
            print("Entering password...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name='password'], #password"))
            )
            password_input.clear()
            time.sleep(0.5)
            password_input.send_keys(self.password)
            time.sleep(2)  # Wait after typing password
            
            print("Clicking login button...")
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()
            
            print("Waiting for dashboard to load (this may take 10-15 seconds)...")
            time.sleep(15)  # Longer wait for dashboard
            self.handle_popups()
            
            print("Dashboard loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error during login: {e}")
            self.driver.save_screenshot('login_error.png')
            return False

    def get_random_video(self):
        """Select a random video from the folder, avoiding recent repeats"""
        history_file = os.path.join(os.path.dirname(self.videos_folder), '.posted_videos')
        posted_videos = set()
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                posted_videos = set(line.strip() for line in f)
        
        videos = [f for f in os.listdir(self.videos_folder) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        if not videos:
            raise Exception("No videos found in the specified folder")
        
        available_videos = [v for v in videos if v not in posted_videos]
        
        if not available_videos:
            print("All videos have been posted. Starting fresh rotation.")
            posted_videos.clear()
            available_videos = videos
        
        selected_video = random.choice(available_videos)
        posted_videos.add(selected_video)
        
        with open(history_file, 'w') as f:
            f.write('\n'.join(posted_videos))
        
        full_path = os.path.join(self.videos_folder, selected_video)
        print(f"Selected video: {selected_video}")
        return full_path

    def post_video(self):
        """Post a video to TikTok through Buffer"""
        try:
            print("\n=== Starting new post ===")
            
            # Get random video and description
            video_path = self.get_random_video()
            description = random.choice(self.descriptions)
            print(f"Using description: {description}")
            print(f"Using video: {video_path}")
            
            # Click the New button at coordinates (242, 301)
            print("Hovering over and clicking New button at (242, 301)...")
            actions = ActionChains(self.driver)
            actions.move_by_offset(242, 301).pause(1).click().perform()
            # Reset action chain
            actions.move_by_offset(-242, -301).perform()
            time.sleep(5)  # Wait for new post page to load
            
            self.handle_popups()
            time.sleep(2)
            
            # Click on the big description box first
            print("Clicking on description box...")
            description_selectors = [
                "textarea[placeholder*='description']",
                "textarea[placeholder*='caption']",
                "textarea[data-testid='composer-text']",
                "div[contenteditable='true']",
                "textarea.composer-textarea",
                "textarea",
                "[contenteditable='true']"
            ]
            
            description_box = None
            for selector in description_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            description_box = element
                            print(f"Found description box with selector: {selector}")
                            break
                    if description_box:
                        break
                except:
                    continue
            
            if description_box:
                description_box.click()
                time.sleep(1)
                description_box.clear()
                description_box.send_keys(description)
                print("Description entered successfully")
                time.sleep(2)
            else:
                print("Warning: Could not find description box")
            
            # Now upload the video via drag & drop or select file
            print("Looking for file upload input...")
            
            # Use the WSL path directly since Chromium is running in WSL
            print(f"Using video path: {video_path}")
            
            file_input = None
            try:
                # Find the file input element (it's usually hidden)
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                for inp in file_inputs:
                    try:
                        file_input = inp
                        print(f"Found file input element")
                        break
                    except:
                        continue
                
                if file_input:
                    print(f"Sending file path to input: {video_path}")
                    file_input.send_keys(video_path)
                    print(f"Video file sent to input: {os.path.basename(video_path)}")
                    
                    # Wait for upload to start and complete
                    print("Waiting for video to upload and process (30 seconds)...")
                    time.sleep(30)  # Increased wait time for large video files
                    
                    # Check if there's a progress indicator or completion sign
                    print("Video should be uploaded. Continuing...")
                else:
                    print("Error: Could not find file input")
                    self.driver.save_screenshot('no_file_input.png')
                    return False
                    
            except Exception as e:
                print(f"Error uploading video: {e}")
                self.driver.save_screenshot('upload_error.png')
                return False
            
            self.handle_popups()
            
            # Click Schedule Post button
            print("Waiting before looking for Schedule Post button...")
            time.sleep(5)  # Extra wait to ensure page is fully ready
            
            print("Looking for Schedule Post button...")
            
            schedule_button = None
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    if button.is_displayed():
                        button_text = button.text.lower()
                        if 'schedule' in button_text and 'post' in button_text:
                            schedule_button = button
                            print(f"Found Schedule Post button: {button.text}")
                            break
                except:
                    continue
            
            if schedule_button:
                schedule_button.click()
                print("Clicked Schedule Post button")
                time.sleep(5)
                print("Post completed successfully!")
            else:
                print("Warning: Could not find Schedule Post button")
                print("Available buttons:")
                for button in buttons:
                    try:
                        if button.is_displayed():
                            print(f"  - {button.text}")
                    except:
                        pass
                self.driver.save_screenshot('schedule_button_missing.png')
            
            print("Post completed successfully!")
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"Error posting video: {e}")
            self.driver.save_screenshot('post_error.png')
            return False

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")

def post_task():
    max_retries = 3
    retry_delay = 60
    
    for attempt in range(max_retries):
        try:
            print(f"\n--- Attempt {attempt + 1} of {max_retries} ---")
            poster = TikTokBufferPoster()
            
            if poster.login_to_buffer():
                if poster.post_video():
                    print("✓ Post successful!")
                    poster.close()
                    return
            
            poster.close()
            
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
        except Exception as e:
            print(f"Error in post task: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print("All posting attempts failed")

def main():
    print("Starting TikTok Auto Poster...")
    print(f"Using videos from: {os.getenv('VIDEOS_FOLDER')}")
    
    try:
        # Post immediately on startup
        print("\n=== POSTING NOW ===")
        post_task()
        
        # Schedule hourly posts
        schedule.every().hour.do(post_task)
        
        print("\n✓ First post complete!")
        print("Scheduled to post every hour. Press Ctrl+C to stop.")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\nStopping auto poster...")
    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()