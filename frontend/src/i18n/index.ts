// src/i18n/index.ts
import { createI18n } from 'vue-i18n'
import zhCn from "element-plus/es/locale/lang/zh-cn";
import En from "element-plus/es/locale/lang/en";

const messages = {
    en: {
        /*
        navigation translation
        * */
        nav_Home: 'Home',
        nav_Transcripts: 'Transcripts',
        nav_Pipeline: 'Pipelines',
        nav_Download: 'Downloads',
        nav_Tools: 'Tools',
        nav_Help: 'Help',
        nav_Contact: 'Contact',
        nav_Login: 'Login',
        nav_Login_out: 'Login Out',

        /*
        home translation
        * */
        home_ExperimentCategory: 'ExperimentCategory',
        home_Experiment: 'Experiment',
        home_SampleCounts: 'SampleCounts',

        Explore: 'Explore',
        mRNA: 'mRNA',
        the: 'the',
        mystery: 'mystery',
        of: 'of',
        blank: ' ',
        title: 'Explore {type} ',
        transcriptome_data_analysis_and: 'Transcriptome Data Analysis and {Visualization} ',
        Visualization: 'Visualization',
        Platform: 'Platform',
        home_desc: 'Our platform uses advanced visualization technology to transform complex transcriptomic data into intuitive visual representations. Through interactive charts and graphics, users can easily understand key information such as gene expression patterns, differential analysis results, and functional annotations.',
        home_start: 'Get Started',
        home_more: 'Learn More',
        home_data_dashboard: 'Data Dashboard',

        home_year_map: 'The Number of Samples with Year',
        home_year_mapDesc: 'The distribution of the number of samples with year, only top 10 years are shown here.',

        home_sample_map: 'The Number of Samples',
        home_sample_mapDesc: 'The distribution of the number of samples, only top 10 experiments are shown here.',

        home_about_platform: 'About Platform',
        home_technical_architecture: 'Technical Architecture',
        home_technical_architecture_introduction: 'This platform is built using modern web technologies. The main technology stack includes:',
        home_tech_1: 'Frontend',
        home_tech_2: 'Data analysis',
        home_tech_3: 'Data storage',
        home_tech_4: 'Backend',
        home_tech_1_desc: 'Vue3 + Element Plus + Tailwind CSS',
        home_tech_2_desc: 'Python (Pandas, NumPy) + R (ggplot2)',
        home_tech_3_desc: 'MySQL + Redis',
        home_tech_4_desc: 'FastAPI',
        home_data_source: 'Data Source',
        home_data_source_desc: 'This platform integrates genomic data from multiple public databases, including:',
        home_db_1: 'NCBI SRA Database',
        home_db_2: 'CNCB GSA Database',
        home_db_3: 'Our laboratory',


        Transcripts_nav: 'Navigation',
        Transcripts_exp_category: 'Category',
        Transcripts_experiment: 'Experiment',
        Transcripts_sample: 'Sample',
        Transcripts_result: 'Result',
        Transcripts_experiment_list: "Experiment List",
        Transcripts_sample_list: "Sample List",

        Transcripts_total: 'total',
        Transcripts_jump: 'jump to',
        Transcripts_page: 'page',

        Transcripts_exp_id: 'UniqueEXID',
        Transcripts_exp_name: 'ExperimentName',
        Transcripts_exp_action: 'Action',

        Transcripts_sample_id: 'SampleID',
        Transcripts_sample_age: 'SampleAge',
        Transcripts_sample_detail: 'SampleDetail',
        Transcripts_sample_db: 'DepositDatabase',
        Transcripts_sample_acn: 'Accession',
        Transcripts_sample_origin: 'Origin',
        Transcripts_sample_cpt: 'CollectionPart',
        Transcripts_sample_cte: 'CollectionTime',
        Transcripts_sample_action: 'Action',

        Transcripts_search: 'Search',
        Transcripts_upload: 'Upload',
        Transcripts_analysis: 'Analysis',
        Transcripts_Analysis_Type: 'Analysis Type',

        Transcripts_option1: 'input',
        Transcripts_option2: 'file',
        Transcripts_option3: 'all',

        Transcripts_sel_col: 'Select Column',
        Transcripts_asc: 'Ascending',
        Transcripts_desc: 'Descending',
        Transcripts_add_sort: 'Add Sort',
        Transcripts_del: 'Delete',
        Transcripts_clear: 'Clear',

        Transcripts_down_images: 'Download Images',
        Transcripts_down_csv: 'Download CSV',


        Pipelines_sample_upload: 'Sample Upload',
        Pipelines_tpm_counts_upload: 'Tpm / Counts Upload',
        Pipelines_rawdata_upload: 'Rawdata Upload',

        Pipelines_pending_upload: 'Pending upload',
        Pipelines_uploaded: 'Uploaded',
        Pipelines_tpm_pending_upload: 'Tpm Pending upload',
        Pipelines_tpm_uploaded: 'Tpm Uploaded',
        Pipelines_counts_pending_upload: 'Counts Pending upload',
        Pipelines_counts_uploaded: 'Counts Uploaded',

        Pipelines_drag_upload: 'drag file to here or',
        Pipelines_click_upload: 'click to upload',

        Pipelines_A1_desc: 'After completing A1, proceed with A2/A3(only one)',
        Pipelines_A1_file_desc: 'Supports CSV, TSV, Excel and JSON; must be uploaded according to the standard format.',

        Pipelines_upload: 'Upload File',

        Pipelines_A1_tip: 'A1 finished to continue',

        Pipelines_btn_start_upstream: 'start upstream analysis',
        Pipelines_btn_upstream_status: 'Status Inquiry',
        Pipelines_btn_upstream_result: 'Get Analysis Results',
        Pipelines_btn_put_database: 'Put into Database',

        Pipelines_file_size: 'One File Size <= 10GB',
        Pipelines_file_example: 'Download Example File',


        Pipelines_analysis_status: 'Analysis Status',
        Pipelines_pre_result: 'Result Preview',

        Pipelines_unknown: 'unknown',
        Pipelines_pending: 'pending',
        Pipelines_running: 'running',
        Pipelines_failed: 'failed',
        Pipelines_finished: 'finished',

        Pipelines_ready: 'ready',
        Pipelines_not_ready: 'not ready',

        Pipelines_task: 'Task Upload List',
        Pipelines_no_task: 'There is no upload task',


        Download_list: 'Download List',
        Download_file_category: 'Category',
        Download_file_name: 'FileName',
        Download_file: 'File',
        Download_file_action: 'Action',
        Download_btn_download: 'Download',

        Contact_lwf_name: 'Wan-Feng Li',
        Contact_lwf_introduction: 'Wan-Feng Li is a Researcher and Master’s Supervisor at the Institute of Forestry, Chinese Academy of Forestry. He holds a Ph.D. in Botany from Peking University. His main research interests include breeding techniques and regulation of forest trees, molecular mechanisms of phase transitions in trees, and genetic improvement of conifers such as larch. Since joining the institute in 2009, he has led several national major research projects and conducted a postdoctoral fellowship at University of Natural Resources and Life Sciences, Vienna',

        Contact_ltq_name: 'Tang-Quan Liao',
        Contact_ltq_introduction: 'Tang-Quan Liao has served as the project leader, overseeing system architecture design and backend development. He received his Bachelor’s degree from Hunan Agricultural University and is currently pursuing a Master’s degree at the Institute of Forestry, Chinese Academy of Forestry, where he researches reproductive phase transitions in Japanese larch (Larix kaempferi) under the supervision of Professor Wan-Feng Li. With a strong passion for data analysis and visualization, he aims to continue contributing to data-driven biological research.',

        Contact_zjj_name: 'Jun-Jie Zhou',
        Contact_zjj_introduction: 'Jun-Jie Zhou is mainly responsible for front - end development, database design, and deployment. He graduated from Jishou University Zhangjiajie College with a bachelor\'s degree in Computer Science, where he focused on web development and operations. He has a strong passion for data visualization and continuously explores the construction and maintenance of cloud platforms.',

        Contact_team: 'Our Team',
        Contact_team_desc: 'We are committed to promoting the integration of forestry science and information technology. We welcome more like-minded partners to join us in exploring new directions for data-driven biological research.',

        footer_analytics: 'Transcriptome Data Analysis',
        footer_desc: 'A professional visualization platform exploring the mysteries of the genome, providing data support for biological research.',
        footer_platform: 'Platform',
        footer_resource: 'Resource',
        footer_support: 'Support',
        footer_support_desc: 'Open source is not easy. Follow github/gitee to get the latest updates. Hope to give a little star to support.',
        footer_copy: '© 2025 Transcriptome Data Analysis Platform, Institute of Forestry, Chinese Academy of Forestry. All rights reserved.',
        footer_copy_txt: 'Copyright 2025 The Institute of Forestry, Chinese Academy of Forestry',

    },

    zh: {
        /*
        导航栏翻译
        * */
        nav_Home: '首页',
        nav_Transcripts: '转录组',
        nav_Pipeline: '流水线',
        nav_Download: '下载',
        nav_Tools: '工具',
        nav_Help: '帮助',
        nav_Contact: '联系我们',
        nav_Login: '登录',
        nav_Login_out: '退出',

        /*
        首页翻译
        * */
        home_ExperimentCategory: '实验种类',
        home_Experiment: '实验名',
        home_SampleCounts: '样本数量',

        Explore: '探索',
        mRNA: 'mRNA',
        the: '的',
        mystery: '奥秘',
        title: '探索{type}',

        transcriptome_data_analysis_and: '转录组数据分析及',
        Visualization: '可视化',
        Platform: '平台',
        blank: ' ',

        home_desc: '我们的平台采用先进的可视化技术，将复杂的转录组数据转化为直观的视觉表现。通过交互式图表和图形，用户可以轻松理解基因表达模式、差异分析结果以及功能注释等关键信息。',
        home_start: '开始探索',
        home_more: '了解更多',
        home_data_dashboard: '数据仪表盘',

        home_year_map: '年份样本数量统计',
        home_year_mapDesc: '年份样本数量分布情况，仅显示前10个年份的样本。',

        home_sample_map: '样本数量统计',
        home_sample_mapDesc: '样本数量分布情况，仅显示前10个实验的样本。',

        home_about_platform: '关于平台',
        home_technical_architecture: '技术架构',
        home_technical_architecture_introduction: '本平台采用现代Web技术构建，主要技术栈包括：',
        home_tech_1: '前端框架',
        home_tech_2: '数据分析',
        home_tech_3: '数据存储',
        home_tech_4: '后端框架',
        home_tech_1_desc: 'Vue3 + Element Plus + Tailwind CSS',
        home_tech_2_desc: 'Python (Pandas, NumPy) + R (ggplot2)',
        home_tech_3_desc: 'MySQL + Redis',
        home_tech_4_desc: 'FastAPI',
        home_data_source: '数据来源',
        home_data_source_desc: '本平台整合了多个公共数据库的基因组数据，包括：',
        home_db_1: 'NCBI SRA 数据库',
        home_db_2: 'CNCB GSA 数据库',
        home_db_3: '我们的实验室',

        Transcripts_nav: '转录组导航',
        Transcripts_experiment: '实验',
        Transcripts_exp_category: '实验种类',
        Transcripts_sample: '样本',
        Transcripts_result: '结果',
        Transcripts_experiment_list: "实验列表",
        Transcripts_sample_list: "样本列表",

        Transcripts_total: '总共',
        Transcripts_jump: '跳至',
        Transcripts_page: '页',

        Transcripts_exp_id: '实验编号',
        Transcripts_exp_name: '实验名称',
        Transcripts_exp_action: '操作',

        Transcripts_sample_id: '编号',
        Transcripts_sample_age: '年龄',
        Transcripts_sample_detail: '详情',
        Transcripts_sample_db: '数据库',
        Transcripts_sample_acn: '接入号',
        Transcripts_sample_origin: '来源',
        Transcripts_sample_cpt: '采集部位',
        Transcripts_sample_cte: '采集时间',
        Transcripts_sample_action: '操作',

        Transcripts_search: '检索',
        Transcripts_upload: '上传',
        Transcripts_analysis: '分析',
        Transcripts_Analysis_Type: '分析类型',
        Transcripts_option1: '输入',
        Transcripts_option2: '文件',
        Transcripts_option3: '全部',

        Transcripts_sel_col: '选择列',
        Transcripts_asc: '升序',
        Transcripts_desc: '降序',
        Transcripts_add_sort: '添加排序',
        Transcripts_del: '删除',
        Transcripts_clear: '清除',
        Transcripts_down_images: '下载所有图片',
        Transcripts_down_csv: '下载所有CSV',

        Pipelines_sample_upload: '样本文件上传',
        Pipelines_tpm_counts_upload: 'Tpm / Counts 文件上传',
        Pipelines_rawdata_upload: 'Rawdata 文件上传',

        Pipelines_pending_upload: '待上传',
        Pipelines_uploaded: '已上传',
        Pipelines_tpm_pending_upload: 'Tpm待上传',
        Pipelines_tpm_uploaded: 'Tpm已上传',
        Pipelines_counts_pending_upload: 'Counts待上传',
        Pipelines_counts_uploaded: 'Counts已上传',
        Pipelines_drag_upload: '拖拽文件到此处，或',
        Pipelines_click_upload: '点击上传',

        Pipelines_upload: '上传文件',

        Pipelines_A1_desc: '完成 A1 后操作 A2/A3（两者二选一继续）',
        Pipelines_A1_file_desc: '支持 CSV，TSV，Excel，JSON，需要按照标准格式上传。',
        Pipelines_A1_tip: 'A1 完成后继续',

        Pipelines_btn_start_upstream: '启动上游分析',
        Pipelines_btn_upstream_status: '状态查询',
        Pipelines_btn_upstream_result: '获取上游分析结果',
        Pipelines_btn_put_database: '写入数据库',


        Pipelines_file_format: '支持扩展名：.csv, .xls, .xlsx, .txt',
        Pipelines_file_size: '单个文件 <= 10GB',
        Pipelines_analysis_status: '分析状态',
        Pipelines_pre_result: '结果准备',

        Pipelines_unknown: '未开始',
        Pipelines_pending: '挂载中',
        Pipelines_running: '分析中',
        Pipelines_failed: '分析失败',
        Pipelines_finished: '已完成',

        Pipelines_ready: '已就绪',
        Pipelines_not_ready: '未就绪',

        Pipelines_task: '任务上床列表',
        Pipelines_no_task: '暂无上传任务',

        Download_list: '下载列表',
        Download_file_category: '种类',
        Download_file_name: '文件名',
        Download_file: '文件',
        Download_file_action: '操作',
        Download_btn_download: '下载',


        Contact_lwf_name: '李万峰',
        Contact_lwf_introduction: '李万峰，北京大学植物学博士，中国林业科学研究院林业研究所研究员、硕士生导师。主要研究方向为林木繁育技术与调控、生殖阶段转变以及落叶松等针叶树的分子育种与细胞遗传机制。2009年加入林业研究所，曾在奥地利维也纳农业与科学大学进行博士后研究。 曾主持多个国家级和重大科研项目，在国际林业与植物生物学领域有较高学术影响力。',

        Contact_ltq_name: '廖堂全',
        Contact_ltq_introduction: '担任此网站开发的负责人，主要负责项目架构设计和后端代码开发。本科毕业于湖南农业大学，硕士阶段在中国林业科学研究院林业研究所，跟随李万峰老师开展日本落叶松生殖阶段转变相关研究。对数据分析和可视化充满兴趣，希望能在数据驱动的生物研究中不断探索与创造价值。',

        Contact_zjj_name: '周俊杰',
        Contact_zjj_introduction: '周俊杰，主要负责项目的前端开发，数据库设计和部署工作，本科毕业于吉首大学张家界学院计算机专业，期间主要致力于Web开发和运维方向，热爱数据可视化，并不断探索云平台建设与维护。',

        Contact_team: '我们的团队',
        Contact_team_desc: '我们致力于推动林业科学与信息技术的融合，欢迎更多志同道合的伙伴加入我们，共同探索数据驱动的生物研究新方向。',


        footer_analytics: '转录组分析',
        footer_platform: '平台',
        footer_resource: '资源',
        footer_support: '支持',
        footer_support_desc: '开源不易，关注github/gitee，获取最新动态，希望给个小星星支持一下。',
        footer_copy: '© 2025 转录组分析平台，中国林业科学研究院林业研究所，保留所有权利.',
        footer_desc: '探索基因组奥秘的专业可视化平台，为生物研究提供数据支持。',
        footer_copy_txt: '版权所有 2025 中国林业科学研究院林业研究所',



    }
}


const i18n = createI18n({
    legacy: false,
    globalInjection: true, // 全局注入 $t 函数
    locale: zhCn,
    messages
})


export default i18n;