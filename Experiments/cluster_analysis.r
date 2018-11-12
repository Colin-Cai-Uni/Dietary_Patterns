library(argparse)
library(cluster)
library(dplyr)
library(ggplot2)
library(readr)
library(Rtsne)

# The script used to conduct all the k-medoids clustering experiments.
# 
# Parameters
# ----------
# inputfile : file location
#     Location of the clustering input data. The input file should be 
#     in csv format.
# columns : file location
#     Location of a file listing the columns to use as input features, 
#     with each column on a new line.
# k : integer
#     The number of clusters to assign.
# silhouette : flag
#     If this flag is present, the script will display the mean silhouette 
#     coefficient of the clustering results.
# export : file location
#     The path to where the newly clustered data file should be saved.
# 
# Acknowledgements
# ----------------
# Code from was taken from the R-bloggers tutorial "Clustering Mixed Data Types in R"
# https://www.r-bloggers.com/clustering-mixed-data-types-in-r/
parser <- ArgumentParser()
    parser$add_argument('inputfile', help = 'Input file')
    parser$add_argument('columns', help = 'Input columns')
    parser$add_argument('k', help = 'Number to clusters assign')
    parser$add_argument('-silhouette', help = 'View silhouette', action = 'store_true')
    parser$add_argument('-export', help = 'Export the processed dataset with labels')

args <- parser$parse_args()

df <- read.csv(args$inputfile)
columns <- scan(args$columns, what = '', sep = '\n')
df <- select(df, columns)

gower_dist <- daisy(df, metric = 'gower')
gower_mat <- as.matrix(gower_dist)
pam_fit <- pam(gower_dist, diss = TRUE, k = args$k)

if(args$silhouette){
    sil_coeff <- pam_fit$silinfo$avg.width
    message(sprintf('For n_clusters = %s The average silhouette_score is : %s', args$k, sil_coeff))
}

if(!is.null(args$export)){
    pam_results <- df %>%
    mutate(cluster = pam_fit$clustering) %>%
    group_by(cluster) %>%
    do(the_summary = summary(.))

    res = data.frame(cluster = pam_fit$clustering - 1)
    write.csv(res, args$export, row.names = FALSE)
}
