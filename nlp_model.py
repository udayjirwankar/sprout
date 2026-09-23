import os
import joblib
from scipy.sparse import hstack


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "sprout_classifier.pkl")
WORD_VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "word_vectorizer.pkl")
CHAR_VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "char_vectorizer.pkl")


# Load the trained local model
model = joblib.load(MODEL_PATH)
word_vectorizer = joblib.load(WORD_VECTORIZER_PATH)
char_vectorizer = joblib.load(CHAR_VECTORIZER_PATH)


def analyze_text(text):
    """
    Analyze journal text using the locally trained Sprout classifier.

    Returns:
        {
            "prediction": predicted class,
            "confidence": model confidence,
            "probabilities": probability for each class
        }
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    # Generate word-level TF-IDF features
    word_features = word_vectorizer.transform([text])

    # Generate character-level TF-IDF features
    char_features = char_vectorizer.transform([text])

    # Combine both feature representations
    features = hstack([word_features, char_features])

    # Prediction
    prediction = model.predict(features)[0]

    # Class probabilities
    probabilities = model.predict_proba(features)[0]

    probability_map = {
        class_name: round(float(probability), 4)
        for class_name, probability in zip(model.classes_, probabilities)
    }

    confidence = round(float(max(probabilities)), 4)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": probability_map
    }