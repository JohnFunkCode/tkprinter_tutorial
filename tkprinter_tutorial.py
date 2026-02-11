"""
TkPrinter Tutorial — Printing a Pandas DataFrame on Windows & Mac
=================================================================
This tutorial app shows how to:
  1. Display a pandas DataFrame in a tkinter Treeview widget
  2. Format the DataFrame as a printable document
  3. Send it to the system printer (cross-platform)

The sample data represents karate tournament competitors with deliberately
missing fields — the kind of error report an organizer would print out
and hand to staff so they can call each competitor's dojo for corrections.

Requirements:
    pip install pandas

Platform notes:
    - macOS  : prints via the `lpr` command (built-in, no extras needed)
    - Windows: prints via PowerShell Out-Printer (built-in, no extras needed)
"""

import os
import platform
import subprocess
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk

import pandas as pd

# ---------------------------------------------------------------------------
# 1.  BUILD THE SAMPLE DATA
# ---------------------------------------------------------------------------
# Each dict is one competitor.  Empty strings ("") represent missing values
# that tournament organizers need to track down by contacting the dojo.

COMPETITORS = [
    {"first_name": "Akira",   "last_name": "Tanaka",    "height": "5'9\"",  "weight": "165",  "belt": "Black",  "dojo": "Rising Sun Dojo"},
    {"first_name": "Maria",   "last_name": "Garcia",    "height": "5'4\"",  "weight": "",     "belt": "Brown",  "dojo": "Pacific Martial Arts"},
    {"first_name": "James",   "last_name": "",          "height": "6'1\"",  "weight": "190",  "belt": "Black",  "dojo": "Iron Fist Academy"},
    {"first_name": "",        "last_name": "Nguyen",    "height": "5'6\"",  "weight": "140",  "belt": "",       "dojo": "Dragon Spirit Karate"},
    {"first_name": "Sarah",   "last_name": "Johnson",   "height": "",       "weight": "130",  "belt": "Green",  "dojo": "Eastside Karate Club"},
    {"first_name": "Kenji",   "last_name": "Yamamoto",  "height": "5'7\"",  "weight": "155",  "belt": "Black",  "dojo": ""},
    {"first_name": "Elena",   "last_name": "Petrov",    "height": "5'5\"",  "weight": "",     "belt": "",       "dojo": "Northern Wind Dojo"},
    {"first_name": "David",   "last_name": "Kim",       "height": "5'10\"", "weight": "170",  "belt": "Brown",  "dojo": "Summit Martial Arts"},
    {"first_name": "Fatima",  "last_name": "",          "height": "5'3\"",  "weight": "120",  "belt": "Purple", "dojo": "Crescent Moon Dojo"},
    {"first_name": "Carlos",  "last_name": "Rivera",    "height": "",       "weight": "",     "belt": "Blue",   "dojo": "Sol Karate Academy"},
    {"first_name": "",        "last_name": "O'Brien",   "height": "6'0\"",  "weight": "185",  "belt": "Black",  "dojo": "Celtic Tiger Dojo"},
    {"first_name": "Yuki",    "last_name": "Sato",      "height": "5'2\"",  "weight": "115",  "belt": "Brown",  "dojo": ""},
    {"first_name": "Marcus",  "last_name": "Thompson",  "height": "5'11\"", "weight": "175",  "belt": "",       "dojo": "Warrior Path Dojo"},
    {"first_name": "Lina",    "last_name": "Chen",      "height": "5'5\"",  "weight": "125",  "belt": "Green",  "dojo": "Jade Mountain Karate"},
    {"first_name": "Andre",   "last_name": "",          "height": "",       "weight": "200",  "belt": "White",  "dojo": "Metro Karate Club"},
]


def build_dataframe() -> pd.DataFrame:
    """Create a DataFrame and replace empty strings with a visible marker.

    We use '---' so missing values stand out both on screen and on paper.
    Using pandas' native NA would display as 'NaN', which is less clear
    for non-technical tournament staff reading a printout.
    """
    df = pd.DataFrame(COMPETITORS)

    # Pretty column headers for display and printing
    df.columns = ["First Name", "Last Name", "Height", "Weight", "Belt", "Dojo"]

    # Mark blanks so they're obvious on the printout
    df.replace("", "---", inplace=True)

    return df


# ---------------------------------------------------------------------------
# 2.  PRINTING LOGIC  (cross-platform)
# ---------------------------------------------------------------------------
# Strategy: write the DataFrame to a plain-text temp file, then hand it to
# the OS printing mechanism.  Plain text keeps things simple and avoids
# dependencies on HTML-to-PDF converters.


def format_for_print(df: pd.DataFrame) -> str:
    """Return a print-ready string with a title, the table, and a legend."""
    # pandas to_string() produces a fixed-width text table that prints well
    # on monospaced printer fonts.
    title = "KARATE TOURNAMENT — MISSING INFORMATION REPORT"
    separator = "=" * len(title)
    legend = (
        "NOTE: '---' indicates missing data.  "
        "Please contact the competitor's dojo to obtain correct information."
    )
    return f"{title}\n{separator}\n\n{df.to_string(index=False)}\n\n{legend}\n"


