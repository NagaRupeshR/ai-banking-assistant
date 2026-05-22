import os
import joblib
import numpy as np
from scipy.sparse import hstack, csr_matrix
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')

MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
TFIDF_PATH = os.path.join(MODEL_DIR, 'tfidf.pkl')
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder.pkl')

print('Loading complaint classifier...')
model = joblib.load(MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

print('Loading SBERT model...')
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')


def rule_based_adjustment(text, predicted_label):
    t = text.lower()

    upi_keywords = [
        'upi', 'vpa', 'virtual payment address',
        'qr', 'gpay', 'phonepe', 'paytm'
    ]

    retail_keywords = [
        'savings account', 'passbook', 'atm',
        'debit card', 'kyc', 'ifsc'
    ]

    has_upi = any(k in t for k in upi_keywords)
    has_retail = any(k in t for k in retail_keywords)

    if has_upi:
        return 'upi_transaction_failures'

    if (not has_upi) and has_retail and predicted_label == 'upi_transaction_failures':
        return 'retail_banking'

    return predicted_label


# Returns:
# category, confidence, top_predictions

def classify_complaint(text):
    try:
        sbert_emb = csr_matrix(sbert_model.encode([text]))
        tfidf_vec = tfidf.transform([text])
        combined = hstack([tfidf_vec, sbert_emb])

        pred_prob = model.predict_proba(combined)[0]
        pred_indices = np.argsort(pred_prob)[::-1]

        class_names = label_encoder.inverse_transform(pred_indices)
        class_probs = [float(pred_prob[i]) for i in pred_indices]

        adjusted_label = rule_based_adjustment(text, class_names[0])
        confidence = class_probs[0]

        top_predictions = [
            {
                'label': class_names[i],
                'probability': round(class_probs[i], 4)
            }
            for i in range(min(6, len(class_names)))
        ]

        return adjusted_label, confidence, top_predictions

    except Exception as e:
        print('Classifier error:', e)
        return 'unknown', 0.5, []