# -*- coding: utf-8 -*-
"""Single_cell_pbmc_norm_tsne_UMAP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17puK_6S6LQqHyB6xwuUmj49shP-RpCTY

**BMEN4480**

**Assignment 1**

**Michelle Campoli (mec2308)**

**Question 1**
Download preprocessed single-cell gene expression data for ~4K PBMCs
(peripheral blood cells) from a healthy donor from here. Note that the top 3 lines of the mtx file are header lines. The third line contains the total number of rows in all the three files in this folder (genes.tsv, barcodes.tsv, matrix.mtx). The next lines (starting from line 4) contain indices for gene id, cell id, and expression counts (more details here).
"""

# MOUNTING GOOGLE DRIVE WHERE DATA IS STORED
from google.colab import drive
drive.mount('/gdrive', force_remount=True) 
#/My Drive/Statistical ML/Homework 1/pbmc4k_filtered_gene_bc_matrices.tar.gz

#Imports
import gc
import os

import shutil
import tarfile
import numpy as np
import pandas as pd
!pip install scanpy
import scanpy as sc
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.io as sio
from scipy.io import mmread

#Extract files from zip folder .tar.gz
directory = '/gdrive/My Drive/Statistical ML/Homework 1/'
filename = "pbmc4k_filtered_gene_bc_matrices.tar.gz"
tf = tarfile.open(directory+filename)
print(tf.getnames())
tf.extractall('gdrive/My Drive/Statistical ML/Homework 1/pbmc4k_filtered_gene_bc_matrices')

"""**Question 1a.**
Load the above data and construct a dense matrix of genes by cells from the sparse list format. What is the size (shape) of this matrix, how many cells and genes are detected?
"""

#Import data
matrix = sio.mmread('gdrive/My Drive/Statistical ML/Homework 1/pbmc4k_filtered_gene_bc_matrices/filtered_gene_bc_matrices/GRCh38/matrix.mtx')

#Convert sparse to dense matrix
B = matrix.todense()

#Create dataframe starting index at 1
df = pd.DataFrame(B, range(1, B.shape[0] + 1), range(1, B.shape[1] + 1))
print(df) #.iloc[:5, :5]
shape = df.shape
print('\nDataFrame Shape :', shape)
print('\nNumber of rows or genes :', shape[0])
print('\nNumber of columns or cells :', shape[1])

np.count_nonzero(df, axis=0)

"""**Question 1b.**
Plot a histogram of log10 of library size (i.e. total counts per cell). Do you think the data requires filtering of cell barcodes? If yes, how does the histogram look like after filtering? What is the median of library size across all cells after any filtering
"""

#Total sum per column: 
df.loc['Total',:]= df.sum(axis=0)

#Total sum per row: 
df.loc[:,'Total'] = df.sum(axis=1)

print(df)

#Histogram log10 of library size
last_row = df.iloc[-1]
_, bins = np.histogram(np.log10(last_row + 1), bins='auto')
plt.hist(last_row, bins=10**bins);
plt.gca().set_xscale("log")
plt.title('Distribution of total UMIs per cell')
plt.xlabel('Log10(library size)')
plt.ylabel('Frequency')

"""Yes, requires filtering of empty droplets that have small library sizes. But it appears this dataset has already been filtered. I will threshold at 10**(3.2) to see if the distribution changes."""

#Filter out cell barcodes with low library size
filtered_last_row = last_row[~(last_row < 10**(3.2))]

print('\nDataFrame Shape:', last_row.shape)
print('\nFiltered DataFrame Shape:', filtered_last_row.shape)

#New histogram log10 of filtered library size
_, bins = np.histogram(np.log10(filtered_last_row + 1), bins='auto')
plt.hist(filtered_last_row, bins=10**bins);
plt.gca().set_xscale("log")
plt.title('Distribution of total UMIs per cell (Filtered)')
plt.xlabel('Log10(library size)')
plt.ylabel('Frequency')

#Median library size before filtering
median_cells = last_row.median()
print('\nMedian library size without filtering:', median_cells)

#Median library size after filtering
median_cells_filter = filtered_last_row.median()
print('\nMedian library size with filtering:', median_cells_filter)

