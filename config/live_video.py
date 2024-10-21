import datetime

import jwt
import requests
from django.contrib.auth import get_user_model

from apps.batch.models import LiveClass

User = get_user_model()


class MeritHubAPI:
    BASE_URL = "https://serviceaccount1.meritgraph.com/v1/"
    CLASS_URL = "https://class1.meritgraph.com/v1/"

    def __init__(self, client_id, secret_key):
        self.client_id = client_id
        self.secret_key = secret_key
        self.access_token = None

    def generate_jwt(self):
        """Generates a JWT token."""
        # Define your client ID and secret
        client_id = self.client_id
        client_secret = self.secret_key

        # Create JWT payload
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        payload = {
            "aud": f"https://serviceaccount1.meritgraph.com/v1/{client_id}/api/token",
            "iss": client_id,
            "expiry": expiry.timestamp()  # Use Unix timestamp for expiry
        }

        # Encode the JWT
        encoded = jwt.encode(payload, client_secret, algorithm='HS256')

        # No need to convert, encoded is already a string
        return encoded

    def get_access_token(self):
        """Get the access token using the generated JWT."""
        url = f"{self.BASE_URL}{self.client_id}/api/token"

        # Generate the JWT token
        jwt_token = self.generate_jwt()

        # Prepare the token request body
        token_request_body = {
            'assertion': jwt_token,
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer'
        }

        # Make the request to get the access token
        response = requests.post(url, data=token_request_body)

        # Raise an error if the request was unsuccessful
        response.raise_for_status()

        # Extract the access token from the response
        self.access_token = response.json().get('access_token')
        return self.access_token

    def _get_headers(self):
        """Helper method to get headers with access token."""
        if not self.access_token:
            self.get_access_token()
        return {
            "Authorization": f"{self.access_token}",
            "Content-Type": "application/json"
        }

    def generate_url(self, link):
        return f"https://live.merithub.com/info/room/{self.client_id}/{link}"

    # Users
    def create_user(self, user_data):
        """Add a user to the account."""
        url = f"{self.BASE_URL}{self.client_id}/users"
        headers = self._get_headers()
        response = requests.post(url, json=user_data, headers=headers)
        response.raise_for_status()
        return response.json()

    # Classes
    def schedule_class(self, user_id, class_data, batch):
        """Schedule a class for the teacher."""
        user = User.objects.get(id=user_id)
        if not user.merit_user_id:
            response = self.create_user({
                'name': user.full_name,
                'email': user.email,
                'clientUserId': str(user_id),
                "role": "C",
                "timeZone": "Asia/Kolkata",
                "permission": "CC"
            })
            user.merit_user_id = response['userId']
            user.save()
        url = f"{self.CLASS_URL}{self.client_id}/{user.merit_user_id}"
        headers = self._get_headers()
        response = requests.post(url, json=class_data, headers=headers)
        response.raise_for_status()
        data = response.json()
        live_class = LiveClass.objects.create(
            batch=batch,
            title=class_data['title'],
            class_id=data['classId'],
            date=class_data['startTime'],
            host_link=self.generate_url(data['hostLink']),
            common_host_link=self.generate_url(data['commonLinks']['commonHostLink']),
            common_moderator_link=self.generate_url(data['commonLinks']['commonModeratorLink']),
            common_participant_link=self.generate_url(data['commonLinks']['commonParticipantLink'])
        )
        return live_class

    def add_students_to_class(self, class_id, users):
        """Add students to a scheduled class."""
        url = f"{self.CLASS_URL}{self.client_id}/{class_id}/users"
        headers = self._get_headers()
        response = requests.post(url, json={"users": users}, headers=headers)
        response.raise_for_status()
        return response.json()

    def remove_users_from_class(self, class_id, users):
        """Remove users from a class."""
        url = f"{self.CLASS_URL}{self.client_id}/{class_id}/removeuser"
        headers = self._get_headers()
        response = requests.post(url, json={"users": users}, headers=headers)
        response.raise_for_status()
        return response.json()

    def delete_class(self, class_id):
        """Delete a class and all related data."""
        url = f"{self.CLASS_URL}{self.client_id}/{class_id}"
        headers = self._get_headers()
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()

    # Webhook Handlers
    def handle_class_status(self, data):
        """Handle class status updates."""
        status = data.get('status')
        if status == 'lv':
            print(f"Class {data.get('classId')} is live.")
        elif status == 'cp':
            print(f"Class {data.get('classId')} has ended.")
        elif status == 'cl':
            print(f"Class {data.get('classId')} is cancelled.")
        elif status == 'ex':
            print(f"Class {data.get('classId')} has expired.")
        elif status == 'up':
            print(f"Class {data.get('classId')} has been edited.")
        else:
            print(f"Unknown status for class {data.get('classId')}: {status}")
        # Log or save data as needed

    def handle_attendance(self, data):
        """Handle attendance data when class ends."""
        class_id = data.get('classId')
        attendance_data = data.get('attendance')
        print(f"Attendance data for class {class_id}:")
        for entry in attendance_data:
            print(f"User ID: {entry.get('userId')}, Total Time: {entry.get('totalTime')}")
        # Log or save data as needed

    def handle_recording(self, data):
        """Handle recording availability notifications."""
        class_id = data.get('classId')
        recording_url = data.get('url')
        print(f"Recording available for class {class_id}: {recording_url}")
        # Log or save data as needed

    def handle_class_files(self, data):
        """Handle file sharing notifications."""
        class_id = data.get('classId')
        files = data.get('Files')
        print(f"Files shared for class {class_id}:")
        for file in files:
            print(f"File ID: {file.get('fileId')}, URL: {file.get('url')}")
        # Log or save data as needed

    def handle_chats(self, data):
        """Handle chat data when generated."""
        class_id = data.get('classId')
        public_chats = data.get('chats').get('public')
        private_chats = data.get('chats').get('private')
        print(f"Public chat link for class {class_id}: {public_chats}")
        print(f"Private chat links for class {class_id}: {private_chats}")
        # Log or save data as needed

# Example Usage:
# api = MeritHubAPI(client_id="cqb8fh1nuvta0dldbsdg",, secret_key="$2a$04$fQ7kQ1or4UnWWC76vtFPKeovH3CJNWHiQTcJH03VuEJvpX7VDWENW    ")
# user_data = {"name": "John Doe", "email": "john@example.com"}
# api.create_user(user_data)
# class_data = {"name": "Math Class", "start_time": "2024-09-20T15:00:00Z", "duration": 60}
# api.schedule_class(user_id="teacher_id", class_data=class_data)
# api.add_students_to_class(class_id="class_id", users=["student1_id", "student2_id"])
# api.remove_users_from_class(class_id="class_id", users=["student1_id"])
# api.delete_class(class_id="class_id")
