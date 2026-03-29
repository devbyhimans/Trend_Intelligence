import pandas as pd
import re
import os

class DataProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def clean_text(self, text):
        """Removes URLs, special characters, and extra whitespace."""
        if not isinstance(text, str):
            return ""
        
        # 1. Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # 2. Remove Special Characters/Emojis (keep only alphanumeric and basic punctuation)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        # 3. Remove extra newlines and spaces
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()

    def process(self):
        if not os.path.exists(self.input_file):
            print(f"❌ Error: {self.input_file} not found!")
            return

        print(f"🧹 Cleaning data from {self.input_file}...")
        df = pd.read_csv(self.input_file)

        # Apply cleaning to Title and Text
        df['title_clean'] = df['title'].apply(self.clean_text)
        df['text_clean'] = df['text'].apply(self.clean_text)

        # Process the joined comments
        # We split the pipe '|', clean each comment, and join them back neatly
        def clean_comments_list(comment_str):
            if pd.isna(comment_str) or comment_str == "No Comments":
                return "no comments"
            individual_comments = comment_str.split(' | ')
            cleaned = [self.clean_text(c) for c in individual_comments if len(c) > 5]
            return " | ".join(cleaned)

        df['comments_clean'] = df['comments'].apply(clean_comments_list)

        # Drop the old 'dirty' columns if you want to save space
        # df = df.drop(columns=['title', 'text', 'comments'])

        df.to_csv(self.output_file, index=False)
        print(f"✅ Success! Cleaned data saved to {self.output_file}")

if __name__ == "__main__":
    # Define paths relative to the processor folder using absolute path logic
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(BASE_DIR, "collectors", "reddit_data.csv")
    clean_path = os.path.join(BASE_DIR, "collectors", "reddit_data_cleaned.csv")

    processor = DataProcessor(raw_path, clean_path)
    processor.process()