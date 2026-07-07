# Render an .Rmd to outputs/reports/ using the pandoc bundled with RStudio.
# Usage: Rscript tools/render.R 01-eda.Rmd
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Usage: Rscript tools/render.R <file.Rmd>")
Sys.setenv(RSTUDIO_PANDOC = "C:/Program Files/RStudio/resources/app/bin/quarto/bin/tools")
rmarkdown::render(args[[1]], output_dir = "outputs/reports", envir = new.env())
