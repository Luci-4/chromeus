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
