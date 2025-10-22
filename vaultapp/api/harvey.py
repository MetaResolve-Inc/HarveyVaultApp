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

    def upload_files(self, project, in_files: List[str], in_paths: List[str], duplicate_mode: Literal["skip", "replace"]):
        if len(in_files) != len(in_paths):
            logger.error(f"Attempted to upload {len(in_files)} files but {len(in_paths)} paths were provided.")
            raise ValueError("Number of files and project paths must be the same")

        if len(in_files) > 50:
            raise ValueError("Maximum of 50 files can be uploaded at a time")

        files = [("files", open(file, "rb")) for file in in_files]

        payload = {
            "file_paths": in_paths,
            "duplicate_mode": duplicate_mode,
        }
        data = self.requester.exec(f"/vault/upload_files/{project}", HTTPMethod.POST, data=payload, files=files)
        return data["file_ids"]
