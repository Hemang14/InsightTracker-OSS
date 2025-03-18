import requests
import datetime
import os
import json
import time

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "TOKEN")

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}

BASE_URL = "https://api.github.com"
JSON_FILE = "repository_metrics.json"

def get_repositories(archived):
    url = f"{BASE_URL}/search/repositories?per_page=61&q=org:apache+archived:{archived}"
    print(f"Fetching repositories from: {url}")
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    
    if response.status_code != 200:
        return []

    return [{"full_name": repo["full_name"], "pushed_at": repo["pushed_at"], "archived": repo["archived"]} for repo in data.get("items", [])]

def get_last_24_months(pushed_date):
    pushed_date = datetime.datetime.strptime(pushed_date, "%Y-%m-%dT%H:%M:%SZ").date()
    months = []
    
    for i in range(1, 26):
        year = pushed_date.year
        month = pushed_date.month - i
        
        while month <= 0:
            year -= 1
            month += 12  

        months.append(f"{year}-{month:02d}")

    return months[::-1]  


def get_commits(repo_full_name, month):
    split_year, split_month = map(int, month.split("-")) 
    start_date = datetime.date(split_year, split_month, 1)  
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1)  
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1)  
    pr_url = f"{BASE_URL}/repos/{repo_full_name}/commits?since={start_date}&until={end_date}&per_page=100"
    response = requests.get(pr_url, headers=HEADERS)
    if response.status_code != 200:
        print(response.status_code)
        return 0
    return len(response.json())

def get_pull_requests(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  
    start_date = datetime.date(split_year, split_month, 1)  
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1) 
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1) 
    pr_url = f"{BASE_URL}/search/issues?q=repo:{repo_full_name}+is:pr+closed:{start_date}..{end_date}"
    response = requests.get(pr_url, headers=HEADERS)
    if response.status_code != 200:
        print(response.status_code)
        return 0
    data = response.json()
    return data["total_count"]
    

def get_issues_resolved(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  
    start_date = datetime.date(split_year, split_month, 1)  
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1) 
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1)  
    issue_url = f"{BASE_URL}/search/issues?q=repo:{repo_full_name}+is:issue+closed:{start_date}..{end_date}"
    response = requests.get(issue_url, headers=HEADERS)
    if response.status_code != 200:
        print(response.status_code)
        return 0
    data = response.json()
    return data["total_count"]

def get_milestones_completed(repo_full_name, month):
    milestones_url = f"{BASE_URL}/repos/{repo_full_name}/milestones?state=closed&per_page=100"
    response = requests.get(milestones_url, headers=HEADERS)
    if response.status_code != 200:
        print(response.status_code)
        return 0

    milestones = response.json()
    return sum(1 for milestone in milestones if milestone["closed_at"][:7] == month)

def get_code_churn(repo_full_name, month):
    split_year, split_month = map(int, month.split("-"))  
    start_date = datetime.date(split_year, split_month, 1)  
    if split_month == 12:
        end_date = datetime.date(split_year + 1, 1, 1) - datetime.timedelta(days=1) 
    else:
        end_date = datetime.date(split_year, split_month + 1, 1) - datetime.timedelta(days=1)  
    commit_url = f"{BASE_URL}/repos/{repo_full_name}/commits?since={start_date}&until={end_date}&per_page=100"
    response = requests.get(commit_url, headers=HEADERS)
    if response.status_code != 200:
        print(response.status_code)
        return 0, 0

    lines_added, lines_removed = 0, 0
    commits = response.json()
    
    for commit in commits:
        commit_url = commit["url"]
        commit_response = requests.get(commit_url, headers=HEADERS)
        if commit_response.status_code != 200:
            print(commit_response.status_code)
        commit_details = commit_response.json()
        if "stats" in commit_details:
            date = commit_details["commit"]["author"]["date"][:7] 
            if date == month:
                lines_added += commit_details["stats"]["additions"]
                lines_removed += commit_details["stats"]["deletions"]

    return lines_added, lines_removed

