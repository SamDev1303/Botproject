import os
import requests
import time
import argparse

class RunwayAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.kie.ai/api/v1/runway'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def generate_video(self, **options):
        response = requests.post(f'{self.base_url}/generate',
                                headers=self.headers, json=options)
        result = response.json()

        if not response.ok or result.get('code') != 200:
            raise Exception(f"Generation failed: {result.get('msg', 'Unknown error')}")

        return result['data']['taskId']

    def wait_for_completion(self, task_id, max_wait_time=600):
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            status = self.get_task_status(task_id)
            state = status['state']

            if state == 'wait':
                print("Task is waiting, continue waiting...")
            elif state == 'queueing':
                print("Task is queueing, continue waiting...")
            elif state == 'generating':
                print("Task is generating, continue waiting...")
            elif state == 'success':
                print("Generation completed successfully!")
                return status
            elif state == 'fail':
                error = status.get('failMsg', 'Task generation failed')
                print(f"Task generation failed: {error}")
                raise Exception(error)
            else:
                print(f"Unknown status: {state}")
                if status.get('failMsg'):
                    print(f"Error message: {status['failMsg']}")

            time.sleep(30) # Wait 30 seconds

        raise Exception('Generation timeout')

    def get_task_status(self, task_id):
        response = requests.get(f'{self.base_url}/record-detail?taskId={task_id}',
                                headers={'Authorization': f'Bearer {self.api_key}'})
        result = response.json()

        if not response.ok or result.get('code') != 200:
            raise Exception(f"Status check failed: {result.get('msg', 'Unknown error')}")

        return result['data']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("KIE_AI_API_KEY")
    if not api_key:
        print("Error: KIE_AI_API_KEY not found in environment.")
        exit(1)

    api = RunwayAPI(api_key)
    try:
        print(f"Starting video generation for: {args.prompt}")
        task_id = api.generate_video(
            prompt=args.prompt,
            duration=5,
            quality='720p',
            aspectRatio='9:16',
            waterMark=''
        )
        print(f"Task ID: {task_id}. Waiting for completion...")
        result = api.wait_for_completion(task_id)
        
        video_url = result['videoInfo']['videoUrl']
        print(f"Video URL: {video_url}")
        
        # Download the video
        video_data = requests.get(video_url).content
        with open(args.filename, 'wb') as f:
            f.write(video_data)
        print(f"Saved to {args.filename}")
        
    except Exception as e:
        print(f"Error: {e}")
