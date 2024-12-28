import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def format_interviews(df):
    """
    Extract domain information from the sender's email address.
    """
    df["domain"] = df["sender"].apply(lambda x: x[x.index("@") + 1 :])
    return df


def get_single_classification(classification):
    """
    Simplifies multiple classifications into a single, prioritized classification.
    Hierarchy: reject > filled > application_confirmation
    """
    hierarchy = ["reject", "filled", "application_confirmation"]
    for level in hierarchy:
        if level in classification:
            return level
    return None  # Return None if no classification matches


def classify_emails(df):
    """
    Classify emails into categories based on their body text.
    Categories: application_confirmation, job_filled, reject
    """
    classifications = {
        "application_confirmation": [
            "received",
            "we contact you",
            "we will review",
            "review",
            "reviewing",
            "submitted successfully",
            "thank you for applying",
            "thanks for applying",
            "submit your application",
            "If",
            "get back to you",
            "will be in touch",
            "high volume",
            "be in touch",
        ],
        "job_filled": ["position filled", "no longer hiring"],
        "reject": [
            "move forward with other candidates",
            "not move forward with your application",
            "not to move forward",
            "not your candidacy",
            "canidate",
            "not be moving forward",
            "unfortunately",
            "other candidates",
            "experience align more closely",
            "appreciate the time and effort",
        ],
    }

    def classify_body(body):
        """
        Classifies the email body based on keyword matches.
        """
        labels = []
        if not isinstance(body, str):
            body = str(body)  # Ensure body is treated as a string
        for label, keywords in classifications.items():
            if any(keyword in body.lower() for keyword in keywords):
                labels.append(label)
        return labels

    # Apply classification to email bodies
    df["classification"] = df["body"].apply(classify_body)

    # Handle missing email bodies
    df["classification"] = df.apply(
        lambda row: (
            ["application_confirmation"]
            if pd.isnull(row["body"])
            else row["classification"]
        ),
        axis=1,
    )

    # Simplify classifications using hierarchy
    df["classification"] = df["classification"].apply(get_single_classification)

    # Replace missing classifications with 'application_confirmation'
    df["classification"] = df["classification"].fillna("application_confirmation")

    # Exclude emails sent from the user's personal email
    df = df[df["sender"] != os.getenv("MY_EMAIL")]

    return df


# Load job application emails
df = pd.read_csv("job_application_emails.csv")
df = classify_emails(df)

# Print the percentage of unclassified emails
print(f"Number of unclassified emails: {df.classification.isna().sum() / len(df):.2%}")

# Load meeting data
df_meetings = pd.read_csv("calendar_meetings.csv")


df_meetings = format_interviews(df_meetings)

# Group meetings by domain
df_meetings_company_group = (
    df_meetings[["message_id", "domain"]].groupby(by="domain").count().reset_index()
)

# Adjust message count for a specific domain
condition = df_meetings_company_group["domain"] == "voxelai.com"
df_meetings_company_group.loc[condition, "message_id"] = 7

print(f"\nNumber of companies interviewed with: {len(df_meetings_company_group)}\n")

# Group applications by classification stage
df_apply_group = (
    df[["message_id", "classification"]].groupby("classification").count().reset_index()
)

# Rename columns for clarity
df_apply_group.rename(
    columns={
        "classification": "stage",
        "message_id": "emails",
    },
    inplace=True,
)

# Calculate ghosted emails
ghosted_email_val = (
    df_apply_group["emails"][0]
    - df_apply_group["emails"][1]
    - len(df_meetings_company_group)
)

# Add ghosted emails as a new row
new_row = pd.DataFrame({"stage": ["ghosted"], "emails": [ghosted_email_val]})
df_apply_group = pd.concat([df_apply_group, new_row], ignore_index=True)

print(df_apply_group)
print("\n")
# Group meetings by number of interviews per stage
df_meetings_group = (
    df_meetings_company_group.groupby(by="message_id").count().reset_index()
)
df_meetings_group.rename(
    columns={"message_id": "interview_stage", "domain": "no_interviews_per_stage"},
    inplace=True,
)
df_meetings_group = df_meetings_group[df_meetings_group.interview_stage < 9]
print(df_meetings_group)
