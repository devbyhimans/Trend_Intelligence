# end-to-end processing
from ml_engine.preprocessing.pipeline import PreprocessingPipeline
from ml_engine.sentiment.inference import SentimentInference

from ml_engine.topic_modeling.embeddings import EmbeddingModel
from ml_engine.topic_modeling.clustering import ClusterModel
from ml_engine.topic_modeling.labeling import TopicLabeler

from ml_engine.trend_detection.velocity import VelocityCalculator
from ml_engine.trend_detection.acceleration import AccelerationCalculator
from ml_engine.trend_detection.scoring import TrendScorer

class TrendPipeline:

    def __init__(self):
        self.preprocessor = PreprocessingPipeline()
        self.sentiment_model = SentimentInference()

        self.embedder = EmbeddingModel()
        self.clusterer = ClusterModel(n_clusters=3)
        self.labeler = TopicLabeler()

        self.velocity_calc = VelocityCalculator()
        self.acceleration_calc = AccelerationCalculator()
        self.scorer = TrendScorer()

    def run(self, raw_texts, prev_counts=None, prev_velocities=None):

        normalized_texts = []
        sentiments = []

        # 🔹 STEP 1: Preprocessing + Sentiment
        for text in raw_texts:
            processed = self.preprocessor.process(text)

            norm_text = " ".join(processed["normalized"])
            normalized_texts.append(norm_text)

            sentiment = self.sentiment_model.analyze(text)
            sentiments.append(sentiment["score"])

        # 🔹 STEP 2: Embeddings
        embeddings = self.embedder.encode(normalized_texts)

        # 🔹 STEP 3: Clustering
        labels = self.clusterer.fit(embeddings)

        # 🔹 STEP 4: Topic Labeling
        topics = self.labeler.get_topic_labels(normalized_texts, labels)

        # 🔹 STEP 5: Aggregate per topic
        topic_counts = {}
        topic_sentiment = {}

        for i, label in enumerate(labels):
            topic_counts[label] = topic_counts.get(label, 0) + 1
            topic_sentiment.setdefault(label, []).append(sentiments[i])

        # 🔹 STEP 6: Trend Scoring
        results = []

        for label in topic_counts:

            volume = topic_counts[label]

            prev_count = prev_counts.get(label, 0) if prev_counts else 0
            velocity = self.velocity_calc.compute(prev_count, volume)

            prev_velocity = prev_velocities.get(label, 0) if prev_velocities else 0
            acceleration = self.acceleration_calc.compute(prev_velocity, velocity)

            avg_sentiment = sum(topic_sentiment[label]) / len(topic_sentiment[label])

            score = self.scorer.compute_score(
                volume,
                velocity,
                acceleration,
                avg_sentiment
            )

            results.append({
                "topic_id": label,
                "keywords": topics[label],
                "volume": volume,
                "velocity": velocity,
                "acceleration": acceleration,
                "sentiment": avg_sentiment,
                "score": score
            })

        return sorted(results, key=lambda x: x["score"], reverse=True)
        
    def run_pipeline(texts):
        pipeline = TrendPipeline()
        return pipeline.run(texts)    