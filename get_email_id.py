import os
import csv
import requests
import re
import time

def fetch_email_from_patch(patch_url, github_token=None, retries=3, delay=2):
    headers = {'Authorization': f'token {github_token}'} if github_token else {}
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(patch_url, headers=headers, timeout=10)

            # Check for rate-limiting
            if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                reset_time = int(response.headers['X-RateLimit-Reset'])
                wait_time = reset_time - int(time.time())
                print(f"Rate limit reached. Waiting {wait_time} seconds.")
                time.sleep(wait_time + 1)
                continue  # Retry after waiting

            response.raise_for_status()
            email_match = re.search(r"From: .+? <(.+?)>", response.text)
            if email_match:
                return email_match.group(1)
            else:
                return None
        except requests.RequestException as e:
            print(f"Error fetching patch for {patch_url}: {e}")
            attempt += 1
            if attempt < retries:
                print(f"Retrying... (Attempt {attempt}/{retries})")
                time.sleep(delay)
            else:
                print(f"Failed to fetch patch for {patch_url} after {retries} attempts.")
                return None

def get_repo_url_from_commit(commit_url):
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/commit/([a-f0-9]+)", commit_url)
    if match:
        owner, repo, _ = match.groups()
        return f"https://github.com/{owner}/{repo}"
    return None

def process_csv_files(input_folder, output_file, github_token=None):
    unique_commit_urls = set()

    with open(output_file, mode='w', newline='') as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=["Repo URL", "Commit URL", "Email ID"])
        writer.writeheader()

        for filename in os.listdir(input_folder):
            if filename.endswith(".csv"):
                file_path = os.path.join(input_folder, filename)
                with open(file_path, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        commit_url = row.get("Commit URL")

                        if commit_url and commit_url not in unique_commit_urls:
                            unique_commit_urls.add(commit_url)

                            patch_url = commit_url + ".patch"
                            email = fetch_email_from_patch(patch_url, github_token)
                            repo_url = get_repo_url_from_commit(commit_url)

                            if email:
                                writer.writerow({"Repo URL": repo_url, "Commit URL": commit_url, "Email ID": email})

                            time.sleep(1)  # Standard delay between requests

# Usage
input_folder = "repo_list"  # Folder containing the CSV files
output_file = "commit_emails.csv"  # Output CSV file with repo URLs, commit URLs, and email IDs
github_token = "GIT_HUB_TOKEN"  # Replace with your GitHub token

process_csv_files(input_folder, output_file, github_token)
