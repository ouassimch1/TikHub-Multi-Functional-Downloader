"""
Enhanced batch download tab for TikHub Downloader with modern UI, improved UX and multithreaded downloads
"""

import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import ttkbootstrap as ttk
try:
    from ttkbootstrap.constants import *
    from ttkbootstrap.toast import ToastNotification
    from ttkbootstrap.scrolled import ScrolledText
    HAS_TTKBOOTSTRAP_EXTENSIONS = True
except ImportError:
    # Fallback if extended components are not available
    HAS_TTKBOOTSTRAP_EXTENSIONS = False
import re

from downloader.core.downloader import VideoDownloader
from downloader.utils.utils import extract_urls_from_text, open_folder
from downloader.utils.logger import logger_instance


class BatchTab:
    """Batch download tab UI and functionality with multithreaded download support"""

    def __init__(self, parent, app):
        """Initialize the batch download tab

        Args:
            parent: Parent widget
            app: Application instance
        """
        self.app = app
        self.frame = ttk.Frame(parent)
        self.translator = app.translator  # Access translator from app

        # Download state tracking
        self.is_downloading = False
        self.download_thread = None
        self.stop_download = False
        self.paused = False

        # Thread coordination
        self.result_queue = queue.Queue()
        self.lock = threading.Lock()

        # Download statistics
        self.completed = 0
        self.failed = 0
        self.successful_urls = []
        self.failed_urls = []
        self.download_times = []
        self.start_time = None
        self.currently_downloading = set()

        # Set the logger
        self.logger = logger_instance

        # Default values
        self.max_workers = 5  # Default number of concurrent downloads

        # Safe theme color initialization
        self.theme_color = "#007bff"  # Default primary blue
        try:
            if hasattr(app, 'style') and hasattr(app.style, 'colors'):
                self.theme_color = app.style.colors.get("primary", "#007bff")
            elif hasattr(app, 'root') and isinstance(app.root, ttk.Window):
                # Try to get color from ttk theme
                self.theme_color = app.root.style.colors.get("primary", "#007bff")
        except Exception:
            # Fallback to default if any error occurs
            pass

        # Create icons dictionary
        self._init_icons()

        # Create UI components
        self._create_widgets()

    def _init_icons(self):
        """Initialize icons dictionary (using Unicode symbols as fallback)"""
        self.icons = {
            "paste": "📋",
            "clear": "🗑️",
            "extract": "🔍",
            "folder": "📁",
            "download": "⬇️",
            "stop": "⏹️",
            "pause": "⏸️",
            "resume": "▶️",
            "settings": "⚙️",
            "info": "ℹ️",
            "warning": "⚠️",
            "success": "✅",
            "error": "❌"
        }

        # Try to load actual icons if they exist
        try:
            # Check if tk_image exists in app
            if hasattr(self.app, 'tk_images') and isinstance(self.app.tk_images, dict):
                for key in self.icons.keys():
                    if key in self.app.tk_images:
                        self.icons[key] = self.app.tk_images[key]
        except Exception:
            pass  # Fallback to Unicode symbols

    def _create_widgets(self):
        """Create tab UI components"""
        # Main container with two-column layout
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left side - URL input and controls
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 7))

        # Right side - Downloads status and statistics
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(7, 0))

        # ----- LEFT SIDE -----

        # Header with title and URL counter
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        title_label = ttk.Label(
            header_frame,
            text=self.translator.translate("batch_tab", "batch_links"),
            font=("", 11, "bold")
        )
        title_label.pack(side=tk.LEFT)

        self.url_count_var = tk.StringVar(value="0 URLs")
        url_count_label = ttk.Label(header_frame, textvariable=self.url_count_var)
        url_count_label.pack(side=tk.RIGHT)

        # URL input with syntax highlighting
        input_frame = ttk.Frame(left_frame, bootstyle=SECONDARY)
        input_frame.pack(fill=tk.BOTH, expand=True)

        # Use ScrolledText for cleaner scrollbar integration
        self.batch_text = ScrolledText(
            input_frame,
            height=10,
            wrap=tk.WORD,
            autohide=True
        )
        self.batch_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Bind URL validation and highlighting
        self.batch_text.bind("<KeyRelease>", self._highlight_urls)

        # Control buttons frame with icon buttons
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # Create modern button group
        btn_group = ttk.Frame(control_frame)
        btn_group.pack(side=tk.LEFT)

        # Buttons with icons and tooltips
        buttons_config = [
            (self.translator.translate("batch_tab", "paste_button"), self._paste_to_batch, "paste",
             self.translator.translate("batch_tab", "paste_tooltip")),
            (self.translator.translate("batch_tab", "clear_button"),
             lambda: [self.batch_text.delete(1.0, tk.END), self._count_urls()], "clear",
             self.translator.translate("batch_tab", "clear_tooltip")),
            (self.translator.translate("batch_tab", "extract_urls_button"), self._extract_urls, "extract",
             self.translator.translate("batch_tab", "extract_tooltip"))
        ]

        for text, command, icon, tooltip in buttons_config:
            btn = ttk.Button(
                btn_group,
                text=f" {text}",
                image=self.icons[icon] if isinstance(self.icons[icon], tk.PhotoImage) else None,
                compound=tk.LEFT,
                command=command,
                bootstyle=OUTLINE
            )
            if not isinstance(self.icons[icon], tk.PhotoImage):
                btn.config(text=f"{self.icons[icon]} {text}")

            btn.pack(side=tk.LEFT, padx=2)
            self._create_tooltip(btn, tooltip)

        # Extract from file button
        file_btn = ttk.Button(
            control_frame,
            text=self.translator.translate("batch_tab", "extract_from_file"),
            command=self._extract_from_file,
            bootstyle=(OUTLINE, INFO)
        )
        file_btn.pack(side=tk.RIGHT)
        self._create_tooltip(
            file_btn,
            self.translator.translate("batch_tab", "extract_from_file_tooltip")
        )

        # Download settings panel
        settings_panel = ttk.LabelFrame(
            left_frame,
            text=self.translator.translate("batch_tab", "download_settings"),
            bootstyle=SECONDARY
        )
        settings_panel.pack(fill=tk.X, pady=(10, 5))

        # Settings grid
        settings_grid = ttk.Frame(settings_panel)
        settings_grid.pack(fill=tk.X, padx=10, pady=10)

        # Row 1: Save location
        save_location_frame = ttk.Frame(settings_grid)
        save_location_frame.pack(fill=tk.X, pady=2)

        self.custom_save_var = tk.BooleanVar(value=False)
        custom_save_check = ttk.Checkbutton(
            save_location_frame,
            text=self.translator.translate("batch_tab", "custom_save_location"),
            variable=self.custom_save_var,
            command=self._toggle_custom_save
        )
        custom_save_check.pack(side=tk.LEFT)

        self.location_display = ttk.Label(
            save_location_frame,
            text=self.app.download_path,
            font=("", 9),
            foreground="gray"
        )
        self.location_display.pack(side=tk.RIGHT)

        # Row 2: Thread count and quality settings
        thread_frame = ttk.Frame(settings_grid)
        thread_frame.pack(fill=tk.X, pady=5)

        # Thread count with visual slider
        thread_label = ttk.Label(
            thread_frame,
            text=self.translator.translate("batch_tab", "concurrent_downloads")
        )
        thread_label.pack(side=tk.LEFT)

        self.thread_count_var = tk.IntVar(value=self.max_workers)

        thread_slider = ttk.Scale(
            thread_frame,
            from_=1,
            to=20,
            variable=self.thread_count_var,
            command=lambda val: self.thread_count_display.config(text=f"{int(float(val))}")
        )
        thread_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.thread_count_display = ttk.Label(thread_frame, text=str(self.max_workers))
        self.thread_count_display.pack(side=tk.LEFT, padx=(0, 10))

        # Action buttons
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill=tk.X, pady=10)

        # Download button
        self.download_button = ttk.Button(
            action_frame,
            text=self.translator.translate("batch_tab", "start_batch_download"),
            command=self._batch_download,
            bootstyle=SUCCESS
        )
        self.download_button.pack(side=tk.LEFT, padx=(0, 5))

        # Control buttons
        control_btns_frame = ttk.Frame(action_frame)
        control_btns_frame.pack(side=tk.LEFT)

        # Pause button
        self.pause_button = ttk.Button(
            control_btns_frame,
            text=self.translator.translate("batch_tab", "pause_download"),
            command=self._toggle_pause,
            state=tk.DISABLED,
            bootstyle=WARNING
        )
        self.pause_button.pack(side=tk.LEFT, padx=2)

        # Stop button
        self.stop_button = ttk.Button(
            control_btns_frame,
            text=self.translator.translate("batch_tab", "stop_download"),
            command=self._stop_download,
            state=tk.DISABLED,
            bootstyle=DANGER
        )
        self.stop_button.pack(side=tk.LEFT, padx=2)

        # ----- RIGHT SIDE -----

        # Progress panel
        progress_panel = ttk.LabelFrame(
            right_frame,
            text=self.translator.translate("batch_tab", "download_progress"),
            padding=10,
            bootstyle=PRIMARY
        )
        progress_panel.pack(fill=tk.X, pady=(0, 10))

        # Progress info
        progress_info_frame = ttk.Frame(progress_panel)
        progress_info_frame.pack(fill=tk.X, pady=(0, 10))

        # Status and count
        self.status_var = tk.StringVar(value=self.translator.translate("batch_tab", "status_ready"))
        status_label = ttk.Label(
            progress_info_frame,
            textvariable=self.status_var,
            font=("", 10, "bold")
        )
        status_label.pack(side=tk.LEFT)

        # Progress counter
        self.progress_var = tk.StringVar(value="0/0")
        progress_label = ttk.Label(
            progress_info_frame,
            textvariable=self.progress_var,
            font=("", 10, "bold")
        )
        progress_label.pack(side=tk.RIGHT)

        # Progress bar with percentage
        progress_bar_frame = ttk.Frame(progress_panel)
        progress_bar_frame.pack(fill=tk.X)

        self.progress = ttk.Progressbar(
            progress_bar_frame,
            maximum=100,
            variable=tk.DoubleVar(value=0),
            bootstyle=(SUCCESS, STRIPED)
        )
        self.progress.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.percent_var = tk.StringVar(value="0%")
        percent_label = ttk.Label(
            progress_bar_frame,
            textvariable=self.percent_var,
            width=5
        )
        percent_label.pack(side=tk.RIGHT, padx=(5, 0))

        # Stats frame
        stats_frame = ttk.Frame(progress_panel)
        stats_frame.pack(fill=tk.X, pady=(10, 0))

        # Left column - time stats
        time_stats = ttk.Frame(stats_frame)
        time_stats.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Elapsed time
        elapsed_frame = ttk.Frame(time_stats)
        elapsed_frame.pack(fill=tk.X, pady=2)

        ttk.Label(elapsed_frame, text=self.translator.translate("batch_tab", "elapsed_time")).pack(side=tk.LEFT)
        self.elapsed_var = tk.StringVar(value="00:00:00")
        ttk.Label(elapsed_frame, textvariable=self.elapsed_var).pack(side=tk.RIGHT)

        # Estimated time
        eta_frame = ttk.Frame(time_stats)
        eta_frame.pack(fill=tk.X, pady=2)

        ttk.Label(eta_frame, text=self.translator.translate("batch_tab", "estimated_time")).pack(side=tk.LEFT)
        self.eta_var = tk.StringVar(value="--:--:--")
        ttk.Label(eta_frame, textvariable=self.eta_var).pack(side=tk.RIGHT)

        # Right column - count stats
        count_stats = ttk.Frame(stats_frame)
        count_stats.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))

        # Success count
        success_frame = ttk.Frame(count_stats)
        success_frame.pack(fill=tk.X, pady=2)

        ttk.Label(
            success_frame,
            text=self.translator.translate("batch_tab", "successful"),
            foreground="green"
        ).pack(side=tk.LEFT)
        self.success_var = tk.StringVar(value="0")
        ttk.Label(
            success_frame,
            textvariable=self.success_var,
            foreground="green"
        ).pack(side=tk.RIGHT)

        # Failed count
        failed_frame = ttk.Frame(count_stats)
        failed_frame.pack(fill=tk.X, pady=2)

        ttk.Label(
            failed_frame,
            text=self.translator.translate("batch_tab", "failed"),
            foreground="red"
        ).pack(side=tk.LEFT)
        self.failed_var = tk.StringVar(value="0")
        ttk.Label(
            failed_frame,
            textvariable=self.failed_var,
            foreground="red"
        ).pack(side=tk.RIGHT)

        # Currently downloading
        current_panel = ttk.LabelFrame(
            right_frame,
            text=self.translator.translate("batch_tab", "currently_downloading"),
            padding=10
        )
        current_panel.pack(fill=tk.BOTH, expand=True)

        # Live download list using Treeview for better visualization
        self.current_downloads = ttk.Treeview(
            current_panel,
            columns=("url", "progress", "time"),
            show="headings",
            height=5
        )
        self.current_downloads.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Configure columns
        self.current_downloads.heading("url", text=self.translator.translate("batch_tab", "video_url"))
        self.current_downloads.heading("progress", text=self.translator.translate("batch_tab", "status"))
        self.current_downloads.heading("time", text=self.translator.translate("batch_tab", "time"))

        self.current_downloads.column("url", width=200)
        self.current_downloads.column("progress", width=80)
        self.current_downloads.column("time", width=80)

        # Add scrollbar to treeview
        download_scroll = ttk.Scrollbar(current_panel, command=self.current_downloads.yview)
        self.current_downloads.configure(yscrollcommand=download_scroll.set)
        download_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Results section
        results_frame = ttk.LabelFrame(
            right_frame,
            text=self.translator.translate("batch_tab", "download_results"),
            padding=10
        )
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Notebook with tabs for successful and failed downloads
        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)

        # Successful tab
        success_tab = ttk.Frame(results_notebook)
        results_notebook.add(success_tab, text=self.translator.translate("batch_tab", "successful"))

        self.success_list = tk.Text(
            success_tab,
            height=5,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=tk.Scrollbar(success_tab).set
        )
        # 创建垂直滚动条
        success_scroll = tk.Scrollbar(success_tab, command=self.success_list.yview)
        self.success_list.config(yscrollcommand=success_scroll.set)
        self.success_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        success_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Failed tab
        failed_tab = ttk.Frame(results_notebook)
        results_notebook.add(failed_tab, text=self.translator.translate("batch_tab", "failed"))

        self.failed_list = tk.Text(
            failed_tab,
            height=5,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=tk.Scrollbar(failed_tab).set
        )
        # 创建垂直滚动条
        failed_scroll = tk.Scrollbar(failed_tab, command=self.failed_list.yview)
        self.failed_list.config(yscrollcommand=failed_scroll.set)
        self.failed_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        failed_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Additional toolbar with utility buttons
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=(10, 0))

        open_folder_btn = ttk.Button(
            toolbar,
            text=self.translator.translate("batch_tab", "open_download_folder"),
            command=lambda: open_folder(self.app.download_path)
        )
        open_folder_btn.pack(side=tk.LEFT)

        export_btn = ttk.Button(
            toolbar,
            text=self.translator.translate("batch_tab", "export_results"),
            command=self._export_results
        )
        export_btn.pack(side=tk.RIGHT)

        # Start update timers
        self._start_progress_update_timer()
        self._start_url_highlight_timer()

    def _start_progress_update_timer(self):
        """Start a timer to update progress UI periodically"""
        def update_timer():
            if self.is_downloading:
                self._process_results_queue()
                self._update_elapsed_time()
            self.frame.after(100, update_timer)

        self.frame.after(100, update_timer)

    def _start_url_highlight_timer(self):
        """Start a timer to periodically highlight URLs"""
        def highlight_timer():
            if not self.is_downloading:
                self._highlight_urls(None)
            self.frame.after(2000, highlight_timer)

        self.frame.after(2000, highlight_timer)

    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget using safer implementation"""
        # Don't create tooltips in this version to avoid UI glitches
        pass

    def _show_tooltip(self, event, text):
        """Show tooltip when mouse enters widget (disabled)"""
        pass

    def _hide_tooltip(self, event):
        """Hide tooltip when mouse leaves widget (disabled)"""
        pass

    def _highlight_urls(self, event=None):
        """Highlight valid URLs in the text input"""
        # Count URLs first
        self._count_urls()

        if not hasattr(self, 'batch_text'):
            return

        # Get all text
        content = self.batch_text.get(1.0, tk.END)

        # Clear existing tags
        self.batch_text.tag_remove("valid_url", "1.0", tk.END)
        self.batch_text.tag_remove("invalid_url", "1.0", tk.END)

        # Configure tags
        self.batch_text.tag_configure("valid_url", foreground="green")
        self.batch_text.tag_configure("invalid_url", foreground="red")

        # Extract URLs from text
        urls = extract_urls_from_text(content)

        # Find and tag all URLs
        for url in urls:
            # Escape special regex characters in the URL
            escaped_url = re.escape(url)

            # Find all occurrences of the URL in the text
            for match in re.finditer(escaped_url, content):
                start_idx = match.start()
                end_idx = match.end()

                # Calculate line and column
                start_line = content[:start_idx].count('\n') + 1
                start_col = start_idx - content[:start_idx].rfind('\n') - 1

                end_line = content[:end_idx].count('\n') + 1
                end_col = end_idx - content[:end_idx].rfind('\n') - 1

                start_pos = f"{start_line}.{start_col}"
                end_pos = f"{end_line}.{end_col}"

                # Always tag as valid_url when extracted by extract_urls_from_text
                self.batch_text.tag_add("valid_url", start_pos, end_pos)

    def _count_urls(self):
        """Count and update the URL counter"""
        if not hasattr(self, 'batch_text') or not hasattr(self, 'url_count_var'):
            return

        content = self.batch_text.get(1.0, tk.END)
        urls = extract_urls_from_text(content)

        # Update the counter
        url_count = len(urls)
        if url_count == 1:
            self.url_count_var.set(f"1 URL")
        else:
            self.url_count_var.set(f"{url_count} URLs")

    def _update_elapsed_time(self):
        """Update the elapsed time display"""
        if self.start_time is None or not self.is_downloading or self.paused:
            return

        # Calculate elapsed time
        elapsed_seconds = int(time.time() - self.start_time)
        hours = elapsed_seconds // 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60

        # Update display
        self.elapsed_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def _format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        if seconds is None:
            return "--:--:--"

        hours = int(seconds) // 3600
        minutes = (int(seconds) % 3600) // 60
        secs = int(seconds) % 60

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _extract_from_file(self):
        """Extract URLs from a text file"""
        file_path = filedialog.askopenfilename(
            title=self.translator.translate("batch_tab", "select_text_file"),
            filetypes=[
                (self.translator.translate("batch_tab", "text_files"), "*.txt"),
                (self.translator.translate("batch_tab", "all_files"), "*.*")
            ]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Extract URLs
            urls = extract_urls_from_text(content)

            if not urls:
                messagebox.showwarning(
                    self.translator.translate("batch_tab", "warning_title"),
                    self.translator.translate("batch_tab", "no_urls_found_in_file")
                )
                return

            # Add URLs to text field
            current_text = self.batch_text.get(1.0, tk.END).strip()
            if current_text:
                self.batch_text.insert(tk.END, "\n")

            self.batch_text.insert(tk.END, "\n".join(urls))
            self._highlight_urls()

            # Show success message
            ToastNotification(
                title=self.translator.translate("batch_tab", "urls_extracted"),
                message=self.translator.translate("batch_tab", "found_urls_in_file").format(count=len(urls)),
                duration=3000
            ).show_toast()

        except Exception as e:
            messagebox.showerror(
                self.translator.translate("batch_tab", "error_title"),
                self.translator.translate("batch_tab", "file_read_error").format(error=str(e))
            )

    def _export_results(self):
        """Export download results to a text file"""
        if not self.successful_urls and not self.failed_urls:
            messagebox.showinfo(
                self.translator.translate("batch_tab", "info_title"),
                self.translator.translate("batch_tab", "no_results_to_export")
            )
            return

        file_path = filedialog.asksaveasfilename(
            title=self.translator.translate("batch_tab", "save_results"),
            defaultextension=".txt",
            filetypes=[
                (self.translator.translate("batch_tab", "text_files"), "*.txt"),
                (self.translator.translate("batch_tab", "all_files"), "*.*")
            ]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(f"=== {self.translator.translate('batch_tab', 'download_results')} ===\n\n")
                file.write(f"{self.translator.translate('batch_tab', 'date')}: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"{self.translator.translate('batch_tab', 'total_videos')}: {len(self.successful_urls) + len(self.failed_urls)}\n")
                file.write(f"{self.translator.translate('batch_tab', 'successful')}: {len(self.successful_urls)}\n")
                file.write(f"{self.translator.translate('batch_tab', 'failed')}: {len(self.failed_urls)}\n\n")

                if self.successful_urls:
                    file.write(f"=== {self.translator.translate('batch_tab', 'successful_downloads')} ===\n")
                    for url in self.successful_urls:
                        file.write(f"- {url}\n")
                    file.write("\n")

                if self.failed_urls:
                    file.write(f"=== {self.translator.translate('batch_tab', 'failed_downloads')} ===\n")
                    for url in self.failed_urls:
                        file.write(f"- {url}\n")

            # Show success message
            self._show_toast(
                self.translator.translate("batch_tab", "export_successful"),
                self.translator.translate("batch_tab", "results_saved").format(path=file_path),
                3000
            )

            # Open the file location
            folder_path = file_path.rsplit('/', 1)[0] if '/' in file_path else file_path.rsplit('\\', 1)[0]
            if folder_path:
                open_folder(folder_path)
            else:
                open_folder(".")  # Open current directory as fallback

        except Exception as e:
            messagebox.showerror(
                self.translator.translate("batch_tab", "error_title"),
                self.translator.translate("batch_tab", "export_error").format(error=str(e))
            )

    def update_language(self):
        """Update the UI text when language changes"""
        # Update all LabelFrames
        for child in self.frame.winfo_children():
            if isinstance(child, ttk.Frame):
                for widget in child.winfo_children():
                    if isinstance(widget, ttk.LabelFrame):
                        if "batch_links" in str(widget).lower():
                            widget.configure(text=self.translator.translate("batch_tab", "batch_links"))
                        elif "download_results" in str(widget).lower():
                            widget.configure(text=self.translator.translate("batch_tab", "download_results"))

        # Update all buttons
        for child in self.frame.winfo_children():
            if isinstance(child, ttk.Frame):
                for container in child.winfo_children():
                    if isinstance(container, ttk.Frame):
                        for widget in container.winfo_children():
                            # Control buttons
                            if isinstance(widget, ttk.Button):
                                if "paste" in str(widget).lower():
                                    widget.configure(text=self.translator.translate("batch_tab", "paste_button"))
                                elif "clear" in str(widget).lower():
                                    widget.configure(text=self.translator.translate("batch_tab", "clear_button"))
                                elif "extract" in str(widget).lower():
                                    widget.configure(text=self.translator.translate("batch_tab", "extract_urls_button"))
                                elif "start" in str(widget).lower():
                                    widget.configure(text=self.translator.translate("batch_tab", "start_batch_download"))
                                elif "stop" in str(widget).lower():
                                    widget.configure(text=self.translator.translate("batch_tab", "stop_download"))

                            # Custom save location checkbox
                            elif isinstance(widget, ttk.Checkbutton):
                                widget.configure(text=self.translator.translate("batch_tab", "custom_save_location"))

                            # Thread count label
                            elif isinstance(widget, ttk.Label) and "concurrent" in str(widget).lower():
                                widget.configure(text=self.translator.translate("batch_tab", "concurrent_downloads"))

        # Update status if it's at default
        if self.status_var.get() in ["Ready", "就绪"]:
            self.status_var.set(self.translator.translate("batch_tab", "status_ready"))

    def _toggle_custom_save(self):
        """Toggle custom save location"""
        if self.custom_save_var.get():
            # Open folder selection dialog
            custom_path = filedialog.askdirectory(
                title=self.translator.translate("batch_tab", "select_download_folder"),
                initialdir=self.app.download_path
            )
            if custom_path:
                self.custom_download_path = custom_path
                # Update location display
                self.location_display.config(text=custom_path)
            else:
                # Uncheck if no folder selected
                self.custom_save_var.set(False)
        else:
            # Reset to default path
            self.custom_download_path = self.app.download_path
            # Update location display
            self.location_display.config(text=self.app.download_path)

    def _extract_urls(self):
        """Extract and display unique URLs from batch text"""
        text_content = self.batch_text.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showwarning(
                self.translator.translate("batch_tab", "warning_title"),
                self.translator.translate("batch_tab", "no_text_to_extract")
            )
            return

        # Extract URLs
        urls = extract_urls_from_text(text_content)

        if not urls:
            messagebox.showwarning(
                self.translator.translate("batch_tab", "warning_title"),
                self.translator.translate("batch_tab", "no_urls_found")
            )
            return

        # 更智能的去重和验证
        unique_urls = []
        seen = set()
        for url in urls:
            # 标准化 URL，去除可能的尾部空格和重复查询参数
            normalized_url = url.strip().split('?')[0]
            if normalized_url and normalized_url not in seen:
                unique_urls.append(normalized_url)
                seen.add(normalized_url)

        # 清除并插入唯一 URL
        self.batch_text.delete(1.0, tk.END)
        self.batch_text.insert(tk.END, "\n".join(unique_urls))

        # 显示去重和验证结果
        total_found = len(urls)
        unique_count = len(unique_urls)

        # 根据去重结果显示不同的消息
        if unique_count == total_found:
            messagebox.showinfo(
                self.translator.translate("batch_tab", "urls_extracted"),
                self.translator.translate("batch_tab", "found_unique_urls").format(count=unique_count)
            )
        else:
            messagebox.showinfo(
                self.translator.translate("batch_tab", "urls_processed"),
                self.translator.translate("batch_tab", "urls_processed_details").format(
                    total=total_found,
                    unique=unique_count,
                    removed=total_found - unique_count
                )
            )

    def _paste_to_batch(self):
        """Paste clipboard content to batch text area"""
        try:
            clipboard_content = self.frame.clipboard_get().strip()
            if clipboard_content:
                self.batch_text.insert(tk.INSERT, clipboard_content + "\n")
            else:
                messagebox.showwarning(
                    self.translator.translate("batch_tab", "warning_title"),
                    self.translator.translate("batch_tab", "clipboard_empty")
                )
        except Exception:
            messagebox.showwarning(
                self.translator.translate("batch_tab", "warning_title"),
                self.translator.translate("batch_tab", "clipboard_error")
            )

    def _show_toast(self, title, message, duration=3000, style=None):
        """Show toast notification with fallback to messagebox"""
        if HAS_TTKBOOTSTRAP_EXTENSIONS:
            try:
                ToastNotification(
                    title=title,
                    message=message,
                    duration=duration,
                    bootstyle=style
                ).show_toast()
            except:
                messagebox.showinfo(title, message)
        else:
            messagebox.showinfo(title, message)

    def _toggle_pause(self):
        """Toggle pause/resume download"""
        if not self.is_downloading:
            return

        self.paused = not self.paused

        if self.paused:
            # Update button to show resume
            try:
                self.pause_button.config(
                    text=self.translator.translate("batch_tab", "resume_download"),
                    style="success.TButton" if HAS_TTKBOOTSTRAP_EXTENSIONS else None
                )
            except:
                self.pause_button.config(
                    text=self.translator.translate("batch_tab", "resume_download")
                )

            self.status_var.set(self.translator.translate("batch_tab", "download_paused"))

            # Update progress bar style if possible
            if HAS_TTKBOOTSTRAP_EXTENSIONS:
                try:
                    self.progress.configure(bootstyle=(WARNING, STRIPED))
                except:
                    pass
        else:
            # Update button to show pause
            try:
                self.pause_button.config(
                    text=self.translator.translate("batch_tab", "pause_download"),
                    style="warning.TButton" if HAS_TTKBOOTSTRAP_EXTENSIONS else None
                )
            except:
                self.pause_button.config(
                    text=self.translator.translate("batch_tab", "pause_download")
                )

            self.status_var.set(self.translator.translate("batch_tab", "download_resumed"))

            # Update progress bar style if possible
            if HAS_TTKBOOTSTRAP_EXTENSIONS:
                try:
                    self.progress.configure(bootstyle=(SUCCESS, STRIPED))
                except:
                    pass

    def _batch_download(self):
        """Handle batch download button click"""
        # Check if already downloading
        if self.is_downloading:
            messagebox.showinfo(
                self.translator.translate("batch_tab", "info_title"),
                self.translator.translate("batch_tab", "download_in_progress")
            )
            return

        text_content = self.batch_text.get(1.0, tk.END).strip()
        if not text_content:
            messagebox.showwarning(
                self.translator.translate("batch_tab", "warning_title"),
                self.translator.translate("batch_tab", "enter_video_urls")
            )
            return

        if not self.app.client.is_configured:
            messagebox.showwarning(
                self.translator.translate("batch_tab", "warning_title"),
                self.translator.translate("batch_tab", "setup_api_key_first")
            )
            return

        # Extract URLs from text
        urls = extract_urls_from_text(text_content)

        if not urls:
            messagebox.showwarning(
                self.translator.translate("batch_tab", "warning_title"),
                self.translator.translate("batch_tab", "no_valid_urls")
            )
            return

        # Confirm large downloads
        if len(urls) > 10:
            confirm = messagebox.askyesno(
                self.translator.translate("batch_tab", "confirm_batch_download"),
                self.translator.translate("batch_tab", "confirm_large_download").format(count=len(urls))
            )
            if not confirm:
                return

        # Determine download path
        download_path = (
            self.custom_download_path
            if hasattr(self, 'custom_download_path') and self.custom_save_var.get()
            else self.app.download_path
        )

        # Get settings
        settings = {}
        if hasattr(self.app, 'settings_tab'):
            settings = self.app.settings_tab.get_settings()

        # Prepare for download
        self.is_downloading = True
        self.stop_download = False
        self.paused = False
        self.start_time = time.time()

        # Update UI
        self.download_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)

        # Try to update progress bar style
        if HAS_TTKBOOTSTRAP_EXTENSIONS:
            try:
                self.progress.configure(bootstyle=(SUCCESS, STRIPED))
            except:
                pass

        # Clear current downloads
        for item in self.current_downloads.get_children():
            self.current_downloads.delete(item)

        # Reset statistics
        self.completed = 0
        self.failed = 0
        self.successful_urls = []
        self.failed_urls = []
        self.download_times = []
        self.currently_downloading = set()

        # Reset progress
        self._update_progress(0, len(urls))
        self.status_var.set(self.translator.translate("batch_tab", "downloading_videos").format(count=len(urls)))
        self.success_var.set("0")
        self.failed_var.set("0")
        self.elapsed_var.set("00:00:00")
        self.eta_var.set("--:--:--")
        self.percent_var.set("0%")

        # Get thread count from UI
        self.max_workers = self.thread_count_var.get()

        # Create downloader with current settings
        downloader = VideoDownloader(
            download_path=download_path,
            use_description=settings.get('rename_with_desc', False),
            skip_existing=settings.get('skip_existing', True),
            max_workers=self.max_workers  # Pass max_workers parameter
        )

        # Show notification
        self._show_toast(
            self.translator.translate("batch_tab", "download_started"),
            self.translator.translate("batch_tab", "batch_download_started").format(count=len(urls)),
            3000,
            "success"
        )

        # Start download in background thread
        self.download_thread = threading.Thread(
            target=self._batch_download_thread,
            args=(urls, downloader),
            daemon=True
        )
        self.download_thread.start()

    def _download_single_video(self, url, downloader, index, total):
        """Download a single video in a worker thread

        Args:
            url: Video URL
            downloader: VideoDownloader instance
            index: Current index in the batch
            total: Total number of URLs

        Returns:
            tuple: (success, url, download_time, error_message)
        """
        if self.stop_download:
            return (False, url, 0, "Download stopped by user")

        # Add to currently downloading list
        self.app.root.after(0, lambda: self._add_to_current_downloads(url))

        # Handle pause state
        while self.paused and not self.stop_download:
            # Update UI to show paused status
            self.app.root.after(0, lambda u=url: self._update_download_status(u, "Paused"))
            time.sleep(0.5)

        if self.stop_download:
            self.app.root.after(0, lambda u=url: self._remove_from_current_downloads(u))
            return (False, url, 0, "Download stopped by user")

        # Start timing
        start_time = time.time()
        try:
            # Update status
            self.app.root.after(0, lambda u=url: self._update_download_status(u, "Fetching info"))

            # Get video info using the refactored API
            video_info = self.app.client.get_data(url, clean_data=True)

            if not video_info:
                self.app.root.after(0, lambda u=url: self._remove_from_current_downloads(u))
                return (False, url, time.time() - start_time, "Failed to retrieve video info")

            # Check if video_urls exists in the response
            if not video_info.get('video_urls'):
                self.app.root.after(0, lambda u=url: self._remove_from_current_downloads(u))
                return (False, url, time.time() - start_time, "No video URLs found in response")

            # Update status
            self.app.root.after(0, lambda u=url: self._update_download_status(u, "Downloading"))

            # Create progress callback for this download
            def progress_callback(current, total):
                # No UI updates needed here as the batch progress is handled separately
                pass

            # Ensure media_type is set
            if 'media_type' not in video_info:
                video_info['media_type'] = 'video'  # Default to video type in Batch Tab

            # Download video using main_downloader
            result = downloader.main_downloader(
                video_info,
                progress_callback=progress_callback,
                max_retries=3  # Use default or get from settings
            )

            # Remove from current downloads
            self.app.root.after(0, lambda u=url: self._remove_from_current_downloads(u))

            if result['success'] and result['files']:
                return (True, url, time.time() - start_time, None)
            else:
                error_msg = "\n".join(result['errors']) if result['errors'] else "Failed to save video"
                return (False, url, time.time() - start_time, error_msg)

        except Exception as e:
            print(f"Error downloading video {url}: {e}")
            # Remove from current downloads
            self.app.root.after(0, lambda u=url: self._remove_from_current_downloads(u))
            return (False, url, time.time() - start_time, str(e))

    def _add_to_current_downloads(self, url):
        """Add URL to the currently downloading list"""
        if url in self.currently_downloading:
            return

        # Add to tracking set
        self.currently_downloading.add(url)

        # Add to UI
        display_url = url[:40] + "..." if len(url) > 40 else url
        item_id = self.current_downloads.insert("", "end", values=(display_url, "Starting", "0s"))

        # Store the item ID with the URL for later updates
        setattr(self, f"download_item_{hash(url)}", item_id)

    def _update_download_status(self, url, status):
        """Update the status of a downloading item"""
        if url not in self.currently_downloading:
            return

        # Get the item ID
        item_id = getattr(self, f"download_item_{hash(url)}", None)
        if not item_id:
            return

        # Calculate elapsed time for this download
        now = time.time()
        start_time = getattr(self, f"download_start_{hash(url)}", now)
        elapsed = int(now - start_time)

        # Store start time if not already set
        if not hasattr(self, f"download_start_{hash(url)}"):
            setattr(self, f"download_start_{hash(url)}", now)

        # Update the item in the treeview
        self.current_downloads.item(item_id, values=(
            url[:40] + "..." if len(url) > 40 else url,
            status,
            f"{elapsed}s"
        ))

    def _remove_from_current_downloads(self, url):
        """Remove URL from the currently downloading list"""
        if url not in self.currently_downloading:
            return

        # Remove from tracking set
        self.currently_downloading.remove(url)

        # Remove from UI
        item_id = getattr(self, f"download_item_{hash(url)}", None)
        if item_id:
            self.current_downloads.delete(item_id)

        # Clean up attributes
        if hasattr(self, f"download_item_{hash(url)}"):
            delattr(self, f"download_item_{hash(url)}")

        if hasattr(self, f"download_start_{hash(url)}"):
            delattr(self, f"download_start_{hash(url)}")

    def _process_results_queue(self):
        """Process results from the queue and update UI"""
        try:
            # Process all available results without blocking
            while not self.result_queue.empty():
                success, url, download_time, error_message = self.result_queue.get_nowait()

                with self.lock:
                    if success:
                        self.completed += 1
                        self.successful_urls.append(url)
                        self.download_times.append(download_time)

                        # Update success counter
                        self.success_var.set(str(self.completed))
                    else:
                        self.failed += 1
                        self.failed_urls.append(url)
                        if error_message:
                            self.logger.error(f"Failed to download {url}: {error_message}")

                        # Update failed counter
                        self.failed_var.set(str(self.failed))

                    total = self.completed + self.failed
                    self._update_progress(total, self.total_urls)

                    # Update estimated time
                    if self.download_times:
                        avg_download_time = sum(self.download_times) / len(self.download_times)
                        remaining_urls = self.total_urls - total

                        # Factor in concurrency for better estimation
                        active_threads = min(remaining_urls, self.max_workers)
                        if active_threads > 0:
                            estimated_remaining_time = avg_download_time * (remaining_urls / active_threads)

                            # Update ETA display
                            self.eta_var.set(self._format_time(estimated_remaining_time))

                            # Update status with estimated time and active downloads
                            status_text = self.translator.translate("batch_tab", "downloading_with_eta").format(
                                active=len(self.currently_downloading),
                                total=self.total_urls,
                                eta=self._format_time(estimated_remaining_time)
                            )
                            self.status_var.set(status_text)

                self.result_queue.task_done()
        except queue.Empty:
            pass

    def _batch_download_thread(self, urls, downloader):
        """Background thread function for batch download using thread pool

        Args:
            urls: List of video URLs
            downloader: VideoDownloader instance
        """
        try:
            self.total_urls = len(urls)

            # Create a thread pool
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all download tasks
                futures = []
                for i, url in enumerate(urls):
                    if self.stop_download:
                        break

                    future = executor.submit(
                        self._download_single_video,
                        url,
                        downloader,
                        i + 1,
                        self.total_urls
                    )
                    futures.append(future)

                # Wait for all futures to complete
                for future in futures:
                    if not self.stop_download:
                        try:
                            result = future.result()
                            self.result_queue.put(result)
                        except Exception as e:
                            print(f"Future exception: {e}")

            # Ensure all results are processed
            self.app.root.after(500, self._process_results_queue)

            # Wait for the queue to be fully processed
            self.result_queue.join()

            # Finalize download
            self.app.root.after(500, self._on_batch_download_complete)

        except Exception as e:
            print(f"Batch download error: {e}")
            self.app.root.after(0, lambda:
                messagebox.showerror(
                    self.translator.translate("batch_tab", "download_error"),
                    str(e)
                )
            )

    def _on_batch_download_complete(self):
        """Handle batch download completion"""
        # Reset UI state
        self.is_downloading = False
        self.download_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)

        # Calculate timing stats
        total_time = time.time() - self.start_time if self.start_time else 0

        # Clean up any remaining items in current downloads
        for item in self.current_downloads.get_children():
            self.current_downloads.delete(item)
        self.currently_downloading.clear()

        # Update status and progress
        total = self.total_urls
        completed = self.completed
        failed = self.failed

        self.status_var.set(self.translator.translate("batch_tab", "batch_download_complete_status").format(
            completed=completed,
            failed=failed
        ))
        self.progress_var.set(f"{completed}/{total}")
        self.progress["value"] = 100
        self.percent_var.set("100%")

        # Set progress bar color based on results if possible
        if HAS_TTKBOOTSTRAP_EXTENSIONS:
            try:
                if failed == 0:
                    self.progress.configure(bootstyle=SUCCESS)
                elif completed > failed:
                    self.progress.configure(bootstyle=INFO)
                else:
                    self.progress.configure(bootstyle=WARNING)
            except:
                pass

        # Show toast notification for completion
        toast_style = "success" if failed == 0 else ("info" if completed > failed else "warning")

        download_message = self.translator.translate("batch_tab", "batch_download_complete_toast").format(
            total=total,
            completed=completed,
            failed=failed,
            time=self._format_time(total_time)
        )

        self._show_toast(
            self.translator.translate("batch_tab", "download_complete"),
            download_message,
            5000,
            toast_style
        )

        # Update success and failed lists
        self.success_list.config(state=tk.NORMAL)
        self.failed_list.config(state=tk.NORMAL)

        # Clear previous content
        self.success_list.delete(1.0, tk.END)
        self.failed_list.delete(1.0, tk.END)

        # Add successful download URLs
        if self.successful_urls:
            self.success_list.insert(tk.END, self.translator.translate("batch_tab", "successful_videos") + "\n")
            for url in self.successful_urls:
                self.success_list.insert(tk.END, f"- {url}\n")
        else:
            self.success_list.insert(tk.END, self.translator.translate("batch_tab", "no_successful_videos") + "\n")

        # Add failed download URLs
        if self.failed_urls:
            self.failed_list.insert(tk.END, self.translator.translate("batch_tab", "failed_videos") + "\n")
            for url in self.failed_urls:
                self.failed_list.insert(tk.END, f"- {url}\n")
        else:
            self.failed_list.insert(tk.END, self.translator.translate("batch_tab", "all_videos_successful") + "\n")

        # Disable text widgets to prevent editing
        self.success_list.config(state=tk.DISABLED)
        self.failed_list.config(state=tk.DISABLED)

        # Open folder based on settings
        settings = {}
        if hasattr(self.app, 'settings_tab'):
            settings = self.app.settings_tab.get_settings()

        if completed > 0 and settings.get('auto_open_folder', False):
            download_path = (
                self.custom_download_path
                if hasattr(self, 'custom_download_path') and self.custom_save_var.get()
                else self.app.download_path
            )
            open_folder(download_path)

    def _stop_download(self):
        """Stop the ongoing download"""
        if self.is_downloading:
            # Update UI
            self.stop_download = True
            self.paused = False
            self.stop_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED)
            self.status_var.set(self.translator.translate("batch_tab", "download_stopped"))

            # Change progress bar style if possible
            if HAS_TTKBOOTSTRAP_EXTENSIONS:
                try:
                    self.progress.configure(bootstyle=(DANGER, STRIPED))
                except:
                    pass

            # Show notification
            self._show_toast(
                self.translator.translate("batch_tab", "download_stopped"),
                self.translator.translate("batch_tab", "batch_download_stopped"),
                3000,
                "danger"
            )

    def _update_progress(self, current, total):
        """Update progress display

        Args:
            current: Current progress
            total: Total items
        """
        if total > 0:
            value = int((current / total) * 100)
        else:
            value = 0

        self.progress_var.set(f"{current}/{total}")
        self.progress["value"] = value
        self.percent_var.set(f"{value}%")

        # Only update progress bar color if ttkbootstrap has advanced features
        if HAS_TTKBOOTSTRAP_EXTENSIONS:
            try:
                if value > 0:
                    if value < 30:
                        self.progress.configure(bootstyle=(SUCCESS, STRIPED))
                    elif value < 70:
                        self.progress.configure(bootstyle=(INFO, STRIPED))
                    else:
                        self.progress.configure(bootstyle=(SUCCESS, STRIPED))
            except:
                pass

        self.app.root.update_idletasks()