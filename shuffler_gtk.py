#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MP3 Shuffler - A simple application to shuffle MP3 files to play on devices that lack a shuffle playback feature.
# by Jason Ritchie

import os
import random
import re
import shutil
import time
from threading import Thread
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gio, GLib

all_files = []


class ShufflerWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MP3 Shuffler")
        self.set_border_width(20)
        self.set_default_size(400, 200)
        # Set the window to not be resizable
        self.set_resizable(False)
        self.app_path = os.path.dirname(os.path.abspath(__file__))

        self.icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join(self.app_path, "org.flatpak.mp3shuffler.png"))
        notification = Gio.Notification()
        notification.set_title("MP3 Shuffler is ready")
        notification.set_body("MP3 Shuffler is ready")

        file = Gio.File.new_for_path(self.get_resource_path("org.flatpak.mp3shuffler24.png"))
        icon = Gio.FileIcon(file=file)

        notification.set_icon(icon)

        # # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Container for source row
        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        self.src_label = Gtk.Label(label="Source:")
        self.src_label.set_width_chars(10)
        self.src_label.set_halign(Gtk.Align.START)
        hbox.pack_start(self.src_label, False, False, 0)

        self.src_entry = Gtk.Entry()
        self.src_entry.set_width_chars(65)
        self.src_entry.set_halign(Gtk.Align.START)
        self.src_entry.set_placeholder_text("Select a folder containing MP3 files")
        hbox.pack_start(self.src_entry, False, False, 0)

        button_src = Gtk.Button(label="Choose Source")
        button_src.set_property("width-request", 25)
        button_src.set_property("height-request", 10)
        button_src.connect("clicked", self.get_src_folder)
        hbox.pack_start(button_src, False, False, 0)
        
        # container for target row
        hbox2 = Gtk.Box(spacing=6)
        vbox.pack_start(hbox2, True, True, 0)

        self.tar_label = Gtk.Label(label="Target:")
        self.tar_label.set_width_chars(10)
        self.tar_label.set_halign(Gtk.Align.START)
        hbox2.pack_start(self.tar_label, False, False, 0)

        self.tar_entry = Gtk.Entry()
        self.tar_entry.set_width_chars(65)
        self.tar_entry.set_halign(Gtk.Align.START)
        self.tar_entry.set_placeholder_text("Select a folder or SD card to copy shuffled MP3 files to")
        hbox2.pack_start(self.tar_entry, False, False, 0)

        button_tar = Gtk.Button(label="Choose Target")
        button_tar.set_property("width-request", 25)
        button_tar.set_property("height-request", 10)
        button_tar.connect("clicked", self.get_tar_folder)
        hbox2.add(button_tar)

        #container for button row
        hbox3 = Gtk.Box(spacing=6)
        vbox.pack_start(hbox3, True, True, 0)

        # Shuffle button
        self.shuffle_button = Gtk.Button(label="Shuffle")
        self.shuffle_button.connect("clicked", self.shuffle)
        hbox3.pack_start(self.shuffle_button, False, False, 0)

        #about button
        self.about_button = Gtk.Button(label="About")
        self.about_button.connect("clicked", self.about_dialog)
        hbox3.pack_start(self.about_button, False, False, 0)

        self.status = Gtk.Label()
        self.status.set_width_chars(80)
        self.status.set_halign(Gtk.Align.START)
        self.status.set_justify(Gtk.Justification.LEFT)
        self.status.set_alignment(0,0)
        self.status.set_text("Ready to shuffle!")
        vbox.pack_start(self.status, False, False, 0)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_property("width-request", 400)
        vbox.pack_start(self.progressbar, False, False, 0)

    def get_resource_path(self, rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource
    
    def about_dialog(self, widget):
        dialog = Gtk.AboutDialog()
        dialog.set_program_name("MP3 Shuffler")
        dialog.set_version("1.0")
        dialog.set_copyright("Copyright © 2025 Jason Ritchie")
        dialog.set_comments("A simple application to shuffle MP3 files to play on devices that lack a shuffle playback feature. Shuffler will randomize both the names and the order of the files as some players sort by file date/time.")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_authors(["Jason Ritchie"])
        dialog.set_website("https://github.com/jasonritchie06/MP3Shuffler")
        dialog.set_website_label("GitHub Repository")
        dialog.set_logo(self.icon)
        dialog.set_modal(True)
        dialog.run()
        dialog.destroy()

    def get_src_folder(self, widget):
        dialog = Gtk.FileChooserDialog(title="Please choose a folder", parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER,)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK)
        dialog.set_default_size(600, 300)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.src_entry.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

    def get_tar_folder(self, widget):
        dialog = Gtk.FileChooserDialog(title="Please choose a folder", parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER,)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK)
        dialog.set_default_size(600, 300)
        # try to preset the dialog to the user's media folder since most modern distros mount removeable media under /run/media/username
        user_run_path = f"/run/media/{os.getlogin()}"
        alt_user_run_path = f"/run/user/{os.getuid()}/media/{os.getlogin()}"
        if os.path.exists(user_run_path):
            dialog.set_current_folder(user_run_path)
        elif os.path.exists(alt_user_run_path):
            dialog.set_current_folder(alt_user_run_path)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.tar_entry.set_text(dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

    def update_status(self, total, cur_count, current_file):
        step = 1.0 / (total)
        new_value = step * cur_count
        if new_value > 1.0:
            new_value = 1.0
        self.progressbar.set_fraction(new_value)
        filename = os.path.basename(current_file)
        GLib.idle_add(self.update_label_text, f"Copying {filename} ({cur_count}/{total})")

    def update_label_text(self, text):
        self.status.set_text(text)
        
    def get_file_list(self, source):
        global all_files
        for root, dirs, files in os.walk(source, topdown=False):
            for name in files:
                if name.endswith(".mp3"):
                    all_files.append(os.path.join(root, name))
    
    def copy_files(self):
        source = self.src_entry.get_text()
        target = self.tar_entry.get_text()
        cur_count = 0
        total_count = 0
        Thread(target=self.get_file_list(source)).start()
        
        if not all_files:
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="No MP3 Files Found",)
            dialog.format_secondary_text("No MP3 files found in the selected source folder.")
            dialog.run()
            dialog.destroy()
            return
 
        total_count = len(all_files)
        random.shuffle(all_files) 
        for file in all_files:
            file_name = os.path.basename(file)
            stripped_name = re.sub(r'^[\W\d_]+', '', file_name)
            new_filename = f"{str(cur_count)} {stripped_name}"
            file_size = os.path.getsize(file)
            free_space = self.get_free_space(target)
            if file_size > free_space:
                dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Insufficient Space",)
                dialog.format_secondary_text("There is not enough space on the target device to copy the file.")
                dialog.run()
                dialog.destroy()
                self.reset_form()
                return
            else:
                self.update_status(total_count +1, cur_count, file)
                Thread(target=self.copy_file(file, os.path.join(target, new_filename))).start()
                cur_count += 1
            
        self.progressbar.set_fraction(0)
        self.status.set_text("Shuffle complete!")
        self.shuffle_button.set_sensitive (True)
        self.about_button.set_sensitive (True)
        all_files.clear() # Clear the list for the next shuffle

    def reset_form(self):
        self.progressbar.set_fraction(0)
        self.status.set_text("Ready to shuffle!")
        self.shuffle_button.set_sensitive(True)
        self.about_button.set_sensitive(True)
        global all_files
        all_files.clear()

    def copy_file(self, file, target):
            try:
                # Copy the file to the target directory
                shutil.copy(file, target)
                # print(f"Copying {file} to {target}") # for debugging
                # time.sleep(.05)  # Simulate time taken to copy file for debugging

            except Exception as e:
                dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Copy Error",)
                dialog.format_secondary_text(f"Could not copy file. Error{e}")
                dialog.run()
                dialog.destroy()
                return
            
    def get_free_space(self, path):
        """
        Returns free disk space in bytes for a given path.
        """
        total, used, free = shutil.disk_usage(path)
        return free
        
    def shuffle(self, widget):
        source = self.src_entry.get_text()
        target = self.tar_entry.get_text()
        if source and target:
            if source != target:
                self.shuffle_button.set_sensitive (False)
                self.about_button.set_sensitive (False)
                self.progressbar.set_fraction(0)
                self.status.set_text("Getting list of files to copy...")
                Thread(target=self.copy_files).start()
            else:
                dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Selection Error",)
                dialog.format_secondary_text("The target cannot be the same as the source.")
                dialog.run()
                dialog.destroy()

        else:
            dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Selection Error",)
            dialog.format_secondary_text("You must select a source and a target")
            dialog.run()
            dialog.destroy()
            return
        
def main():
    win = ShufflerWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()