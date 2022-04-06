from importlib.metadata import requires
from optparse import Values
from reprlib import recursive_repr
from turtle import clear
import tkinter as TK
from weakref import ref
from xxlimited import new
import requests
from requests.auth import HTTPBasicAuth
import gitlab
from atlassian import Bitbucket
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv()

#########**GITLAB AUTH**############

gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))
gl.auth()


#########**BITBUCKET AUTH**############
bitbucket = Bitbucket(
    url=os.getenv("BITBUCKET_URL"),
    username=os.getenv("BITBUCKET_USERNAME"),
    password=os.getenv("BITBUCKET_PASSWORD")
)

#########**FETCH DATA OF BITBUCKET**############
bitbucket_proj=bitbucket.project_list()
gl_projects = gl.projects.list()



for b_proj in bitbucket_proj:
    b_repo = bitbucket.repo_list(b_proj['key'])
    for brepo in b_repo:
        try: 
            gl_repo = gl.projects.list(search=brepo.get("name"))[0]
        except:
            print(brepo.get("name"),"repository does not exist")
            continue
        bb_branches = bitbucket.get_branches(b_proj['key'], brepo.get("name"), details=False)
        bb_files={"file":[]}
        gl_files={"file":[]}
        status={"project":[],"repo":[],"branch":[], "file":[]}
        for branch in bb_branches:
            gl_branch = gl_repo.branches.get(branch.get('displayId')).name
            url="http://localhost:7990/rest/api/1.0/projects/{}/repos/{}/files?at={}".format(b_proj['key'],brepo.get('name'),gl_branch)
            request = requests.get(url,auth=HTTPBasicAuth(os.getenv("BITBUCKET_USERNAME"), os.getenv("BITBUCKET_PASSWORD")))
            new_data = request.json()
            data= new_data['values']
            for details in data:
                bb_files["file"].append(details.split("/")[-1])
            items = gl_repo.repository_tree(path="",recursive=True, all=True, ref=branch['displayId'])
            for item in items:
                if item['type'] != "tree":
                    gl_files["file"].append(item['name'])

            for value in bb_files['file']:
                if value in gl_files['file']:
                    pass
                else:
                    status["project"].append(b_proj.get('name'))
                    status["repo"].append(brepo.get('name'))
                    status["branch"].append(branch['displayId'])
                    status["file"].append(value)
        df=pd.DataFrame(status)
        if os.path.exists("file_status.csv"):
            df.to_csv("file_status.csv", mode="a", header=False, index=False)
        else:
            df.to_csv("file_status.csv",  index=False)
        print(status)
    