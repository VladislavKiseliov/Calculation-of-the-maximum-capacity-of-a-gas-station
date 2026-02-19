from tkinter import filedialog, messagebox


class UiService:
    def show_info(self, title: str, message: str):
        raise NotImplementedError

    def show_warning(self, title: str, message: str):
        raise NotImplementedError

    def show_error(self, title: str, message: str):
        raise NotImplementedError

    def ask_open_file(self, **kwargs):
        raise NotImplementedError

    def ask_save_file(self, **kwargs):
        raise NotImplementedError


class TkUiService(UiService):
    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)

    def ask_open_file(self, **kwargs):
        return filedialog.askopenfilename(**kwargs)

    def ask_save_file(self, **kwargs):
        return filedialog.asksaveasfilename(**kwargs)
