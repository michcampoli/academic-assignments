Files in this folder:
Using single-cell gene expression data for ~4K PBMCs (peripheral blood cells) from a healthy donor: 
- Histogram of library size & total number cells, Normalization, tsne/UMAP labeling
- Normalize the data by scaling to median library size and log transform the normalized data, PCA, tsne/UMAP on the top 20 PCs, cluster cells using Kmeans, KNN & adjacency matrix, Louvain with the kNN, t-test to find differentially expressed genes 
