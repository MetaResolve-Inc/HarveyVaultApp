import logging
import os.path
import tkinter as tk
from itertools import batched
from tkinter import filedialog, ttk, messagebox
from typing import List
from urllib.error import HTTPError

from vaultapp.api import Harvey, HarveyRegion

logger = logging.getLogger(__name__)


class UploadView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #  TODO: Make batch size configurable.
        self.batch_size = 20  # Max 50
        self.file_list: List[str] = []

        tk.Label(self, text="Upload Files").grid(row=0, column=0, sticky='w')

        self.progress_bar = ttk.Progressbar(self)
        self.progress_bar.grid(row=1, column=0, columnspan=4, sticky="ew")

        self.back_button = ttk.Button(self, text="Back", command=lambda: self.handle_back())
        self.back_button.grid(row=2, column=0, sticky='w')

        self.select_button = ttk.Button(self, text="Select Files", command=lambda: self.select_files())
        self.select_button.grid(row=2, column=2, sticky='e')

        self.upload_button = ttk.Button(self, text="Upload Files", command=lambda: self.upload_files(),
                                        state="disabled")
        self.upload_button.grid(row=2, column=3, sticky='e')

    def select_files(self):
        self.file_list = list(filedialog.askopenfilenames(title="Select files to upload", filetypes=(
            ("All files", "*.*"),
            ("PDF Files", "*.pdf"),
            ("Word Documents", "*.docx"),
        )))
        if len(self.file_list) > 0:
            self.upload_button.configure(text=f"Upload {len(self.file_list)} Files", state="normal")
        else:
            self.upload_button.configure(text="Upload Files", state="disabled")

    def _wait_for(self, seconds):
        flag = tk.IntVar()
        self.after(seconds * 1000, flag.set, 1)
        self.wait_variable(flag)

    def _reset_upload_ui(self):
        self.progress_bar.configure(maximum=100)
        self.progress_bar.step(100)
        self.back_button.configure(state="normal")
        self.select_button.configure(state="normal")
        self.upload_button.configure(text="Upload Files", state="normal")

    def upload_files(self):
        if len(self.file_list) == 0:
            messagebox.showerror("Error", "No files selected.")
            return

        logger.info(f"Starting upload to project id {self.controller.selected_project.get()}.")

        self.back_button.configure(state="disabled")
        self.select_button.configure(state="disabled")
        self.upload_button.configure(text="Uploading...", state="disabled")

        batched_files = list(batched(self.file_list, self.batch_size))

        self.progress_bar.configure(maximum=len(batched_files))

        harvey = Harvey(self.controller.api_key.get(), HarveyRegion[self.controller.api_region.get()].value)

        logger.info(f"Uploading {len(self.file_list)} files in {len(batched_files)} batches.")

        uploaded_files = []

        for i, batch in enumerate(batched_files):
            self.progress_bar.step(i + 0.9)

            batched_paths = [os.path.basename(file) for file in batch]

            is_uploading = True
            while is_uploading:
                try:
                    logger.info(f"Uploading batch {i + 1} of {len(batched_files)} with {len(batch)} files.")
                    response = harvey.upload_files(self.controller.selected_project.get(), list(batch), batched_paths,
                                                   "skip")
                    uploaded_files.extend(response["file_ids"])
                    is_uploading = False
                except HTTPError as e:
                    if e.response.status_code == 429:
                        retry_after = e.response.headers['Retry-After']
                        wait_seconds = (int(retry_after) if retry_after else 60) + 2
                        logger.warning(
                            f"Rate limited by Harvey API for {retry_after + " seconds" if retry_after else "an unknown amount of time"}.")
                        logger.warning(f"Waiting for {wait_seconds} seconds before trying again.")
                        self._wait_for(wait_seconds)
                    else:
                        messagebox.showerror("Error", f"An error occurred while uploading files: {e}")
                        self._reset_upload_ui()
                        return

        # Done uploading. Reset UI.
        self._reset_upload_ui()
        messagebox.showinfo("Upload Complete", f"Successfully uploaded {len(uploaded_files)} files.")

    def handle_back(self):
        self.controller.show_frame("ProjectsView")
