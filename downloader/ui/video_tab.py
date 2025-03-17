"""
Video download tab for TikHub Downloader with multilingual support
使用优化后的VideoDownloader实现下载功能
"""

import os
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from tkinter import filedialog

from downloader.utils.logger import logger_instance
from downloader.utils.utils import format_timestamp, format_number, open_folder
from downloader.core.downloader import VideoDownloader


class VideoTab:
    """Video download tab UI and functionality"""

    def __init__(self, parent, app):
        """Initialize the video download tab

        Args:
            parent: Parent widget
            app: Application instance
        """
        self.app = app
        self.frame = ttk.Frame(parent)
        self.translator = app.translator  # Access translator from app

        # Download state tracking
        self.is_downloading = False

        # Set the logger
        self.logger = logger_instance

        # Create UI components
        self._create_widgets()

    def _create_widgets(self):
        """Create tab UI components"""
        # URL input frame
        url_frame = ttk.Frame(self.frame)
        url_frame.pack(fill=tk.X, pady=10, padx=10)

        url_label = ttk.Label(url_frame, text=self.translator.translate("video_tab", "video_url_label"))
        url_label.pack(side=tk.LEFT, padx=5)

        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        paste_button = ttk.Button(url_frame, text=self.translator.translate("video_tab", "paste_button"), command=self._paste_url)
        paste_button.pack(side=tk.LEFT, padx=5)

        clear_button = ttk.Button(url_frame, text=self.translator.translate("video_tab", "clear_button"), command=lambda: self.url_var.set(""))
        clear_button.pack(side=tk.LEFT, padx=5)

        # Download options frame
        options_frame = ttk.Frame(self.frame)
        options_frame.pack(fill=tk.X, pady=5, padx=10)

        # Custom save location checkbox
        self.custom_save_var = tk.BooleanVar(value=False)
        custom_save_check = ttk.Checkbutton(
            options_frame,
            text=self.translator.translate("video_tab", "custom_save_location"),
            variable=self.custom_save_var,
            command=self._toggle_custom_save
        )
        custom_save_check.pack(side=tk.LEFT, padx=5)

        # Download button
        download_button = ttk.Button(
            options_frame,
            text=self.translator.translate("video_tab", "download_video_button"),
            command=self._download_video,
            style="Accent.TButton"
        )
        download_button.pack(side=tk.RIGHT, padx=5)

        # Video info frame
        info_frame = ttk.LabelFrame(self.frame, text=self.translator.translate("video_tab", "video_information"))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbar
        info_scroll = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Status and Progress frame
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, pady=10, padx=10)

        # Status label - Takes the entire width of the frame
        self.status_var = tk.StringVar(value=self.translator.translate("video_tab", "status_ready"))
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # Progress bar - Now below the status label
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            style="Accent.Horizontal.TProgressbar"
        )
        self.progress.pack(side=tk.TOP, fill=tk.X, expand=True)

    def update_language(self):
        """Update the UI text when language changes"""
        # Update labels, buttons, and frame titles
        for child in self.frame.winfo_children():
            # Handle URL frame (first frame)
            if isinstance(child, ttk.Frame) and child == self.frame.winfo_children()[0]:
                for widget in child.winfo_children():
                    if isinstance(widget, ttk.Label):
                        widget.configure(text=self.translator.translate("video_tab", "video_url_label"))
                    elif isinstance(widget, ttk.Button):
                        if "paste" in str(widget).lower():
                            widget.configure(text=self.translator.translate("video_tab", "paste_button"))
                        elif "clear" in str(widget).lower():
                            widget.configure(text=self.translator.translate("video_tab", "clear_button"))

            # Handle options frame (second frame)
            elif isinstance(child, ttk.Frame) and child == self.frame.winfo_children()[1]:
                for widget in child.winfo_children():
                    if isinstance(widget, ttk.Checkbutton):
                        widget.configure(text=self.translator.translate("video_tab", "custom_save_location"))
                    elif isinstance(widget, ttk.Button) and "download" in str(widget).lower():
                        widget.configure(text=self.translator.translate("video_tab", "download_video_button"))

            # Handle video info frame
            elif isinstance(child, ttk.LabelFrame):
                child.configure(text=self.translator.translate("video_tab", "video_information"))

        # Update status if it's at default
        if self.status_var.get() in ["Ready", "就绪"]:
            self.status_var.set(self.translator.translate("video_tab", "status_ready"))

    def _toggle_custom_save(self):
        """Toggle custom save location"""
        if self.custom_save_var.get():
            # Open folder selection dialog
            custom_path = filedialog.askdirectory(
                title=self.translator.translate("video_tab", "select_download_folder"),
                initialdir=self.app.download_path
            )
            if custom_path:
                self.custom_download_path = custom_path
            else:
                # Uncheck if no folder selected
                self.custom_save_var.set(False)
        else:
            # Reset to default path
            self.custom_download_path = self.app.download_path

    def _paste_url(self):
        """Paste clipboard content to URL input"""
        try:
            clipboard_content = self.frame.clipboard_get().strip()
            if clipboard_content:
                self.url_var.set(clipboard_content)
            else:
                messagebox.showwarning(
                    self.translator.translate("video_tab", "warning_title"),
                    self.translator.translate("video_tab", "clipboard_empty")
                )
        except Exception:
            messagebox.showwarning(
                self.translator.translate("video_tab", "warning_title"),
                self.translator.translate("video_tab", "clipboard_error")
            )

    def _download_video(self):
        """Handle video download button click"""
        # Check if download is in progress
        if self.is_downloading:
            messagebox.showinfo(
                self.translator.translate("video_tab", "info_title"),
                self.translator.translate("video_tab", "download_in_progress")
            )
            return

        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning(
                self.translator.translate("video_tab", "warning_title"),
                self.translator.translate("video_tab", "enter_video_url")
            )
            return

        if not self.app.client.is_configured:
            messagebox.showwarning(
                self.translator.translate("video_tab", "warning_title"),
                self.translator.translate("video_tab", "setup_api_key_first")
            )
            return

        # Determine download path
        download_path = (
            self.custom_download_path
            if hasattr(self, 'custom_download_path') and self.custom_save_var.get()
            else self.app.download_path
        )

        # Reset and prepare for download
        self.is_downloading = True
        self.progress_var.set(0)
        self.status_var.set(self.translator.translate("video_tab", "getting_video_info"))
        self.app.main_window.update_status(f"{self.translator.translate('video_tab', 'getting_video_info')}: {url}")

        # Get settings
        settings = {}
        if hasattr(self.app, 'settings_tab'):
            settings = self.app.settings_tab.get_settings()

        # Run in background thread
        self.app.run_in_thread(
            self._download_video_thread,
            self._on_download_complete,
            url=url,
            download_path=download_path,
            settings=settings
        )

    def _download_video_thread(self, url, download_path, settings):
        """Background thread function for video download

        Args:
            url: Video URL
            download_path: Path to save the downloaded file
            settings: Download settings from settings tab

        Returns:
            tuple: (success, file_path, error_message)
        """
        try:
            # Get video info from API
            self.logger.info(f"Getting video info for URL: {url}")
            self.app.root.after(0, lambda: self.status_var.set(self.translator.translate("video_tab", "getting_video_info")))

            video_info = self.app.client.get_data(url, clean_data=True)
            self.logger.debug(f"Received video info: {video_info}")

            if not video_info:
                self.logger.error("Failed to retrieve video info")
                return False, None, self.translator.translate("video_tab", "failed_retrieve_video_info")

            # Update UI with video info
            self.app.root.after(0, lambda: self._display_video_info(video_info))
            self.app.root.after(0, lambda: self.progress_var.set(20))

            # 检查视频URLs是否存在
            if not video_info.get('video_urls'):
                self.logger.error("No video URLs found in response")
                return False, None, self.translator.translate("video_tab", "video_url_not_found")

            # 准备下载
            self.logger.info("Preparing to download video")
            self.app.root.after(0, lambda: self.status_var.set(self.translator.translate("video_tab", "downloading_video")))
            self.app.root.after(0, lambda: self.app.main_window.update_status(self.translator.translate("video_tab", "downloading_video")))

            # 创建下载器实例（不包含template_dir参数）
            downloader = VideoDownloader(
                download_path=download_path,
                use_description=settings.get('rename_with_desc', False),
                skip_existing=settings.get('skip_existing', True),
                max_workers=settings.get('max_workers', 4)
            )

            # 创建进度回调
            def progress_callback(current, total):
                if total > 0:
                    # 下载进度从20%到90%
                    percentage = 20 + (current / total) * 70
                    self.app.root.after(0, lambda: self.progress_var.set(percentage))

            # 确保设置正确的media_type
            if 'media_type' not in video_info:
                video_info['media_type'] = 'video'  # 在Video Tab中，默认为视频类型

            # 直接使用main_downloader下载
            self.logger.info("Starting download with VideoDownloader")
            result = downloader.main_downloader(
                video_info,  # 直接传入整个video_info
                progress_callback=progress_callback,
                max_retries=settings.get('max_retries', 3)
            )

            # 检查下载结果
            if result['success'] and result['files']:
                self.logger.info(f"Download successful. Files: {result['files']}")
                return True, result['files'][0], None
            else:
                error_msg = "\n".join(result['errors']) if result['errors'] else self.translator.translate("video_tab", "download_failed")
                self.logger.error(f"Download failed: {error_msg}")
                return False, None, error_msg

        except Exception as e:
            self.logger.exception(f"Error in download thread: {str(e)}")
            return False, None, str(e)

    def _on_download_complete(self, result):
        """Handle download completion

        Args:
            result: (success, file_path, error_message) tuple from download thread
        """
        success, file_path, error_message = result

        # Reset downloading state
        self.is_downloading = False

        if success:
            self.progress_var.set(100)
            self.status_var.set(self.translator.translate("video_tab", "download_complete"))
            self.app.main_window.update_status(f"{self.translator.translate('video_tab', 'video_downloaded')}: {file_path}")
            self.logger.info(f"Download completed successfully: {file_path}")

            # Create custom download complete dialog
            self._show_download_complete_dialog(file_path)
        else:
            self.progress_var.set(0)
            self.status_var.set(self.translator.translate("video_tab", "download_failed"))
            self.app.main_window.update_status(self.translator.translate("video_tab", "download_failed"))
            self.logger.error(f"Download failed: {error_message}")

            # Show error message
            error_msg = error_message or self.translator.translate("video_tab", "failed_download_video")
            messagebox.showerror(
                self.translator.translate("video_tab", "download_error"),
                error_msg
            )

    def _show_download_complete_dialog(self, file_path):
        """Show a custom download completion dialog

        Args:
            file_path: Path to the downloaded file
        """
        # Create dialog
        dialog = tk.Toplevel(self.app.root)
        dialog.title(self.translator.translate("video_tab", "download_complete"))
        dialog.geometry("500x250")
        dialog.minsize(500, 250)

        # Make it modal
        dialog.transient(self.app.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.app.root.winfo_width() - width) // 2 + self.app.root.winfo_x()
        y = (self.app.root.winfo_height() - height) // 2 + self.app.root.winfo_y()
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Main frame with padding
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Success icon and header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Create checkmark icon label
        check_label = ttk.Label(header_frame, text="✓", font=("Helvetica", 24, "bold"), foreground="green")
        check_label.pack(side=tk.LEFT, padx=(0, 10))

        # Header text
        header_label = ttk.Label(
            header_frame,
            text=self.translator.translate("video_tab", "download_complete"),
            font=("Helvetica", 14, "bold")
        )
        header_label.pack(side=tk.LEFT)

        # File path display
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=10)

        ttk.Label(path_frame, text=self.translator.translate("video_tab", "saved_to")).pack(side=tk.LEFT)
        path_entry = ttk.Entry(path_frame, width=50)
        path_entry.insert(0, file_path)
        path_entry.configure(state='readonly')
        path_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Open folder button
        open_folder_button = ttk.Button(
            button_frame,
            text=self.translator.translate("video_tab", "open_folder_button"),
            style="Accent.TButton",
            command=lambda: [open_folder(os.path.dirname(file_path)), dialog.destroy()]
        )
        open_folder_button.pack(side=tk.LEFT, padx=(0, 10))

        # Close button
        close_button = ttk.Button(
            button_frame,
            text=self.translator.translate("video_tab", "close_button"),
            command=dialog.destroy
        )
        close_button.pack(side=tk.RIGHT)

        # Wait for the dialog to close
        self.app.root.wait_window(dialog)

    def _display_video_info(self, video_info):
        """Display video information in the text area

        Args:
            video_info: Video information dictionary
        """
        try:
            # Clear previous info
            self.info_text.delete(1.0, tk.END)

            # Build info string
            info = f"{self.translator.translate('video_tab', 'video_id_label')}: {video_info.get('id', '')}\n"

            # Add creation time
            if 'create_time' in video_info:
                create_time = video_info['create_time']
                info += f"{self.translator.translate('video_tab', 'created_label')}: {create_time}\n"

            # Add description (if available)
            if 'desc' in video_info and video_info['desc']:
                info += f"{self.translator.translate('video_tab', 'description_label')}: {video_info['desc']}\n"

            # Add author information
            if 'author_name' in video_info:
                info += f"\n{self.translator.translate('video_tab', 'author_label')}: {video_info['author_name']}\n"

            if 'author_id' in video_info:
                info += f"{self.translator.translate('video_tab', 'user_id_label')}: {video_info['author_id']}\n"

            # Add statistics
            if 'like_count' in video_info:
                info += f"\n{self.translator.translate('video_tab', 'likes_label')}: {format_number(video_info['like_count'])}\n"

            if 'comment_count' in video_info:
                info += f"{self.translator.translate('video_tab', 'comments_label')}: {format_number(video_info['comment_count'])}\n"

            if 'share_count' in video_info:
                info += f"{self.translator.translate('video_tab', 'shares_label')}: {format_number(video_info['share_count'])}\n"

            if 'play_count' in video_info:
                info += f"{self.translator.translate('video_tab', 'plays_label')}: {format_number(video_info['play_count'])}\n"

            # Add video quality information if available
            if 'resolution' in video_info:
                info += f"\n{self.translator.translate('video_tab', 'resolution_label')}: {video_info['resolution']}\n"

            if 'duration' in video_info:
                # Duration可能是毫秒
                duration_seconds = int(video_info['duration']) / 1000 if int(video_info['duration']) > 1000 else int(video_info['duration'])
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                info += f"{self.translator.translate('video_tab', 'duration_label')}: {minutes}:{seconds:02d}\n"

            if 'data_size' in video_info:
                info += f"{self.translator.translate('video_tab', 'size_label')}: {video_info['data_size']}\n"

            # 如果有音乐信息，添加音乐信息
            if 'music_title' in video_info:
                info += f"\n{self.translator.translate('video_tab', 'music_label')}: {video_info['music_title']}\n"

            if 'music_author' in video_info:
                info += f"{self.translator.translate('video_tab', 'music_author_label')}: {video_info['music_author']}\n"

            # 如果有标签，显示标签
            if 'tags' in video_info and video_info['tags']:
                tags_str = ", ".join(video_info['tags'])
                info += f"\n{self.translator.translate('video_tab', 'tags_label')}: {tags_str}\n"

            # Display info
            self.info_text.insert(tk.END, info)
            self.logger.info("Video information displayed successfully")
        except Exception as e:
            error_msg = f"{self.translator.translate('video_tab', 'parse_video_info_error')}: {str(e)}"
            self.info_text.insert(tk.END, error_msg)
            self.logger.error(f"Error displaying video info: {e}", exc_info=True)