from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import random
import time
import schedule
from datetime import datetime

# Load environment variables
load_dotenv()

class TikTokBufferPoster:
    def __init__(self):
        self.email = os.getenv('BUFFER_EMAIL')
        self.password = os.getenv('BUFFER_PASSWORD')
        self.videos_folder = os.getenv('VIDEOS_FOLDER')
        self.description = "\"If you don't find a way to make money while you sleep, you will work until you die.\" - Warren Buffett\n\nYou may see some of my recent passive rewards in this video. If not check my other videos.\n\nClick the link in my bio for more information"
        self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        
        # Use webdriver-manager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)  # Increased timeout to 30 seconds
        print("Chrome driver initialized successfully")

    def handle_popups(self):
        """Close any popups that appear"""
        try:
            popup_selectors = [
                "button[aria-label='Close']",
                "button.close",
                "[data-testid='close-button']",
                "button[title='Close']",
                ".modal-close"
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
    
    def find_and_click_tiktok_new_button(self):
        """Find the TikTok channel and click its new post button"""
        print("Searching for TikTok channel new post button...")
        
        # Wait a moment for any dynamic content to load
        time.sleep(2)
        
        # Look for channel cards/containers
        try:
            # Common class names for channel containers in Buffer
            channel_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                "[class*='channel'], [class*='account'], [class*='profile'], [data-testid*='channel']")
            
            print(f"Found {len(channel_containers)} potential channel containers")
            
            for container in channel_containers:
                try:
                    # Check if this container has "TikTok" text
                    container_text = container.text.lower()
                    if 'tiktok' in container_text:
                        print(f"Found TikTok container: {container_text[:100]}")
                        
                        # Hover over it to reveal the plus icon
                        actions = ActionChains(self.driver)
                        actions.move_to_element(container).perform()
                        time.sleep(1)
                        
                        # Look for clickable elements within this container
                        clickables = container.find_elements(By.CSS_SELECTOR, 
                            "button, a, [role='button'], [onclick]")
                        
                        for clickable in clickables:
                            try:
                                if clickable.is_displayed():
                                    clickable.click()
                                    print("Successfully clicked TikTok new post button!")
                                    return True
                            except:
                                continue
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error in find_and_click_tiktok_new_button: {e}")
        
        return False

    def login_to_buffer(self):
        """Login to Buffer"""
        try:
            print("Navigating to Buffer login page...")
            self.driver.get('https://login.buffer.com/login')
            time.sleep(5)
            
            self.handle_popups()
            
            print("Entering email...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email"))
            )
            email_input.clear()
            time.sleep(0.5)
            email_input.send_keys(self.email)
            time.sleep(2)
            
            print("Entering password...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name='password'], #password"))
            )
            password_input.clear()
            time.sleep(0.5)
            password_input.send_keys(self.password)
            time.sleep(2)
            
            print("Clicking login button...")
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()
            
            print("Waiting for dashboard to load (this may take 10-15 seconds)...")
            
            # Wait for URL to change from login page
            max_wait = 20  # 20 seconds max wait
            start_time = time.time()
            while 'login' in self.driver.current_url.lower() and (time.time() - start_time) < max_wait:
                time.sleep(1)
                print(".", end="", flush=True)
            
            print("\n")  # New line after dots
            
            if 'login' in self.driver.current_url.lower():
                print("WARNING: Still on login page after 20 seconds. Login may have failed.")
                print("Please check if credentials are correct or if 2FA is required.")
                return False
            
            time.sleep(5)  # Additional wait for page to fully load
            self.handle_popups()
            
            # Verify dashboard loaded by checking URL and page elements
            current_url = self.driver.current_url
            print(f"Current URL after login: {current_url}")
            
            # Try to detect common Buffer dashboard elements
            try:
                # Look for common dashboard elements
                dashboard_indicators = [
                    "button",
                    "[data-testid='new-post']",
                    "a[href*='publish']",
                    "nav",
                    "header"
                ]
                
                found_elements = []
                for selector in dashboard_indicators:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        found_elements.append(f"{selector} ({len(elements)} found)")
                
                print(f"Dashboard elements detected: {', '.join(found_elements[:3])}")
                
            except Exception as e:
                print(f"Warning checking dashboard elements: {e}")
            
            print("Dashboard loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error during login: {e}")
            return False

    def get_random_video(self):
        """Select the next video in order, cycling through all videos"""
        # Save tracking file in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        history_file = os.path.join(script_dir, 'posted_videos.txt')
        posted_videos = []
        
        print(f"Tracking file location: {history_file}")
        
        # Read the list of posted videos in order
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                posted_videos = [line.strip() for line in f if line.strip()]
            print(f"Previously posted: {len(posted_videos)} videos")
            with open(history_file, 'r') as f:
                posted_videos = [line.strip() for line in f if line.strip()]
        
        # Get all videos in folder
        videos = sorted([f for f in os.listdir(self.videos_folder) 
                 if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))])
        
        if not videos:
            raise Exception("No videos found in the specified folder")
        
        # Find videos not yet posted
        available_videos = [v for v in videos if v not in posted_videos]
        
        # If all videos have been posted, start over
        if not available_videos:
            print("All videos have been posted. Starting fresh cycle from the beginning.")
            posted_videos = []
            available_videos = videos
        
        # Select the first available video (maintains order)
        selected_video = available_videos[0]
        posted_videos.append(selected_video)
        
        # Save the updated history
        with open(history_file, 'w') as f:
            f.write('\n'.join(posted_videos))
        
        full_path = os.path.join(self.videos_folder, selected_video)
        print(f"Selected video: {selected_video} ({len(posted_videos)}/{len(videos)} posted)")
        return full_path

    def post_video(self):
        """Post a video to TikTok through Buffer"""
        try:
            print("\n=== Starting new post ===")
            
            # Get random video and description
            video_path = self.get_random_video()
            description = self.description
            print(f"Using description: {description}")
            print(f"Using video: {video_path}")
            
            # Use keyboard shortcut N then P to open new post modal
            print("Pressing 'N' then 'P' to open new post modal...")
            try:
                actions = ActionChains(self.driver)
                # Press N and P together quickly
                actions.send_keys('np')
                actions.perform()
                print("Keyboard shortcut sent: NP")
                time.sleep(5)
            except Exception as e:
                print(f"Error with keyboard shortcut: {e}")
                return False
            
            self.handle_popups()
            time.sleep(3)
            
            print("Modal opened")
            
            # Wait for composer to fully load
            time.sleep(3)
            
            # Upload the video FIRST (before entering text)
            print("\n=== UPLOADING VIDEO ===")
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
                    time.sleep(30)
                    
                    print("Video uploaded. Now adding description...")
                else:
                    print("Error: Could not find file input")
                    return False
                    
            except Exception as e:
                print(f"Error uploading video: {e}")
                return False
            
            # NOW enter the description AFTER video is uploaded
            print("\n=== ENTERING DESCRIPTION ===")
            time.sleep(3)
            
            # Click in the text area and type character by character
            try:
                # Find the text input area
                print("Looking for text input...")
                
                # Try to find textarea elements
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                
                if textareas:
                    print(f"Found {len(textareas)} textarea elements")
                    # Click the first visible one
                    for textarea in textareas:
                        try:
                            if textarea.is_displayed():
                                print("Clicking textarea...")
                                textarea.click()
                                time.sleep(1)
                                
                                # Type character by character using ActionChains
                                print(f"Typing description character by character...")
                                actions = ActionChains(self.driver)
                                for char in description:
                                    actions.send_keys(char)
                                    actions.perform()
                                    time.sleep(0.05)  # Small delay between characters
                                
                                time.sleep(2)
                                print("Description entered")
                                break
                        except Exception as e:
                            print(f"Error with textarea: {e}")
                            continue
                else:
                    # If no textarea, try contenteditable
                    print("No textarea found, trying contenteditable...")
                    editable_divs = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
                    if editable_divs:
                        editable_divs[0].click()
                        time.sleep(1)
                        
                        # Type character by character
                        print(f"Typing description character by character in contenteditable...")
                        actions = ActionChains(self.driver)
                        for char in description:
                            actions.send_keys(char)
                            actions.perform()
                            time.sleep(0.05)
                        
                        time.sleep(2)
                        print("Description entered in contenteditable div")
                
            except Exception as e:
                print(f"Error entering description: {e}")
                print("Continuing without description...")
            
            time.sleep(2)
            
            self.handle_popups()
            
            # Click Schedule Post button
            print("Waiting before looking for Schedule Post button...")
            time.sleep(5)
            
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
                        continue
                self.driver.save_screenshot('schedule_button_missing.png')
            
            time.sleep(5)
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
    
    def keep_alive(self):
        """Keep the browser session alive by moving mouse slightly"""
        try:
            # Move mouse slightly to keep session active
            actions = ActionChains(self.driver)
            actions.move_by_offset(5, 5).move_by_offset(-5, -5).perform()
        except:
            pass

