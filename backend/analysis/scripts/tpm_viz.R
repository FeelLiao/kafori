## 用ComplexHeatmap包实现绘制热图

suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(svglite))

plot_to_raw <- function(plot_obj, width = 800, height = 600) {
  tf <- tempfile(fileext = ".svg")
  svglite(file = tf, width = width / 72, height = height / 72)
  print(plot_obj)
  dev.off()
  img_raw <- readChar(tf, nchars = file.info(tf)$size, useBytes = TRUE)
  unlink(tf)
  return(img_raw)
}

suppressPackageStartupMessages({
  library(ComplexHeatmap)
  library(circlize)
  library(cluster)
})

gene_tpm <- read_csv("基因表达量表-tpm标准化.csv")
width <- 900
height <- 600
cluster_k <- NA
max_k <- 12
palette <- NULL
# 1. Clean & numeric coercion
var_top_n <- 2000
large_threshold <- 5000
kmeans_max_k <- 15

stopifnot("gene_id" %in% colnames(gene_tpm))
df <- gene_tpm |>
  gather(key = "sample", value = "tpm", -gene_id) |>
  mutate(sample = str_replace_all(sample, "\\-.*", "")) |>
  group_by(gene_id, sample) |>
  summarise(tpm = mean(tpm)) |>
  ungroup() |>
  pivot_wider(names_from = sample, values_from = tpm) |>
  as.data.frame() |>
  tibble::remove_rownames()
sample_cols <- setdiff(colnames(df), "gene_id")
df[sample_cols] <- lapply(
  df[sample_cols],
  function(x) suppressWarnings(as.numeric(x))
)
df <- df[rowSums(!is.na(df[sample_cols])) > 0, , drop = FALSE]
n_genes <- nrow(df)
if (n_genes == 0) stop("No valid genes after filtering.")

mat <- df |>
  column_to_rownames("gene_id") |>
  as.matrix()

# 填充 NA
row_means <- rowMeans(mat, na.rm = TRUE)
for (i in seq_len(nrow(mat))) {
  nas <- is.na(mat[i, ])
  if (any(nas)) mat[i, nas] <- if (is.finite(row_means[i])) row_means[i] else 0
}

# 行标准化
mu <- rowMeans(mat)
sdv <- apply(mat, 1, sd)
sdv[sdv == 0 | is.na(sdv)] <- 1
mat_z <- (mat - mu) / sdv

# 大规模数据: 先按方差选前 var_top_n
if (n_genes > large_threshold) {
  vars <- apply(mat_z, 1, var)
  keep_n <- min(var_top_n, length(vars))
  keep_genes <- names(sort(vars, decreasing = TRUE))[seq_len(keep_n)]
  mat_z <- mat_z[keep_genes, , drop = FALSE]
  message(sprintf(
    "Large matrix (%d genes) reduced to top %d variable genes.",
    n_genes, keep_n
  ))
}

current_n <- nrow(mat_z)

# 选择聚类方式
auto_choose_k_hclust <- function(mz, max_k) {
  if (nrow(mz) < 4) {
    return(1L)
  }
  upper <- min(max_k, nrow(mz) - 1, 20)
  if (upper < 2) {
    return(1L)
  }
  sub_mz <- mz
  if (nrow(mz) > 2500) {
    set.seed(123)
    sub_idx <- sample(seq_len(nrow(mz)), 2500)
    sub_mz <- mz[sub_idx, , drop = FALSE]
  }
  d <- dist(sub_mz)
  hc <- hclust(d, method = "ward.D2")
  ks <- 2:upper
  best_k <- 2
  best_sil <- -Inf
  for (k in ks) {
    cl <- cutree(hc, k = k)
    sil <- tryCatch(mean(cluster::silhouette(cl, d)[, 3]),
      error = function(e) NA_real_
    )
    if (is.finite(sil) && sil > best_sil) {
      best_sil <- sil
      best_k <- k
    }
  }
  best_k
}

