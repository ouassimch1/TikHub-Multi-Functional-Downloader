"""
Main window layout for TikHub Downloader with multilingual support
"""

import tkinter as tk
import ttkbootstrap as ttk

from downloader.constants import APP_VERSION
from downloader.ui.video_tab import VideoTab
from downloader.ui.user_tab import UserTab
from downloader.ui.batch_tab import BatchTab
from downloader.ui.settings_tab import SettingsTab


class MainWindow:
    """Main window for the TikHub Downloader application"""

    def __init__(self, root, app):
        """Initialize the main window

        Args:
            root: The tkinter root window
            app: The application instance
        """
        self.root = root
        self.app = app
        self.translator = app.translator  # Access the translator from the app

        # Create UI elements
        self._create_widgets()

    def _create_widgets(self):
        """Create all UI components"""
        # App title
        title_label = ttk.Label(
            self.root,
            text=self.translator.translate("main_window", "app_title"),
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=10)

        # Create notebook (tabbed interface)
        self.tab_control = ttk.Notebook(self.root)

        # Create tabs
        self.video_tab = VideoTab(self.tab_control, self.app)
        self.tab_control.add(self.video_tab.frame, text=self.translator.translate("main_window", "video_tab"))

        self.user_tab = UserTab(self.tab_control, self.app)
        self.tab_control.add(self.user_tab.frame, text=self.translator.translate("main_window", "user_tab"))

        self.batch_tab = BatchTab(self.tab_control, self.app)
        self.tab_control.add(self.batch_tab.frame, text=self.translator.translate("main_window", "batch_tab"))

        self.settings_tab = SettingsTab(self.tab_control, self.app)
        self.tab_control.add(self.settings_tab.frame, text=self.translator.translate("main_window", "settings_tab"))

        # Pack the notebook
        self.tab_control.pack(expand=1, fill="both")

        # Create status bar
        self._create_status_bar()

    def _create_status_bar(self):
        """Create the status bar at the bottom of the window"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        # Status text
        self.status_var = tk.StringVar()
        self.status_var.set(self.translator.translate("main_window", "ready_status"))
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT)

        # Version info
        version_label = ttk.Label(status_frame, text=APP_VERSION, anchor=tk.E)
        version_label.pack(side=tk.RIGHT)

    def update_status(self, message):
        """Update the status bar message

        Args:
            message: The status message to display
        """
        self.status_var.set(message)
        self.root.update_idletasks()

    def update_language(self):
        """Update UI text when language changes"""
        # Update app title
        self.root.title(self.translator.translate("app", "welcome_title"))

        # Update main title
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Label) and "Helvetica" in child["font"]:
                child.config(text=self.translator.translate("main_window", "app_title"))
                break

        # Update tab names
        self.tab_control.tab(0, text=self.translator.translate("main_window", "video_tab"))
        self.tab_control.tab(1, text=self.translator.translate("main_window", "user_tab"))
        self.tab_control.tab(2, text=self.translator.translate("main_window", "batch_tab"))
        self.tab_control.tab(3, text=self.translator.translate("main_window", "settings_tab"))

        # Update status if it's the default "Ready" message
        if self.status_var.get() == "Ready":
            self.status_var.set(self.translator.translate("main_window", "ready_status"))

        # Update child tabs if they have update_language method
        for tab in [self.video_tab, self.user_tab, self.batch_tab, self.settings_tab]:
            if hasattr(tab, 'update_language'):
                tab.update_language()
