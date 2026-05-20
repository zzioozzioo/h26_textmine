from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from konlpy.tag import Okt
import joblib
import numpy as np

class SentimentAnalyzer:
    def __init__(self, model_file, encoder_file):
        self.model = load_model(model_file)
        self.encoder = joblib.load(encoder_file)
        self.korean_tokenizer = Okt().morphs
    
    def analyze_sentiment(self, review):
        # 데이터 준비 : 정제
        # 한국어 형태소 분석
        tokens = [word for word in self.korean_tokenizer(review)]
        
        # Integer Encoding
        encoded_tokens = self.encoder.texts_to_sequences([tokens])

        # padding
        X = pad_sequences(encoded_tokens, maxlen=self.model.input_shape[1])

        # 예측
        results = self.model.predict(X, verbose=0)
        labels = ['부정', '긍정']
        index = np.argmax(results[0])
        user_outputs = labels[index]
        return user_outputs, results[0][index]
