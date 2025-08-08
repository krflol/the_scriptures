# Scripture Viewer

This is a simple, self-contained web application to read and search the scriptures compiled from your Obsidian vault. It is a single HTML file that contains all the necessary data, styling, and logic, so it can be opened in any web browser without needing a web server.

## How to Use

1.  **Update the Application:**
    Whenever you make changes to your scripture files in Obsidian, you need to rebuild the `index.html` file.
    Open a terminal in the root directory of your project (`the_scriptures`) and run the following command:
    ```bash
    python scripture_viewer/build.py
    ```
    This will scan your `The Tanak` directory and regenerate the `scripture_viewer/index.html` file with the latest content.

2.  **View the Application:**
    Simply open the `index.html` file in your web browser.
    ```bash
    # On most systems, you can open it directly from the terminal:
    open scripture_viewer/index.html
    # Or on Windows:
    start scripture_viewer/index.html
    # Or on Linux:
    xdg-open scripture_viewer/index.html
    ```
    Alternatively, just navigate to the `scripture_viewer` folder on your computer and double-click the `index.html` file.