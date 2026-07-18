def print_banner(path):
    """
    Print banner text from a file.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print(f"⚠️ Banner file not found: {path}")
    except Exception as e:
        print(f"❌ Error reading banner: {str(e)}")