"""**Question 1c.**
Plot a histogram of log10 of the total number cells that each gene is expressed in. Is this distribution unimodal or multimodal? If the latter, how many genes remain if you filter the lower mode as noisy genes?
"""

#Histogram log10 of the total number of cells that each gene is expressed in
last_column = df.iloc[: , -1]
_, bins = np.histogram(np.log10(last_column + 1), bins='auto')
plt.hist(last_column, bins=10**bins);
plt.gca().set_xscale("log")
plt.title('Cells per gene')
plt.xlabel('Log10(Cells per gene)')
plt.ylabel('Frequency')

"""Without filtering, this looks like a bimodal distribution. I will now filter out the noisey genes."""

#Filter out noisey genes
filtered_last_column = last_column[~(last_column < 10**(1.4))]

print('\nDataFrame Shape:', last_column.shape)
print('\nFiltered DataFrame Shape (the number of genes remaining):', filtered_last_column.shape)

#New histogram log10 with filtered out noisey genes
_, bins = np.histogram(np.log10(filtered_last_column + 1), bins='auto')
plt.hist(filtered_last_column, bins=10**bins);
plt.gca().set_xscale("log")
plt.title('Filtered cells per gene')
plt.xlabel('Log10(Cells per gene)')
plt.ylabel('Frequency')

"""**Question 2**
Normalize and visualize the data as follows:
"""

adata = sc.read_10x_mtx('/content/gdrive/My Drive/Statistical ML/Homework 1/pbmc4k_filtered_gene_bc_matrices/filtered_gene_bc_matrices/GRCh38/',  # the directory with the `.mtx` file
    var_names='gene_symbols',                # use gene symbols for the variable names (variables-axis index)
    cache=True)                              # write a cache file for faster subsequent reading

adata.var_names_make_unique()

adata #Rows correspond to cells and columns to genes.

#filtering
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

sc.pp.calculate_qc_metrics(adata, expr_type='counts', var_type='genes', inplace= True)

print(adata.var)

"""**Question 2a.**
Normalize the data in Q1 with global scaling to the median library size
"""

#Normalize to median of library size, or'total_counts', which is specified with target_sum= None
sc.pp.normalize_total(adata, target_sum= None)

sc.pp.calculate_qc_metrics(adata, expr_type='counts', var_type='genes')

"""**Question 2b.**
Embed the normalized data to 2D using t-SNE or Umap or the first two principal components. Discuss the assumptions of your method of choice.
"""

#Principle Component Analysis
sc.tl.pca(adata, svd_solver='arpack')

sc.pl.pca(adata, color='CST3')

"""PCA aims to identify two main axes that capture most of the variation in the data. One assumption is that the data are independent so the observations are independent. Another assumption is that the correlation between variables are true correlations and are not biased.

**Question 2c.**
Color cells in the embedded 2D map by log10 of library size. Interpret the plot.
"""

#Color   cells   in   the   embedded   2D   map   by   log10   of library size
sc.tl.pca(adata, svd_solver='arpack')
sc.pl.pca(adata, color = 'log1p_total_counts' )

"""There is no clear separation in the data. The first plot was colored based on gene expression, and the colors form two separate clusters. This means there is some separation between cells based on gene expression. The second plot shows no distinct clustering based on library size. 2 principle components were not able to capture the variance here.

**Question 3**
Regress out library size using a linear regression model (after scaling to median library size performed in Q2a) and redo Q2b-c. Explain if/why you used a regularizer.
"""

sc.pp.regress_out(adata, ['total_counts'])

sc.tl.pca(adata, svd_solver='arpack')
sc.pl.pca(adata, color='CST3')

#Color   cells   in   the   embedded   2D   map   by   log10   of library size
sc.tl.pca(adata, svd_solver='arpack')
sc.pl.pca(adata, color = 'log1p_total_counts' )

"""After regressing out the library size the PCA plots look similar to before. The first PCA plot, colored based on gene expression, had the best separation of colors/cells into clusters. The second plot has overlap of different library sizes within clusters and no apparent subpopulations are formed. """