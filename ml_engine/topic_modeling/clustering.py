from sklearn.cluster import KMeans

class ClusterModel:

    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters)

    def fit(self, embeddings):
        self.model.fit(embeddings)
        return self.model.labels_