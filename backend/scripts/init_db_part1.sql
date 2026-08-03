-- =====================================================
-- 校园匿名社交论坛（树洞） · 数据库初始化脚本
-- Database: campus_forum
-- Charset:  utf8mb4
-- Engine:   InnoDB
-- Author:   陈超滨
-- Source:   docs/ER-Diagram-数据库设计文档.md §5 + 种子数据 §7
-- Updated:  2026-7-8
-- =====================================================
-- 执行方式: mysql -uroot -p450881 < init_db.sql
-- 或在 MySQL 客户端: source init_db.sql;
-- =====================================================

-- 1. 删除已存在的库（首次部署可注释）
-- DROP DATABASE IF EXISTS campus_forum;

-- 2. 创建数据库
CREATE DATABASE IF NOT EXISTS `campus_forum`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `campus_forum`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- 3. 建表（按依赖顺序）
-- =====================================================

-- 3.1 学校表 pf_schools
DROP TABLE IF EXISTS `pf_schools`;
CREATE TABLE `pf_schools` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
    `code`          VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '学校代码',
    `name`          VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '学校名称',
    `email_suffix`  VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '邮箱后缀',
    `domain`        VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '子域名',
    `logo`          VARCHAR(255) NOT NULL DEFAULT '' COMMENT '校徽URL',
    `status`        TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '1启用 0停用',
    `sort_order`    INT          NOT NULL DEFAULT 0 COMMENT '排序号',
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`),
    UNIQUE KEY `uk_email_suffix` (`email_suffix`),
    UNIQUE KEY `uk_domain` (`domain`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='学校表(多租户基础)';

-- 3.2 用户表 pf_users
DROP TABLE IF EXISTS `pf_users`;
CREATE TABLE `pf_users` (
    `id`                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
    `school_id`           BIGINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '学校id',
    `student_id`          VARCHAR(128) NOT NULL DEFAULT '' COMMENT '学号,AES-256加密',
    `email`               VARCHAR(255) NOT NULL DEFAULT '' COMMENT '校园邮箱,AES-256加密',
    `password_hash`       VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'bcrypt cost=12',
    `nickname`            VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '登录态昵称',
    `avatar`              VARCHAR(255) NOT NULL DEFAULT '' COMMENT '头像URL',
    `gender`              TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '1男 2女 0未知',
    `bio`                 VARCHAR(255) NOT NULL DEFAULT '' COMMENT '个人简介',
    `role`                TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '1用户 2审核员 3管理员',
    `status`              TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '1正常 2禁言 3封号 4未激活',
    `email_verified_at`   DATETIME     DEFAULT NULL,
    `last_login_at`       DATETIME     DEFAULT NULL,
    `last_login_ip`       VARCHAR(45)  NOT NULL DEFAULT '',
    `failed_login_count`  INT          NOT NULL DEFAULT 0,
    `locked_until`        DATETIME     DEFAULT NULL,
    `is_deleted`          TINYINT(1)   NOT NULL DEFAULT 0,
    `created_at`          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_student_id_school` (`student_id`, `school_id`),
    UNIQUE KEY `uk_email` (`email`),
    KEY `idx_school_status` (`school_id`, `status`),
    KEY `idx_created_at` (`created_at`),
    CONSTRAINT `fk_users_school` FOREIGN KEY (`school_id`) REFERENCES `pf_schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='用户表(真实身份,AES加密)';

-- 3.3 匿名身份映射表 pf_anonymous_id_mapping
DROP TABLE IF EXISTS `pf_anonymous_id_mapping`;
CREATE TABLE `pf_anonymous_id_mapping` (
    `id`                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id`            BIGINT UNSIGNED NOT NULL COMMENT '真实用户id',
    `school_id`          BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `anonymous_name`     VARCHAR(64)  NOT NULL DEFAULT '',
    `anonymous_avatar`   VARCHAR(255) NOT NULL DEFAULT '',
    `signature`          VARCHAR(255) NOT NULL DEFAULT '',
    `use_count`          INT          NOT NULL DEFAULT 0,
    `is_default`         TINYINT(1)   NOT NULL DEFAULT 0,
    `is_active`          TINYINT(1)   NOT NULL DEFAULT 1,
    `is_deleted`         TINYINT(1)   NOT NULL DEFAULT 0,
    `created_at`         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_active` (`user_id`, `is_active`),
    KEY `idx_school` (`school_id`),
    KEY `idx_use_count` (`use_count` DESC),
    CONSTRAINT `fk_anon_user` FOREIGN KEY (`user_id`) REFERENCES `pf_users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_anon_school` FOREIGN KEY (`school_id`) REFERENCES `pf_schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='匿名身份映射表';

-- 3.4 板块表 pf_boards
DROP TABLE IF EXISTS `pf_boards`;
CREATE TABLE `pf_boards` (
    `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`    BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `slug`         VARCHAR(32)  NOT NULL DEFAULT '',
    `name`         VARCHAR(32)  NOT NULL DEFAULT '',
    `description`  VARCHAR(255) NOT NULL DEFAULT '',
    `icon`         VARCHAR(255) NOT NULL DEFAULT '',
    `cover`        VARCHAR(255) NOT NULL DEFAULT '',
    `sort_order`   INT          NOT NULL DEFAULT 0,
    `post_count`   INT          NOT NULL DEFAULT 0,
    `online_count` INT          NOT NULL DEFAULT 0,
    `moderator_id` BIGINT UNSIGNED DEFAULT NULL,
    `status`       TINYINT(1)   NOT NULL DEFAULT 1,
    `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_school_slug` (`school_id`, `slug`),
    KEY `idx_status_sort` (`status`, `sort_order`),
    CONSTRAINT `fk_boards_school` FOREIGN KEY (`school_id`) REFERENCES `pf_schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='板块表(8大固定板块)';
