from src.messages import msg
from src.gui.widgets import ActionWidget, ConfigWidget, WorkplaceWidget
from tkinter import Frame, Tk
from src.archive import ArchiveManager


class Application(Frame):
    """Fenêtre principale de l'application."""

    def __init__(self, master: Tk):
        super().__init__(master)
        self.manager = ArchiveManager()
        self.actions = ActionWidget(self)
        self.actions.pack()
        self.workplace = WorkplaceWidget(self, self.manager)
        self.workplace.pack()
        self.config = ConfigWidget(self)
        self.config.pack()
        self.pack()


if __name__ == '__main__':
    root = Tk()
    root.title(msg.get('title'))
    app = Application(root)
    app.mainloop()
