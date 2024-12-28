# Job Application Data API Processor

This repository contains Python scripts for extracting and processing emails using the Gmail API. The primary purpose of this project is to determine how many jobs one has applied to and classify the stages of job applications (e.g., application confirmation, rejection, interviews, etc.). The extracted data can be used to create visualizations like a Sankey chart to analyze the job application process and track progress.

## Features

- **JobEmailProcessor**: Fetches emails related to job applications based on specific search queries.
- **MeetingEmailProcessor**: Fetches emails related to calendar meetings (e.g., `.ics`, `.ical` files).
- **Reusable GmailClient**: Handles Gmail API authentication, email searching, and message extraction.

The output data from these scripts can help visualize:
1. The number of jobs applied to.
2. The progression through different application stages.
3. The overall outcome of the job application process.

---

## Setup

### Prerequisites
1. **Python**: Ensure you have Python 3.7 or later installed.
2. **Google API Client**: Install the required library for interacting with the Gmail API:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas
   ```
3. **Google Cloud Project**: Set up a Google Cloud project and enable the Gmail API.

---

### Steps to Enable Gmail API and Get `credentials.json`

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing project).
3. Navigate to **APIs & Services > Library**.
4. Search for "Gmail API" and enable it for your project.
5. Navigate to **APIs & Services > Credentials**.
6. Click **Create Credentials** and select "OAuth 2.0 Client IDs".
7. Configure the consent screen if prompted.
8. Choose "Desktop App" as the application type and click **Create**.
9. Download the `credentials.json` file and save it in the root directory of this project.

---

### Running the Scripts

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Ensure `credentials.json` is in the same directory as the scripts.
3. Run the main script to process job application and meeting emails:
   ```bash
   python gmail_email_processor.py
   ```

---

## File Structure

- **`gmail_email_processor.py`**: Consolidated script for processing emails.
  - Includes the `GmailClient`, `JobEmailProcessor`, and `MeetingEmailProcessor` classes.
- **`credentials.json`**: OAuth 2.0 credentials for accessing Gmail API (not included; follow the setup instructions to obtain).
- **Output CSVs**:
  - `job_application_emails.csv`: Contains processed job application emails.
  - `calendar_meetings.csv`: Contains processed meeting-related emails.

---

## Example Queries

- **Job Emails Query**:
  ```
  "applying" OR "application" after:2023/11/01
  ```
- **Meeting Emails Query**:
  ```
  filename:ics OR filename:ical OR filename:icalendar after:2023/11/01
  ```

---

## Goal: Sankey Chart

The ultimate goal of this project is to provide data for creating a Sankey chart, which visually represents the flow of job applications through various stages. For example:
- Applications submitted
- Rejections
- Interview invitations
- Final outcomes (e.g., offers or no response)

By organizing and classifying email data, users can generate meaningful insights into their job search journey and identify patterns or areas for improvement.

---

## Contributing

Feel free to submit issues or pull requests for enhancements or bug fixes.

---

## License

This project is licensed under the MIT License.

