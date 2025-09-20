from textwrap import dedent
deg_code = dedent(r"""
suppressPackageStartupMessages({
  library(edgeR)
  library(limma)
})

# 从 Python 注入的变量读取参数（提供默认兜底）
FDR_CUT <- if (exists("fdr_threshold")) as.numeric(fdr_threshold)[1] else 0.05
LFC_CUT <- if (exists("log2fc_threshold")) as.numeric(log2fc_threshold)[1] else 1
NORM_MTH <- if (exists("normalize_method")) as.character(normalize_method)[1] else "TMM"

# 主函数：对 expression_counts 的所有组做两两对比
deg_all_contrasts <- function(expression_counts, normalize_method = "TMM") {
  stopifnot("gene_id" %in% colnames(expression_counts))
  df <- as.data.frame(expression_counts, stringsAsFactors = FALSE)

  # 数值化 counts
  num_cols <- setdiff(colnames(df), "gene_id")
  for (nm in num_cols) df[[nm]] <- suppressWarnings(as.numeric(df[[nm]]))

  # 构造分组（列名中 '-' 前缀为组名；无 '-' 则用完整列名）
  samples <- num_cols
  if (length(samples) < 2) stop("需要至少两个样本列")
  groups_chr <- ifelse(str_detect(samples, "-"),
    str_split_fixed(samples, "-", 2)[, 1],
    samples
  )
  groups <- factor(groups_chr, levels = unique(groups_chr))

  # DGEList
  y <- DGEList(
    counts = df |> column_to_rownames("gene_id") |> as.matrix(),
    group = groups
  )

  keep <- filterByExpr(y, group = groups)
  y <- y[keep, , keep.lib.sizes = FALSE]
  y <- calcNormFactors(y, method = normalize_method)

  # 设计矩阵与拟合
  design <- model.matrix(~ 0 + groups)
  colnames(design) <- levels(groups)
  rownames(design) <- colnames(y)

  y <- estimateDisp(y, design = design, robust = TRUE)
  fit <- glmQLFit(y, design = design)

  lv <- levels(groups)
  if (length(lv) < 2) stop("组别少于2")

  combs <- combn(lv, 2, simplify = FALSE)

  res <- purrr::map(combs, function(pair) {
    A <- pair[1]
    B <- pair[2]
    cname <- sprintf("%s_vs_%s", A, B)

    contr <- limma::makeContrasts(
      contrasts = sprintf("%s-%s", A, B),
      levels = colnames(design)
    )
    qlf <- glmQLFTest(fit, contrast = contr[, 1, drop = TRUE])
    tt <- topTags(qlf, n = nrow(qlf$table))$table

    full <- as_tibble(tt, rownames = "gene_id") |>
      transmute(gene_id, logFC, logCPM, PValue, FDR)

    sig <- full |> filter(FDR < FDR_CUT, abs(logFC) > LFC_CUT)

    p <- ggplot(full, aes(x = logFC, y = -log10(pmax(FDR, 1e-300)))) +
      geom_point(aes(color = (FDR < FDR_CUT & abs(logFC) > LFC_CUT)),
        size = 0.9, alpha = 0.85
      ) +
      scale_color_manual(
        values = c(`FALSE` = "grey80", `TRUE` = "#d73027"),
        guide = "none"
      ) +
      geom_vline(xintercept = c(-LFC_CUT, LFC_CUT), linetype = "dashed", color = "grey50") +
      geom_hline(yintercept = -log10(FDR_CUT), linetype = "dashed", color = "grey50") +
      labs(title = cname, x = "log2FC", y = "-log10(FDR)") +
      theme_bw(base_size = 12)

    svg_txt <- plot_to_svg(p, width = width, height = height)

    list(name = cname, full = full, sig = sig, svg = svg_txt)
  })
  names(res) <- purrr::map_chr(combs, ~ sprintf("%s_vs_%s", .x[1], .x[2]))

  tables <- setNames(lapply(res, `[[`, "full"), names(res))
  sig_tables <- setNames(lapply(res, `[[`, "sig"), names(res))
  plots <- setNames(lapply(res, `[[`, "svg"), names(res))

  list(
    tables = tables,
    sig_tables = sig_tables,
    plots = plots,
    meta = list(
      groups = lv, contrasts = names(res),
      fdr_cut = FDR_CUT, lfc_cut = LFC_CUT, norm = normalize_method
    )
  )
}

# 入口：expression_counts 由 Python 注入；normalize_method/FDR/LFC 来自上面变量
deg_result <- deg_all_contrasts(expression_counts, normalize_method = NORM_MTH)
deg_result
""")

# p <- ggplot(deg_table, aes(logFC, -log10(adj.P.Val))) +
#   geom_hline(yintercept = -log10(0.05), linetype = "dashed", color = "black") +
#   geom_vline(xintercept = c(-1.2, 1.2), linetype = "dashed", color = "black") +
#   geom_point(aes(
#     size = -log10(adj.P.Val),
#     color = -log10(adj.P.Val)
#   )) +
#   scale_color_gradientn(
#     values = seq(0, 1, 0.2),
#     colors = c("#39489f", "#39bbec", "#f9ed36", "#f38466", "#b81f25")
#   ) +
#   scale_size_continuous(range = c(0, 1)) +
#   theme_bw(base_size = 12) +
#   theme(
#     panel.grid = element_blank(),
#     legend.position = "right",
#     legend.justification = c(0, 1)
#   ) +
#   # 设置图例
#   guides(
#     col =
#       guide_colorbar(
#         title = "-Log10_q-value",
#         ticks.colour = NA,
#         reverse = T,
#         title.vjust = 0.8,
#         barheight = 8,
#         barwidth = 1
#       ),
#     size = "none"
#   ) +
#   # 添加标签：
#   # geom_text_repel(
#   #   data = filter(data, gene %in% core_gene),
#   #   max.overlaps = getOption("ggrepel.max.overlaps", default = 20),
#   #   # 这里的filter很关键，筛选你想要标记的基因
#   #   aes(label = gene),
#   #   size = 2,
#   #   color = "black"
#   # ) +
#   xlab("Log2FC") +
#   ylab("-Log10(FDR q-value)")
