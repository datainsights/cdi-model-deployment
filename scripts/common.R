# 📦 Common R Packages for General Data Science
if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv")
if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
library(BiocManager)

common_pkgs <- c(
  "tidyverse", 
  "skimr", 
  "janitor", 
  "broom", 
  "infer", 
  "ggplot2", 
  "plotly", 
  "ggpubr",
  "DiagrammeR",
  "pheatmap",
  "DiagrammeRsvg",
  "remotes",
  "rsvg"
  )

for (pkg in common_pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE)) renv::install(pkg)
}
