# presentation/main.py
"""
Entry point for the presentation component.
"""


def main():
    from presentation.PresentationManager import PresentationManager
    PresentationManager.get_instance().run_event_loop()


if __name__ == "__main__":
    main()
