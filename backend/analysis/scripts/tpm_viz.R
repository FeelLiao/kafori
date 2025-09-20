## 用ComplexHeatmap包实现绘制热图

## 用ComplexHeatmap包实现绘制热图（优化版）

suppressPackageStartupMessages({
  library(tidyverse) # dplyr / tidyr / stringr / readr
  library(svglite)
  library(ComplexHeatmap)
  library(circlize)
  library(cluster)
  library(grid)
  library(matrixStats) # 高性能行/列统计
})

# 可配置参数
INPUT_CSV <- "upload/基因表达量表-tpm标准化.csv"
OUTPUT_SVG <- "upload/tpm_heatmap.svg"

width <- 600 # 像素（SVG 仍是向量图，此处只影响比例）
height <- 700
font_sz <- 14 # 列名/行名基础字体
legend_sz <- 12
rotate_colnames <- 90
show_dendrogram <- FALSE # 是否显示顶部/右侧树（顺序仍可按聚类）
cluster_cols <- TRUE # 列是否参与聚类（即便不显示树，仍会排序）
max_k <- 12
var_top_n <- 2000 # 极大数据时选前 N 个方差最大的基因
large_threshold <- 5000
kmeans_max_k <- 15
seed <- 123

# 颜色：对称蓝-白-红
col_fun <- circlize::colorRamp2(
  c(-2, 0, 2),
  c("#b2182b", "#f7f7f7", "#2166ac")
)

# 修正：在设备内执行绘图函数，确保 ComplexHeatmap 样式生效
plot_to_raw <- function(draw_fn, width = 800, height = 600) {
  tf <- tempfile(fileext = ".svg")
  svglite(file = tf, width = width / 72, height = height / 72)
  grid::grid.newpage()
  draw_fn()
  dev.off()
  img_raw <- readChar(tf, nchars = file.info(tf)$size, useBytes = TRUE)
  unlink(tf)
  img_raw
}

# 读取数据
stopifnot(file.exists(INPUT_CSV))
gene_tpm <- readr::read_csv(INPUT_CSV, show_col_types = FALSE)

if (!"gene_id" %in% colnames(gene_tpm)) {
  stop("Input CSV must contain column 'gene_id'")
}

# 整理为 matrix：行=gene，列=sample
df <- gene_tpm |>
  tidyr::pivot_longer(-gene_id, names_to = "sample", values_to = "tpm") |>
  mutate(sample = stringr::str_replace_all(sample, "\\-.*", "")) |>
  group_by(gene_id, sample) |>
  summarise(tpm = mean(suppressWarnings(as.numeric(tpm))), .groups = "drop") |>
  tidyr::pivot_wider(names_from = sample, values_from = tpm) |>
  as.data.frame() |>
  tibble::remove_rownames()

sample_cols <- setdiff(colnames(df), "gene_id")
if (length(sample_cols) == 0) stop("No sample columns found.")

# 强制数值
df[sample_cols] <- lapply(df[sample_cols], function(x) suppressWarnings(as.numeric(x)))
# 丢弃全 NA 的行
df <- df[rowSums(!is.na(df[sample_cols])) > 0, , drop = FALSE]
n_genes <- nrow(df)
if (n_genes == 0) stop("No valid genes after filtering.")

mat <- df |>
  tibble::column_to_rownames("gene_id") |>
  as.matrix()

# 向量化填充 NA：用每行均值
row_means <- rowMeans2(mat, na.rm = TRUE)
na_idx <- which(is.na(mat), arr.ind = TRUE)
if (length(na_idx)) {
  mat[na_idx] <- row_means[na_idx[, 1]]
}
mat[is.na(mat)] <- 0 # 如整行 NA，均值为 NA 时兜底

# 行标准化为 z-score：更高效的 rowMeans2/rowSds
mu <- rowMeans2(mat)
sdv <- rowSds(mat)
sdv[sdv == 0 | !is.finite(sdv)] <- 1
mat_z <- sweep(mat, 1, mu, "-")
mat_z <- sweep(mat_z, 1, sdv, "/")

# 大矩阵时仅保留方差最高的前 var_top_n 行
current_n <- nrow(mat_z)
if (current_n > large_threshold) {
  vars <- rowVars(mat_z)
  keep_n <- min(var_top_n, length(vars))
  keep_idx <- order(vars, decreasing = TRUE)[seq_len(keep_n)]
  mat_z <- mat_z[keep_idx, , drop = FALSE]
  message(sprintf("Large matrix (%d genes) reduced to top %d variable genes.", current_n, keep_n))
  current_n <- nrow(mat_z)
}

