import tkinter as tk


class DragDropListbox(tk.Listbox):
    """ドラッグ＆ドロップ対応Listbox"""

    def __init__(self, master, drag_callback=None, **kw):
        kw["selectmode"] = tk.SINGLE
        super().__init__(master, **kw)
        self.drag_callback = drag_callback
        self.bind("<Button-1>", self.set_current)
        self.bind("<B1-Motion>", self.shift_selection)
        self.cur_index = None

    def set_current(self, event):
        """ドラッグ開始位置を記録"""
        self.cur_index = self.nearest(event.y)

    def shift_selection(self, event):
        """ドラッグ中の並び替え"""
        i = self.nearest(event.y)
        if self.cur_index is None or i == self.cur_index:
            return

        if i < self.cur_index:
            x = self.get(i)
            self.delete(i)
            self.insert(i + 1, x)
            self.cur_index = i
            if self.drag_callback:
                self.drag_callback(i + 1, i)
        elif i > self.cur_index:
            x = self.get(i)
            self.delete(i)
            self.insert(i - 1, x)
            self.cur_index = i
            if self.drag_callback:
                self.drag_callback(i - 1, i)
