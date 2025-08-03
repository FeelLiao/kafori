library(ComplexHeatmap)

## 用ComplexHeatmap包实现绘制热图

tpm_aver <- gene_tpm |>
  gather(key = "sample", value = "tpm", -gene_id) |>
  mutate(sample = str_replace_all(sample, "\\-.*", "")) |>
  group_by(gene_id, sample) |>
  summarise(tpm = mean(tpm)) |>
  ungroup() |>
  pivot_wider(names_from = sample, values_from = tpm) |>
  column_to_rownames(var = "gene_id")

scale_rows <- function(data) {
  scale_r <- function(x) {
    m <- apply(x, 1, mean, na.rm = TRUE)
    s <- apply(x, 1, sd, na.rm = TRUE)
    return((x - m) / s)
  }
  mat <- switch("row",
    none = data,
    row = scale_r(data),
    column = t(scale_r(t(data)))
  )
  return(mat)
}

inter_s <- scale_rows(inter)
inter_d <- dist(inter_s, method = "euclidean")
inter_dh <- hclust(inter_d, method = "ward.D2")
inter_dhc <- cutree(inter_dh, k = 2)

inter_dhc <- as.data.frame(inter_dhc)

annotation_row_in <- inter_dhc |>
  rename(cluster_id = inter_dhc) |>
  mutate(
    cluster_id = paste("Cluster", cluster_id, sep = "")
  )
ann_colors <- list(cluster_id = c(
  `Cluster1` = "#7793b3",
  `Cluster2` = "#a2af9f"
))

inter_hp <- pheatmap(inter,
  color = colorRampPalette(c(
    "#ffffff", "#d8ead4",
    "#acd1bf", "#80b7b1", "#589ca7", "#3a7f9b", "#30628c"
  ))(100),
  scale = "row",
  cluster_rows = TRUE,
  clustering_method = "ward.D2",
  cluster_cols = FALSE,
  show_rownames = FALSE,
  show_colnames = TRUE,
  annotation_row = annotation_row_in,
  annotation_names_row = FALSE,
  annotation_colors = ann_colors,
  fontsize = 12,
  main = "Expression of ARGs in AS",
)