create database ss;

use ss;



create table dept (
	id int auto_increment primary key,
    name varchar(40)
);

CREATE TABLE emp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    dept_id INT,
    CONSTRAINT fk_dept FOREIGN KEY (dept_id) REFERENCES dept(id)
);




INSERT INTO dept (name) 
VALUES ('developer');




-- ALTER TABLE emp 
-- MODIFY COLUMN dept_id INT;




describe emp;

INSERT INTO emp (name,dept_id) 
VALUES ('Harsh',1) , ("axit",1);

INSERT INTO dept (name) 
VALUES ('AI/ML');

INSERT INTO emp (name,dept_id) 
VALUES ('jaydeep',2) , ("pratham",2);


select emp.id,emp.name,dept.name 
from emp join dept 
on emp.dept_id = dept.id;


SELECT dept.name, COUNT(emp.id) AS total_employees
FROM emp
JOIN dept ON emp.dept_id = dept.id
GROUP BY dept.name;



ALTER TABLE emp ADD COLUMN salary INT;


UPDATE emp SET salary = 80000 WHERE id IN (1, 2); 

UPDATE emp SET salary = 50000 WHERE dept_id = 2; 

delete from emp where id in (7,8);

select * from emp;



