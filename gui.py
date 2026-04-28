import os
import tkinter as tk
from tkinter import filedialog, messagebox

from pipeline import process_file, write_output


def run_gui():
    root = tk.Tk()
    root.title('SWRCB 30DayRule Calculator')
    # root.geometry('760x580')
    root.resizable(False, False)

    background_color = '#f3f6f8'
    panel_color = '#ffffff'
    accent_color = '#1f5f8b'
    text_color = '#1f2933'
    muted_text = '#52606d'
    border_color = '#d9e2ec'
    success_color = '#1f7a4d'
    warning_color = '#b44d12'
    button_text_on_light = '#102a43'
    ready_button = '#1f7a4d'
    inactive_button = '#e8eef3'
    inactive_button_text = '#7b8794'
    neutral_button = '#d9e2ec'
    neutral_button_hover = '#c7d3df'
    root.configure(bg=background_color)

    content_frame = tk.Frame(root, bg=background_color, padx=24, pady=20)
    content_frame.pack(fill='both', expand=True)

    selected_path = tk.StringVar(value='')
    accepted_text = (
        'Required columns: Date, Year, Month, and Reservoir Volume. '
        'Reservoir Volume may be numeric or formatted like "123,456".'
    )

    def clear_view():
        for widget in content_frame.winfo_children():
            widget.destroy()

    def make_action_button(parent, text, command, width, bg_color, fg_color, hover_bg=None, cursor='hand2'):
        frame = tk.Frame(parent, bg=bg_color, padx=2, pady=2)
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
            frame.configure(bg=background)
            label.configure(bg=background, fg=foreground, cursor=next_cursor)

        def on_enter(_event):
            if hover_bg and label.cget('cursor') == 'hand2':
                set_colors(hover_bg, label.cget('fg'), 'hand2')

        def on_leave(_event):
            if label.cget('cursor') == 'hand2':
                set_colors(bg_color, label.cget('fg'), 'hand2')

        def on_click(_event):
            if not state['enabled']:
                return
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

    def render_main_view():
        clear_view()
        # root.geometry('550x625')
        selected_path.set('')

        selected_name = tk.StringVar(value='No file selected yet')
        status_text = tk.StringVar(value='Choose a .csv or .xlsx input file to begin.')

        header_frame = tk.Frame(content_frame, bg=background_color)
        header_frame.pack(fill='x', pady=(0, 14))

        tk.Label(
            header_frame,
            text='Reservoir Data Processor',
            font=('Helvetica', 20, 'bold'),
            bg=background_color,
            fg=text_color,
        ).pack(anchor='w')
        tk.Label(
            header_frame,
            text='Choose an input file first, then process it and save the output CSV.',
            font=('Helvetica', 11),
            bg=background_color,
            fg=muted_text,
        ).pack(anchor='w', pady=(3, 0))

        step1_card = tk.Frame(
            content_frame,
            bg=panel_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=18,
            pady=16,
        )
        step1_card.pack(fill='x', pady=(0, 12))

        step2_card = tk.Frame(
            content_frame,
            bg=panel_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=18,
            pady=16,
        )
        step2_card.pack(fill='x', pady=(0, 12))

        footer_card = tk.Frame(
            content_frame,
            bg=panel_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=18,
            pady=16,
        )
        footer_card.pack(fill='x')

        tk.Label(
            step1_card,
            text='Step 1',
            font=('Helvetica', 10, 'bold'),
            bg=panel_color,
            fg=accent_color,
        ).pack(anchor='w')
        tk.Label(
            step1_card,
            text='Choose your input file',
            font=('Helvetica', 14, 'bold'),
            bg=panel_color,
            fg=text_color,
        ).pack(anchor='w', pady=(4, 4))
        tk.Label(
            step1_card,
            text='Pick the reservoir dataset you want to process.',
            font=('Helvetica', 10),
            bg=panel_color,
            fg=muted_text,
        ).pack(anchor='w', pady=(0, 5))

        tk.Label(
            step1_card,
            text='Accepted input: .csv or .xlsx with Date, Year, Month, and Reservoir Volume.',
            wraplength=660,
            justify='left',
            font=('Helvetica', 9),
            bg=panel_color,
            fg=muted_text,
        ).pack(anchor='w', pady=(0, 10))

        file_card = tk.Frame(
            step1_card,
            bg='#f9fbfc',
            highlightbackground=border_color,
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
            fg=muted_text,
        ).pack(anchor='w')
        tk.Label(
            file_card,
            textvariable=selected_name,
            wraplength=660,
            justify='left',
            font=('Helvetica', 12, 'bold'),
            bg='#f9fbfc',
            fg=text_color,
        ).pack(anchor='w', pady=(4, 4))
        path_label = tk.Label(
            file_card,
            text='No file path available yet',
            wraplength=370,
            justify='left',
            font=('Helvetica', 10),
            bg='#f9fbfc',
            fg=muted_text,
        )
        path_label.pack(anchor='w')

        button_row = tk.Frame(step1_card, bg=panel_color)
        button_row.pack(fill='x', pady=(0, 10))

        tk.Label(
            step2_card,
            text='Step 2',
            font=('Helvetica', 10, 'bold'),
            bg=panel_color,
            fg=accent_color,
        ).pack(anchor='w')
        tk.Label(
            step2_card,
            text='Process and save output',
            font=('Helvetica', 14, 'bold'),
            bg=panel_color,
            fg=text_color,
        ).pack(anchor='w', pady=(4, 4))
        tk.Label(
            step2_card,
            text='After processing, you will choose where to save the output CSV.',
            font=('Helvetica', 10),
            bg=panel_color,
            fg=muted_text,
        ).pack(anchor='w', pady=(0, 10))

        process_button_state = {'mode': 'inactive'}

        status_footer = tk.Frame(footer_card, bg=panel_color)

        status_label = tk.Label(
            status_footer,
            textvariable=status_text,
            wraplength=680,
            justify='left',
            font=('Helvetica', 10, 'bold'),
            bg=panel_color,
            fg=accent_color,
        )
        status_label.pack(anchor='w')

        def update_status(message, color=accent_color):
            status_text.set(message)
            status_label.configure(fg=color)

        def set_process_button_style(mode):
            process_button_state['mode'] = mode
            if mode == 'ready':
                process_button.configure_button(ready_button, 'white', 'hand2', True)
            elif mode == 'busy':
                process_button.configure_button('#9fb3c8', button_text_on_light, 'arrow', False)
            else:
                process_button.configure_button(inactive_button, inactive_button_text, 'arrow', True)

        def reset_selection():
            if not selected_path.get():
                # messagebox.showerror('No Selection', 'There is no selected input file to clear.')
                update_status('There is no selected input file to clear.', warning_color)
                return

            selected_path.set('')
            selected_name.set('No file selected yet')
            path_label.configure(text='No file path available yet')
            reset_button.configure_button(inactive_button, inactive_button_text, 'arrow', True)
            set_process_button_style('inactive')
            update_status('Choose a .csv or .xlsx input file to begin.')

        def choose_input_file():
            filepath = filedialog.askopenfilename(
                title='Select Input File',
                filetypes=[('Data files', '*.csv *.xlsx'), ('CSV files', '*.csv'), ('Excel files', '*.xlsx'), ('All files', '*.*')],
            )
            root.lift()
            root.focus_force()
            if not filepath:
                update_status('File selection cancelled. Choose an input file when you are ready.', warning_color)
                return

            selected_path.set(filepath)
            selected_name.set(os.path.basename(filepath))
            path_label.configure(text=os.path.normpath(filepath))
            reset_button.configure_button(neutral_button, text_color, 'hand2', True)
            set_process_button_style('ready')
            update_status('Click "Process File" and choose where to save the output CSV.', success_color)

        def process_selected_file():
            input_filepath = selected_path.get()
            if not input_filepath:
                # messagebox.showerror('Missing Input File', 'Select an input CSV or Excel file first.')
                update_status('Select an input CSV or Excel file first.', warning_color)
                return

            save_path = filedialog.asksaveasfilename(
                title='Save Output CSV As',
                defaultextension='.csv',
                initialfile='CALCULATED_DATA.csv',
                filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            )
            root.lift()
            root.focus_force()
            if not save_path:
                update_status('Save cancelled. The input file is still selected and ready to process.', warning_color)
                return

            set_process_button_style('busy')
            choose_button.configure_button(neutral_button, inactive_button_text, 'arrow', False)
            reset_button.configure_button(inactive_button, inactive_button_text, 'arrow', False)
            update_status('Processing file. This may take a moment.', accent_color)
            root.update_idletasks()

            try:
                df = process_file(input_filepath)
                write_output(df, save_path)
            except Exception as exc:
                choose_button.configure_button(neutral_button, text_color, 'hand2', True)
                reset_button.configure_button(neutral_button, text_color, 'hand2', True)
                set_process_button_style('ready')
                update_status('Processing failed. Review the error message and adjust the input file if needed.', warning_color)
                messagebox.showerror('Processing Failed', str(exc))
                root.lift()
                root.focus_force()
                return

            render_completion_view(save_path)

        choose_button = make_action_button(
            button_row,
            'Choose Input File',
            choose_input_file,
            18,
            neutral_button,
            text_color,
            hover_bg=neutral_button_hover,
            cursor='hand2',
        )
        choose_button.pack(side='left', padx=(0, 10))

        reset_button = make_action_button(
            button_row,
            'Clear Selection',
            reset_selection,
            16,
            inactive_button,
            inactive_button_text,
            hover_bg=neutral_button_hover,
            cursor='arrow',
        )
        reset_button.pack(side='left', padx=(0, 10))

        process_button = make_action_button(
            step2_card,
            'Process File',
            process_selected_file,
            16,
            inactive_button,
            inactive_button_text,
            hover_bg=ready_button,
            cursor='arrow',
        )
        process_button.pack(anchor='w', pady=(0, 8))

        status_footer.pack(fill='x', pady=(2, 0))

    def render_completion_view(output_filepath):
        clear_view()
        # root.geometry('550x275')

        completion_card = tk.Frame(
            content_frame,
            bg=panel_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=24,
            pady=24,
        )
        completion_card.pack(fill='both', expand=True)

        tk.Label(
            completion_card,
            text='Processing Complete',
            font=('Helvetica', 20, 'bold'),
            bg=panel_color,
            fg=success_color,
        ).pack(anchor='w')
        tk.Label(
            completion_card,
            text='The output file was created successfully.',
            font=('Helvetica', 11),
            bg=panel_color,
            fg=text_color,
        ).pack(anchor='w', pady=(8, 20))
        tk.Label(
            completion_card,
            text='Saved output',
            font=('Helvetica', 10, 'bold'),
            bg=panel_color,
            fg=muted_text,
        ).pack(anchor='w')
        tk.Label(
            completion_card,
            text=output_filepath,
            wraplength=660,
            justify='left',
            font=('Helvetica', 11),
            bg=panel_color,
            fg=text_color,
        ).pack(anchor='w', pady=(6, 24))

        action_row = tk.Frame(completion_card, bg=panel_color)
        action_row.pack(anchor='w')
        make_action_button(
            action_row,
            'Process Another File',
            render_main_view,
            20,
            neutral_button,
            text_color,
            hover_bg=neutral_button_hover,
            cursor='hand2',
        ).pack(side='left', padx=(0, 10))
        make_action_button(
            action_row,
            'Close',
            root.destroy,
            12,
            neutral_button,
            text_color,
            hover_bg=neutral_button_hover,
            cursor='hand2',
        ).pack(side='left')

    render_main_view()
    root.after(10, lambda: (root.lift(), root.focus_force()))
    root.mainloop()
