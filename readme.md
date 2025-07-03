# Aspect-Based Sentiment Analysis App

Extracts aspects (e.g., battery, camera) from reviews and shows sentiment for each.

## How to run

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app/main.py
