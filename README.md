# MP3 Shuffler

A lot of bluetooth speakers that feature MP3 playback lack a shuffle function. MP3 Shuffler is a simple application that allows users to randomly shuffle and copy MP3 files from a source directory to a target device or directory. MP3 shuffler shuffles the files in addition to copying randomly as some players play by sorted file date instead of filename. The application features a user-friendly graphical interface built with the Gtk 3.0 framework.

## Features

- Select source and target directories.
- Randomly copy MP3 files from the source to the target directory.
- Progress bar to indicate the copying status.
- Error handling for file copying issues.

## Requirements

To run this application, you need to have Python installed along with the following dependencies:

- Gtk libraries (included on Gnome desktops)
- At least Python 3.8
- Other dependencies listed in `requirements.txt`

## Installation

### Using Flatpak

1. Ensure you have Flatpak installed on your system.
2. Navigate to the `flatpak` directory in your terminal.
3. Build the Flatpak package using the following command:

   ```
   flatpak-builder --force-clean build-dir flatpak/manifest.json
   ```

4. Install the application with:

   ```
   flatpak install build-dir
   ```

5. Run the application using:

   ```
   flatpak run org.flatpak.mp3shuffler
   ```

### Running from Source

If you prefer to run the application directly from the source:

1. Clone the repository or download the source code.
2. Navigate to the `src` directory.
3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Run the application:

   ```
   python shuffler_gtk.py
   ```

## Usage

1. Launch the application.
2. Select the source directory containing your MP3 files.
3. Select the target directory where you want to copy the shuffled files.
4. Click on the "Shuffle to Target" button to start the process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