def main():
    print("Starting TikTok Auto Poster...")
    print(f"Using videos from: {os.getenv('VIDEOS_FOLDER')}")
    print("Posting schedule: Every 30 minutes between 2:25 PM and 12:25 AM")
    
    poster = None
    
    try:
        # Initialize poster and login once
        print("\n=== Initializing and logging in ===")
        poster = TikTokBufferPoster()
        
        if not poster.login_to_buffer():
            print("Failed to login. Exiting.")
            return
        
        print("\n=== Login successful! Browser will stay open ===")
        print("Will post every 30 minutes between 2:25 PM and 12:25 AM. Press Ctrl+C to stop.\n")
        
        post_count = 0
        last_post_time = 0  # Start at 0 so first post happens immediately if in time window
        
        while True:
            current_time = time.time()
            time_since_last_post = current_time - last_post_time
            
            # Get current hour and minute
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            
            # Check if we're in the posting time window (2:25 PM to 12:25 AM)
            # 2:25 PM = 14:25 (hour=14, minute>=25)
            # 12:25 AM = 00:25 (hour=0, minute<=25)
            in_time_window = False
            
            if current_hour == 14 and current_minute >= 25:
                # Between 2:25 PM and 2:59 PM
                in_time_window = True
            elif current_hour > 14 and current_hour < 24:
                # Between 3:00 PM and 11:59 PM
                in_time_window = True
            elif current_hour == 0 and current_minute <= 25:
                # Between 12:00 AM and 12:25 AM
                in_time_window = True
            
            if not in_time_window:
                # Outside posting window
                if post_count == 0 or time_since_last_post > 300:  # Print status every 5 minutes
                    print(f"[{now.strftime('%I:%M %p')}] Outside posting window (2:25 PM - 12:25 AM). Waiting...")
                    last_post_time = current_time  # Update to avoid spam printing
                time.sleep(60)
                continue
            
            # Post every 30 minutes (1800 seconds) if we're in the time window
            if time_since_last_post >= 1800 or post_count == 0:
                print(f"\n=== POSTING VIDEO #{post_count + 1} ===")
                
                try:
                    # Check if browser is still alive
                    try:
                        poster.driver.current_url
                    except:
                        print("Browser connection lost! Restarting browser and logging in again...")
                        try:
                            poster.close()
                        except:
                            pass
                        
                        # Reinitialize
                        poster = TikTokBufferPoster()
                        if not poster.login_to_buffer():
                            print("Failed to re-login. Exiting.")
                            return
                        print("Re-login successful!")
                    
                    if poster.post_video():
                        print(f"✓ Post #{post_count + 1} completed successfully!")
                        post_count += 1
                        last_post_time = current_time
                    else:
                        print("Post failed, will retry in next cycle")
                except Exception as e:
                    print(f"Error during post: {e}")
                    
                    # Check if it's a session error and restart
                    if "invalid session id" in str(e).lower() or "session deleted" in str(e).lower():
                        print("Session lost! Restarting browser...")
                        try:
                            poster.close()
                        except:
                            pass
                        
                        poster = TikTokBufferPoster()
                        if not poster.login_to_buffer():
                            print("Failed to re-login. Exiting.")
                            return
                        print("Browser restarted and logged in successfully!")
                    else:
                        try:
                            poster.driver.save_screenshot(f'post_error_{post_count}.png')
                        except:
                            print("Could not save screenshot")
                
                # After successful post, wait and prepare for next one
                if post_count > 0:
                    next_post_time = datetime.fromtimestamp(last_post_time + 1800)
                    print(f"\nNext post in 30 minutes at {next_post_time.strftime('%I:%M %p')}. Browser staying open...")
            
            # Keep session alive every 5 minutes
            if int(current_time) % 300 == 0:  # Every 5 minutes
                poster.keep_alive()
            
            # Sleep for 1 minute between checks
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\n=== Stopping auto poster ===")
        print(f"Total posts made: {post_count}")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        if poster:
            print("\nClosing browser...")
            poster.close()

if __name__ == "__main__":
    main()
