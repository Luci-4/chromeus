# Chromeus

**Chromeus** is a Python-based automation tool for controlling a Chrome browser using the Chrome DevTools Protocol via WebSocket. It enables navigation, JavaScript evaluation, full and partial screenshots, and DOM inspection capabilities in a browser environment. Currently in a prototype phase.

## Features

- Launch Chrome in debugging mode.
- Connect and communicate with Chrome via WebSocket.
- Navigate to URLs.
- Run and evaluate JavaScript code.
- Capture full-page screenshots.
- Capture screenshots of specific DOM elements.
- Retrieve DOM properties and object values.

## Requirements

- Python 3.7+
- Google Chrome installed (for the prototype tested on Windows OS the default path is hardcoded to: `C:\Program Files\Google\Chrome\Application\chrome.exe`)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/your-username/chromeus.git
cd chromeus
```

2. Install the libraries:

```bash
pip install websockets requests
```

## Usage example

```python
from chromeus import Chromeus
import time
import base64
import asyncio


async def main():
    chromeus = Chromeus()
    print(await chromeus.send_js('3*4+1'))
    print(await chromeus.send_js('20 === 10*2'))
    print(await chromeus.navigate_to_url('https://example.com/'))
    time.sleep(5)
    ss_result = await chromeus.capture_screenshot() 
    print(20*'-')
    print(ss_result)
    print(20*'-')
    image_data = base64.b64decode(ss_result['data'])

    with open("decoded_image.png", "wb") as image_file:
        image_file.write(image_data)

    print("Image saved as decoded_image.png")
    ss_result = await chromeus.capture_element_screenshot("h1") 

    if ss_result:
        image_data = base64.b64decode(ss_result['data'])
        with open("element_screenshot.png", "wb") as image_file:
            image_file.write(image_data)
        print("Image saved as element_screenshot.png")


if __name__ == "__main__":
    asyncio.run(main())
```

## Classes & Methods

### Chromeus

Main class responsible for managing the connection to Chrome and sending commands via the DevTools Protocol.

#### Methods

- **navigate_to_url(url: str)**  
  Navigates to the specified URL in the browser.  
  **Parameters:** `url` — Target URL string.  
  **Returns:** Navigation response result from Chrome.

- **send_js(command: str)**  
  Executes raw JavaScript and returns the result object or reference.  
  **Parameters:** `command` — JavaScript expression.  
  **Returns:** Result object or object reference.

- **get_value_by_js(command: str)**  
  Executes JavaScript and returns a primitive value if available.  
  **Parameters:** `command` — JavaScript expression.  
  **Returns:** The extracted primitive value.

- **wait_for_true(expression: str)**  
  Waits in a loop until the provided JavaScript expression evaluates to `true`.  
  **Parameters:** `expression` — JavaScript expression expected to return `true`.  
  **Returns:** `True` once the expression evaluates as expected.

- **capture_screenshot()**  
  Captures a full-page screenshot as a base64-encoded string.  
  **Returns:** Screenshot capture result (base64-encoded PNG).

- **capture_element_screenshot(selector: str)**  
  Captures a screenshot of a specific DOM element using a CSS selector.  
  **Parameters:** `selector` — CSS selector string for the target element.  
  **Returns:** Partial screenshot result (base64-encoded PNG).

### Helper Classes (Internal Use)

- **PageNavigate**  
  Represents a navigation command to a given URL.

- **CaptureScreenshot**  
  Triggers a full-page screenshot capture.

- **CapturePartialScreenshot**  
  Triggers a screenshot for a defined bounding box clip.

- **GetProperties**  
  Retrieves the properties of an object given its `objectId`.
