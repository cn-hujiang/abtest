#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/13
# @Author : jiang.hu
# @File : create_db_sql.py 

CREATE_T_ABTEST_EXPERIMENT = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_EXPERIMENT   (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(100) NULL COMMENT '实验名称',
      `diversion_strategy_id` bigint(20) NULL COMMENT '分流策略id',
      `is_published` tinyint(4) DEFAULT 1 COMMENT '是否发布,0：未发布；1：已发布; 发布时配置才生效',
      `is_locked` tinyint(4) DEFAULT 0 COMMENT '是否锁定,0：未锁定；1：已锁定; 锁定时不可被编辑',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除 0：未删除；1：删除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_exp_id`(`id`) USING BTREE,
      UNIQUE KEY `idx_exp_name` (`name`) USING BTREE
    ) ENGINE = InnoDB COMMENT = '实验表';
"""

CREATE_T_ABTEST_DIVERSION_STRATEGY = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_DIVERSION_STRATEGY  (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(100) NULL COMMENT '分流策略名称',
      `diver_config` varchar(20) NULL COMMENT '分流器配置，与分流器id关联，可以多个id组合, {分流器id:优先级}',
      `experiment_id` varchar(100) NULL COMMENT '实验id',
      `scene_id` bigint(20) DEFAULT 0 COMMENT '场景id 与场景表id关联, 默认值0，表示没有scene',
      `layer_id` bigint(20) DEFAULT 0 COMMENT '分层id 与流量层表id关联, 默认值0，表示没有layer',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除 0：未删除；1：删除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_diversion_strategy`(`id`) USING BTREE,
      UNIQUE KEY `idx_strategy` (`name`, `layer_id`, `scene_id`, `experiment_id`) USING BTREE
    ) ENGINE = InnoDB COMMENT = '分流策略表';
"""

CREATE_T_ABTEST_DIVERSION = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_DIVERSION  (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(100) NULL COMMENT '分流器名称',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除 0：未删除；1：删除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_diversion`(`id`) USING BTREE,
      UNIQUE KEY `unique_diversion_name` (`name`) USING BTREE
    ) ENGINE = InnoDB COMMENT = '分流器数据表';
"""

CREATE_T_ABTEST_SCENE = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_SCENE  (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(100) NULL COMMENT '场景名称',
      `experiment_id` bigint(20) NULL COMMENT '实验id 与实验表id关联',
      `allocation_ratio` decimal NULL COMMENT '分流比例',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除 0：未删除；1：删除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_scene`(`id`) USING BTREE,
      INDEX `idx_experiment_id`(`experiment_id`) USING BTREE,
      UNIQUE KEY `unique_scene` (`name`, `experiment_id`) USING BTREE
    ) ENGINE = InnoDB COMMENT = '场景信息表';
"""

CREATE_T_ABTEST_LAYER = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_LAYER  (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(100) NULL COMMENT '流量层名称',
      `diversion_strategy_id` bigint(20) NULL COMMENT '分流策略id',
      `experiment_id` bigint(20) NULL COMMENT '实验id 与实验表id关联',
      `scene_id` bigint(20) DEFAULT 0 COMMENT '场景id 与场景表id关联, 默认值0，表示没有scene',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除 0：未删除；1：删除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_layer`(`id`) USING BTREE,
      INDEX `idx_experiment_id`(`experiment_id`) USING BTREE,
      INDEX `idx_diversion_strategy_id`(`diversion_strategy_id`) USING BTREE,
      INDEX `idx_scene_id`(`scene_id`) USING BTREE,
      UNIQUE KEY `unique_layer` (`name`, `scene_id`, `experiment_id`) USING BTREE
    ) ENGINE = InnoDB COMMENT = '流量层表';
"""

CREATE_T_ABTEST_BUCKET = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_BUCKET  (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(100) NULL COMMENT '桶名称',
      `experiment_id` bigint(20) NULL COMMENT '实验id 与实验表id关联',
      `scene_id` bigint(20) DEFAULT 0 COMMENT '场景id 与场景表id关联, 默认值0，表示没有scene',
      `layer_id` bigint(20) DEFAULT 0 COMMENT '分层id 与流量层表id关联, 默认值0，表示没有layer',
      `allocation_ratio` decimal NULL COMMENT '分流比例',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除 0：未删除；1：删除',
      `white_list_id` tinyint(4) DEFAULT 0 COMMENT '白名单类型id，默认0表示是不是白名单bucket',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_bucket_id`(`id`) USING BTREE,
      INDEX `idx_experiment_id`(`experiment_id`) USING BTREE,
      INDEX `idx_layer_id_id`(`layer_id`) USING BTREE,
      INDEX `idx_scene_id`(`scene_id`) USING BTREE,
      UNIQUE KEY `unique_bucket` (`name`, `layer_id`, `scene_id`, `experiment_id`, `white_list_id`) USING BTREE

    ) ENGINE = InnoDB COMMENT = '具体分桶表';
"""

CREATE_T_ABTEST_BUCKET_PARAMS = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_BUCKET_PARAMS  (
      `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(100) NULL COMMENT '参数名称',
      `value` varchar(500) NULL COMMENT '参数值',
      `bucket_id` bigint(20) NULL COMMENT '桶id 与桶表id关联',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除 0：未删除；1：删除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_params`(`id`) USING BTREE,
      INDEX `idx_bucket_id`(`bucket_id`) USING BTREE,
      UNIQUE KEY `unique_bucket_param` (`name`, `bucket_id`) USING BTREE
    ) ENGINE = InnoDB COMMENT = '分桶表对应参数值表';
"""

CREATE_T_ABTEST_WHITE_LIST_TYPE = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_WHITE_LIST_TYPE  (
      `id` int NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `name` varchar(255) COMMENT '白名单类型名称',
      `experiment_id` bigint(20) DEFAULT 0 COMMENT '实验id 与实验表id关联, 默认值0，表示没有exp',
      `scene_id` bigint(20) DEFAULT 0 COMMENT '场景id 与场景表id关联, 默认值0，表示没有scene',
      `layer_id` bigint(20) DEFAULT 0 COMMENT '分层id 与流量层表id关联, 默认值0，表示没有layer',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否删除白名单，0：未移除，1：移除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_white_list_type`(`id`) USING BTREE,
      UNIQUE KEY `unique_white_list_type` (`name`, `layer_id`, `scene_id`, `experiment_id`) USING BTREE
    ) ENGINE = InnoDB COMMENT = '白名单类型数据表';
"""


CREATE_T_ABTEST_USER_WHITE_LIST = """
    CREATE TABLE IF NOT EXISTS T_ABTEST_USER_WHITE_LIST  (
      `id` int NOT NULL AUTO_INCREMENT COMMENT '自增主键',
      `user_id` varchar(255) NOT NULL COMMENT '用户id',
      `white_list_id` varchar(255) COMMENT '白名单类型，与白名单类型表id关联',
      `is_deleted` tinyint(4) DEFAULT 0 COMMENT '是否移除白名单，0：未移除，1：移除',
      `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`),
      INDEX `idx_white_list`(`id`) USING BTREE,
      UNIQUE INDEX `unique_user_white_list` (`user_id`, `white_list_id`)
    ) ENGINE = InnoDB COMMENT = '用户白名单';
"""

if __name__ == '__main__':
    pass
