from cmath import e
from dotenv import load_dotenv
import json
import os
import gitlab
from gitlab.exceptions import GitlabCreateError
from gitlab.exceptions import GitlabHttpError

load_dotenv()

#---------------
gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))  #Added
gl.auth()
with open('tetsing_file.json') as file:
    data = json.load(file)
    for group_name in data:
        group_name=group_name['Group'].replace(" ", "_")
        try:
            group = gl.groups.create({'name': group_name, 'path': group_name})
        except (GitlabCreateError, GitlabHttpError):
            pass
#----------------


with open('authors20220309.txt') as file:
    for name in file:
        username=name.split("=")[0]
        email_id=name.split("<")[1].strip("<>")
        email_id_new=email_id.split(">")[0]
        full_name=name.split()
        f_name=full_name[2]
        l_name=full_name[3]
        if "unknown" not in email_id_new:
            print(email_id_new)
            try:
                user = gl.users.create({'email': email_id_new.strip(),
                                'force_random_password': True,
                                'username': username.strip(),
                                'name': f_name + " " + l_name})
            except (GitlabCreateError, GitlabHttpError):
                print(e)