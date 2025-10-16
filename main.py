import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests


class HarveyVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Harvey.ai Vault Manager")
        self.root.geometry("950x750")

        self.api_key = ""
        self.base_url = "https://api.harvey.ai/v1"
        self.region = "US"  # Default region

        self.setup_ui()

    def setup_ui(self):
        # API Key Frame
        api_frame = ttk.LabelFrame(self.root, text="API Configuration", padding=10)
        api_frame.pack(fill="x", padx=10, pady=5)

        # Region selection
        region_frame = ttk.Frame(api_frame)
        region_frame.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        ttk.Label(region_frame, text="Region:").pack(side="left", padx=5)
        self.region_var = tk.StringVar(value="US")
        region_combo = ttk.Combobox(region_frame, textvariable=self.region_var, values=["US", "EU", "AU"],
                                    state="readonly", width=10)
        region_combo.pack(side="left", padx=5)
        region_combo.bind("<<ComboboxSelected>>", self.update_region)

        ttk.Label(region_frame, text="API Endpoint:").pack(side="left", padx=(20, 5))
        self.endpoint_label = ttk.Label(region_frame, text=self.base_url, foreground="blue")
        self.endpoint_label.pack(side="left", padx=5)

        # API Key
        ttk.Label(api_frame, text="API Key:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.api_key_entry = ttk.Entry(api_frame, width=50, show="*")
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(api_frame, text="Set API Key", command=self.set_api_key).grid(row=1, column=2, padx=5, pady=5)

        # Show/Hide API Key
        self.show_key_var = tk.BooleanVar()
        ttk.Checkbutton(api_frame, text="Show API Key", variable=self.show_key_var,
                        command=self.toggle_api_key_visibility).grid(row=1, column=3, padx=5, pady=5)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Upload Tab
        self.upload_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.upload_frame, text="Upload Document")
        self.setup_upload_tab()

        # List Files Tab
        self.list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.list_frame, text="List Files")
        self.setup_list_tab()

        # File Details Tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="File Details")
        self.setup_details_tab()

        # Project Management Tab
        self.project_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.project_frame, text="Projects")
        self.setup_project_tab()

        # Status Bar
        self.status_var = tk.StringVar(value="Ready - Please set your API key")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.pack(fill="x", side="bottom", padx=10, pady=5)

    def update_region(self, event=None):
        region = self.region_var.get()
        if region == "EU":
            self.base_url = "https://eu.api.harvey.ai/v1"
        elif region == "AU":
            self.base_url = "https://au.api.harvey.ai/v1"
        else:
            self.base_url = "https://api.harvey.ai/v1"

        self.endpoint_label.config(text=self.base_url)
        self.status_var.set(f"Region set to {region} - Endpoint: {self.base_url}")

    def toggle_api_key_visibility(self):
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def setup_upload_tab(self):
        # File Selection
        file_frame = ttk.LabelFrame(self.upload_frame, text="Select File", padding=10)
        file_frame.pack(fill="x", padx=10, pady=10)

        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side="left", padx=5)

        # Options
        options_frame = ttk.LabelFrame(self.upload_frame, text="Upload Options", padding=10)
        options_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(options_frame, text="Project ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.project_id_entry = ttk.Entry(options_frame, width=40)
        self.project_id_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(options_frame, text="(Group by matter/client/team)", font=("Arial", 8)).grid(row=0, column=2,
                                                                                               sticky="w", padx=5)

        ttk.Label(options_frame, text="Display Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.display_name_entry = ttk.Entry(options_frame, width=40)
        self.display_name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(options_frame, text="File Path (relative):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.file_path_entry = ttk.Entry(options_frame, width=40)
        self.file_path_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(options_frame, text="(e.g., folder/subfolder/)", font=("Arial", 8)).grid(row=2, column=2, sticky="w",
                                                                                           padx=5)

        ttk.Label(options_frame, text="Tags (comma-separated):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.tags_entry = ttk.Entry(options_frame, width=40)
        self.tags_entry.grid(row=3, column=1, padx=5, pady=5)

        # Upload Button
        ttk.Button(self.upload_frame, text="Upload to Vault", command=self.upload_file).pack(pady=20)

        # Response Area
        response_frame = ttk.LabelFrame(self.upload_frame, text="Response", padding=10)
        response_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.upload_response = scrolledtext.ScrolledText(response_frame, height=10)
        self.upload_response.pack(fill="both", expand=True)

    def setup_list_tab(self):
        # Controls
        controls_frame = ttk.Frame(self.list_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(controls_frame, text="Refresh File List", command=self.list_files).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Delete Selected", command=self.delete_file).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="View Details", command=self.view_selected_details).pack(side="left", padx=5)

        # Treeview for files
        tree_frame = ttk.Frame(self.list_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.file_tree = ttk.Treeview(tree_frame, columns=("Name", "Size", "Type", "Created"), show="tree headings")
        self.file_tree.heading("#0", text="ID")
        self.file_tree.heading("Name", text="Display Name")
        self.file_tree.heading("Size", text="Size")
        self.file_tree.heading("Type", text="Type")
        self.file_tree.heading("Created", text="Created")

        self.file_tree.column("#0", width=200)
        self.file_tree.column("Name", width=200)
        self.file_tree.column("Size", width=100)
        self.file_tree.column("Type", width=100)
        self.file_tree.column("Created", width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_details_tab(self):
        # File ID Input
        id_frame = ttk.Frame(self.details_frame)
        id_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(id_frame, text="File ID:").pack(side="left", padx=5)
        self.file_id_entry = ttk.Entry(id_frame, width=40)
        self.file_id_entry.pack(side="left", padx=5)
        ttk.Button(id_frame, text="Get Details", command=self.get_file_details).pack(side="left", padx=5)

        # Details Display
        details_display_frame = ttk.LabelFrame(self.details_frame, text="File Information", padding=10)
        details_display_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.details_text = scrolledtext.ScrolledText(details_display_frame, height=20)
        self.details_text.pack(fill="both", expand=True)

    def setup_project_tab(self):
        # Project ID Input
        project_input_frame = ttk.Frame(self.project_frame)
        project_input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(project_input_frame, text="Project ID:").pack(side="left", padx=5)
        self.project_metadata_entry = ttk.Entry(project_input_frame, width=40)
        self.project_metadata_entry.pack(side="left", padx=5)
        ttk.Button(project_input_frame, text="Get Project Metadata", command=self.get_project_metadata).pack(
            side="left", padx=5)

        # Project Metadata Display
        metadata_frame = ttk.LabelFrame(self.project_frame, text="Project Information", padding=10)
        metadata_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.project_metadata_text = scrolledtext.ScrolledText(metadata_frame, height=20)
        self.project_metadata_text.pack(fill="both", expand=True)

        # Delete Project Button
        delete_frame = ttk.Frame(self.project_frame)
        delete_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(delete_frame, text="Delete Project", command=self.delete_project).pack(side="left", padx=5)
        ttk.Label(delete_frame, text="(Deletes all files in the project)", foreground="red", font=("Arial", 9)).pack(
            side="left", padx=5)

    def set_api_key(self):
        self.api_key = self.api_key_entry.get().strip()
        if self.api_key:
            messagebox.showinfo("Success",
                                "API Key set successfully!\n\nNote: Contact your Customer Success Manager to obtain your organization's bearer token.")
            self.status_var.set(f"API Key configured - Region: {self.region_var.get()}")
        else:
            messagebox.showwarning("Warning", "Please enter a valid API key")

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select a file to upload",
            filetypes=[("All Files", "*.*"), ("PDF Files", "*.pdf"), ("Word Documents", "*.docx"),
                ("Text Files", "*.txt")])
        if filename:
            self.file_path_var.set(filename)

    def make_request(self, method, endpoint, **kwargs):
        """Helper method to make API requests with proper error handling"""
        if not self.api_key:
            raise Exception("API key not set. Please configure your API key first.")

        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.api_key}'

        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)

        # Handle different status codes
        if response.status_code == 401:
            raise Exception("Unauthorized - Invalid API key. Please check your credentials.")
        elif response.status_code == 404:
            raise Exception("Not Found - The requested resource does not exist.")
        elif response.status_code == 400:
            error_msg = response.json().get('error', 'Bad Request - Missing or invalid input')
            raise Exception(error_msg)
        elif response.status_code == 500:
            raise Exception("Internal Server Error - Please try again later.")

        response.raise_for_status()
        return response

    def upload_file(self):
        file_path = self.file_path_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return

        self.status_var.set("Uploading file...")
        self.upload_response.delete(1.0, tk.END)

        try:
            # Prepare file
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}

                # Prepare data
                data = {}

                project_id = self.project_id_entry.get().strip()
                if project_id:
                    data['project_id'] = project_id

                display_name = self.display_name_entry.get().strip()
                if display_name:
                    data['display_name'] = display_name

                file_path_relative = self.file_path_entry.get().strip()
                if file_path_relative:
                    data['file_paths'] = file_path_relative

                tags = self.tags_entry.get().strip()
                if tags:
                    data['tags'] = [tag.strip() for tag in tags.split(',')]

                # Make request
                response = self.make_request('POST', '/vault/files', files=files, data=data)
                result = response.json()

                self.upload_response.insert(tk.END, json.dumps(result, indent=2))
                self.status_var.set("File uploaded successfully! (Status: 201)")
                messagebox.showinfo("Success",
                                    f"File uploaded!\n\nID: {result.get('id', 'N/A')}\nProject: {project_id or 'Default'}")

        except Exception as e:
            self.upload_response.insert(tk.END, f"Error: {str(e)}")
            self.status_var.set("Upload failed")
            messagebox.showerror("Error", f"Upload failed:\n{str(e)}")

    def list_files(self):
        self.status_var.set("Fetching files...")

        try:
            response = self.make_request('GET', '/vault/files')
            result = response.json()

            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)

            # Add files to tree
            for file in result.get('files', []):
                self.file_tree.insert("", "end", text=file.get('id', 'N/A'),
                                      values=(file.get('display_name', 'N/A'), f"{file.get('size_bytes', 0)} bytes",
                                              file.get('mime_type', 'N/A'), file.get('created_at', 'N/A')))

            self.status_var.set(f"Loaded {len(result.get('files', []))} files")

        except Exception as e:
            self.status_var.set("Failed to load files")
            messagebox.showerror("Error", f"Failed to list files:\n{str(e)}")

    def delete_file(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to delete")
            return

        file_id = self.file_tree.item(selected[0])['text']

        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete file:\n{file_id}?"):
            return

        try:
            response = self.make_request('DELETE', f'/vault/files/{file_id}')

            self.status_var.set("File deleted successfully (Status: 200)")
            messagebox.showinfo("Success", "File deleted successfully!")
            self.list_files()  # Refresh list

        except Exception as e:
            self.status_var.set("Delete failed")
            messagebox.showerror("Error", f"Failed to delete file:\n{str(e)}")

    def view_selected_details(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to view details")
            return

        file_id = self.file_tree.item(selected[0])['text']
        self.file_id_entry.delete(0, tk.END)
        self.file_id_entry.insert(0, file_id)
        self.notebook.select(2)  # Switch to details tab
        self.get_file_details()

    def get_file_details(self):
        file_id = self.file_id_entry.get().strip()
        if not file_id:
            messagebox.showwarning("Warning", "Please enter a file ID")
            return

        self.status_var.set("Fetching file details...")
        self.details_text.delete(1.0, tk.END)

        try:
            response = self.make_request('GET', f'/vault/files/{file_id}')
            result = response.json()

            self.details_text.insert(tk.END, json.dumps(result, indent=2))
            self.status_var.set("File details loaded (Status: 200)")

        except Exception as e:
            self.details_text.insert(tk.END, f"Error: {str(e)}")
            self.status_var.set("Failed to load details")
            messagebox.showerror("Error", f"Failed to get file details:\n{str(e)}")

    def get_project_metadata(self):
        project_id = self.project_metadata_entry.get().strip()
        if not project_id:
            messagebox.showwarning("Warning", "Please enter a project ID")
            return

        self.status_var.set("Fetching project metadata...")
        self.project_metadata_text.delete(1.0, tk.END)

        try:
            response = self.make_request('GET', f'/vault/get_metadata/{project_id}')
            result = response.json()

            self.project_metadata_text.insert(tk.END, json.dumps(result, indent=2))
            self.status_var.set(f"Project metadata loaded (Status: 200)")

        except Exception as e:
            self.project_metadata_text.insert(tk.END, f"Error: {str(e)}")
            self.status_var.set("Failed to load project metadata")
            messagebox.showerror("Error", f"Failed to get project metadata:\n{str(e)}")

    def delete_project(self):
        project_id = self.project_metadata_entry.get().strip()
        if not project_id:
            messagebox.showwarning("Warning", "Please enter a project ID to delete")
            return

        if not messagebox.askyesno("Confirm Project Deletion",
                                   f"Are you sure you want to delete project:\n{project_id}\n\nThis will delete ALL files in this project!",
                                   icon='warning'):
            return

        try:
            response = self.make_request('DELETE', f'/vault/projects/{project_id}')

            self.status_var.set("Project deleted successfully (Status: 200)")
            self.project_metadata_text.delete(1.0, tk.END)
            self.project_metadata_text.insert(tk.END,
                                              "Project deleted successfully.\n\nVerify the project no longer appears in your workspace projects list.")
            messagebox.showinfo("Success", "Project and all associated files deleted successfully!")

        except Exception as e:
            self.status_var.set("Delete project failed")
            messagebox.showerror("Error", f"Failed to delete project:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HarveyVaultApp(root)
    root.mainloop()
