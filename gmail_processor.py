import base64
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailClient:
    def __init__(self, credentials_file):
        self.service = self.authenticate_gmail(credentials_file)

    def authenticate_gmail(self, credentials_file):
        """Authenticate with the Gmail API."""
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        return build("gmail", "v1", credentials=creds)

    def search_emails(self, query):
        """Search for emails matching a query."""
        try:
            messages = []
            response = (
                self.service.users().messages().list(userId="me", q=query).execute()
            )

            while "messages" in response:
                messages.extend(response["messages"])
                if "nextPageToken" in response:
                    response = (
                        self.service.users()
                        .messages()
                        .list(userId="me", q=query, pageToken=response["nextPageToken"])
                        .execute()
                    )
                else:
                    break

            return messages
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_email_details(self, message_id):
        """Fetch email details given a message ID."""
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
            headers = message["payload"]["headers"]

            sender = next(
                (
                    header["value"]
                    for header in headers
                    if header["name"].lower() == "from"
                ),
                None,
            )
            subject = next(
                (
                    header["value"]
                    for header in headers
                    if header["name"].lower() == "subject"
                ),
                None,
            )

            body = self.extract_body(message["payload"])
            return {
                "message_id": message_id,
                "sender": sender,
                "subject": subject,
                "body": body,
            }
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def extract_body(self, payload):
        """Extract the body from an email payload."""
        if "body" in payload and "data" in payload["body"]:
            return (
                base64.urlsafe_b64decode(payload["body"]["data"])
                .decode("utf-8")
                .replace("\n", "")
                .replace("\r", "")
            )

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain" and "data" in part["body"]:
                    return (
                        base64.urlsafe_b64decode(part["body"]["data"])
                        .decode("utf-8")
                        .replace("\n", "")
                        .replace("\r", "")
                    )

        return ""


class JobEmailProcessor:
    def __init__(self, gmail_client):
        self.gmail_client = gmail_client

    def process_job_emails(self, query):
        """Process job application emails."""
        messages = self.gmail_client.search_emails(query)
        email_data = []

        if messages:
            print(f"Found {len(messages)} emails. Fetching details...")
            for msg in messages:
                details = self.gmail_client.get_email_details(msg["id"])
                if details:
                    email_data.append(details)

        df = pd.DataFrame(email_data)
        df.to_csv("job_application_emails.csv", index=False)
        print("Job application data saved to job_application_emails.csv")
        return df


class MeetingEmailProcessor:
    def __init__(self, gmail_client):
        self.gmail_client = gmail_client

    def process_meeting_emails(self, query):
        """Process meeting-related emails."""
        messages = self.gmail_client.search_emails(query)
        email_data = []

        if messages:
            print(f"Found {len(messages)} emails. Fetching details...")
            for msg in messages:
                details = self.gmail_client.get_email_details(msg["id"])
                if details:
                    email_data.append(details)

        df = pd.DataFrame(email_data)
        df.to_csv("calendar_meetings.csv", index=False)
        print("Meeting data saved to calendar_meetings.csv")
        return df


if __name__ == "__main__":
    client = GmailClient("credentials.json")

    # Process job application emails
    job_processor = JobEmailProcessor(client)
    job_emails_query = '"applying" OR "application" after:2023/11/01'
    job_processor.process_job_emails(job_emails_query)

    # Process meeting emails
    meeting_processor = MeetingEmailProcessor(client)
    meeting_emails_query = (
        "filename:ics OR filename:ical OR filename:icalendar after:2023/11/01"
    )
    meeting_processor.process_meeting_emails(meeting_emails_query)
