-- =====================================================
-- Part 3: 治理域 (pf_reports, pf_notifications, pf_user_sessions, pf_anonymous_letters, pf_sensitive_words, pf_audit_logs)
-- =====================================================

-- 3.10 举报表 pf_reports
DROP TABLE IF EXISTS `pf_reports`;
CREATE TABLE `pf_reports` (
    `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`      BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `reporter_id`    BIGINT UNSIGNED NOT NULL,
    `target_type`    VARCHAR(16)  NOT NULL DEFAULT 'post',
    `target_id`      BIGINT UNSIGNED NOT NULL,
    `reason_type`    TINYINT(1)   NOT NULL,
    `reason_text`    TEXT         NOT NULL,
    `status`         TINYINT(1)   NOT NULL DEFAULT 1,
    `handler_id`     BIGINT UNSIGNED DEFAULT NULL,
    `handler_action` VARCHAR(32)  NOT NULL DEFAULT '',
    `handler_note`   TEXT         NOT NULL,
    `handled_at`     DATETIME     DEFAULT NULL,
    `created_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_status_school_created` (`status`, `school_id`, `created_at` ASC),
    KEY `idx_target` (`target_type`, `target_id`),
    KEY `idx_reporter` (`reporter_id`, `created_at` DESC),
    KEY `idx_handler` (`handler_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='举报表';

-- 3.11 通知表 pf_notifications
DROP TABLE IF EXISTS `pf_notifications`;
CREATE TABLE `pf_notifications` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`   BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `user_id`     BIGINT UNSIGNED NOT NULL,
    `type`        VARCHAR(32)  NOT NULL DEFAULT '',
    `title`       VARCHAR(128) NOT NULL DEFAULT '',
    `content`     TEXT         NOT NULL,
    `target_type` VARCHAR(16)  NOT NULL DEFAULT '',
    `target_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `sender_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `is_read`     TINYINT(1)   NOT NULL DEFAULT 0,
    `read_at`     DATETIME     DEFAULT NULL,
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_read_created` (`user_id`, `is_read`, `created_at` DESC),
    KEY `idx_target` (`target_type`, `target_id`),
    KEY `idx_school` (`school_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='站内通知表';

-- 3.12 会话表 pf_user_sessions
DROP TABLE IF EXISTS `pf_user_sessions`;
CREATE TABLE `pf_user_sessions` (
    `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id`    BIGINT UNSIGNED NOT NULL,
    `session_id` VARCHAR(128) NOT NULL DEFAULT '',
    `ip`         VARCHAR(45)  NOT NULL DEFAULT '',
    `user_agent` VARCHAR(255) NOT NULL DEFAULT '',
    `device`     VARCHAR(16)  NOT NULL DEFAULT 'web',
    `expire_at`  DATETIME     NOT NULL,
    `is_active`  TINYINT(1)   NOT NULL DEFAULT 1,
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_session_id` (`session_id`),
    KEY `idx_user_active` (`user_id`, `is_active`),
    KEY `idx_expire` (`expire_at`),
    CONSTRAINT `fk_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `pf_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='登录会话表';

-- 3.13 匿名信箱表 pf_anonymous_letters
DROP TABLE IF EXISTS `pf_anonymous_letters`;
CREATE TABLE `pf_anonymous_letters` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`   BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `sender_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `receiver_id` BIGINT UNSIGNED NOT NULL,
    `post_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `content`     TEXT         NOT NULL,
    `is_read`     TINYINT(1)   NOT NULL DEFAULT 0,
    `read_at`     DATETIME     DEFAULT NULL,
    `is_deleted`  TINYINT(1)   NOT NULL DEFAULT 0,
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_receiver_read_created` (`receiver_id`, `is_read`, `created_at` DESC),
    KEY `idx_sender_created` (`sender_id`, `created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='匿名信箱表';

-- 3.14 敏感词库表 pf_sensitive_words
DROP TABLE IF EXISTS `pf_sensitive_words`;
CREATE TABLE `pf_sensitive_words` (
    `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`  BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `word`       VARCHAR(64)  NOT NULL DEFAULT '',
    `level`      TINYINT(1)   NOT NULL DEFAULT 1,
    `category`   VARCHAR(32)  NOT NULL DEFAULT '',
    `status`     TINYINT(1)   NOT NULL DEFAULT 1,
    `created_by` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_school_word` (`school_id`, `word`),
    KEY `idx_status_category` (`status`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='敏感词库表';

-- 3.15 审计日志表 pf_audit_logs
DROP TABLE IF EXISTS `pf_audit_logs`;
CREATE TABLE `pf_audit_logs` (
    `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`      BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `operator_id`    BIGINT UNSIGNED NOT NULL,
    `operator_role`  VARCHAR(16)  NOT NULL DEFAULT 'admin',
    `action_type`    VARCHAR(32)  NOT NULL DEFAULT '',
    `target_type`    VARCHAR(16)  NOT NULL DEFAULT '',
    `target_id`      BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `before_value`   TEXT         NOT NULL,
    `after_value`    TEXT         NOT NULL,
    `reason`         VARCHAR(255) NOT NULL DEFAULT '',
    `ip`             VARCHAR(45)  NOT NULL DEFAULT '',
    `created_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_school_operator_created` (`school_id`, `operator_id`, `created_at` DESC),
    KEY `idx_target` (`target_type`, `target_id`),
    KEY `idx_action` (`action_type`, `created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='审计日志表';
