import requests
import datetime
from collections import defaultdict

# GitHub API Headers (Use a personal access token if you have rate limits)
HEADERS = {"Accept": "application/vnd.github.v3+json"}

# Base API URL
BASE_URL = "https://api.github.com"

# Function to fetch repositories
def get_repositories():
    url = f"{BASE_URL}/orgs/apache/repos?per_page=5"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

# Function to fetch contributors per month
def get_contributors(repo_full_name, month):
    url = f"{BASE_URL}/repos/{repo_full_name}/contributors"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return 0
    return len(response.json())

# Function to fetch pull request data
def get_pull_requests(repo_full_name, month):
    pr_url = f"{BASE_URL}/repos/{repo_full_name}/pulls?state=all&per_page=100"
    response = requests.get(pr_url, headers=HEADERS)
    if response.status_code != 200:
        return 0, 0

    prs = response.json()
    opened, closed = 0, 0
    for pr in prs:
        created_at = datetime.datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m")
        closed_at = pr["closed_at"]
        if created_at == month:
            opened += 1
        if closed_at and datetime.datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m") == month:
            closed += 1

    return opened, closed

# Function to fetch issues resolved per month
def get_issues_resolved(repo_full_name, month):
    issues_url = f"{BASE_URL}/repos/{repo_full_name}/issues?state=closed&per_page=100"
    response = requests.get(issues_url, headers=HEADERS)
    if response.status_code != 200:
        return 0

    issues = response.json()
    return sum(1 for issue in issues if "pull_request" not in issue and 
               datetime.datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m") == month)

# Function to fetch completed milestones per month
def get_milestones_completed(repo_full_name, month):
    milestones_url = f"{BASE_URL}/repos/{repo_full_name}/milestones?state=closed"
    response = requests.get(milestones_url, headers=HEADERS)
    if response.status_code != 200:
        return 0

    milestones = response.json()
    return sum(1 for milestone in milestones if 
               datetime.datetime.strptime(milestone["closed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m") == month)

# Function to fetch code churn per month (lines added vs removed)
def get_code_churn(repo_full_name, month):
    commits_url = f"{BASE_URL}/repos/{repo_full_name}/commits?per_page=100"
    response = requests.get(commits_url, headers=HEADERS)
    if response.status_code != 200:
        return 0, 0

    lines_added, lines_removed = 0, 0
    commits = response.json()
    
    for commit in commits:
        commit_url = commit["url"]
        commit_details = requests.get(commit_url, headers=HEADERS).json()
        if "stats" in commit_details:
            date = datetime.datetime.strptime(commit_details["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m")
            if date == month:
                lines_added += commit_details["stats"]["additions"]
                lines_removed += commit_details["stats"]["deletions"]

    return lines_added, lines_removed

# Function to estimate mails per month from PR discussions and commit messages
def get_mails_per_month(repo_full_name, month):
    comments_url = f"{BASE_URL}/repos/{repo_full_name}/issues/comments?per_page=100"
    response = requests.get(comments_url, headers=HEADERS)
    if response.status_code != 200:
        return 0

    comments = response.json()
    return sum(1 for comment in comments if datetime.datetime.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m") == month)

# Function to collect all data for a given month
def collect_metrics_for_month(month):
    repos = get_repositories()
    results = []

    for repo in repos:
        repo_name = repo["full_name"]
        print(f"Processing {repo_name}...")

        contributors = get_contributors(repo_name, month)
        pr_opened, pr_closed = get_pull_requests(repo_name, month)
        issues_resolved = get_issues_resolved(repo_name, month)
        milestones_completed = get_milestones_completed(repo_name, month)
        lines_added, lines_removed = get_code_churn(repo_name, month)
        mails = get_mails_per_month(repo_name, month)

        results.append({
            "Repository": repo_name,
            "Contributors": contributors,
            "PRs Opened": pr_opened,
            "PRs Closed": pr_closed,
            "Issues Resolved": issues_resolved,
            "Milestones Completed": milestones_completed,
            "Code Churn (Added)": lines_added,
            "Code Churn (Removed)": lines_removed,
            "Emails": mails,
        })

    return results

# Run script for a specific month
if __name__ == "__main__":
    month = input("Enter month (YYYY-MM): ")
    data = collect_metrics_for_month(month)

    # Print results
    for row in data:
        print(row)
