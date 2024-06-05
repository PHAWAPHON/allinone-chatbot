import json
from locust import HttpUser, TaskSet, task, between


with open('mock_data.json') as f:
    mock_data = json.load(f)

class UserBehavior(TaskSet):
    @task(1)
    def get_images(self):
        customer = mock_data["customers"][0]
        self.client.get(f"/files_contents/folder/U16cbbdc57e4f3a0df2099d022d693f80/images", name="Get Images")
    
    @task(1)
    def get_videos(self):
        customer = mock_data["customers"][0]
        self.client.get(f"/files_contents/folder/U16cbbdc57e4f3a0df2099d022d693f80/videos", name="Get Videos")

    @task(1)
    def get_audios(self):
        customer = mock_data["customers"][0]
        self.client.get(f"/files_contents/folder/U16cbbdc57e4f3a0df2099d022d693f80/audios", name="Get Audios")
    
    @task(1)
    def reset_token(self):
        self.client.post("/files_contents/reset_token/1", name="Reset Token")
    
    @task(1)
    def insert_or_get_customer(self):
        customer = mock_data["customers"][0]
        self.client.post("/customer/insert_or_get_customer", name="Insert or Get Customer", json={"id": customer["id"]})
    
    @task(1)
    def insert_customer_all(self):
        customer = mock_data["customers"][0]
        self.client.post("/customer/insert_customer_all", name="Insert Customer All", json={
            "id": customer["id"],
            "GDRIVE_FOLDER_ID": customer["GDRIVE_FOLDER_ID"],
            "GDRIVE_FOLDER_IMAGE_ID": customer["GDRIVE_FOLDER_IMAGE_ID"],
            "GDRIVE_FOLDER_VIDEO_ID": customer["GDRIVE_FOLDER_VIDEO_ID"],
            "GDRIVE_FOLDER_AUDIO_ID": customer["GDRIVE_FOLDER_AUDIO_ID"]
        })
    
    @task(1)
    def insert_folder_id(self):
        customer = mock_data["customers"][0]
        self.client.post("/customer/insert_folder_id", name="Insert Folder ID", json={
            "id": customer["id"],
            "GDRIVE_FOLDER_ID": customer["GDRIVE_FOLDER_ID"]
        })
    
    @task(1)
    def insert_image_id(self):
        customer = mock_data["customers"][0]
        self.client.post("/customer/insert_image_id", name="Insert Image ID", json={
            "id": customer["id"],
            "GDRIVE_FOLDER_IMAGE_ID": customer["GDRIVE_FOLDER_IMAGE_ID"]
        })
    
    @task(1)
    def insert_video_id(self):
        customer = mock_data["customers"][0]
        self.client.post("/customer/insert_video_id", name="Insert Video ID", json={
            "id": customer["id"],
            "GDRIVE_FOLDER_VIDEO_ID": customer["GDRIVE_FOLDER_VIDEO_ID"]
        })
    
    @task(1)
    def insert_audio_id(self):
        customer = mock_data["customers"][0]
        self.client.post("/customer/insert_audio_id", name="Insert Audio ID", json={
            "id": customer["id"],
            "GDRIVE_FOLDER_AUDIO_ID": customer["GDRIVE_FOLDER_AUDIO_ID"]
        })
    
    @task(1)
    def insert_google_calendar_id(self):
        customer = mock_data["customers"][0]
        self.client.post("/customer/insert_google_calendar_id", name="Insert Google Calendar ID", json={
            "id": customer["id"],
            "calendar_id": "misternarn@gmail.com"
        })

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

if __name__ == "__main__":
    import os
    os.system("locust -f locustfile.py")
