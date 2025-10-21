import logging

from vaultapp.gui import GuiApp


logger = logging.getLogger("HarveyVaultApp")

def main() -> None:
    logging.basicConfig(level=logging.INFO, filename="harvey.log")
    app = GuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