def send_to_printer(text: str) -> None:
    """Send a plain-text string to the default system printer.

    macOS  — pipes text to `lpr`, which talks to CUPS.
    Windows — writes a temp file and prints via PowerShell Out-Printer.

    Raises RuntimeError if printing fails so the caller can show an error dialog.
    """
    system = platform.system()

    if system == "Darwin":
        # ------- macOS -------
        # `lpr` is the standard CUPS command-line print utility.
        # Passing text via stdin avoids needing a temp file on macOS.
        result = subprocess.run(
            ["lpr"],
            input=text.encode("utf-8"),
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode())

    elif system == "Windows":
        # ------- Windows -------
        # PowerShell's Out-Printer cmdlet sends text directly to the
        # default printer via the Windows print spooler.  It's built-in
        # on Windows 11 (PowerShell 5.1+), requires no extra packages,
        # and runs silently with no window flash.
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        try:
            tmp.write(text)
            tmp.close()  # flush & close before PowerShell reads it
            # Get-Content reads the file, Out-Printer sends it to the
            # default printer.  `-NoProfile` speeds up startup by
            # skipping the user's PowerShell profile scripts.
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"Get-Content '{tmp.name}' | Out-Printer",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
        finally:
            # Safe to delete — subprocess.run blocked until PowerShell finished
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
    else:
        # ------- Linux (bonus) -------
        # `lpr` also works on most Linux distros with CUPS installed.
        result = subprocess.run(
            ["lpr"],
            input=text.encode("utf-8"),
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode())


# ---------------------------------------------------------------------------
# 3.  TKINTER APPLICATION
# ---------------------------------------------------------------------------


class TournamentApp(tk.Tk):
    """Main application window.

    Layout (top to bottom):
        - Title label
        - Treeview showing the DataFrame
        - Status bar with record count
        - Print button
    """

    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__()
        self.df = df

        # -- Window setup --
        self.title("Karate Tournament — Missing Info Report")
        self.minsize(800, 400)

        self._build_ui()

    # ---- UI construction (separated for clarity) ----

    def _build_ui(self) -> None:
        """Build all widgets and layout."""
        self._build_header()
        self._build_treeview()
        self._build_footer()

    def _build_header(self) -> None:
        """Title label at the top of the window."""
        header = ttk.Label(
            self,
            text="Missing Information Report",
            font=("Helvetica", 16, "bold"),
        )
        header.pack(pady=(12, 4))

        subtitle = ttk.Label(
            self,
            text="Entries marked '---' need correction. Print this report and contact each dojo.",
            font=("Helvetica", 10),
        )
        subtitle.pack(pady=(0, 8))

    def _build_treeview(self) -> None:
        """Scrollable Treeview that displays the DataFrame rows.

        Treeview is tkinter's table widget.  Each column maps to a
        DataFrame column, and each row is inserted from df.itertuples().
        """
        # -- Container frame with scrollbar --
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create Treeview — "show='headings'" hides the default tree column
        columns = list(self.df.columns)
        self.tree = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree.yview)

        # -- Configure each column header and width --
        for col in columns:
            self.tree.heading(col, text=col)
            # Adjust width: Dojo names are longer, so give that column more space
            width = 160 if col == "Dojo" else 100
            self.tree.column(col, width=width, anchor=tk.W)

        # -- Populate rows from the DataFrame --
        # itertuples() is faster than iterrows() and gives named access,
        # but here we just need the values (skip index at position 0).
        for row in self.df.itertuples(index=False):
            self.tree.insert("", tk.END, values=list(row))

        self.tree.pack(fill=tk.BOTH, expand=True)

    def _build_footer(self) -> None:
        """Status bar and Print button at the bottom."""
        footer = ttk.Frame(self)
        footer.pack(fill=tk.X, padx=12, pady=8)

        # Count how many rows have at least one missing field
        missing_count = (self.df == "---").any(axis=1).sum()
        status_text = (
            f"{len(self.df)} competitors loaded  •  "
            f"{missing_count} records with missing data"
        )
        ttk.Label(footer, text=status_text).pack(side=tk.LEFT)

        # Print button — calls our cross-platform print function
        print_btn = ttk.Button(
            footer,
            text="Print Report",
            command=self._on_print,
        )
        print_btn.pack(side=tk.RIGHT)

    # ---- Event handlers ----

    def _on_print(self) -> None:
        """Handle the Print button click.

        Formats the DataFrame, sends it to the printer, and shows
        a success/error message.
        """
        text = format_for_print(self.df)
        try:
            send_to_printer(text)
            messagebox.showinfo("Print", "Report sent to printer.")
        except RuntimeError as e:
            messagebox.showerror("Print Error", f"Could not print:\n{e}")


# ---------------------------------------------------------------------------
# 4.  ENTRY POINT
# ---------------------------------------------------------------------------

def main() -> None:
    df = build_dataframe()
    app = TournamentApp(df)
    app.mainloop()


if __name__ == "__main__":
    main()
