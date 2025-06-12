import websockets
import threading
import json
import requests
import asyncio
import subprocess
import enum
import time


class PageNavigate:
    def __init__(self, url):
        self.url = url


class CaptureScreenshot:
    pass


class CapturePartialScreenshot:
    def __init__(self, clip):
        self.clip = clip

class GetProperties:
    def __init__(self, objectId):
        self.objectId = objectId


class Chromeus:
    PORT = 9222
    CMD_COMMAND = f"\"C:\Program Files\Google\Chrome\Application\chrome.exe\" --remote-debugging-port={PORT} --incognito"

    def __init__(self):
        subprocess.Popen(Chromeus.CMD_COMMAND, shell=True)

        while True:
            try:
                response = requests.get(f"http://localhost:{Chromeus.PORT}/json")
                print(response)
                print("Chrome is ready for debugging")
                break

            except requests.exceptions.ConnectionError as e:
                print("Waiting for Chrome to open...")
                time.sleep(1)
        self.command = None
        self.result = None
        self.notifier = asyncio.Event()
        self.ready_event = asyncio.Event()
        self.new_command_event = asyncio.Event()
        self.chrome_connection_task = asyncio.create_task(self.__connect_to_chrome())


    async def __connect_to_chrome(self):
        print('connecting to chrome')
        response = requests.get(f"http://localhost:{Chromeus.PORT}/json")
        print('got a response')
        web_socket_debugger_url = response.json()[0]['webSocketDebuggerUrl']
        print('got a web socket debugger url')

        async with websockets.connect(web_socket_debugger_url) as websocket:
            print('connected to websocket')

            await websocket.send(json.dumps({'id': 1, 'method': 'Page.enable'}))
            await websocket.send(json.dumps({'id': 2, 'method': 'Network.enable'}))
            await websocket.send(json.dumps({'id': 3, 'method': 'Console.enable'}))
            await websocket.send(json.dumps({'id': 4, 'method': 'DOM.enable'}))
            print('enabled permissions')

            command_id = 5
            self.ready_event.set()
            while True:
                await self.new_command_event.wait()

                if isinstance(self.command, str):
                    await websocket.send(json.dumps({
                        'id': command_id,
                        'method': 'Runtime.evaluate',
                        'params': {
                            'expression': self.command,
                        }
                    }))
                elif isinstance(self.command, PageNavigate):
                    await websocket.send(json.dumps({
                        'id': command_id,
                        'method': 'Page.navigate',
                        'params': {'url': self.command.url}
                    }))
                elif isinstance(self.command, CaptureScreenshot):
                    await websocket.send(json.dumps({
                        'id': command_id, 'method': 'Page.captureScreenshot'
                    }))
                elif isinstance(self.command, GetProperties):
                    await websocket.send(json.dumps({
                        'id': command_id,
                        'method': 'Runtime.getProperties',
                        'params': {
                            'objectId': self.command.objectId,
                        }
                    }))
                elif isinstance(self.command, CapturePartialScreenshot):
                    await websocket.send(json.dumps({
                        'id': command_id, 
                        'method': 'Page.captureScreenshot',
                        'params': {'clip': self.command.clip}
                        }))

                response = await websocket.recv()
                message = json.loads(response)

                # print(self.command, list(message.keys()))
                self.command = None
                if 'error' in message:
                    print(message['error'])
                if 'result' in message and bool(message['result']):
                    message_id = message['id']
                    result = message['result']
                    if message_id == command_id:
                        self.__set_result(result)
                        continue
                # self.__set_result(message)


    def __set_result(self, result):
        self.result = result
        self.notifier.set()
        self.new_command_event.clear()

    async def __run_command(self, command):
        await self.ready_event.wait()
        self.command = command
        self.new_command_event.set()
        await self.notifier.wait()

        self.command = None
        self.notifier = asyncio.Event()
        return self.result

    async def send_js(self, command: str):
        if command is None:
            return None
        result = await self.__run_command(command)
        if 'objectId' in result['result'] and not ('value' in result['result']):
            return await self.__get_object(result['result']['objectId'])
        return result

    async def get_value_by_js(self, command: str):
        if command is None:
            return None
        result = await self.__run_command(command)
        if 'objectId' in result['result'] and not ('value' in result['result']):
            object_result = await self.__get_object(result['result']['objectId']) 
            if isinstance(object_result['result'], list): 
                return object_result['result']
            return object_result['result']['value']
        return result['result']['value']

    async def wait_for_true(self, expression: str):
        while not (await self.get_value_by_js(expression)):
            pass
        return True

    async def navigate_to_url(self, url: str):
        command = PageNavigate(url)
        return await self.__run_command(command)

    async def capture_screenshot(self):
        command = CaptureScreenshot()
        return await self.__run_command(command)

    async def __get_object(self, objectId):
        command = GetProperties(objectId)
        return await self.__run_command(command)

    async def __get_bounding_box(self, selector):
        js_code = f'''
        (function() {{
            const element = document.querySelector("{selector}");
            if (!element) return null;
            const rect = element.getBoundingClientRect();
            return {{
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                scale: window.devicePixelRatio
            }};
        }})()
        '''
        return await self.get_value_by_js(js_code)

    async def capture_element_screenshot(self, selector):
        bounding_box = await self.__get_bounding_box(selector)
        print(bounding_box)
        if not bounding_box:
            print(f"Element with selector '{selector}' not found.")
            return None
        bounding_box_dict = {}
        for i in bounding_box:
            if 'value' in i:
                if 'value' in i['value']:
                    bounding_box_dict[i['name']] = i['value']['value']
        print(bounding_box_dict)
        clip = {
            'x': bounding_box_dict['x'],
            'y': bounding_box_dict['y'],
            'width': bounding_box_dict['width'],
            'height': bounding_box_dict['height'],
            'scale': bounding_box_dict['scale']
        }

        return await self.__run_command(CapturePartialScreenshot(clip))


