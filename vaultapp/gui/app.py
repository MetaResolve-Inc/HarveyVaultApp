import tkinter as tk

from vaultapp.gui.views import ProjectsView
from vaultapp.gui.views import ConfigView
from vaultapp.gui.views import UploadView


class GuiApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Harvey.ai Vault App")

        self.resizable(False, True)

        self.api_key = tk.StringVar()
        self.api_region = tk.StringVar()
        self.selected_project = tk.StringVar()

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self.frames = {}

        for F in (ConfigView, ProjectsView, UploadView):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ConfigView")

        self.withdraw()
        self.update_idletasks()

        pos_x = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        pos_y = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))

        self.geometry(f"+{pos_x}+{pos_y}")

        self.deiconify()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
