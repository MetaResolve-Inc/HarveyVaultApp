import logging

from vaultapp.gui import GuiApp


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    app = GuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
