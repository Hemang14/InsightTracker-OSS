import requests
import datetime
import os

# GitHub Token for Authentication
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "ADD_GITHUB_TOKEN_HERE") # Add GitHub token here

# GitHub API Headers with Authentication
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}

# Base API URL
BASE_URL = "https://api.github.com"

# Function to get repositories
def get_repositories():
    url = f"{BASE_URL}/orgs/apache/repos?per_page=100&sort=pushed"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

# Function to fetch commits per month
def get_commits(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  # Extract year and month from string
    start_date = datetime.date(split_year, split_month, 1)  # First day of the month
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1)  # Dec 31st
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1)  # Last day of month
    pr_url = f"{BASE_URL}/repos/{repo_full_name}/commits?since={start_date}&until={end_date}&per_page=100"
    response = requests.get(pr_url, headers=HEADERS)
    return len(response.json()) if response.status_code == 200 else 0

# Function to fetch pull request data
def get_pull_requests(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  # Extract year and month from string
    start_date = datetime.date(split_year, split_month, 1)  # First day of the month
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1)  # Dec 31st
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1)  # Last day of month
    pr_url = f"{BASE_URL}/search/issues?q=repo:{repo_full_name}+is:pr+closed:{start_date}..{end_date}"
    response = requests.get(pr_url, headers=HEADERS)
    data = response.json()
    return data["total_count"] if response.status_code == 200 else 0
    

# Function to fetch issues resolved per month
def get_issues_resolved(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  # Extract year and month from string
    start_date = datetime.date(split_year, split_month, 1)  # First day of the month
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1)  # Dec 31st
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1)  # Last day of month
    issue_url = f"{BASE_URL}/search/issues?q=repo:{repo_full_name}+is:issue+closed:{start_date}..{end_date}"
    response = requests.get(issue_url, headers=HEADERS)
    data = response.json()
    return data["total_count"] if response.status_code == 200 else 0

# Function to fetch completed milestones per month
def get_milestones_completed(repo_full_name, month):
    milestones_url = f"{BASE_URL}/repos/{repo_full_name}/milestones?state=closed&per_page=100"
    response = requests.get(milestones_url, headers=HEADERS)
    if response.status_code != 200:
        return 0

    milestones = response.json()
    return sum(1 for milestone in milestones if milestone["closed_at"][:7] == month)

# Function to fetch code churn per month (lines added vs removed)
def get_code_churn(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  # Extract year and month from string
    start_date = datetime.date(split_year, split_month, 1)  # First day of the month
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1)  # Dec 31st
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1)  # Last day of month
    commit_url = f"{BASE_URL}/repos/{repo_full_name}/commits?since={start_date}&until={end_date}&per_page=100"
    response = requests.get(commit_url, headers=HEADERS)
    if response.status_code != 200:
        return 0, 0

    lines_added, lines_removed = 0, 0
    commits = response.json()
    
    for commit in commits:
        commit_url = commit["url"]
        commit_details = requests.get(commit_url, headers=HEADERS).json()
        if "stats" in commit_details:
            date = commit_details["commit"]["author"]["date"][:7]  # Extract YYYY-MM
            if date == month:
                lines_added += commit_details["stats"]["additions"]
                lines_removed += commit_details["stats"]["deletions"]

    return lines_added, lines_removed

# Function to estimate mails per month from PR discussions and commit messages
def get_mails_per_month(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  # Extract year and month from string
    start_date = datetime.date(split_year, split_month, 1)  # First day of the month
    comments_url = f"{BASE_URL}/repos/{repo_full_name}/issues/comments?since={start_date}&per_page=100"
    response = requests.get(comments_url, headers=HEADERS)
    if response.status_code != 200:
        return 0

    comments = response.json()
    return sum(1 for comment in comments if comment["created_at"][:7] == month)

# Function to calculate the composite score
def calculate_composite_score(data):
    weights = {
        'commits': 20,
        'pull_requests': 15,
        'issues_resolved': 20,
        'milestones': 20,
        'code_churn': 10,
        'community_engagement': 15
    }
    
    score = 0
    for metric, weight in weights.items():
        percent_change = (data[metric]['current'] - data[metric]['previous']) / data[metric]['previous'] if data[metric]['previous'] > 0 else 0
        score += percent_change * (weight / 100)
    
    return score

# Function to assign labels based on the composite score
def assign_label(score):
    if score > 0.30:
        return 'Accelerating'
    elif 0.10 < score <= 0.30:
        return 'Consolidating'
    elif 0.00 < score <= 0.10:
        return 'Maintaining'
    elif -0.10 < score <= 0.00:
        return 'Plateauing'
    elif -0.30 < score <= -0.10:
        return 'Declining'
    elif score <= -0.30:
        return 'Crisis'
    else:
        return 'Data Insufficient'

# Function to collect data for a given month
def collect_metrics_for_month(month):
    repos = get_repositories()
    results = {}

    for repo in repos:
        repo_name = repo["full_name"]
        print(f"Processing {repo_name} for {month}...")

        commits = get_commits(repo_name, month)
        pr_closed = get_pull_requests(repo_name, month)
        issues_resolved = get_issues_resolved(repo_name, month)
        milestones_completed = get_milestones_completed(repo_name, month)
        lines_added, lines_removed = get_code_churn(repo_name, month)
        mails = get_mails_per_month(repo_name, month)

        results[repo_name] = {
            'commits': commits,
            'pull_requests': pr_closed,
            'issues_resolved': issues_resolved,
            'milestones': milestones_completed,
            'code_churn': lines_added - lines_removed,
            'community_engagement': mails
        }

    return results

# Run script for a specific month and calculate the composite score
if __name__ == "__main__":
    month = input("Enter month (YYYY-MM): ")

    # Compute the previous month
    year, month_num = map(int, month.split("-"))
    prev_month = f"{year - 1}-12" if month_num == 1 else f"{year}-{month_num - 1:02d}"

    print(f"Fetching data for {month} and {prev_month}...")

    current_data = collect_metrics_for_month(month)
    previous_data = collect_metrics_for_month(prev_month)

    print("\nFinal Report:\n")
    for repo, metrics in current_data.items():
        previous_metrics = previous_data.get(repo, {metric: 0 for metric in metrics})

        data = {metric: {'current': metrics[metric], 'previous': previous_metrics.get(metric, 0)}
                for metric in metrics}

        score = calculate_composite_score(data)
        label = assign_label(score)

        print(f"{repo} - Score: {score:.2f}, Label: {label}")
