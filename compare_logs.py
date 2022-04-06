from importlib.metadata import requires
from optparse import Values
import gitlab
from atlassian import Bitbucket
from pprint import pprint
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime 

load_dotenv()

bitbucket = Bitbucket(
    url=os.getenv("BITBUCKET_URL"),
    username=os.getenv("BITBUCKET_USERNAME"),
    password=os.getenv("BITBUCKET_PASSWORD")
)

bb_logs = {}
projects = bitbucket.project_list()

gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))  #Added
gl.auth()
gl_logs = {}

for project in projects:
    proj_key = project["key"]

    bit_repos = bitbucket.repo_list(proj_key)
    for bb_repo in bit_repos:
        try:
            gl_repo = gl.projects.list(search=bb_repo.get("name"))[0]
        except:
            print(bb_repo.get("name"), ": Repository doesn not exist.")
            continue
        bb_branches = bitbucket.get_branches(proj_key, bb_repo.get("name"), details=False)
        for branch in bb_branches:
            gl_branch = gl_repo.branches.get(branch.get('displayId'))

            bb_branch_commits=[data for data in bitbucket.get_commits(proj_key, bb_repo.get("name"),hash_newest=branch.get("latestCommit"))]
    
            bb_dict = {}
            gl_dict = {}   

            gl_branch_commits = gl_repo.commits.list(ref_name=gl_branch.name)


            for i in range(max(len(bb_branch_commits), len(gl_branch_commits))):
 
                try:
                    bb_commit = bb_branch_commits[i]
                    bb_commit_id = bb_commit["id"]
                    bb_message = bb_commit["message"].replace("\n", "")
                    bb_author = bb_commit.get("author").get("displayName")
                    bb_email = bb_commit.get('author').get('emailAddress')
                    bb_author_tp = bb_commit.get('authorTimestamp')
                    bb_dict[bb_commit_id]= [bb_message, bb_author, bb_email, bb_author_tp]
                except:
                    pass

                try:
                    gl_commit = gl_branch_commits[i]
                    gl_comm = gl_commit.__dict__["_attrs"]
                    gl_commit_id = gl_comm['id']
                    gl_message = gl_comm["message"].replace("\n", "").lower()
                    gl_author = gl_comm["author_name"].lower()
                    gl_email = gl_comm['committer_email']
                    if "+00:00" in gl_comm['committed_date']:
                        gitlab_utc = datetime.strptime(gl_comm['committed_date'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
                    else:
                        gitlab_utc = datetime.strptime(gl_comm['committed_date'], '%Y-%m-%dT%H:%M:%S.%f+05:30')
                    gl_author_tp = int(datetime.timestamp(gitlab_utc)*1000)
                    gl_dict[gl_commit_id] = [gl_message, gl_author, gl_email, gl_author_tp]
                except:
                    pass
            report={"commit_id":[],"branch":[] ,"commit_message":[]}#, "difference_location":[]}
            for key, value in bb_dict.items():
                if key not in gl_dict:
                    # print(gl_dict)
                    report["commit_id"].append(key)
                    report["branch"].append(gl_branch.name)
                    report["commit_message"].append(value)
            report=pd.DataFrame(report)

            if len(report):  
                print(report)
            else:
                print("NO DIFFERENCES FOUND")