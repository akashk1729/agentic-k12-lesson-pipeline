from src.ingestion import extract_pdf, RAW

if __name__ == "__main__":
    extract_pdf(RAW / "english.pdf", "english")
    extract_pdf(RAW / "hindi.pdf", "hindi")
    print("Ingestion complete.")
