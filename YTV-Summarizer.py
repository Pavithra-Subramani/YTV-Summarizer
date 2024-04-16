import tkinter as tk
from tkinter import scrolledtext, messagebox
from youtube_transcript_api import YouTubeTranscriptApi as yta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from yake import KeywordExtractor

class YoutubeTranscriberApp:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YTV  Summarizer")
        self.root.geometry("900x600")

        # Load the background image
        self.bg_image = tk.PhotoImage(file="backgrd2.png")  # Change "background_image.png" to your image file
        self.background_label = tk.Label(self.root, image=self.bg_image)
        self.background_label.place(relwidth=1, relheight=1)

        # self.create_database()  # Remove this line if not using any database
        self.create_widgets()
        
    def create_widgets(self):
        title_font = ("Helvetica", 25, "bold")
        smaller_title_font = ("Helvetica", 18, "bold")

        # Title label
        self.title_label = tk.Label(self.root, text="Rapid Recap🎬", font=title_font)
        self.title_label.pack(pady=20)
        
        t_font = ("Helvetica", 15, "bold")
        self.author_label = tk.Label(self.root, text="  🎙️Transcribe , Summarize and Save The Essence.. 📄 ", font=t_font)
        self.author_label.pack(pady=10)

        m_font = ("Helvetica", 10, "bold")
        self.youtube_id_label = tk.Label(self.root, text=" Youtube ID:", font=m_font)
        self.youtube_id_label.pack(pady=5)


        # Frame for YouTube ID and Keywords
        youtube_keywords_frame = tk.Frame(self.root)
        youtube_keywords_frame.pack(pady=5)

        # YouTube ID Label and Entry
        m_font = ("Helvetica", 10, "bold")
        self.youtube_id_label = tk.Label(youtube_keywords_frame, text="Youtube ID:", font=m_font)
        self.youtube_id_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.youtube_id_entry = tk.Entry(youtube_keywords_frame)
        self.youtube_id_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Get Transcript Button
        g_font = ("Helvetica", 10, "bold")
        self.transcript_button = tk.Button(youtube_keywords_frame, text="Get Transcript", command=self.get_transcription, font=g_font)
        self.transcript_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Frames for Transcript and Summary
        text_frames = tk.Frame(self.root)
        text_frames.pack(pady=10)

        # Transcript Frame with Heading
        transcript_frame = tk.Frame(text_frames)
        transcript_frame.pack(side=tk.LEFT, padx=10)

        transcript_title_label = tk.Label(transcript_frame, text="Transcript", font=smaller_title_font)
        transcript_title_label.pack()

        # Transcript Text Box
        self.transcript_text = scrolledtext.ScrolledText(transcript_frame, wrap=tk.WORD, width=40, height=10)
        self.transcript_text.pack(pady=5)

        # Summary Frame with Heading
        summary_frame = tk.Frame(text_frames)
        summary_frame.pack(side=tk.RIGHT, padx=10)

        summary_title_label = tk.Label(summary_frame, text="Summary", font=smaller_title_font)
        summary_title_label.pack()

        # Summary Text Box
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, width=40, height=10)
        self.summary_text.pack(pady=5)

        # Keywords Label and Text Box
        self.keywords_label = tk.Label(self.root, text="Keywords:", font=m_font)
        self.keywords_label.pack(pady=5)

        self.keywords_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=40, height=5)
        self.keywords_text.pack(pady=5)

        # Buttons Frame
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)

        # Save Transcript Button
        self.save_pdf_button = tk.Button(buttons_frame, text="Save Transcript", command=self.save_as_pdf, font=g_font)
        self.save_pdf_button.pack(side=tk.LEFT, padx=10)

        # Save Summaries Button
        self.save_summaries_button = tk.Button(buttons_frame, text="Save Summarize", command=self.save_summaries_line_by_line, font=g_font)
        self.save_summaries_button.pack(side=tk.LEFT, padx=10)

        # Clear Button
        self.clear_button = tk.Button(buttons_frame, text="Clear", command=self.clear_all, font=g_font)
        self.clear_button.pack(side=tk.LEFT, padx=10)

    def get_transcription(self):
        youtube_id = self.youtube_id_entry.get()
        if not youtube_id:
            messagebox.showinfo("Error", "❌ Please enter a valid Youtube ID.")
            return

        try:
            data = yta.get_transcript(youtube_id)
            transcript = ''
            for value in data:
                for key, val in value.items():
                    if key == 'text':
                        transcript += val + '\n'

            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.insert(tk.END, transcript)

            # Generate video summary and extract keywords
            self.generate_summary(transcript)

            # Save data to the database
            youtube_link = f"https://www.youtube.com/watch?v={youtube_id}"
            # self.insert_into_database(youtube_id, youtube_link, transcript, self.summary_text.get(1.0, tk.END))  # Uncomment this if you have a database

        except Exception as e:
            messagebox.showinfo("Error", f"❌ An error occurred: {str(e)}")

    def generate_summary(self, transcript):
        parser = PlaintextParser.from_string(transcript, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, 3)
        summary = ' '.join(str(sentence) for sentence in summary_sentences)
        
        # Extract keywords using YAKE
        extractor = KeywordExtractor()
        keywords = extractor.extract_keywords(text=transcript)
        keywords_text = '\n'.join([keyword for keyword, _ in keywords])
        
        # Append keywords to the end of the summary
        summary_with_keywords = summary
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_with_keywords)

        self.keywords_text.delete(1.0, tk.END)
        self.keywords_text.insert(tk.END, keywords_text)

    def save_summaries_line_by_line(self):
        summary_text = self.summary_text.get(1.0, tk.END)

        if not summary_text.strip():
            messagebox.showinfo("Error", "❌ Summary is empty. Please generate a summary first.")
            return

        self.save_summaries_as_pdf()

    def save_as_pdf(self):
        transcript_text = self.transcript_text.get(1.0, tk.END)

        if not transcript_text.strip():
            messagebox.showinfo("Error", "❌ Transcript is empty. Please get the transcript first.")
            return

        pdf_filename = "transcript.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter
        lines = transcript_text.split('\n')
        y_position = height - 100

        for line in lines:
            c.drawString(100, y_position, line)
            y_position -= 12

        c.save()
        messagebox.showinfo("Success", f"✅ Transcript saved as {pdf_filename}")

        # Save data to the database
        youtube_id = self.youtube_id_entry.get()
        youtube_link = f"https://www.youtube.com/watch?v={youtube_id}"
        # self.insert_into_database(youtube_id, youtube_link, transcript_text, self.summary_text.get(1.0, tk.END))  # Uncomment this if you have a database

    def save_summaries_as_pdf(self):
        summary_text = self.summary_text.get(1.0, tk.END)
        if not summary_text.strip():
            messagebox.showinfo("Error", "❌ Summary is empty. Please generate a summary first.")
            return

        pdf_filename = "summaries.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter
        lines = summary_text.split('\n')
        y_position = height - 100

        for line in lines:
            c.drawString(100, y_position, line.strip())  # Print each line of summary
            y_position -= 12

        c.save()
        messagebox.showinfo("Success", f"✅ Summaries saved as {pdf_filename}")

    def clear_all(self):
        self.transcript_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        self.keywords_text.delete(1.0, tk.END)

    def __del__(self):
        pass
        # self.connection.close()  # Uncomment this if you have a database

if __name__ == "__main__":
    app = YoutubeTranscriberApp()
    app.root.mainloop()