# 自动选择行聚类的 k（用于统计输出；热图不强制分组显示）
set.seed(seed)

auto_choose_k_hclust <- function(mz, max_k) {
  if (nrow(mz) < 4) {
    return(1L)
  }
  upper <- min(max_k, nrow(mz) - 1, 20)
  if (upper < 2) {
    return(1L)
  }
  sub_mz <- if (nrow(mz) > 2500) mz[sample(seq_len(nrow(mz)), 2500), , drop = FALSE] else mz
  d <- dist(sub_mz)
  hc <- hclust(d, method = "ward.D2")
  ks <- 2:upper
  best_k <- 2
  best_sil <- -Inf
  for (k in ks) {
    cl <- cutree(hc, k = k)
    sil <- tryCatch(mean(cluster::silhouette(cl, d)[, 3]), error = function(e) NA_real_)
    if (is.finite(sil) && sil > best_sil) {
      best_sil <- sil
      best_k <- k
    }
  }
  best_k
}

auto_choose_k_kmeans <- function(mz, max_k) {
  ks <- 2:min(max_k, 30, nrow(mz) - 1)
  if (length(ks) == 0) {
    return(1L)
  }
  sse <- vapply(ks, function(k) kmeans(mz, centers = k, iter.max = 50)$tot.withinss, numeric(1))
  diffs <- -diff(sse) / sse[-length(sse)]
  cut_idx <- which(diffs < 0.10)[1]
  if (!is.na(cut_idx)) ks[cut_idx] else ks[which.min(sse)]
}

use_kmeans <- current_n > large_threshold
cluster_k <- if (use_kmeans) auto_choose_k_kmeans(mat_z, kmeans_max_k) else auto_choose_k_hclust(mat_z, max_k)
cluster_k <- max(1L, as.integer(cluster_k))

# 输出一些统计（保留）
if (cluster_k == 1L || current_n < 3) {
  clusters <- rep(1L, current_n)
  names(clusters) <- rownames(mat_z)
} else if (use_kmeans) {
  clusters <- kmeans(mat_z, centers = cluster_k, iter.max = 100)$cluster
} else {
  clusters <- cutree(hclust(dist(mat_z), method = "ward.D2"), k = cluster_k)
}
cluster_factor <- factor(clusters, levels = sort(unique(clusters)))
cluster_table <- tibble(gene_id = rownames(mat_z), cluster = paste0("Cluster_", as.integer(cluster_factor)))
cluster_summary <- cluster_table |>
  dplyr::group_by(.data$cluster) |>
  dplyr::tally(name = "n_genes") |>
  dplyr::arrange(.data$cluster)

# 构建热图（无树状图；底部列名旋转；字体更大；无图例标题）
ht <- Heatmap(
  mat_z,
  name = NULL,
  col = col_fun,
  show_row_names = FALSE,
  show_column_names = TRUE,
  column_names_side = "bottom",
  column_names_rot = rotate_colnames,
  column_names_gp = gpar(fontsize = font_sz),
  column_names_max_height = unit(18, "mm"),
  row_names_gp = gpar(fontsize = font_sz),
  cluster_rows = TRUE,
  cluster_columns = isTRUE(cluster_cols),
  show_row_dend = isTRUE(show_dendrogram),
  show_column_dend = isTRUE(show_dendrogram),
  column_title = NULL,
  show_heatmap_legend = TRUE,
  heatmap_legend_param = list(
    title = NULL,
    labels_gp = gpar(fontsize = legend_sz)
  ),
  use_raster = TRUE,
  raster_device = "png",
  raster_quality = 2,
  border = FALSE
)

# 在设备内绘制，确保样式生效
heatmap_svg <- plot_to_raw(
  function() {
    draw(ht, heatmap_legend_side = "right", annotation_legend_side = "right")
  },
  width = width,
  height = height
)

# 返回/保存
writeLines(heatmap_svg, con = OUTPUT_SVG, useBytes = TRUE)
message("Heatmap SVG saved to: ", normalizePath(OUTPUT_SVG, winslash = "/"))

invisible(list(
  heatmap_svg = heatmap_svg,
  cluster_table = cluster_table,
  cluster_summary = cluster_summary,
  used_cluster_k = cluster_k,
  reduced_from = n_genes,
  drawn_rows = current_n,
  method = if (use_kmeans) "kmeans+split" else "hclust"
))
