import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import tkcalendar

from pipeline import process_file, read_and_validate_file, write_output, plot_data


class ReservoirApp:
    def __init__(self, root):
        self.root = root
        self.root.title('SWRCB 30DayRule Calculator')
        self.root.resizable(False, False)

        style = ttk.Style(root)
        style.theme_use('default')

        self.background_color = '#f3f6f8'
        self.panel_color = '#ffffff'
        self.accent_color = '#1f5f8b'
        self.text_color = '#1f2933'
        self.muted_text = '#52606d'
        self.border_color = '#d9e2ec'
        self.success_color = '#1f7a4d'
        self.warning_color = '#b44d12'
        self.button_text_on_light = '#102a43'
        self.ready_button = '#1f7a4d'
        self.inactive_button = '#e8eef3'
        self.inactive_button_text = '#7b8794'
        self.neutral_button = '#d9e2ec'
        self.neutral_button_hover = '#c7d3df'

        self.selected_path = tk.StringVar(value='')
        self.selected_name = tk.StringVar(value='No file selected yet')
        self.status_text = tk.StringVar(value='Choose a .csv or .xlsx input file to begin.')
        self.selected_date_label = tk.StringVar(value='Default start date')
        self.selected_date_text = tk.StringVar(value='Select a valid file')

        self.process_button_state = {'mode': 'inactive'}

        self.path_label = None
        self.status_label = None
        self.choose_button = None
        self.reset_button = None
        self.process_button = None
        self.calendar = None
        self.calendar_container = None
        self.calendar_overlay = None

        self.root.configure(bg=self.background_color)
        self.content_frame = tk.Frame(root, bg=self.background_color, padx=24, pady=20)
        self.content_frame.pack(fill='both', expand=True)

        self.render_main_view()
        self.root.after(10, lambda: (self.root.lift(), self.root.focus_force()))

    def clear_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def make_action_button(self, parent, text, command, width, bg_color, fg_color, hover_bg=None, cursor='hand2'):
        frame = tk.Frame(parent, bg=bg_color, padx=2, pady=2, cursor=cursor)
        label = tk.Label(
            frame,
            text=text,
            width=width,
            bg=bg_color,
            fg=fg_color,
            padx=10,
            pady=8,
            cursor=cursor,
        )
        label.pack()
        state = {'enabled': True}

        def set_colors(background, foreground, next_cursor):
            frame.configure(bg=background, cursor=next_cursor)
            label.configure(bg=background, fg=foreground, cursor=next_cursor)

        def on_enter(_event):
            if hover_bg and label.cget('cursor') == 'hand2':
                set_colors(hover_bg, label.cget('fg'), 'hand2')

        def on_leave(_event):
            if label.cget('cursor') == 'hand2':
                set_colors(bg_color, label.cget('fg'), 'hand2')

        def on_click(_event):
            if state['enabled']:
                command()

        label.bind('<Enter>', on_enter)
        label.bind('<Leave>', on_leave)
        label.bind('<Button-1>', on_click)

        def configure_button(background=None, foreground=None, next_cursor=None, enabled=None):
            nonlocal bg_color
            if background is not None:
                bg_color = background
            if foreground is None:
                foreground = label.cget('fg')
            if next_cursor is None:
                next_cursor = label.cget('cursor')
            if enabled is not None:
                state['enabled'] = enabled
            set_colors(bg_color, foreground, next_cursor)

        frame.configure_button = configure_button
        return frame

    def make_card(self, parent, padx=18, pady=16):
        return tk.Frame(
            parent,
            bg=self.panel_color,
            highlightbackground=self.border_color,
            highlightthickness=1,
            padx=padx,
            pady=pady,
        )

    def render_main_view(self):
        self.clear_view()
        self.reset_state_vars()

        self.build_header()

        top_frame = tk.Frame(self.content_frame, bg=self.background_color)
        top_frame.pack(fill='x')

        step1_card = self.make_card(top_frame)
        step1_card.pack(side=tk.LEFT, fill='y', pady=(0, 12))

        step2_card = self.make_card(top_frame)
        step2_card.pack(side=tk.LEFT, fill='y', padx=(12, 12), pady=(0, 12))

        step3_card = self.make_card(top_frame)
        step3_card.pack(side=tk.RIGHT, fill='y', pady=(0, 12))

        footer_card = self.make_card(self.content_frame)
        footer_card.pack(fill='x')

        self.build_step1_card(step1_card)
        self.build_step2_card(step2_card)
        self.build_step3_card(step3_card)
        self.build_footer(footer_card)
        self.show_calendar_overlay()

    def reset_state_vars(self):
        self.selected_path.set('')
        self.selected_name.set('No file selected yet')
        self.status_text.set('Choose a .csv or .xlsx input file to begin.')
        self.selected_date_label.set('Default start date')
        self.selected_date_text.set('Select a valid file')
        self.process_button_state = {'mode': 'inactive'}

    def build_header(self):
        header_frame = tk.Frame(self.content_frame, bg=self.background_color)
        header_frame.pack(fill='x', pady=(0, 14))

        tk.Label(
            header_frame,
            text='Reservoir Data Processor',
            font=('Helvetica', 20, 'bold'),
            bg=self.background_color,
            fg=self.text_color,
        ).pack(anchor='w')
        tk.Label(
            header_frame,
            text='Choose an input file first, then process it and save the output CSV.',
            font=('Helvetica', 11),
            bg=self.background_color,
            fg=self.muted_text,
        ).pack(anchor='w', pady=(3, 0))

    def build_step1_card(self, parent):
        tk.Label(
            parent,
            text='Step 1',
            font=('Helvetica', 10, 'bold'),
            bg=self.panel_color,
            fg=self.accent_color,
        ).pack(anchor='w')
        tk.Label(
            parent,
            text='Choose your input file',
            font=('Helvetica', 14, 'bold'),
            bg=self.panel_color,
            fg=self.text_color,
        ).pack(anchor='w', pady=(4, 4))
        tk.Label(
            parent,
            text='Pick the reservoir dataset you want to process.',
            font=('Helvetica', 10),
            bg=self.panel_color,
            fg=self.muted_text,
        ).pack(anchor='w', pady=(0, 5))
        tk.Label(
            parent,
            text='Accepted input: .csv or .xlsx with Date, Year, Month, and Reservoir Volume.',
            wraplength=660,
            justify='left',
            font=('Helvetica', 9),
            bg=self.panel_color,
            fg=self.muted_text,
        ).pack(anchor='w', pady=(0, 10))

        file_card = tk.Frame(
            parent,
            bg='#f9fbfc',
            highlightbackground=self.border_color,
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        file_card.pack(fill='x', pady=(0, 12))

        tk.Label(
            file_card,
            text='Selected file',
            font=('Helvetica', 10, 'bold'),
            bg='#f9fbfc',
            fg=self.muted_text,
        ).pack(anchor='w')
        tk.Label(
            file_card,
            textvariable=self.selected_name,
            wraplength=660,
            justify='left',
            font=('Helvetica', 12, 'bold'),
            bg='#f9fbfc',
            fg=self.text_color,
        ).pack(anchor='w', pady=(4, 4))

        self.path_label = tk.Label(
            file_card,
            text='No file path available yet',
            wraplength=370,
            justify='left',
            font=('Helvetica', 10),
            bg='#f9fbfc',
            fg=self.muted_text,
        )
        self.path_label.pack(anchor='w')

        button_row = tk.Frame(parent, bg=self.panel_color)
        button_row.pack(fill='x', pady=(0, 10))

        self.choose_button = self.make_action_button(
            button_row,
            'Choose Input File',
            self.choose_input_file,
            18,
            self.neutral_button,
            self.text_color,
            hover_bg=self.neutral_button_hover,
            cursor='hand2',
        )
        self.choose_button.pack(side='left', padx=(0, 10))

        self.reset_button = self.make_action_button(
            button_row,
            'Clear Selection',
            self.reset_selection,
            16,
            self.inactive_button,
            self.inactive_button_text,
            hover_bg=self.neutral_button_hover,
            cursor='arrow',
        )
        self.reset_button.pack(side='left', padx=(0, 10))

    def build_step2_card(self, parent):
        tk.Label(
            parent,
            text='Step 2',
            font=('Helvetica', 10, 'bold'),
            bg=self.panel_color,
            fg=self.accent_color,
        ).pack(anchor='w')
        tk.Label(
            parent,
            text='Choose Start Date',
            font=('Helvetica', 14, 'bold'),
            bg=self.panel_color,
            fg=self.text_color,
        ).pack(anchor='w', pady=(4, 4))
        tk.Label(
            parent,
            text='Opt to pick a different start date than the beginning of the file.',
            font=('Helvetica', 10),
            bg=self.panel_color,
            fg=self.muted_text,
        ).pack(anchor='w', pady=(0, 10))

        date_graphic = tk.Frame(
            parent,
            bg='#f9fbfc',
            highlightbackground=self.border_color,
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        date_graphic.pack(fill='x', pady=(0, 10))

        date_summary_row = tk.Frame(date_graphic, bg='#f9fbfc')
        date_summary_row.pack(fill='x')

        tk.Label(
            date_summary_row,
            textvariable=self.selected_date_label,
            font=('Helvetica', 10, 'bold'),
            bg='#f9fbfc',
            fg=self.muted_text,
        ).pack(side=tk.LEFT, anchor='w')
        tk.Label(
            date_summary_row,
            textvariable=self.selected_date_text,
            font=('Helvetica', 12, 'bold'),
            bg='#f9fbfc',
            fg=self.text_color,
        ).pack(side=tk.RIGHT, anchor='e')

        self.calendar_container = tk.Frame(parent, bg=self.panel_color)
        self.calendar_container.pack(padx=10, pady=10)
        self.calendar = tkcalendar.Calendar(self.calendar_container, selectmode='day')
        self.calendar.pack()
        self.build_calendar_overlay()

    def build_calendar_overlay(self):
        self.calendar_overlay = tk.Frame(self.calendar_container, bg=self.inactive_button, cursor='arrow')
        overlay_label = tk.Label(
            self.calendar_overlay,
            text='Select a valid file to enable the calendar',
            wraplength=190,
            justify='center',
            font=('Helvetica', 10),
            bg=self.inactive_button,
            fg=self.inactive_button_text,
            cursor='arrow',
        )
        overlay_label.place(relx=0.5, rely=0.5, anchor='center')
        self.calendar_overlay.bind('<Button-1>', self.on_disabled_calendar_clicked)
        overlay_label.bind('<Button-1>', self.on_disabled_calendar_clicked)

    def build_step3_card(self, parent):
        tk.Label(
            parent,
            text='Step 3',
            font=('Helvetica', 10, 'bold'),
            bg=self.panel_color,
            fg=self.accent_color,
        ).pack(anchor='w')
        tk.Label(
            parent,
            text='Process and save output',
            font=('Helvetica', 14, 'bold'),
            bg=self.panel_color,
            fg=self.text_color,
        ).pack(anchor='w', pady=(4, 4))
        tk.Label(
            parent,
            text='After processing, you will choose where to save the output CSV.',
            font=('Helvetica', 10),
            bg=self.panel_color,
            fg=self.muted_text,
        ).pack(anchor='w', pady=(0, 10))

        self.process_button = self.make_action_button(
            parent,
            'Process File',
            self.process_selected_file,
            16,
            self.inactive_button,
            self.inactive_button_text,
            hover_bg=self.ready_button,
            cursor='arrow',
        )
        self.process_button.pack(anchor='w', pady=(0, 8))

    def build_footer(self, parent):
        status_footer = tk.Frame(parent, bg=self.panel_color)
        status_footer.pack(fill='x', pady=(2, 0))

        self.status_label = tk.Label(
            status_footer,
            textvariable=self.status_text,
            wraplength=680,
            justify='left',
            font=('Helvetica', 10, 'bold'),
            bg=self.panel_color,
            fg=self.accent_color,
        )
        self.status_label.pack(side=tk.BOTTOM, anchor='w')

    def update_status(self, message, color=None):
        self.status_text.set(message)
        self.status_label.configure(fg=color or self.accent_color)

    def set_process_button_style(self, mode):
        self.process_button_state['mode'] = mode
        if mode == 'ready':
            self.process_button.configure_button(self.ready_button, 'white', 'hand2', True)
        elif mode == 'busy':
            self.process_button.configure_button('#9fb3c8', self.button_text_on_light, 'arrow', False)
        else:
            self.process_button.configure_button(self.inactive_button, self.inactive_button_text, 'arrow', True)

    def show_calendar_overlay(self):
        self.calendar_container.update_idletasks()
        self.calendar_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.calendar_overlay.lift()

    def hide_calendar_overlay(self):
        self.calendar_overlay.place_forget()

    def on_disabled_calendar_clicked(self, _event=None):
        self.update_status('Select a valid input file before choosing a start date.', self.warning_color)

    def reset_selection(self):
        if not self.selected_path.get():
            self.update_status('There is no selected input file to clear.', self.warning_color)
            return

        self.selected_path.set('')
        self.selected_name.set('No file selected yet')
        self.path_label.configure(text='No file path available yet')
        self.selected_date_label.set('Default start date')
        self.selected_date_text.set('Select a valid file')
        self.show_calendar_overlay()
        self.reset_button.configure_button(self.inactive_button, self.inactive_button_text, 'arrow', True)
        self.set_process_button_style('inactive')
        self.update_status('Choose a .csv or .xlsx input file to begin.')

    def update_selected_date_display(self, selected_date, label_text='Selected start date'):
        self.selected_date_label.set(label_text)
        self.selected_date_text.set(selected_date.strftime('%b %d, %Y'))

    def on_calendar_selected(self, _event=None):
        self.update_selected_date_display(self.calendar.selection_get())

    def update_calendar_bounds(self, df):
        date_values = df['Date'].dt.date
        min_date = date_values.min()
        max_date = date_values.max()

        self.calendar.destroy()
        self.calendar = tkcalendar.Calendar(
            self.calendar_container,
            selectmode='day',
            year=min_date.year,
            month=min_date.month,
            day=min_date.day,
            mindate=min_date,
            maxdate=max_date,
        )
        self.calendar.pack()
        self.calendar.selection_set(min_date)
        self.calendar.bind('<<CalendarSelected>>', self.on_calendar_selected)
        self.update_selected_date_display(min_date, 'Default start date')
        self.hide_calendar_overlay()
        return min_date, max_date

    def choose_input_file(self):
        filepath = filedialog.askopenfilename(
            title='Select Input File',
            filetypes=[('Data files', '*.csv *.xlsx'), ('CSV files', '*.csv'), ('Excel files', '*.xlsx')],
        )
        self.root.lift()
        self.root.focus_force()
        if not filepath:
            self.update_status('File selection cancelled. Choose an input file when you are ready.', self.warning_color)
            return

        self.selected_path.set(filepath)
        self.selected_name.set(os.path.basename(filepath))
        self.path_label.configure(text=os.path.normpath(filepath))
        self.reset_button.configure_button(self.neutral_button, self.text_color, 'hand2', True)

        try:
            df = read_and_validate_file(filepath)
            min_date, max_date = self.update_calendar_bounds(df)
        except Exception as exc:
            self.reset_selection()
            self.choose_button.configure_button(self.neutral_button, self.text_color, 'hand2', True)
            self.update_status(
                'Validation failed. Review the error message and adjust the input file if needed.',
                self.warning_color,
            )
            messagebox.showerror('Validation Failed', str(exc))
            self.root.lift()
            self.root.focus_force()
            return

        self.set_process_button_style('ready')
        self.update_status(
            f'Valid file selected. Calendar range: {min_date:%b %d, %Y} to {max_date:%b %d, %Y}.',
            self.success_color,
        )

    def process_selected_file(self):
        input_filepath = self.selected_path.get()
        if not input_filepath:
            self.update_status('Select an input CSV or Excel file first.', self.warning_color)
            return

        save_path = filedialog.asksaveasfilename(
            title='Save Output CSV As',
            defaultextension='.csv',
            initialfile='CALCULATED_DATA.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
        )
        self.root.lift()
        self.root.focus_force()
        if not save_path:
            self.update_status('Save cancelled. The input file is still selected and ready to process.', self.warning_color)
            return

        self.set_busy_state()

        try:
            start_date = self.calendar.selection_get()
            df = process_file(input_filepath, start_date)
            write_output(df, save_path)
            plot_data(df)
        except Exception as exc:
            self.restore_ready_state_after_error()
            self.update_status('Processing failed. Review the error message and adjust the input file if needed.', self.warning_color)
            messagebox.showerror('Processing Failed', str(exc))
            self.root.lift()
            self.root.focus_force()
            return

        self.render_completion_view(save_path)

    def set_busy_state(self):
        self.set_process_button_style('busy')
        self.choose_button.configure_button(self.neutral_button, self.inactive_button_text, 'arrow', False)
        self.reset_button.configure_button(self.inactive_button, self.inactive_button_text, 'arrow', False)
        self.update_status('Processing file. This may take a moment.', self.accent_color)
        self.root.update_idletasks()

    def restore_ready_state_after_error(self):
        self.choose_button.configure_button(self.neutral_button, self.text_color, 'hand2', True)
        self.reset_button.configure_button(self.neutral_button, self.text_color, 'hand2', True)
        self.set_process_button_style('ready')

    def render_completion_view(self, output_filepath):
        self.clear_view()

        completion_card = self.make_card(self.content_frame, padx=24, pady=24)
        completion_card.pack(fill='both', expand=True)

        tk.Label(
            completion_card,
            text='Processing Complete',
            font=('Helvetica', 20, 'bold'),
            bg=self.panel_color,
            fg=self.success_color,
        ).pack(anchor='w')
        tk.Label(
            completion_card,
            text='The output file was created successfully.',
            font=('Helvetica', 11),
            bg=self.panel_color,
            fg=self.text_color,
        ).pack(anchor='w', pady=(8, 20))
        tk.Label(
            completion_card,
            text='Saved output',
            font=('Helvetica', 10, 'bold'),
            bg=self.panel_color,
            fg=self.muted_text,
        ).pack(anchor='w')
        tk.Label(
            completion_card,
            text=output_filepath,
            wraplength=660,
            justify='left',
            font=('Helvetica', 11),
            bg=self.panel_color,
            fg=self.text_color,
        ).pack(anchor='w', pady=(6, 24))

        action_row = tk.Frame(completion_card, bg=self.panel_color)
        action_row.pack(anchor='w')
        self.make_action_button(
            action_row,
            'Process Another File',
            self.render_main_view,
            20,
            self.neutral_button,
            self.text_color,
            hover_bg=self.neutral_button_hover,
            cursor='hand2',
        ).pack(side='left', padx=(0, 10))
        self.make_action_button(
            action_row,
            'Close',
            self.root.destroy,
            12,
            self.neutral_button,
            self.text_color,
            hover_bg=self.neutral_button_hover,
            cursor='hand2',
        ).pack(side='left')


def run_gui():
    root = tk.Tk()
    ReservoirApp(root)
    root.mainloop()
