library(argparse)
library(cluster)
library(dplyr)
library(ggplot2)
library(readr)
library(Rtsne)

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
