import tkinter as tk
from tkinter import ttk

from vaultapp.api import Harvey, HarveyRegion


class ProjectsView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.page = 1

        # Add widgets here
        tk.Label(self, text="Projects").grid(row=0, column=0)
        self.project_list = ttk.Treeview(self, columns=("name", "creator", "files", "size"), show="headings")
        self.project_list.heading("name", text="Project Name")
        self.project_list.heading("creator", text="Creator")
        self.project_list.heading("files", text="Files")
        self.project_list.heading("size", text="Size")

        self.project_list.column("name", anchor='w', width=250)
        self.project_list.column("creator", anchor='w', width=200)
        self.project_list.column("files", anchor='w', width=125)
        self.project_list.column("size", anchor='w', width=125)

        self.project_list.grid(row=1, column=0)

        #self.load_projects()

        # TODO: Pagination buttons

        # TODO: Handle file uploads for selected project

    def load_projects(self):
        harvey = Harvey(self.controller.api_key.get(), HarveyRegion[self.controller.api_region.get()].value)
        projects_list = harvey.get_projects(self.page, per_page=25)

        # TODO: Parse out project details and populate the treeview
