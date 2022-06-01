"""
File to load in memory the sentiment analysis classifier.
"""
from transformers import pipeline


class Classifier:
    """Class that contains the sentiment analysis classifier model.
    """
    def __init__(self, model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment") -> None:
        """Classifier initializer. Load in memory the model.

        Args:
            model_path (str, optional): huggingface url for the sentiment analysis task. Defaults to "cardiffnlp/twitter-xlm-roberta-base-sentiment".
        """
        self.__model_path = model_path
        self.__sentiment_task = pipeline("sentiment-analysis", model=self.__model_path, tokenizer=self.__model_path)

    def get_sentiment(self, text):
        """Function that returns the sentiment (positive, negative, neutral) for a given text.

        Args:
            text (str): Text to classify

        Returns:
            str: Label (Positive, Negative, Neutral) for the given text.
        """
        return self.__category_to_int(self.__sentiment_task(text)[0]['label'])

    def __category_to_int(self, label):
        if label == "Positive":
            return 1
        elif label == "Negative":
            return -1
        elif label == "Neutral":
            return 0
        else:
            raise ValueError("Error, label not recognized.")