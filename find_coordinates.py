from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    
    # Use webdriver-manager for Windows
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def inject_mouse_tracker(driver):
    js_code = """
    if (!window.mouseTrackerInjected) {
        window.mouseTrackerInjected = true;
        var coordsDiv = document.createElement('div');
        coordsDiv.style.position = 'fixed';
        coordsDiv.style.top = '10px';
        coordsDiv.style.left = '10px';
        coordsDiv.style.backgroundColor = 'black';
        coordsDiv.style.color = 'white';
        coordsDiv.style.padding = '10px';
        coordsDiv.style.zIndex = '999999';
        coordsDiv.style.fontFamily = 'monospace';
        coordsDiv.style.fontSize = '14px';
        coordsDiv.innerHTML = 'Mouse position: X=?, Y=?';
        document.body.appendChild(coordsDiv);

        document.addEventListener('mousemove', function(e) {
            coordsDiv.innerHTML = 'Mouse position: X=' + e.clientX + ', Y=' + e.clientY;
        });

        document.addEventListener('click', function(e) {
            var originalBg = coordsDiv.style.backgroundColor;
            coordsDiv.style.backgroundColor = 'red';
            coordsDiv.innerHTML = 'CLICKED at: X=' + e.clientX + ', Y=' + e.clientY;
            setTimeout(function() {
                coordsDiv.style.backgroundColor = originalBg;
            }, 400);
        });
    }
    """
    driver.execute_script(js_code)

def find_coordinates():
    driver = setup_driver()
    try:
        driver.get('https://login.buffer.com/login')
        print("Navigate through Buffer — mouse coordinates will display on every page.")
        print("Press Ctrl+C to exit.")

        last_url = ""
        while True:
            current_url = driver.current_url
            if current_url != last_url:
                # New page loaded → reinject the script
                time.sleep(1.5)  # small delay to let page load
                try:
                    inject_mouse_tracker(driver)
                    print(f"Injected tracker on: {current_url}")
                except Exception as e:
                    print(f"Failed to inject on {current_url}: {e}")
                last_url = current_url
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting coordinate finder...")
    finally:
        driver.quit()

if __name__ == "__main__":
    find_coordinates()
