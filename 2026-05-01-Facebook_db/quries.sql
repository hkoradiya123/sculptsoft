use facebook;
SET SQL_SAFE_UPDATES = 0;
-- I. View users’s all posts and display the number of likes and number of comments to that post.

select id , like_count , comment_count from post where user_id = 1;


-- II. Display the comments posted by the user.

select id , post_id, content created_at from comment where user_id = 1;

-- III. Display the online friends of a particular user.

select friend.user_id , user.first_name, friend.friend_id  , friend_name.first_name 
		from user join friend 
			on user.id = friend.user_id 
        join user as friend_name 
			on friend_name.id = friend.friend_id;
 
 --  main 
select friend.friend_id, user_friend.first_name 
	from user join friend on user.id = friend.user_id 
	join user as user_friend on friend.friend_id = user_friend.id 
		where friend.user_id = 1 
        and user.status = "online";

-- IV. Display the Group name, number of members of that Group and admin of that Group.

select user_group.name, COUNT(group_members.id) as total_members , admin_user.first_name as admin from user_group 
	join user as admin_user 
		on user_group.admin_id = admin_user.id 
	right join  group_members 
		on user_group.id = group_members.group_id 
	group by user_group.id; 



-- V. Display the Members of the particular Group.

-- main
select user.first_name from user_group 
	join group_members 
		on user_group.id = group_members.group_id 
	join user 
		on group_members.member_id = user.id 
	where user_group.id =1; 

-- VI. Display post which don’t have any like.

select post.id from post where post.like_count = 0 ;

-- VII. Display post which don’t have any comment.

select post.id from post where post.comment_count = 0 ;

-- VIII. Display post which are liked by user's friend.

select * from post_like;
-- main
select post_like.post_id 
from post_like 
where user_id 
	in (select friend.friend_id 
		from friend  
        where friend.user_id = 1);
	

-- IX. Display Comments of a particular user which are liked by user’s friends.


select comment.id,comment.content 
from comment 
join comment_reaction 
	on  comment.id = comment_reaction.comment_id 
where comment_reaction.user_id 
	in (select friend.friend_id 
		from friend  
        where friend.user_id = 1);


-- X. Display Posts of a particular user which are liked by user’s friends.

select post_like.post_id,count(post_like.user_id) as total_friend_like
from post_like 
where post_like.user_id 
	in (select friend.friend_id 
		from friend  
        where friend.user_id = 1)
group by post_like.post_id ;

-- XI. Display Posts to particular group and also display the user’s name who posted it.

select group_post.post_id , post_user.first_name from group_post 
join post on post.id = group_post.post_id
join user as post_user on post_user.id = post.user_id
where group_post.group_id = 2;

-- XII. Display posts of a group that is not liked by anyone.

select group_post.post_id  from group_post 
join post on post.id = group_post.post_id
where post.like_count = 0;




