# subtitle_generator/__main__.py
from subtitle_generator import SubtitleGenerator

def main():
    """
    Main entry point for running the subtitle generator.
    Initializes the SubtitleGenerator and starts the process.
    """
    generator = SubtitleGenerator()
    generator.run()

if __name__ == "__main__":
    main()
