import tkinter as tk
from tkinter import ttk

from vaultapp.api import HarveyRegion


class ConfigView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="API Region:").grid(row=0, column=0)

        self.region_combo = ttk.Combobox(self, state="readonly", values=[region.name for region in HarveyRegion], width=10)
        self.region_combo.bind("<<ComboboxSelected>>", lambda _: controller.api_region.set(self.region_combo.get()))
        self.region_combo.grid(row=0, column=1, sticky='w')

        tk.Label(self, text="API Key:").grid(row=1, column=0, sticky='w')

        self.api_key_entry = tk.Entry(self, width=50, show='*')
        self.api_key_entry.grid(row=1, column=1)

        ttk.Button(self, text="Continue", command=lambda: (
            controller.api_key.set(self.api_key_entry.get().strip()),
            controller.show_frame("ProjectsView")
        )).grid(row=2, column=1, sticky='e')
