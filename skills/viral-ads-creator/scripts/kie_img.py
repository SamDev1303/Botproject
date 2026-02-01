import os
import requests
import time
import argparse

class KieImageAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.kie.ai/api/v1'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def generate_image(self, prompt):
        url = f"{self.base_url}/runway/generate" # Reverting to known working endpoint structure
        payload = {
            "prompt": prompt,
            "duration": 5,
            "quality": "720p",
            "aspectRatio": "1:1",
            "waterMark": ""
        }
        # Since text-to-image specialized endpoint failed, using 1:1 video generation to get the image frame/preview
        response = requests.post(url, headers=self.headers, json=payload)
        result = response.json()
        if not response.ok or result.get('code') != 200:
            raise Exception(f"Task failed: {result.get('msg', 'Unknown error')}")
        return result['data']['taskId']

    def wait_for_completion(self, task_id, max_wait_time=300):
        start_time = time.time()
        url = f"{self.base_url}/runway/record-detail?taskId={task_id}" # Polling endpoint seems consistent
        while time.time() - start_time < max_wait_time:
            response = requests.get(url, headers={'Authorization': f'Bearer {self.api_key}'})
            result = response.json()
            if not response.ok or result.get('code') != 200:
                # If specific image record-detail fails, try general record-detail
                url_alt = f"{self.base_url}/jobs/getTaskDetail?taskId={task_id}"
                response = requests.get(url_alt, headers={'Authorization': f'Bearer {self.api_key}'})
                result = response.json()

            data = result.get('data', {})
            state = data.get('state', 'wait')
            
            if state == 'success':
                # For images, URL might be in a different field
                info = data.get('videoInfo') or data.get('imageInfo') or data
                return info.get('imageUrl') or info.get('videoUrl')
            elif state == 'fail':
                raise Exception(data.get('failMsg', 'Task failed'))
            
            print(f"Image task {task_id} status: {state}...")
            time.sleep(15)
        raise Exception('Timeout')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("KIE_AI_API_KEY")
    api = KieImageAPI(api_key)
    try:
        print(f"Generating image: {args.prompt}")
        tid = api.generate_image(args.prompt)
        img_url = api.wait_for_completion(tid)
        print(f"Image URL: {img_url}")
        img_data = requests.get(img_url).content
        with open(args.filename, 'wb') as f:
            f.write(img_data)
        print(f"Saved to {args.filename}")
    except Exception as e:
        print(f"Error: {e}")
