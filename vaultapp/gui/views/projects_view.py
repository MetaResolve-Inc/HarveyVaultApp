import tkinter as tk
from tkinter import ttk, messagebox

from requests import HTTPError

from vaultapp.api import Harvey, HarveyRegion


def _format_size(size):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"):
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}Yi{size}"

class ProjectsView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.page = 1
        self.per_page = 40
        self.total_pages = 1

        tk.Label(self, text="Projects").grid(row=0, column=0, sticky='w')

        self.project_list = ttk.Treeview(self, show="headings", selectmode="browse", height=self.per_page, columns=(
            "id",
            "name",
            "creator",
            "files",
            "size",
            "created",
        ))

        self.project_list.heading("name", text="Project Name")
        self.project_list.heading("creator", text="Creator")
        self.project_list.heading("files", text="Files")
        self.project_list.heading("size", text="Size")
        self.project_list.heading("created", text="Created")

        self.project_list.column("id", width=0, stretch=tk.NO)
        self.project_list.column("name", anchor='w', width=250)
        self.project_list.column("creator", anchor='w', width=200)
        self.project_list.column("files", anchor='w', width=100)
        self.project_list.column("size", anchor='w', width=100)
        self.project_list.column("created", anchor='w', width=200)

        self.project_list.grid(row=1, column=0, sticky="nsew", columnspan=4)

        ttk.Button(self, text="Back", command=lambda: self.handle_back()).grid(row=2, column=0, sticky='w')

        ttk.Button(self, text="<-", command=lambda: self.load_projects(back=True)).grid(row=2, column=1)
        ttk.Button(self, text="->", command=lambda: self.load_projects()).grid(row=2, column=2)

        ttk.Button(self, text="Continue", command=lambda: self.handle_continue()).grid(row=2, column=3, sticky='e')

    def load_projects(self, back=False):
        harvey = Harvey(self.controller.api_key.get(), HarveyRegion[self.controller.api_region.get()].value)

        if len(self.project_list.get_children()) > 0:
            if back and self.page > 1:
                self.page = self.page - 1
            if not back and self.page < self.total_pages:
                self.page = self.page + 1
            if not back and self.page >= self.total_pages:
                self.page = self.total_pages

        try:
            paginated_projects = harvey.get_paginated_projects(self.page, per_page=self.per_page)
        except HTTPError as e:
            if e.response.status_code == 429:
                wait_time = int(e.response.headers['Retry-After']) if e.response.headers['Retry-After'] else 60
                messagebox.showerror(
                    "Rate Limited",
                    f"The harvey API rate limit has been reached. Please try again in {wait_time} seconds."
                )
                return
            messagebox.showerror("Error", f"Error loading projects: {e}")
            return

        self.total_pages = paginated_projects["pagination"]["total_pages"]

        # Clear the treeview
        self.project_list.delete(*self.project_list.get_children())

        for project in paginated_projects["projects"]:
            self.project_list.insert("", "end", values=(
                project["id"],
                project["name"],
                project["creator_email"],
                project["files_count"],
                _format_size(project["size_bytes"]),
                project["created_at"],
            ))

    def handle_continue(self):
        focus = self.project_list.focus()
        if focus == "":
            messagebox.showerror("Error", "No project selected")
            return

        project_id = self.project_list.item(focus)["values"][0].strip()
        self.controller.selected_project.set(project_id)

        self.controller.show_frame("UploadView")

    def handle_back(self):
        self.controller.show_frame("ConfigView")
