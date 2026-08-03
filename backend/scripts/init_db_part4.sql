-- =====================================================
-- Part 4: 用户维度评论数持久化字段
-- 任务：修复个人中心「我的数据」发表评论数不实时、删除不递减问题
-- 应用顺序：在 part1/part2/part3 之后执行
-- =====================================================

-- 1) 给 pf_users 增加 comment_count 字段（已存在则跳过）
SET @col_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pf_users' AND COLUMN_NAME = 'comment_count'
);
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE pf_users ADD COLUMN comment_count INT NOT NULL DEFAULT 0 COMMENT ''用户维度评论数（持久化字段），由应用层在评论 create/delete 时维护'' AFTER status',
    'SELECT ''comment_count column already exists, skipping ALTER'' AS msg'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 1.1) 给 pf_users 增加 liked_post_count 字段（已存在则跳过）
SET @col_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pf_users' AND COLUMN_NAME = 'liked_post_count'
);
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE pf_users ADD COLUMN liked_post_count INT NOT NULL DEFAULT 0 COMMENT ''被点赞的帖子数（持久化字段），由 post.py 在 like_post 维护'' AFTER comment_count',
    'SELECT ''liked_post_count column already exists, skipping ALTER'' AS msg'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 1.2) 给 pf_users 增加 liked_comment_count 字段
SET @col_exists = (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pf_users' AND COLUMN_NAME = 'liked_comment_count'
);
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE pf_users ADD COLUMN liked_comment_count INT NOT NULL DEFAULT 0 COMMENT ''被点赞的评论数（持久化字段），由 comment.py 在 like_comment 维护'' AFTER liked_post_count',
    'SELECT ''liked_comment_count column already exists, skipping ALTER'' AS msg'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2) 用现有评论数据初始化（一次性回填，老用户评论数从 0 变为真实值）
UPDATE pf_users u
SET u.comment_count = (
    SELECT COUNT(*)
    FROM pf_comments c
    WHERE c.user_id = u.id AND c.is_deleted = 0
);

-- 2.1) 用现有帖子点赞数初始化 liked_post_count
--      语义：被点赞过的不同帖子数（like_count > 0 的帖子数）
UPDATE pf_users u
SET u.liked_post_count = (
    SELECT COUNT(*) FROM pf_posts p
    WHERE p.user_id = u.id AND p.is_deleted = 0 AND p.like_count > 0
);

-- 2.2) 用现有评论点赞数初始化 liked_comment_count
--      语义：被点赞过的不同评论数
UPDATE pf_users u
SET u.liked_comment_count = (
    SELECT COUNT(*) FROM pf_comments c
    WHERE c.user_id = u.id AND c.is_deleted = 0 AND c.like_count > 0
);

-- 3) 验证：所有用户的 comment_count 应等于其未删除评论数
--    若数据不一致，说明历史评论表里 user_id 引用了不存在的用户
SELECT
    u.id, u.nickname, u.comment_count,
    (SELECT COUNT(*) FROM pf_comments c WHERE c.user_id = u.id AND c.is_deleted = 0) AS real_count
FROM pf_users u
WHERE u.comment_count <> (
    SELECT COUNT(*) FROM pf_comments c WHERE c.user_id = u.id AND c.is_deleted = 0
);

-- 3.1) 验证 liked_post_count
SELECT
    u.id, u.nickname, u.liked_post_count,
    (SELECT COUNT(*) FROM pf_posts p WHERE p.user_id = u.id AND p.is_deleted = 0 AND p.like_count > 0) AS real_liked_post
FROM pf_users u
WHERE u.liked_post_count <> (
    SELECT COUNT(*) FROM pf_posts p WHERE p.user_id = u.id AND p.is_deleted = 0 AND p.like_count > 0
);

-- 3.2) 验证 liked_comment_count
SELECT
    u.id, u.nickname, u.liked_comment_count,
    (SELECT COUNT(*) FROM pf_comments c WHERE c.user_id = u.id AND c.is_deleted = 0 AND c.like_count > 0) AS real_liked_comment
FROM pf_users u
WHERE u.liked_comment_count <> (
    SELECT COUNT(*) FROM pf_comments c WHERE c.user_id = u.id AND c.is_deleted = 0 AND c.like_count > 0
);

-- =====================================================
-- Part 4 补充：清理历史孤儿评论并修正帖子计数
-- 背景：之前的版本删除评论时只软删除当前评论，不会删除子评论
--       导致出现「父评论已删除但子评论还活着」的孤儿，且 comment_count 偏大
-- 策略：对每个帖子，找出未删除评论组成的子树，若某个子树的根是「孤儿」
--       （即根的 parent_id 指向已删除评论，或其 parent_id 不为 NULL 但祖先链上有已删除节点）
--       则把根挂回到顶层（parent_id = NULL），并修正帖子 comment_count
-- =====================================================

-- 4) 重新挂载孤儿：找出所有未删除评论，向上追溯父链，若链上出现 is_deleted=1，则把当前评论 parent_id 置 NULL
-- 4.1 创建临时表，存放所有需要重新挂载的评论 id
DROP TEMPORARY TABLE IF EXISTS tmp_orphan_comments;
CREATE TEMPORARY TABLE tmp_orphan_comments (
    comment_id BIGINT PRIMARY KEY
);

-- 4.2 用递归 CTE 找出所有「祖先链上有已删除节点」的评论
INSERT INTO tmp_orphan_comments (comment_id)
WITH RECURSIVE ancestor_chain AS (
    -- 起始：所有未删除评论
    SELECT id AS comment_id, parent_id
    FROM pf_comments
    WHERE is_deleted = 0
    UNION ALL
    -- 向上找父节点
    SELECT ac.comment_id, c.parent_id
    FROM ancestor_chain ac
    JOIN pf_comments c ON c.id = ac.parent_id
    WHERE c.is_deleted = 0
)
SELECT DISTINCT ac.comment_id
FROM ancestor_chain ac
JOIN pf_comments c ON c.id = ac.parent_id
WHERE c.is_deleted = 1;  -- 祖先链上至少有一个节点已删

-- 4.3 一次性 UPDATE
UPDATE pf_comments c
JOIN tmp_orphan_comments t ON c.id = t.comment_id
SET c.parent_id = NULL
WHERE c.parent_id IS NOT NULL;

-- 4.4 清理临时表
DROP TEMPORARY TABLE tmp_orphan_comments;

-- 5) 重新同步所有帖子 comment_count（与 pf_users 一致策略）
UPDATE pf_posts p
SET p.comment_count = (
    SELECT COUNT(*) FROM pf_comments c
    WHERE c.post_id = p.id AND c.is_deleted = 0
)
WHERE p.is_deleted = 0;

-- 6) 验证：所有帖子的 comment_count 应等于真实评论数
SELECT id, title, comment_count,
    (SELECT COUNT(*) FROM pf_comments c WHERE c.post_id = p.id AND c.is_deleted = 0) AS real_count
FROM pf_posts p
WHERE p.is_deleted = 0
  AND p.comment_count <> (SELECT COUNT(*) FROM pf_comments c WHERE c.post_id = p.id AND c.is_deleted = 0);