auto_choose_k_kmeans <- function(mz, max_k) {
  # 用肘部法或 silhouette 近似 (这里只用总 SSE 下降比例简单估计)
  set.seed(123)
  ks <- 2:min(max_k, 30, nrow(mz) - 1)
  if (length(ks) == 0) {
    return(1L)
  }
  sse <- numeric(length(ks))
  for (i in seq_along(ks)) {
    km <- kmeans(mz, centers = ks[i], iter.max = 50)
    sse[i] <- km$tot.withinss
  }
  # 找“拐点”：相邻差分比率降幅 < 10% 则停止
  diffs <- -diff(sse) / sse[-length(sse)]
  cut_idx <- which(diffs < 0.10)[1]
  if (!is.na(cut_idx)) ks[cut_idx] else ks[which.min(sse)]
}

use_kmeans <- current_n > large_threshold

if (is.na(cluster_k) || cluster_k <= 0) {
  cluster_k <- if (use_kmeans) {
    auto_choose_k_kmeans(
      mat_z,
      kmeans_max_k
    )
  } else {
    auto_choose_k_hclust(mat_z, max_k)
  }
} else {
  cluster_k <- max(1L, as.integer(cluster_k))
}

if (cluster_k == 1L || current_n < 3) {
  clusters <- rep(1L, current_n)
  names(clusters) <- rownames(mat_z)
} else if (use_kmeans) {
  set.seed(123)
  km <- kmeans(mat_z, centers = cluster_k, iter.max = 100)
  clusters <- km$cluster
} else {
  d_all <- dist(mat_z)
  hc_all <- hclust(d_all, method = "ward.D2")
  clusters <- cutree(hc_all, k = cluster_k)
}

cluster_factor <- factor(clusters, levels = sort(unique(clusters)))
cluster_table <- tibble(
  gene_id = rownames(mat_z),
  cluster = paste0("Cluster_", as.integer(cluster_factor))
)
cluster_summary <- cluster_table |>
  count(cluster, name = "n_genes") |>
  arrange(cluster)

# 颜色
if (is.null(palette) || length(palette) < 3) {
  palette <- c(
    "#4575B4", "#91BFDB",
    "#E0F3F8", "#FFFFBF", "#FEE090",
    "#FC8D59", "#D73027"
  )
}
qv <- quantile(mat_z, probs = c(0.02, 0.5, 0.98), na.rm = TRUE)
col_fun <- circlize::colorRamp2(
  c(qv[1], qv[2], qv[3]),
  c(palette[1], palette[ceiling(length(palette) / 2)], palette[length(palette)])
)

# 行注释
if (!requireNamespace("RColorBrewer", quietly = TRUE)) {
  cluster_palette <- grDevices::rainbow(length(levels(cluster_factor)))
} else {
  cluster_palette <- RColorBrewer::brewer.pal(
    max(3, min(8, length(levels(cluster_factor)))), "Set2"
  )
}
cluster_colors <- setNames(
  rep_len(cluster_palette, length(levels(cluster_factor))),
  paste0("Cluster_", levels(cluster_factor))
)
row_ha <- rowAnnotation(
  Cluster = factor(paste0("Cluster_", as.integer(cluster_factor)),
    levels = paste0("Cluster_", levels(cluster_factor))
  ),
  col = list(Cluster = cluster_colors),
  annotation_name_side = "top"
)

# 只对列聚类（行已由聚类结果分割），避免再次 O(n^2)
ht <- Heatmap(
  mat_z,
  name = "Z",
  col = col_fun,
  show_row_names = FALSE,
  show_column_names = TRUE,
  row_split = cluster_factor,
  cluster_rows = FALSE, # 关键：大数据时不要再层次聚类行
  cluster_columns = TRUE,
  column_title = "Gene Expression (row z-score)",
  use_raster = current_n > 1500,
  raster_device = "png",
  raster_quality = 2
) + row_ha

# 显式 draw，避免重复计算
heatmap_svg <- plot_to_raw(
  {
    draw(ht, heatmap_legend_side = "right", annotation_legend_side = "right")
  },
  width = width,
  height = height
)

list(
  heatmap_svg = heatmap_svg,
  cluster_table = cluster_table,
  cluster_summary = cluster_summary,
  used_cluster_k = cluster_k,
  reduced_from = n_genes,
  drawn_rows = current_n,
  method = if (use_kmeans) "kmeans+split" else "hclust"
)

output_svg <- "tpm_heatmap.svg"

writeLines(heatmap_svg, con = output_svg, useBytes = TRUE)
message("Heatmap SVG saved to: ", normalizePath(output_svg, winslash = "/"))
