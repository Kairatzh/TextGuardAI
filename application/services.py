"""
Application Services

Сервисы приложения содержат бизнес-логику, которая координирует работу
различных компонентов системы.

Паттерны:
- Service Layer Pattern
- Strategy Pattern (для различных моделей)
"""

import asyncio
import time
from typing import Tuple

import structlog
import torch
import pickle

from application.interfaces import IModelService, ITextPreprocessingService
from configs.config import load_configs

logger = structlog.get_logger(__name__)


class TextPreprocessingService(ITextPreprocessingService):
    """
    Сервис предобработки текста.
    
    Реализует стандартные техники NLP предобработки:
    - Токенизация
    - Лемматизация
    - Удаление стоп-слов
    - Нормализация
    
    Использует NLTK для обработки текста.
    """
    
    def __init__(self):
        """Инициализация сервиса предобработки."""
        import nltk
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        from nltk.tokenize import RegexpTokenizer
        
        try:
            self.stopwords = stopwords.words("english")
            self.lemmatizer = WordNetLemmatizer()
            self.tokenizer = RegexpTokenizer(r'\w+')
        except LookupError:
            logger.warning("NLTK data not found, downloading required resources")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            self.stopwords = stopwords.words("english")
            self.lemmatizer = WordNetLemmatizer()
            self.tokenizer = RegexpTokenizer(r'\w+')
    
    def preprocess(self, text: str) -> str:
        """
        Предобработать текст.
        
        Процесс:
        1. Приведение к нижнему регистру
        2. Токенизация
        3. Удаление стоп-слов
        4. Лемматизация
        5. Объединение в строку
        
        Args:
            text: Исходный текст
            
        Returns:
            str: Предобработанный текст
        """
        text = text.lower()
        tokens = self.tokenizer.tokenize(text)
        tokens = [word for word in tokens if word not in self.stopwords]
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return " ".join(tokens)


class ModelService(IModelService):
    """
    Сервис для работы с ML моделью.
    
    Инкапсулирует логику загрузки и использования модели PyTorch.
    Использует ленивую загрузку (lazy loading) для оптимизации памяти.
    
    Паттерны:
    - Singleton (для модели)
    - Strategy (можно расширить для разных моделей)
    - Lazy Loading
    """
    
    def __init__(self, preprocessor: ITextPreprocessingService):
        """
        Инициализация сервиса модели.
        
        Args:
            preprocessor: Сервис предобработки текста
        """
        self.preprocessor = preprocessor
        self._model = None
        self._vectorizer = None
        self._model_version = None
        self._config = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("ModelService initialized", device=str(self._device))
    
    def _load_model(self):
        """
        Ленивая загрузка модели и векторaйзера.
        
        Загружает модель только при первом использовании.
        Это оптимизирует время старта приложения.
        
        Примечание: Предполагается, что модель сохранена как state_dict.
        Если модель сохранена полностью, используйте torch.load напрямую.
        """
        if self._model is None:
            config = load_configs()
            self._config = config
            
            model_path = config["model"]["model_path"]
            vectorizer_path = config["model"]["vectorizer_path"]
            self._model_version = config["model"].get("model_version", "1.0")
            
            logger.info("Loading model", model_path=model_path, vectorizer_path=vectorizer_path)
            
            try:
                # Загрузка state_dict модели
                checkpoint = torch.load(model_path, map_location=self._device)
                
                # Импорт класса модели
                from model.train import TextClassifier
                
                # Определение размеров модели (в production лучше хранить в конфиге)
                # Используем типичные значения для TF-IDF + MLP
                input_size = 100000  # Примерный размер, должен совпадать с обучением
                hidden_size = 128
                output_size = 2
                
                # Создание модели и загрузка весов
                self._model = TextClassifier(input_size=input_size, hidden_size=hidden_size, output_size=output_size)
                
                if isinstance(checkpoint, dict):
                    # Если это словарь (state_dict)
                    self._model.load_state_dict(checkpoint)
                else:
                    # Если это уже модель (legacy)
                    self._model = checkpoint
                
                self._model.eval()
                self._model.to(self._device)
                
            except Exception as e:
                logger.error("Failed to load model", error=str(e), exc_info=True)
                raise RuntimeError(f"Could not load model from {model_path}: {str(e)}")
            
            # Загрузка векторaйзера
            try:
                with open(vectorizer_path, "rb") as f:
                    self._vectorizer = pickle.load(f)
            except Exception as e:
                logger.error("Failed to load vectorizer", error=str(e))
                # Fallback: создаем простой векторaйзер
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._vectorizer = TfidfVectorizer(ngram_range=(1, 2))
            
            logger.info("Model loaded successfully", version=self._model_version)
    
    async def predict(self, text: str) -> Tuple[float, float]:
        """
        Выполнить асинхронное предсказание токсичности текста.
        
        Процесс:
        1. Предобработка текста
        2. Векторизация (TF-IDF)
        3. Преобразование в тензор
        4. Предсказание модели
        5. Вычисление confidence
        
        Args:
            text: Текст для анализа
            
        Returns:
            Tuple[float, float]: (toxicity_score, confidence)
                - toxicity_score: Оценка токсичности (0.0 - 1.0)
                - confidence: Уверенность модели (0.0 - 1.0)
        """
        # Ленивая загрузка модели
        if self._model is None:
            self._load_model()
        
        # Предобработка текста
        preprocessed_text = self.preprocessor.preprocess(text)
        
        # Векторизация
        text_vector = self._vectorizer.transform([preprocessed_text])
        text_vector = text_vector.toarray()
        
        # Преобразование в тензор
        text_tensor = torch.tensor(text_vector, dtype=torch.float32, device=self._device)
        text_tensor = text_tensor.unsqueeze(0)
        
        # Предсказание (синхронно, но в executor для неблокирующей работы)
        loop = asyncio.get_event_loop()
        with torch.no_grad():
            output = await loop.run_in_executor(None, self._model, text_tensor)
            probabilities = torch.softmax(output, dim=1)
            predicted_class = output.argmax(dim=1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Для бинарной классификации: токсичный класс = 1
            toxicity_score = probabilities[0][1].item() if output.shape[1] > 1 else float(predicted_class)
        
        return toxicity_score, confidence
    
    def get_model_version(self) -> str:
        """
        Получить версию модели.
        
        Returns:
            str: Версия модели
        """
        if self._model_version is None:
            config = load_configs()
            self._model_version = config["model"].get("model_version", "1.0")
        return self._model_version

