from cgi import print_arguments
from logging import exception
from traceback import print_tb
import gitlab
from atlassian import Bitbucket
from dotenv import load_dotenv
from numpy import append, diff
import pandas as pd
from gitlab.exceptions import GitlabGetError
import os

load_dotenv()

gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))
gl.auth()

bitbucket = Bitbucket(
    url=os.getenv("BITBUCKET_URL"),
    username=os.getenv("BITBUCKET_USERNAME"),
    password=os.getenv("BITBUCKET_PASSWORD")
)


bb_projects = bitbucket.project_list()

for project in bb_projects:
    repositories = bitbucket.repo_list(project["key"])

    for repo in repositories:
        bb_tag_dict={}
        gl_tag_dict={}
        try:
            gl_repo = gl.projects.list(search=repo.get("name"))[0]
        except:
            pass
        tags=bitbucket.get_tags(project['key'], repository_slug= repo['slug'])
        report={"project":[],"repo":[],"tag":[],"status":[]}
        for tag in tags:     
            bb_tag_dict[repo['slug']] = bb_tag_dict.get(repo['slug'], [])
            bb_tag_dict[repo['slug']].append(tag['displayId'])
            try:
                if tag["displayId"] != gl_repo.tags.get(id=tag['displayId']).name:
                    print(tag['displayId'])
                else:
                    report["status"].append("success")
                    report["repo"].append(repo['slug'])
                    report['tag'].append(tag['displayId'])
                    report['project'].append(project['name'])        
            except gitlab.GitlabGetError:
                report["status"].append("fail")
                report["repo"].append(repo['slug'])
                report['tag'].append(tag['displayId'])
                report['project'].append(project['name'])
        df=pd.DataFrame(report)
        if os.path.exists("tags_status.csv"):
            df.to_csv("tags_status.csv", mode="a", header=False, index=False)
        else:
            df.to_csv("tags_status.csv",  index=False)