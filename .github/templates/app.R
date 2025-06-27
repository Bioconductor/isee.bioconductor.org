# Launch the ShinyApp (Do not remove this comment)

sce <- readRDS(url(##PLACEHOLDERDATASETURI##))
source(url(##PLACEHOLDERCONFIGURI##))
iSEE::iSEE(se = sce, initial = initial)
