from app.sentiment import analyze_sentiment

def test_analyze_sentiment():
    result = analyze_sentiment("Battery life is great.")
    assert result["label"] in ["POSITIVE", "NEGATIVE"]
