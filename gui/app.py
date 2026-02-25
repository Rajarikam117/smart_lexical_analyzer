import tkinter as tk
from tkinter import ttk, messagebox

try:
    # Preferred when package is run as a module
    from ..lexer.tokenizer import Tokenizer
except Exception:
    # Fallback when running this file directly (script mode)
    import sys, os
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if pkg_root not in sys.path:
        sys.path.insert(0, os.path.abspath(os.path.join(pkg_root, '..')))
    from smart_lexer.lexer.tokenizer import Tokenizer


class LexerApp:
    def __init__(self, root):
        self.root = root
        root.title('Smart Lexical Analyzer')
        root.geometry('1000x700')

        self.tokenizer = Tokenizer()
        self.last_analysis = {"tokens": [], "errors": []}

        # Main layout
        main = ttk.Frame(root)
        main.pack(fill='both', expand=True)

        # Left: editor
        editor_frame = ttk.Frame(main)
        editor_frame.pack(side='left', fill='both', expand=True)

        # Toolbar above editor
        toolbar = ttk.Frame(editor_frame)
        toolbar.pack(fill='x')

        ttk.Label(toolbar, text='Mode:').pack(side='left', padx=(4, 2))
        self.mode_var = tk.StringVar(value='AI Mode')
        mode_combo = ttk.Combobox(toolbar, textvariable=self.mode_var, values=['Manual Mode', 'AI Mode'], state='readonly', width=12)
        mode_combo.pack(side='left')

        analyze_btn = ttk.Button(toolbar, text='Analyze Code', command=self.analyze_code)
        analyze_btn.pack(side='left', padx=6)

        # Editor text
        self.text = tk.Text(editor_frame, wrap='none', undo=True)
        self.text.pack(fill='both', expand=True)
        self.text.tag_configure('error', background='#ffebeb')

        # Right: outputs
        right = ttk.Frame(main, width=420)
        right.pack(side='right', fill='y')

        # Tokens table
        ttk.Label(right, text='Tokens').pack(anchor='w', padx=5, pady=(6,0))
        tokens_frame = ttk.Frame(right)
        tokens_frame.pack(fill='both', padx=5)
        cols = ('type', 'value', 'line', 'column')
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=cols, show='headings', height=10)
        for c in cols:
            self.tokens_tree.heading(c, text=c.title())
        self.tokens_tree.column('type', width=100, anchor='w')
        self.tokens_tree.column('value', width=160, anchor='w')
        self.tokens_tree.column('line', width=60, anchor='center')
        self.tokens_tree.column('column', width=60, anchor='center')
        vsb = ttk.Scrollbar(tokens_frame, orient='vertical', command=self.tokens_tree.yview)
        hsb = ttk.Scrollbar(tokens_frame, orient='horizontal', command=self.tokens_tree.xview)
        self.tokens_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tokens_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tokens_frame.rowconfigure(0, weight=1)
        tokens_frame.columnconfigure(0, weight=1)

        # Make tokens table sortable by clicking headers
        for col in cols:
            # store a closure with the column name
            self.tokens_tree.heading(col, command=lambda c=col: self.sort_tokens(c))

        # Errors list
        ttk.Label(right, text='Errors').pack(anchor='w', padx=5, pady=(10,0))
        self.errors_list = tk.Listbox(right, height=8)
        self.errors_list.pack(fill='x', padx=5)
        self.errors_list.bind('<<ListboxSelect>>', self.on_error_select)

        ttk.Label(right, text='Suggestion:').pack(anchor='w', padx=5, pady=(6,0))
        self.suggestion_var = tk.StringVar(value='')
        self.suggestion_label = ttk.Label(right, textvariable=self.suggestion_var, wraplength=380)
        self.suggestion_label.pack(fill='x', padx=5)
        btn_frame = ttk.Frame(right)
        btn_frame.pack(padx=5, pady=6)
        self.preview_btn = ttk.Button(btn_frame, text='Preview Suggestion', command=self.preview_suggestion)
        self.preview_btn.grid(row=0, column=0, padx=(0,6))
        self.apply_btn = ttk.Button(btn_frame, text='Apply Suggestion', command=self.apply_suggestion)
        self.apply_btn.grid(row=0, column=1, padx=(0,6))
        self.undo_btn = ttk.Button(btn_frame, text='Undo Last Fix', command=self.undo_last_fix)
        self.undo_btn.grid(row=0, column=2)

        # internal state for preview/undo
        self._preview_backup = None
        self._undo_stack = []
        self._sort_dir = {}

        # Full errors text
        self.errors_text = tk.Text(right, height=6, wrap='word', fg='red')
        self.errors_text.pack(fill='x', padx=5)

        # Status bar
        self.status = ttk.Label(root, text='Ready')
        self.status.pack(fill='x')

    def clear_highlights(self):
        self.text.tag_remove('error', '1.0', 'end')

    def highlight_error_line(self, line_no):
        try:
            self.text.tag_add('error', f"{line_no}.0", f"{line_no}.end")
        except Exception:
            pass

    def analyze_code(self):
        source = self.text.get('1.0', 'end-1c')
        mode = self.mode_var.get()
        self.clear_highlights()
        # clear tokens table
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
        # clear errors
        self.errors_list.delete(0, 'end')
        self.suggestion_var.set('')
        self.errors_text.delete('1.0', 'end')
        self.status.config(text='Analyzing...')

        try:
            out = self.tokenizer.analyze(source, mode=mode)
            tokens = out.get('tokens', [])
            errors = out.get('errors', [])
            self.last_analysis = out

            # populate tokens table
            for t in tokens:
                self.tokens_tree.insert('', 'end', values=(t.get('type'), t.get('value'), t.get('line'), t.get('column')))

            if errors:
                for idx, e in enumerate(errors):
                    display = f"{idx+1}. {e.type} (Line {e.line}, Col {e.column})"
                    self.errors_list.insert('end', display)
                    self.errors_text.insert('end', str(e) + "\n")
                    try:
                        self.highlight_error_line(e.line)
                    except Exception:
                        pass
                self.status.config(text=f"Found {len(errors)} error(s)")
            else:
                self.status.config(text='No lexical errors found')

        except Exception as ex:
            messagebox.showerror('Analyzer Error', str(ex))
            self.status.config(text='Error during analysis')

    def on_error_select(self, event):
        sel = event.widget.curselection()
        if not sel:
            self.suggestion_var.set('')
            return
        idx = sel[0]
        errors = self.last_analysis.get('errors', []) if self.last_analysis else []
        if idx < 0 or idx >= len(errors):
            self.suggestion_var.set('')
            return
        e = errors[idx]
        sugg = getattr(e, 'suggestion', None) or 'No suggestion available.'
        self.suggestion_var.set(sugg)

    def preview_suggestion(self):
        sel = self.errors_list.curselection()
        if not sel:
            return
        idx = sel[0]
        errors = self.last_analysis.get('errors', [])
        if idx < 0 or idx >= len(errors):
            return
        e = errors[idx]
        # backup current content for preview revert
        self._preview_backup = self.text.get('1.0', 'end')
        # apply the same heuristics as apply_suggestion, but do not push to undo stack
        self._apply_fix(e, push_undo=False)

    def undo_last_fix(self):
        if not self._undo_stack:
            return
        prev = self._undo_stack.pop()
        # restore full editor content
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', prev)
        self.status.config(text='Undid last fix')

    def revert_preview(self):
        if self._preview_backup is None:
            return
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', self._preview_backup)
        self._preview_backup = None
        self.status.config(text='Reverted preview')

    def _apply_fix(self, e, push_undo=True):
        # helper used by preview and apply
        # capture previous content when push_undo True
        if push_undo:
            prev = self.text.get('1.0', 'end')
            self._undo_stack.append(prev)

        line = e.line
        col = e.column
        try:
            line_text = self.text.get(f"{line}.0", f"{line}.end")
        except Exception:
            return

        def replace_range(start_pos, end_pos, new_text):
            try:
                self.text.delete(start_pos, end_pos)
                self.text.insert(start_pos, new_text)
            except Exception:
                pass

        if e.type == 'Invalid Character':
            start = f"{line}.{max(col-1,0)}"
            end = f"{line}.{col}"
            replace_range(start, end, '')
            return

        if e.type == 'Unterminated String':
            sugg = getattr(e, 'suggestion', '')
            quote = '"' if '"' in sugg else "'"
            self.text.insert(f"{line}.end", quote)
            return

        if e.type == 'Malformed Number':
            start_idx = max(col-1, 0)
            s = line_text
            i = start_idx
            while i < len(s) and (s[i].isdigit() or s[i]=='.'):
                i += 1
            token = s[start_idx:i]
            if token.endswith('.'):
                start = f"{line}.{start_idx}"
                end = f"{line}.{i}"
                replace_range(start, end, token[:-1])
            return

        if e.type == 'Invalid Identifier':
            start_idx = max(col-1, 0)
            s = line_text
            i = start_idx
            while i < len(s) and (s[i].isalnum() or s[i]=='_'):
                i += 1
            bad = s[start_idx:i]
            newname = '_' + bad
            start = f"{line}.{start_idx}"
            end = f"{line}.{i}"
            replace_range(start, end, newname)
            return

        if e.type == 'Duplicate Declaration':
            start_idx = max(col-1, 0)
            s = line_text
            i = start_idx
            while i < len(s) and (s[i].isalnum() or s[i]=='_'):
                i += 1
            name = s[start_idx:i]
            newname = name + '_dup'
            start = f"{line}.{start_idx}"
            end = f"{line}.{i}"
            replace_range(start, end, newname)
            return

        return

    def apply_suggestion(self):
        sel = self.errors_list.curselection()
        if not sel:
            return
        idx = sel[0]
        errors = self.last_analysis.get('errors', [])
        if idx < 0 or idx >= len(errors):
            return
        e = errors[idx]
        # apply and push to undo stack
        self._apply_fix(e, push_undo=True)
        self.status.config(text='Applied suggestion')

    def sort_tokens(self, col):
        # Toggle sort direction
        dir = self._sort_dir.get(col, False)
        items = [(self.tokens_tree.set(k, col), k) for k in self.tokens_tree.get_children('')]
        # convert numeric columns to numbers for proper sorting
        if col in ('line', 'column'):
            def keyfn(x):
                try:
                    return int(x[0])
                except Exception:
                    return 0
        else:
            def keyfn(x):
                return x[0].lower() if isinstance(x[0], str) else str(x[0])

        items.sort(key=keyfn, reverse=dir)
        for index, (val, k) in enumerate(items):
            self.tokens_tree.move(k, '', index)
        # flip direction
        self._sort_dir[col] = not dir

    def apply_suggestion(self):
        sel = self.errors_list.curselection()
        if not sel:
            return
        idx = sel[0]
        errors = self.last_analysis.get('errors', [])
        if idx < 0 or idx >= len(errors):
            return
        e = errors[idx]
        line = e.line
        col = e.column

        # fetch the text of the line
        try:
            line_text = self.text.get(f"{line}.0", f"{line}.end")
        except Exception:
            return

        def replace_range(start_pos, end_pos, new_text):
            try:
                self.text.delete(start_pos, end_pos)
                self.text.insert(start_pos, new_text)
            except Exception:
                pass

        if e.type == 'Invalid Character':
            # remove single character at column (1-based)
            start = f"{line}.{max(col-1,0)}"
            end = f"{line}.{col}"
            replace_range(start, end, '')
            return

        if e.type == 'Unterminated String':
            # append matching quote at line end
            sugg = getattr(e, 'suggestion', '')
            quote = '"' if '"' in sugg else "'"
            self.text.insert(f"{line}.end", quote)
            return

        if e.type == 'Malformed Number':
            # remove trailing dot if present in token
            start_idx = max(col-1, 0)
            s = line_text
            i = start_idx
            while i < len(s) and (s[i].isdigit() or s[i]=='.'):
                i += 1
            token = s[start_idx:i]
            if token.endswith('.'):
                start = f"{line}.{start_idx}"
                end = f"{line}.{i}"
                replace_range(start, end, token[:-1])
            return

        if e.type == 'Invalid Identifier':
            start_idx = max(col-1, 0)
            s = line_text
            i = start_idx
            while i < len(s) and (s[i].isalnum() or s[i]=='_'):
                i += 1
            bad = s[start_idx:i]
            newname = '_' + bad
            start = f"{line}.{start_idx}"
            end = f"{line}.{i}"
            replace_range(start, end, newname)
            return

        if e.type == 'Duplicate Declaration':
            start_idx = max(col-1, 0)
            s = line_text
            i = start_idx
            while i < len(s) and (s[i].isalnum() or s[i]=='_'):
                i += 1
            name = s[start_idx:i]
            newname = name + '_dup'
            start = f"{line}.{start_idx}"
            end = f"{line}.{i}"
            replace_range(start, end, newname)
            return

        # fallback: do nothing
        return
