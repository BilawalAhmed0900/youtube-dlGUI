#!/usr/bin/env python3
# import re
import threading
import tkinter
import tkinter.ttk
import youtube_dl


class HookClass:
    """
    Class containing hook function passed to youtube_dl
    Class allows hook_function to have variables other than the
    dictionary passed by youtube_dl
    """

    def __init__(self, per_progress_bar, all_progress_bar, total_value):
        self.per_progress_bar = per_progress_bar
        self.all_progress_bar = all_progress_bar

        self.total = total_value
        self.all_progress_bar.configure(value=0)
        self.per_progress_bar.configure(value=0)
        self.all_progress_bar.configure(maximum=self.total)
        self.get_size = True
        self.done = 0

    def hook_function(self, dictionary):
        if self.get_size:
            self.per_progress_bar.configure(
                maximum=int(dictionary["total_bytes"]))
            self.get_size = False

        if dictionary["status"] == "downloading":
                self.per_progress_bar.configure(
                    value=int(dictionary["downloaded_bytes"]))

        elif dictionary["status"] == "finished":
            self.get_size = True
            self.done += 1
            self.all_progress_bar.configure(value=self.done)


def download_internal(button, quality,
                      per_progress_bar, all_progress_bar, string):
    """

    :param button: Button to change state to disabled and normal
    :param quality: To be passed to youtube_dl as "format" string
    :param per_progress_bar: Updating progress bar per download
    :param all_progress_bar: Updating progress bar for all
    :param string: String with youtube links in it
    :return: None
    """
    ydl_opts_playlist = {
        "quiet": True,
        "in_playlist": True,
        "extract_flat": True
    }

    button.configure(state="disabled")
    # string = re.sub(pattern=r"&list=[a-zA-Z0-9-]+", repl="", string=string)
    list_links = string.split(" ")
    list_links = [link for link in list_links if link.strip() != ""]
    total_videos = 0
    for link in list_links:
        if "?list=" in link:
            with youtube_dl.YoutubeDL(ydl_opts_playlist) as ydl:
                playlist_dict = ydl.extract_info(link, download=False)
                total_videos += sum([1 for video in playlist_dict["entries"]
                                     if video is not None])
        else:
            total_videos += 1

    # e.g. "bestvideo+bestaudo". This needs seperate download for audio and video
    # Merged by ffmpeg
    if "+" in quality:
        total_videos *= 2

    hook_class = HookClass(per_progress_bar=per_progress_bar,
                           all_progress_bar=all_progress_bar,
                           total_value=total_videos)

    ydl_opts = {
        "format": quality,
        "progress_hooks": [hook_class.hook_function],
        "quiet": True,
        "no_warnings": True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(list_links)
        except youtube_dl.utils.DownloadError:
            pass
    button.configure(state="normal")


def download(button, quality, per_progress_bar, all_progress_bar, string):
    thread = threading.Thread(target=download_internal,
                              args=(button, quality,
                                    per_progress_bar,
                                    all_progress_bar,
                                    string))
    # thread.setDaemon(True)
    thread.start()


def main():
    root = tkinter.Tk()
    root.title("Youtube-dl GUI")

    input_label = tkinter.Label(master=root,
                                text="Input: (seperate with spaces)")
    input_text = tkinter.Text(master=root, height=10)
    input_text_scrollb = tkinter.Scrollbar(master=root,
                                           command=input_text.yview)

    input_label.grid(row=0, column=0, padx=(15, 0), pady=5, sticky="W")
    input_text.grid(row=1, column=0, padx=(25, 0))
    input_text_scrollb.grid(row=1, column=1, sticky="NS", padx=(0, 15))
    input_text["yscrollcommand"] = input_text_scrollb.set

    # To be shown to GUI
    options_show = ["Best quality", "Default quality",
                    "Audio only", "Video Only"]

    # To be passed to youtube_dl
    options = {options_show[0]: "bestvideo+bestaudio",
               options_show[1]: "best",
               options_show[2]: "bestaudio",
               options_show[3]: "bestvideo"}

    options_stringvar = tkinter.StringVar()
    options_stringvar.set(options_show[1])

    dropdown_menu = tkinter.OptionMenu(root, options_stringvar, *options_show)
    dropdown_menu.grid(row=2, column=0, sticky="E", pady=5)

    per_progress_bar = tkinter.ttk.Progressbar(master=root,
                                               orient="horizontal", length=550,
                                               maximum=1000)
    per_progress_bar.grid(row=5, column=0, sticky="W", padx=(25, 0),
                          pady=(5, 0))

    all_progress_bar = tkinter.ttk.Progressbar(master=root,
                                               orient="horizontal", length=550,
                                               maximum=1000)
    all_progress_bar.grid(row=6, column=0, sticky="W", padx=(25, 25))

    download_button = tkinter.Button(master=root, text="Download...",
                                     command=lambda:
                                     download(download_button,
                                              options[options_stringvar.get()],
                                              per_progress_bar,
                                              all_progress_bar,
                                              input_text.get(
                                                  "1.0", tkinter.END)
                                              ),
                                     width=15)
    download_button.grid(row=6, column=0, padx=5, pady=5,
                         sticky="E", columnspan=2)

    root.mainloop()


if __name__ == '__main__':
    main()
