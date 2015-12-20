import os
import sublime
import sublime_plugin
from subprocess import Popen, PIPE


class GotoWindowCommand(sublime_plugin.WindowCommand):
    def run(self):
        folders = self._get_folders()
        
        folders_alone = [x for (x, y) in folders]
        folders_for_list = []
        for folder in folders_alone:
            folders_for_list.append([os.path.basename(folder), folder])

        self.window.show_quick_panel(folders_for_list, self.on_done, 0)

    def on_done(self, selected_index):
        current_index = self._get_current_index()
        if selected_index == -1 or current_index == selected_index:
            return

        folders = self._get_folders()
        window_index = folders[selected_index][1]
        window_to_move_to = sublime.windows()[window_index]

        self.focus(window_to_move_to)

    def focus(self, window_to_move_to):

        active_view = window_to_move_to.active_view()
        active_group = window_to_move_to.active_group()

        if sublime.platform() == 'osx':
            name = 'Sublime Text'
            if int(sublime.version()) < 3000:
                name = 'Sublime Text 2'

            cmd_context = {
                'window_filename': active_view.file_name().replace(os.getenv('HOME'), '~'),
                'name': name
            }

            cmd = """
                set window_filename to "{window_filename}"

                tell application "System Events"
                    tell process "{name}"
                        set menuItems to name of every menu item of menu 1 of menu bar item "Window" of menu bar 1
                        repeat with menuItem in menuItems
                            if {{menuItem starts with window_filename}} then
                                tell application "System Events" to tell process "Sublime Text"
                                    click menu item menuItem of menu 1 of menu bar item "Window" of menu bar 1
                                    tell application "{name}" to activate
                                end tell
                            end if
                        end repeat
                    end tell
                end tell
            """.format(**cmd_context)

            Popen(['/usr/bin/osascript', "-e", cmd], stdout=PIPE, stderr=PIPE)
            return

        # Calling focus then the command then focus again is needed to make this
        # work on Windows
        if active_view is not None:
            window_to_move_to.focus_view(active_view)
            window_to_move_to.run_command('focus_neighboring_group')
            window_to_move_to.focus_view(active_view)
            return

        if active_group is not None:
            window_to_move_to.focus_group(active_group)
            window_to_move_to.run_command('focus_neighboring_group')
            window_to_move_to.focus_group(active_group)

    def _get_current_index(self):
        active_window = sublime.active_window()
        windows = sublime.windows()
        current_index = -1
        for i, folder in enumerate(self._get_folders()):
            if windows[folder[1]] == active_window:
                current_index = i
                break

        return current_index

    def _get_folders(self):
        folders = []
        home = os.getenv('HOME')
        for i, window in enumerate(sublime.windows()):
            for folder in window.folders():
                if folder.startswith(home):
                    folder = folder.replace(home, '~')

                folders.append((folder, i))

        return sorted(folders)
