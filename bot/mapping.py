from bot.github_api.issues import comment_issue, list_issues
from bot.github_api.milestone import more_than_x_days, set_milestone
from bot.github_api.pull_request import search_file_in_pull_request


func_mapping = {
    "more_than_x_days": more_than_x_days,
    "set_milestone": set_milestone,
    "add_reply": comment_issue,
    "search_file": search_file_in_pull_request,
    "list_issues": list_issues,
}