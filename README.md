# TkPrinter Tutorial

A minimal tkinter app that demonstrates how to display a pandas DataFrame and send it to a physical printer — working on both **macOS** and **Windows 11**.

## Purpose

Printing a DataFrame from a desktop app is a common need, but most resources cover either web-based solutions or platform-specific code. This tutorial provides a single, concise Python file that handles cross-platform printing with no complex dependencies.

The sample scenario is a **karate tournament error report**: a list of competitors where some registration fields (name, height, weight, belt rank, dojo) are missing. Tournament organizers print the report so staff can call each competitor's dojo to get the correct information.

## What You'll Learn

1. **Displaying a DataFrame in tkinter** — using a `ttk.Treeview` widget as a table with column headers and a scrollbar
2. **Formatting a DataFrame for print** — converting it to a fixed-width text layout with a title and legend using `df.to_string()`
3. **Cross-platform printing** — sending text to the default system printer on macOS and Windows without third-party print libraries
4. **Structuring a tkinter app** — organizing a GUI application into clear sections (data, logic, UI, entry point)

## How Printing Works

| Platform | Method | Details |
|----------|--------|---------|
| macOS    | `lpr`  | Pipes text to the built-in CUPS print command via `subprocess` — no temp file needed |
| Windows  | PowerShell `Out-Printer` | Writes a temp file, then runs `Get-Content <file> \| Out-Printer` via `subprocess` — built-in on Windows 11, no extra packages |
| Linux    | `lpr`  | Same approach as macOS (requires CUPS) |

## Requirements

- **Python 3.8+**
- **pandas** — `pip install pandas`
- **tkinter** — included with standard Python installations

No platform-specific packages are required. Both the macOS and Windows printing methods use tools built into the operating system.

## Quick Start

```bash
# Install the only dependency
pip install pandas

# Run the app
python tkprinter_tutorial.py
```

Click **Print Report** to send the missing-information table to your default printer.

## Code Structure

The tutorial is a single file (`tkprinter_tutorial.py`) organized into four clearly commented sections:

```
Section 1 — Sample Data
    COMPETITORS list and build_dataframe() function.
    15 competitor records with deliberately missing fields marked as '---'.

Section 2 — Printing Logic
    format_for_print()  — builds a print-ready text string from the DataFrame.
    send_to_printer()   — detects the OS and routes to the appropriate print command.

Section 3 — Tkinter Application
    TournamentApp class with:
      _build_header()   — title and subtitle labels
      _build_treeview() — scrollable table displaying the DataFrame
      _build_footer()   — status bar (record/error counts) and Print button
      _on_print()       — button handler that formats and prints

Section 4 — Entry Point
    main() function that builds the DataFrame and launches the app.
```

## Adapting for Your Own Project

The printing logic is intentionally decoupled from the UI. To reuse it in your own code:

1. **Format your data** — call `df.to_string()` or build any plain-text layout
2. **Print it** — pass the string to `send_to_printer()`

```python
from tkprinter_tutorial import format_for_print, send_to_printer

text = your_dataframe.to_string()
send_to_printer(text)
```

## License

This project is licensed under the [MIT License](LICENSE).
