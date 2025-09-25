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

        Transcripts_nav: 'Navigation',
        Transcripts_exp_category: 'Experiment Category',
        Transcripts_experiment: 'Experiment',
        Transcripts_sample: 'Sample',
        Transcripts_result: 'Result',
        Transcripts_experiment_list: "Experiment List",
        Transcripts_sample_list: "Sample List",

        Transcripts_total: 'total',
        Transcripts_jump: 'jump to',
        Transcripts_page: 'page',

        Transcripts_exp_id: 'UniqueEXID',
        Transcripts_exp_category: 'ExperimentCategory',
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
        Transcripts_exp_category: '实验类别',
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

    }
}


const i18n = createI18n({
    legacy: false,
    globalInjection: true, // 全局注入 $t 函数
    locale: zhCn,
    messages
})


export default i18n;