
CREATE TABLE exp_class (
    exp_class      VARCHAR(100) PRIMARY KEY comment "实验类别唯一编号",
    experiment_category VARCHAR(255) NOT NULL UNIQUE comment "实验类别名字",
    INDEX idx_name (experiment_category)             -- 用于快速模糊匹配
) ENGINE=InnoDB;

CREATE TABLE experiment (
    unique_ex_id   VARCHAR(100) PRIMARY KEY comment "实验唯一编号",
    exp_class      VARCHAR(100) NOT NULL comment "实验类别",
    experiment     VARCHAR(255) NOT NULL comment "样本所属实验"
) ENGINE=InnoDB;


CREATE TABLE sample (
    unique_id        VARCHAR(100),
    unique_ex_id     VARCHAR(100) NOT NULL,
    filename         VARCHAR(255),
    sample_id        VARCHAR(255) NOT NULL,
    sample           VARCHAR(255),
    collection_time  DATE NOT NULL,
    sample_age       TINYINT,
    collection_part  VARCHAR(100) NOT NULL,
    sample_detail    TEXT,
    deposit_database VARCHAR(100),
    accession        VARCHAR(100),
    origin           VARCHAR(100),
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (unique_id, collection_time),
    KEY idx_ex (unique_ex_id),
    KEY idx_sample_id (sample_id),
    KEY idx_sample_time (sample_id, collection_time),
    KEY idx_time_part (collection_time, collection_part),
    KEY idx_age (sample_age),
    KEY idx_age_time (sample_age,collection_time),
    KEY idx_age_time_part (sample_age, collection_time, collection_part),
    KEY idx_exp_time (unique_ex_id, collection_time)
) ENGINE=InnoDB
PARTITION BY RANGE (YEAR(collection_time)) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION pmax  VALUES LESS THAN MAXVALUE
);

CREATE TABLE gene_express_counts (
    unique_id   VARCHAR(100) primary key comment "sample的 unique_id + gene_id",
    sample_real_id   VARCHAR(255) NOT NULL ,
    sample_id   VARCHAR(255),
    gene_id     VARCHAR(10),
    counts      INT,

    KEY idx_sample_id (sample_id),
    KEY idx_sample_real_id (sample_real_id)
) ENGINE=InnoDB;

CREATE TABLE gene_express_tpm (
     unique_id   VARCHAR(100) primary key comment "sample的 unique_id + gene_id",
     sample_real_id   VARCHAR(255) NOT NULL ,
     sample_id   VARCHAR(255) ,
     gene_id     VARCHAR(10),
     tpm         FLOAT,

     KEY idx_sample_id (sample_id),
     KEY idx_sample_real_id (sample_real_id)
) ENGINE=InnoDB;


CREATE TABLE `user` (
                        `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户 id',
                        `username` varchar(20) NOT NULL COMMENT '用户名',
                        `password` varchar(64) NOT NULL COMMENT '用户密码',
                        `phone` varchar(11) DEFAULT NULL COMMENT '用户手机号',
                        `email` varchar(128) NOT NULL COMMENT '用户邮箱',
                        `user_avatar` varchar(255) DEFAULT NULL COMMENT '用户头像',
                        `introduction` varchar(255) DEFAULT NULL COMMENT '用户简介',
                        `create_time` datetime NOT NULL COMMENT '用户创建时间',
                        `update_time` datetime NOT NULL COMMENT '用户修改时间',
                        `status` tinyint NOT NULL COMMENT '用户状态：0-启用，1-禁用',
                        PRIMARY KEY (`id`),
                        UNIQUE KEY `email` (`email`),
                        UNIQUE KEY `username` (`username`),
                        UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',NULL,'xxxxxxxx@qq.com',NULL,NULL,'2025-09-06 01:50:12','2025-10-06 01:50:17',0);


