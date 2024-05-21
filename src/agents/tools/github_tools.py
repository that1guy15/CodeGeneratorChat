import os
import requests
from typing_extensions import Annotated

def create_github_gist(
        filename: Annotated[str, "The name of the file to include in the gist."],
        content: Annotated[str, "The content of the file."],
        description: Annotated[str, "A description of the gist."],
        public: Annotated[bool, "Whether the gist is public or not."]
) -> Annotated[str, "The html_url of the created gist."]:
    url = "https://api.github.com/gists"
    headers = {
        "Authorization": f"token {os.environ.get('GITHUB_API_KEY')}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "files": {
            filename: {
                "content": content
            }
        },
        "description": description,
        "public": public
    }

    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        return response.json()['html_url']
    else:
        return f"There was an issue creating the gist. Error: {response.json}"
