USE FACEBOOK;



INSERT INTO user (first_name, last_name, gender, dob, email, secondary_email, contact_no, last_seen) VALUES
('Axit','Sharma','male','1998-05-12','Axit@gmail.com',NULL,'9876543210',NOW()),
('harsh','Patel','female','1999-08-22','harsh@gmail.com','priya.alt@gmail.com','9123456780',NOW()),
('Rahul','Verma','male','1997-03-15','rahul.verma@gmail.com',NULL,'9988776655',NOW()),
('jaydeep','Iyer','female','2000-11-30','jaydeep@gmail.com',NULL,'9090909090',NOW()),
('pari','Reddy','male','1996-01-05','pari@gmail.com','arjun.alt@gmail.com','9812345678',NOW());

INSERT INTO interest (name) VALUES
('cricket'),
('coding'),
('gym'),
('music'),
('travel');

INSERT INTO user_interest (user_id, interest_id) VALUES
(1,1),(1,2),(2,2),(2,4),(3,1),(3,3),(4,4),(4,5),(5,2),(5,3);

INSERT INTO credential (user_id, password_hash) VALUES
(1,'hash1'),
(2,'hash2'),
(3,'hash3'),
(4,'hash4'),
(5,'hash5');

INSERT INTO post (user_id, src, media_type) VALUES
(1,'/img/post1.jpg','photo'),
(2,'/img/post2.jpg','photo'),
(3,'/video/post3.mp4','video'),
(4,'/img/post4.jpg','photo'),
(5,'/video/post5.mp4','video');

INSERT INTO post_like (post_id, user_id) VALUES
(1,2),(1,3),(2,1),(3,4),(4,5);

INSERT INTO comment (post_id, user_id, content, parent_id) VALUES
(1,2,'Nice post!',NULL),
(1,3,'Great!',NULL),
(2,1,'Awesome!',NULL),
(3,4,'Cool video!',NULL),
(1,4,'Reply to nice',1);

INSERT INTO comment_reaction (comment_id, user_id, reaction_type) VALUES
(1,3,'like'),
(2,1,'like'),
(3,2,'dislike'),
(4,5,'like');

INSERT INTO user_group (name, admin_id) VALUES
('Tech Lovers',1),
('Fitness Club',3);

INSERT INTO group_members (group_id, member_id) VALUES
(1,1),(1,2),(1,3),
(2,3),(2,4),(2,5);

INSERT INTO group_post (group_id, post_id) VALUES
(1,1),
(1,2),
(2,3),
(2,4);

INSERT INTO friend (user_id, friend_id, status) VALUES
(1,2,'accepted'),
(2,1,'accepted'),
(1,3,'accepted'),
(3,1,'accepted'),
(2,4,'pending'),
(4,2,'pending'),
(3,5,'accepted'),
(5,3,'accepted');

commit;

-- SET FOREIGN_KEY_CHECKS = 0;

-- TRUNCATE TABLE friend;
-- TRUNCATE TABLE group_post;
-- TRUNCATE TABLE group_members;
-- TRUNCATE TABLE user_group;
-- TRUNCATE TABLE comment_reaction;
-- TRUNCATE TABLE comment;
-- TRUNCATE TABLE post_like;
-- TRUNCATE TABLE post;
-- TRUNCATE TABLE credential;
-- TRUNCATE TABLE user_interest;
-- TRUNCATE TABLE interest;
-- TRUNCATE TABLE user;

-- SET FOREIGN_KEY_CHECKS = 1;