def get_mails_per_month(repo_full_name, month):
    split_year, split_month = map(int, month.split("-")) 
    start_date = datetime.date(split_year, split_month, 1)  
    comments_url = f"{BASE_URL}/repos/{repo_full_name}/issues/comments?since={start_date}&per_page=100"
    response = requests.get(comments_url, headers=HEADERS)
    if response.status_code != 200:
        print(response.status_code)
        return 0

    comments = response.json()
    return sum(1 for comment in comments if comment["created_at"][:7] == month)

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

def map_label_to_number(label):
    label_mapping = {
        "Accelerating": 6,
        "Consolidating": 5,
        "Maintaining": 4,
        "Plateauing": 3,
        "Declining": 2,
        "Crisis": 1
    }
    return label_mapping.get(label, -1)  

def convert_month_format(month):
    """Convert 'YYYY-MM' to 'YYMM' format."""
    year, month_num = month.split("-")
    return f"{year[-2:]}{month_num}"

def load_existing_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []  
    return []

def filter_unprocessed_repos(repos, existing_data):
    processed_repos = {entry["Github_link"] for entry in existing_data}
    return [repo for repo in repos if f"https://github.com/{repo['full_name']}" not in processed_repos]

if __name__ == "__main__":
    existing_data = load_existing_data()  

    archived_repos = get_repositories(archived="true")
    non_archived_repos = get_repositories(archived="false")
    all_repos = archived_repos + non_archived_repos

    repos = filter_unprocessed_repos(all_repos, existing_data)

    print("\nProcessing the following new repositories:")
    for repo in repos:
        print(f"{repo['full_name']} (Last Pushed: {repo['pushed_at']})")

    for repo in repos:
        repo_name = repo["full_name"]
        repo_url = f"https://github.com/{repo_name}"
        last_pushed = repo["pushed_at"]

        print(f"\nProcessing {repo_name} (Last Pushed: {last_pushed})")

        last_24_months = get_last_24_months(last_pushed)

        repo_data = []

        curr_month = last_24_months[len(last_24_months) - 1]
        print(f"Fetching data for {repo_name} in {curr_month}...")

        commits = get_commits(repo_name, curr_month)
        pr_closed = get_pull_requests(repo_name, curr_month)
        issues_resolved = get_issues_resolved(repo_name, curr_month)
        milestones_completed = get_milestones_completed(repo_name, curr_month)
        lines_added, lines_removed = get_code_churn(repo_name, curr_month)
        mails = get_mails_per_month(repo_name, curr_month)

        for i in range(len(last_24_months) - 1):

            prev_month = last_24_months[len(last_24_months) - i - 2]
            print(f"Fetching data for {repo_name} in {prev_month}...")

            commits_prev = get_commits(repo_name, prev_month)
            pr_closed_prev = get_pull_requests(repo_name, prev_month)
            issues_resolved_prev = get_issues_resolved(repo_name, prev_month)
            milestones_completed_prev = get_milestones_completed(repo_name, prev_month)
            
            time.sleep(4) 

            lines_added_prev, lines_removed_prev = get_code_churn(repo_name, prev_month)
            mails_prev = get_mails_per_month(repo_name, prev_month)

            score = calculate_composite_score({
                "commits": {"current": commits, "previous": commits_prev},  
                "pull_requests": {"current": pr_closed, "previous": pr_closed_prev},
                "issues_resolved": {"current": issues_resolved, "previous": issues_resolved_prev},
                "milestones": {"current": milestones_completed, "previous": milestones_completed_prev},
                "code_churn": {"current": lines_added - lines_removed, "previous": lines_added_prev - lines_removed_prev},
                "community_engagement": {"current": mails, "previous": mails_prev}
            })
            label = assign_label(score)

            repo_data.append({
                "Month": convert_month_format(curr_month),
                "Score": score,
                "Label": map_label_to_number(label)
            })

            commits = commits_prev
            pr_closed = pr_closed_prev
            issues_resolved = issues_resolved_prev
            milestones_completed = milestones_completed_prev
            lines_added, lines_removed = lines_added_prev, lines_removed_prev
            mails = mails_prev
            curr_month = prev_month

            time.sleep(4) 

        existing_data.append({
                "Github_link": repo_url,
                "monthly_metrics": repo_data,
                "final_status": 0.0 if repo["archived"] else 1.0
            })

        with open(JSON_FILE, "w") as f:
            json.dump(existing_data, f, indent=4)

    print("Processing complete! Data saved in repository_metrics.json")