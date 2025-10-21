import logging
import logging.handlers
from sys import platform

from vaultapp.gui import GuiApp

logger = logging.getLogger("HarveyVaultApp")

# Alternate bootstrapper for pyinstaller.
if __name__ == "__main__":
    if platform == "darwin":
        handler = logging.handlers.SysLogHandler(address="/var/run/syslog")
        logging.basicConfig(level=logging.INFO, handlers=[handler])
    else:
        logging.basicConfig(level=logging.INFO, filename="harvey.log")

    app = GuiApp()
    app.mainloop()
