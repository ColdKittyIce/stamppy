#!/usr/bin/env python3
"""
MicroSIP → Audition / Audacity Marker Exporter

This script reads a raw MicroSIP call log (CSV), filters all answered calls
(incoming, outgoing, and outgoing voicemails) within a user-specified show window
(entered in GMT), and exports a tab-delimited file for Adobe Audition markers
or an Audacity label track.

Requirements:
  - Python 3.6+
  - pandas
  - pytz
"""
import pandas as pd
import pytz
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# --- Configuration ---
TZ = pytz.timezone('America/Detroit')
INPUT_TIME_FMT = "%a, %d %b %Y %H:%M:%S"
ACCENT_BG = '#87CEEB'   # sky blue background
ACCENT_FG = '#FFA500'   # mid orange accent


def secs_to_hms(sec):
    td = timedelta(seconds=int(sec))
    hrs, rem = divmod(td.seconds, 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs}:{mins:02d}:{secs:02d}"


def parse_gmt_to_local(dt_str):
    naive = datetime.strptime(dt_str, INPUT_TIME_FMT)
    utc_dt = pytz.utc.localize(naive)
    return utc_dt.astimezone(TZ)


def human_duration(delta):
    hrs, rem = divmod(int(delta.total_seconds()), 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs} hours, {mins} minutes, {secs} seconds"


class MarkerExporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroSIP Marker Exporter")
        self.df = None
        self.out_df = None
        self._apply_styles()
        self._build_ui()

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Header.TLabel', background=ACCENT_BG,
                        foreground='black', font=('Arial',14,'bold'), padding=10)
        style.configure('TButton', font=('Arial',10,'bold'))
        style.configure('Accent.TButton', background=ACCENT_FG, foreground='white')
        style.map('Accent.TButton', background=[('active','#EF7B00')])
        style.configure('Treeview.Heading', background=ACCENT_BG,
                        foreground='black', font=('Arial',10,'bold'))

    def _build_ui(self):
        header = ttk.Label(self.root, text="MicroSIP → Audition/Audacity Export",
                           style='Header.TLabel')
        header.pack(fill='x')

        frame_top = ttk.Frame(self.root, padding=10)
        frame_top.pack(fill='x')
        ttk.Label(frame_top, text="Show Start (GMT):").grid(row=0, column=0,
                           sticky='e', padx=5, pady=2)
        self.start_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.start_var, width=25)
        ttk.Entry(frame_top, textvariable=self.start_var, width=25).grid(
            row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_top, text="Show End (GMT):").grid(row=1, column=0,
                           sticky='e', padx=5, pady=2)
        self.end_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.end_var, width=25)
        ttk.Entry(frame_top, textvariable=self.end_var, width=25).grid(
            row=1, column=1, padx=5, pady=2)

        fmt_frame = ttk.LabelFrame(frame_top, text="Export Format", padding=5)
        fmt_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=2)
        self.format_var = tk.StringVar(value='audition')
        ttk.Radiobutton(fmt_frame, text='Audition', variable=self.format_var,
                        value='audition', command=self._on_format_change).pack(anchor='w')
        ttk.Radiobutton(fmt_frame, text='Audacity', variable=self.format_var,
                        value='audacity', command=self._on_format_change).pack(anchor='w')

        self.duration_label = ttk.Label(frame_top, text="Duration: —")
        self.duration_label.grid(row=2, column=0, columnspan=3, pady=5)

        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Load CSV", command=self.load_csv).pack(
            side='left', padx=5)
        self.export_btn = ttk.Button(btn_frame, text="Export",
                                     command=self.export_csv,
                                     state='disabled', style='Accent.TButton')
        self.export_btn.pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset).pack(
            side='left', padx=5)

        self.tree_frame = ttk.Frame(self.root, padding=10)
        self.tree_frame.pack(fill='both', expand=True)
        self.tree = None
        self._create_tree(['Name','Start','Duration Time','Format','Type','Description'])

    def _create_tree(self, cols):
        if self.tree:
            self.tree.destroy()
        self.tree = ttk.Treeview(self.tree_frame, columns=cols,
                                 show='headings', height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor='center')
        vsb = ttk.Scrollbar(self.tree_frame, orient='vertical',
                             command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)

    def load_csv(self):
        path = filedialog.askopenfilename(
            title="Select MicroSIP CSV",
            filetypes=[('CSV','*.csv')]
        )
        if not path:
            return
        try:
            self.df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Read Error", str(e))
            return
        self.process_data()

    def process_data(self):
        # clear preview
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.export_btn.state(['disabled'])
        self.out_df = None

        # parse show times
        start, end = self.start_var.get().strip(), self.end_var.get().strip()
        if not start or not end:
            messagebox.showerror("Input Error",
                                 "Enter both start and end times.")
            return
        try:
            show_start = parse_gmt_to_local(start)
            show_end = parse_gmt_to_local(end)
            if show_end <= show_start:
                raise ValueError
        except Exception:
            messagebox.showerror("Parse Error",
                                 "Check GMT time format.")
            return

        # display duration
        self.duration_label.config(
            text=f"Duration: {human_duration(show_end - show_start)}"
        )

        # convert and filter calls: ended or voicemail
        df2 = (
            self.df.assign(
                call_dt=pd.to_datetime(self.df['Time'], unit='s', utc=True)
                         .dt.tz_convert(TZ)
            )
            # include answered and voicemail calls
            .loc[lambda d: (
                d['Info'].eq('Call Ended') |
                d['Info'].str.contains('Voicemail', na=False)
            )]
            .loc[lambda d: (
                (d['call_dt'] >= show_start) &
                (d['call_dt'] <= show_end)
            )]
            .sort_values('call_dt')
        )
        if df2.empty:
            messagebox.showinfo("No Calls",
                                 "No matching calls.")
            return

        # build rows for export
        rows = []
        is_audacity = (self.format_var.get() == 'audacity')
        for idx, row in enumerate(df2.itertuples(), start=1):
            rel = (row.call_dt - show_start).total_seconds()
            dur = row.Duration
            if is_audacity:
                rows.append({
                    'Start': f"{rel:.3f}",
                    'End':   f"{rel + dur:.3f}",
                    'Label': f"Marker {idx}"
                })
            else:
                rows.append({
                    'Name':          f"Marker {idx}",
                    'Start':         secs_to_hms(rel),
                    'Duration Time': secs_to_hms(dur),
                    'Format':        'decimal',
                    'Type':          'Cue',
                    'Description':   ''
                })
        self.out_df = pd.DataFrame(rows)

        # update preview
        cols = list(self.out_df.columns)
        self._create_tree(cols)
        for r in self.out_df.itertuples(index=False):
            self.tree.insert('', 'end', values=tuple(r))
        self.export_btn.state(['!disabled'])

    def export_csv(self):
        if self.out_df is None:
            return
        is_audacity = (self.format_var.get() == 'audacity')
        if is_audacity:
            default_ext = '.txt'
            file_types = [('Labels (tab-delimited)','*.txt'),
                          ('All files','*.*')]
            dlg_title = 'Save Audacity Label Track'
        else:
            default_ext = '.csv'
            file_types = [('Markers (tab-delimited)','*.csv'),
                          ('All files','*.*')]
            dlg_title = 'Save Audition Markers CSV'

        path = filedialog.asksaveasfilename(
            title=dlg_title,
            defaultextension=default_ext,
            filetypes=file_types
        )
        if not path:
            return
        try:
            self.out_df.to_csv(path, sep='\t', index=False)
            messagebox.showinfo("Exported",
                                f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Write Error", str(e))

    def _on_format_change(self):
        if self.df is not None:
            self.process_data()

    def reset(self):
        self.start_var.set('')
        self.end_var.set('')
        self.duration_label.config(text="Duration: —")
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.export_btn.state(['disabled'])
        self.out_df = None


def main():
    root = tk.Tk()
    root.geometry('800x600')
    app = MarkerExporterApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
