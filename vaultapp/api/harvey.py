import logging
from http import HTTPMethod
from typing import List, Dict, Any, Literal

from vaultapp.api.request import HarveyRequest

logger = logging.getLogger(__name__)

class Harvey:
    def __init__(self, auth_key, region):
        self.requester = HarveyRequest(auth_key, region)


    def get_paginated_projects(self, page=1, per_page=100) -> Dict[str, Any]:
        data = self.requester.exec(f"/vault/workspace/projects?page={page}&per_page={per_page}", HTTPMethod.GET)
        return data["response"]["content"]

    def get_project_files(self, project_id) -> List[str]:
        data = self.requester.exec(f"/vault/get_metadata/{project_id}", HTTPMethod.GET)
        return data["file_ids"]

    def upload_files(self, project, files: List[str], paths: List[str], duplicate_mode: Literal["skip", "replace"]):
        if len(files) != len(paths):
            logger.error(f"Attempted to upload {len(files)} files but {len(paths)} paths were provided.")
            raise ValueError("Number of files and project paths must be the same")

        batch_size = 50
        responses = []

        for i in range(0, len(files), batch_size):
            batch_files = files[i:i+batch_size]
            batch_paths = paths[i:i+batch_size]
            data = {
                "files": batch_files,
                "file_paths": batch_paths,
                "duplicate_mode": duplicate_mode,
            }
            response = self.requester.exec(f"/vault/upload_files/{project}", HTTPMethod.POST, data=data)
            responses.append(response)

        return responses
