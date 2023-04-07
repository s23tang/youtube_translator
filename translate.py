import sys
import tqdm
import whisper
import whisper.transcribe 
import tkinter
from tkinter import ttk
from pytube import YouTube
from whisper.utils import get_writer

class _ProgressWithTkinter(tqdm.tqdm):
    window = None
    update_button = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current = self.n  # Set the initial value
        
    def update(self, n):
        super().update(n)
        self._current += n
        
        completed_percentage = self._current / self.total * 100
        self.update_button.configure(text=f'{completed_percentage:.2f}% Translated')
        self.window.update()


transcribe_module = sys.modules['whisper.transcribe']
transcribe_module.tqdm.tqdm = _ProgressWithTkinter


class Window:
  def __init__(self):
    self.win = tkinter.Tk()
    self.win.title('Youtube Subtitler')

    self.__setup_url_input()
    self.__setup_language_selector()
    self.__setup_model_selector()
    self.__setup_start_button()
    self.__setup_notification_area()
    self.__setup_progress_with_tkinter()

    self.url_input.focus()
    
    self.win.mainloop()
  
  def __setup_url_input(self, width=50, row=0):
    self.url = tkinter.StringVar()

    ttk.Label(self.win, text="Youtube URL:", anchor="w", width=width).grid(column=0, row=row)
    self.url_input = ttk.Entry(self.win, width=width, textvariable=self.url)
    self.url_input.grid(column=0, row=row+1)
  
  def __setup_language_selector(self, width=10, languages=('Japanese', 'Korean'), row=2):
    self.language = tkinter.StringVar()

    ttk.Label(self.win, text="Language:", anchor='w', width=width+4).grid(column=0, row=row, pady=(5, 0))
    self.language_selector = ttk.Combobox(self.win, state="readonly", width=width, textvariable=self.language, values=languages)
    self.language_selector.current(0)
    self.language_selector.grid(column=0, row=row+1)

  def __setup_model_selector(self, width=10, models=('small', 'medium'), row=4):
    self.model = tkinter.StringVar()

    ttk.Label(self.win, text="Model:", anchor='w', width=width+4).grid(column=0, row=row, pady=(5, 0))
    self.model_selector = ttk.Combobox(self.win, state="readonly", width=width, textvariable=self.model, values=models)
    self.model_selector.current(0)
    self.model_selector.grid(column=0, row=row+1)
  
  def __setup_start_button(self, row=6):
    self.start_button = ttk.Button(self.win, text='Start', command=self.__translate)
    self.start_button.grid(column=0, row=row, pady=(10, 0))

  def __setup_notification_area(self, row=7):
    self.notification_area = ttk.Label(self.win, text="", wraplength=200)
    self.notification_area.grid(column=0, row=row, pady=10)
  
  def __setup_progress_with_tkinter(self):
    _ProgressWithTkinter.window = self.win
    _ProgressWithTkinter.update_button = self.start_button
  
  def __translate(self):
    if not self.url.get():
      self.notification_area.configure(text="Please input a proper Youtube URL")
      return

    self.start_button.configure(text='Downloading...')
    self.win.update()

    video = YouTube(self.url.get(), on_progress_callback=self.__on_progress) \
      .streams.filter(progressive=True, file_extension='mp4') \
        .order_by('resolution').desc().first().download()

    self.notification_area.configure(text=f'Download completed')
    self.start_button.configure(text='Translating...')
    self.win.update()

    print(f'Loading Whisper model {self.model.get()}')
    model = whisper.load_model(self.model.get())
    print('Starting video transcribe')
    transcript = model.transcribe(video, condition_on_previous_text=False, task='translate', language=self.language.get())
    print('Completed video transcribe')

    self.notification_area.configure(text=f'Translate completed')
    self.start_button.configure(text='Start')
    self.win.update()

    get_writer('srt', '.')(transcript, video)
  
  def __on_progress(self, stream, chunk, bytes_remaining):
    percent_completed = (stream.filesize - bytes_remaining) / stream.filesize * 100
    self.start_button.configure(text=f'{percent_completed:.2f}% Downloaded')
    self.win.update()


if __name__ == '__main__':
   Window()