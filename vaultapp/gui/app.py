import tkinter as tk

from vaultapp.gui.views.projects_view import ProjectsView
from vaultapp.gui.views.config_view import ConfigView


class GuiApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Harvey.ai Vault App")
        #self.geometry("850x600")

        self.resizable(False, True)

        self.api_key = tk.StringVar()
        self.api_region = tk.StringVar(value="NA")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self.frames = {}

        for F in (ConfigView, ProjectsView):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ConfigView")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
