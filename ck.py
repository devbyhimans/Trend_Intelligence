from ml_engine.pipelines.full_pipeline import TrendPipeline

pipeline = TrendPipeline()

texts = [
    "AI is amazing",
    "ChatGPT is powerful",
    "AI is transforming industry",
    "IPL match today",
    "Dhoni hits six",
    "Cricket fans excited"
]

results = pipeline.run(texts)

for r in results:
    print(r)

