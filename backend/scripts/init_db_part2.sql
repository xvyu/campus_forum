-- =====================================================
-- Part 2: 内容域 (pf_posts, pf_comments, pf_likes, pf_favorites, pf_follows)
-- =====================================================

-- 3.5 帖子表 pf_posts
DROP TABLE IF EXISTS `pf_posts`;
CREATE TABLE `pf_posts` (
    `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`       BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `user_id`         BIGINT UNSIGNED NOT NULL,
    `board_id`        BIGINT UNSIGNED NOT NULL,
    `anonymous_id`    BIGINT UNSIGNED NOT NULL,
    `title`           VARCHAR(100) NOT NULL DEFAULT '',
    `content`         LONGTEXT     NOT NULL COMMENT '富文本，可含 base64 图片',
    `content_html`    LONGTEXT     NOT NULL,
    `images`          JSON         DEFAULT NULL,
    `view_count`      INT          NOT NULL DEFAULT 0,
    `like_count`      INT          NOT NULL DEFAULT 0,
    `dislike_count`   INT          NOT NULL DEFAULT 0,
    `comment_count`   INT          NOT NULL DEFAULT 0,
    `favorite_count`  INT          NOT NULL DEFAULT 0,
    `report_count`    INT          NOT NULL DEFAULT 0,
    `status`          TINYINT(1)   NOT NULL DEFAULT 1,
    `is_top`          TINYINT(1)   NOT NULL DEFAULT 0,
    `is_essence`      TINYINT(1)   NOT NULL DEFAULT 0,
    `ip`              VARCHAR(45)  NOT NULL DEFAULT '',
    `ip_location`     VARCHAR(32)  NOT NULL DEFAULT '',
    `last_comment_at` DATETIME     DEFAULT NULL,
    `is_deleted`      TINYINT(1)   NOT NULL DEFAULT 0,
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_school_board_status_created` (`school_id`, `board_id`, `status`, `created_at` DESC),
    KEY `idx_user_created` (`user_id`, `created_at` DESC),
    KEY `idx_anonymous` (`anonymous_id`),
    KEY `idx_status_top_created` (`status`, `is_top` DESC, `created_at` DESC),
    KEY `idx_last_comment` (`last_comment_at` DESC),
    KEY `idx_essence` (`is_essence`, `created_at` DESC),
    FULLTEXT KEY `ft_title_content` (`title`, `content`) WITH PARSER ngram,
    CONSTRAINT `fk_posts_school` FOREIGN KEY (`school_id`) REFERENCES `pf_schools` (`id`),
    CONSTRAINT `fk_posts_user` FOREIGN KEY (`user_id`) REFERENCES `pf_users` (`id`),
    CONSTRAINT `fk_posts_board` FOREIGN KEY (`board_id`) REFERENCES `pf_boards` (`id`),
    CONSTRAINT `fk_posts_anon` FOREIGN KEY (`anonymous_id`) REFERENCES `pf_anonymous_id_mapping` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='帖子表';

-- 3.6 评论表 pf_comments
DROP TABLE IF EXISTS `pf_comments`;
CREATE TABLE `pf_comments` (
    `id`               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `school_id`        BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `post_id`          BIGINT UNSIGNED NOT NULL,
    `user_id`          BIGINT UNSIGNED NOT NULL,
    `anonymous_id`     BIGINT UNSIGNED NOT NULL,
    `parent_id`        BIGINT UNSIGNED DEFAULT NULL,
    `reply_to_user_id` BIGINT UNSIGNED DEFAULT NULL,
    `content`          LONGTEXT     NOT NULL,
    `content_html`     LONGTEXT     NOT NULL,
    `like_count`       INT          NOT NULL DEFAULT 0,
    `reply_count`      INT          NOT NULL DEFAULT 0,
    `status`           TINYINT(1)   NOT NULL DEFAULT 1,
    `ip`               VARCHAR(45)  NOT NULL DEFAULT '',
    `ip_location`      VARCHAR(32)  NOT NULL DEFAULT '',
    `is_deleted`       TINYINT(1)   NOT NULL DEFAULT 0,
    `created_at`       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_post_created` (`post_id`, `created_at` ASC),
    KEY `idx_user_created` (`user_id`, `created_at` DESC),
    KEY `idx_parent` (`parent_id`),
    KEY `idx_school` (`school_id`),
    CONSTRAINT `fk_comments_school` FOREIGN KEY (`school_id`) REFERENCES `pf_schools` (`id`),
    CONSTRAINT `fk_comments_post` FOREIGN KEY (`post_id`) REFERENCES `pf_posts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comments_user` FOREIGN KEY (`user_id`) REFERENCES `pf_users` (`id`),
    CONSTRAINT `fk_comments_anon` FOREIGN KEY (`anonymous_id`) REFERENCES `pf_anonymous_id_mapping` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='评论表(楼中楼3层)';

-- 3.7 点赞表 pf_likes
DROP TABLE IF EXISTS `pf_likes`;
CREATE TABLE `pf_likes` (
    `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id`      BIGINT UNSIGNED NOT NULL,
    `school_id`    BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `target_type`  VARCHAR(16)  NOT NULL DEFAULT 'post',
    `target_id`    BIGINT UNSIGNED NOT NULL,
    `action_type`  TINYINT(1)   NOT NULL DEFAULT 1,
    `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_target_action` (`user_id`, `target_type`, `target_id`, `action_type`),
    KEY `idx_target` (`target_type`, `target_id`),
    KEY `idx_school_user` (`school_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='点赞/点踩表';

-- 3.8 收藏表 pf_favorites
DROP TABLE IF EXISTS `pf_favorites`;
CREATE TABLE `pf_favorites` (
    `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id`    BIGINT UNSIGNED NOT NULL,
    `school_id`  BIGINT UNSIGNED NOT NULL DEFAULT 1,
    `post_id`    BIGINT UNSIGNED NOT NULL,
    `folder_id`  BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_post` (`user_id`, `post_id`),
    KEY `idx_user_created` (`user_id`, `created_at` DESC),
    KEY `idx_post` (`post_id`),
    KEY `idx_folder` (`user_id`, `folder_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='收藏表';

-- 3.9 关注表 pf_follows
DROP TABLE IF EXISTS `pf_follows`;
CREATE TABLE `pf_follows` (
    `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `follower_id`  BIGINT UNSIGNED NOT NULL,
    `followee_id`  BIGINT UNSIGNED NOT NULL,
    `status`       TINYINT(1)   NOT NULL DEFAULT 1,
    `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_follow_pair` (`follower_id`, `followee_id`),
    KEY `idx_followee` (`followee_id`, `status`),
    KEY `idx_follower_created` (`follower_id`, `created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='关注表';
