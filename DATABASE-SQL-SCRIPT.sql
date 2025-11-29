-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 35.212.249.216    Database: inf2003-db
-- ------------------------------------------------------
-- Server version	8.0.44-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `enrollments`
--

DROP TABLE IF EXISTS `enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollments` (
  `student_id` int NOT NULL,
  `module_id` varchar(10) NOT NULL,
  `enrolled_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `final_grade` varchar(2) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Enrolled',
  PRIMARY KEY (`student_id`,`module_id`),
  KEY `fk_enroll_module` (`module_id`),
  CONSTRAINT `fk_enroll_module` FOREIGN KEY (`module_id`) REFERENCES `modules` (`module_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_enroll_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollments`
--

LOCK TABLES `enrollments` WRITE;
/*!40000 ALTER TABLE `enrollments` DISABLE KEYS */;
INSERT INTO `enrollments` VALUES (1001,'AAI1001','2025-11-27 16:01:17',NULL,'Enrolled'),(1001,'AAI2002','2025-11-29 12:37:17',NULL,'Enrolled'),(1001,'AAI2006','2025-11-29 12:37:31',NULL,'Enrolled'),(1001,'ICT1011','2025-11-22 16:11:33','A','Completed'),(1001,'ICT1012','2025-11-22 16:11:33','B+','Completed'),(1001,'INF1001','2025-11-22 16:11:33','A-','Completed'),(1001,'INF1002','2025-11-22 16:11:33','A','Completed'),(1001,'INF1003','2025-11-22 16:11:33','A-','Completed'),(1001,'INF1004','2025-11-22 16:11:33','A','Completed'),(1001,'INF1005','2025-11-22 16:11:33','A-','Completed'),(1001,'INF1006','2025-11-22 16:11:33','A-','Completed'),(1001,'INF1007','2025-11-22 16:11:33','A','Completed'),(1001,'INF1008','2025-11-22 16:11:33','A','Completed'),(1001,'INF1009','2025-11-22 16:11:33','B+','Completed'),(1001,'INF2001','2025-11-22 16:11:33',NULL,'Enrolled'),(1001,'INF2002','2025-11-22 16:11:33',NULL,'Enrolled'),(1001,'INF2003','2025-11-22 16:11:33',NULL,'Enrolled'),(1001,'INF2004','2025-11-22 16:11:33',NULL,'Enrolled'),(2403053,'AAI1001','2025-11-28 15:44:29',NULL,'Enrolled'),(2403066,'INF2002','2025-11-29 12:07:22',NULL,'Enrolled');
/*!40000 ALTER TABLE `enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `instructors`
--

DROP TABLE IF EXISTS `instructors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `instructors` (
  `instructor_id` int NOT NULL,
  `department_code` varchar(50) NOT NULL,
  `office_location` varchar(50) DEFAULT NULL,
  `office_hours` text,
  `title` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`instructor_id`),
  CONSTRAINT `fk_instructor_user` FOREIGN KEY (`instructor_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instructors`
--

LOCK TABLES `instructors` WRITE;
/*!40000 ALTER TABLE `instructors` DISABLE KEYS */;
INSERT INTO `instructors` VALUES (1,'CS','SIT@Dover, C-01-01','Mon/Wed 10-12','Professor'),(2,'INF','SIT@Dover, D-05-01','Mon 10:00-12:00','Associate Professor'),(3,'BUS','SIT@Dover, B-02-05','Wed 14:00-16:00','Lecturer'),(4,'GEN','SIT@Dover, A-04-01','Fri 09:00-11:00','Lecturer'),(5,'INF','SIT@Dover, D-04-01','Wed 09:00-11:00','Mascot');
/*!40000 ALTER TABLE `instructors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modules`
--

DROP TABLE IF EXISTS `modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modules` (
  `module_id` varchar(10) NOT NULL,
  `module_name` varchar(150) NOT NULL,
  `description` text,
  `credits` int NOT NULL DEFAULT '3',
  `academic_term` varchar(20) DEFAULT NULL,
  `max_capacity` int DEFAULT '30',
  `current_enrollment` int DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `instructor_id` int DEFAULT NULL,
  `target_majors` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`module_id`),
  KEY `fk_module_instructor` (`instructor_id`),
  KEY `idx_modules_academic_term` (`academic_term`),
  CONSTRAINT `fk_module_instructor` FOREIGN KEY (`instructor_id`) REFERENCES `instructors` (`instructor_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modules`
--

LOCK TABLES `modules` WRITE;
/*!40000 ALTER TABLE `modules` DISABLE KEYS */;
INSERT INTO `modules` VALUES ('AAI1001','Data Engineering and Visualization','Techniques for collecting, cleaning, and visualizing large datasets.',6,'Y1T3',80,2,'2025-11-27 01:05:03',1,'AI'),('AAI2002','ITP: Cross Domain Prototyping','Integrative team project focused on prototyping solutions.',6,'Y2T2',80,1,'2025-11-27 01:05:03',4,'AI'),('AAI2006','Industry Certification Module','Preparation for an industry certification in AI or data science.',6,'Y2T3',80,1,'2025-11-27 01:05:03',4,'AI'),('AAI2007','Artificial Intelligence in Business and Society','Examines the impact of AI on business and societal issues.',3,'Y1T3',100,0,'2025-11-27 01:05:03',4,'AI'),('AAI2114','ITP: Execution and Delivery','Integrative team project focused on product delivery.',6,'Y2T3',80,0,'2025-11-27 01:05:03',4,'AI'),('AAI3001','Computer Vision and Deep Learning','Advanced topics in deep learning with a focus on computer vision.',6,'Y2T1',70,0,'2025-11-27 01:05:03',1,'AI'),('AAI3008','Large Language Models','Study of large language models (LLMs) and their applications.',6,'Y2T2',70,0,'2025-11-27 01:05:03',1,'AI'),('AAI4001','Capstone Project','A final year project for Applied AI students.',5,'Y3T1',100,0,'2025-11-27 01:05:03',4,'AI'),('AAI4002B','Integrated Work Study Programme (Work Attachment)','Work placement for Applied AI students.',10,'Y3T1',100,0,'2025-11-27 01:05:03',4,'AI'),('BAC1001','Introduction to Fintech (Integrated Workplace Learning 1)','An overview of financial technologies and their applications.',6,'Y1T3',80,0,'2025-11-27 01:05:03',4,'AC'),('BAC1002','Industry Certification','Preparation for a professional industry certification in finance or tech.',6,'Y1T3',80,0,'2025-11-27 01:05:03',4,'AC'),('BAC2001','Software Requirements Engineering and Design','Principles of Requirements Engineering and Software Design.',6,'Y2T2',70,0,'2025-11-27 01:05:03',1,'AC'),('BAC2002','Blockchain and Cryptocurrency','Fundamentals of blockchain technology and cryptocurrencies.',6,'Y2T2',70,0,'2025-11-27 01:05:03',1,'AC'),('BAC2003','Fintech Projects (Integrated Workplace Learning 2)','A project-based module on fintech solutions.',6,'Y2T3',70,0,'2025-11-27 01:05:03',4,'AC'),('BAC2004','Foundations of Fintech Finance','Core principles of finance as applied to financial technology.',6,'Y1T3',80,0,'2025-11-27 01:05:03',4,'AC'),('BAC2005','Fintech Investment and Risk Management','Managing investments and risk using fintech solutions.',6,'Y2T1',70,0,'2025-11-27 01:05:03',4,'AC'),('BAC3001','Business Valuation and Analysis','Techniques for valuing businesses and analyzing financial performance.',6,'Y2T2',60,0,'2025-11-27 01:05:03',4,'AC'),('BAC3002','Fintech: Advanced Topics','Explores advanced and emerging topics in financial technology.',6,'Y2T3',60,0,'2025-11-27 01:05:03',1,'AC'),('BAC3003B','Integrated Work Study Programme (Work Attachment)','Work placement for Applied Computing students.',10,'Y3T1',80,0,'2025-11-27 01:05:03',4,'AC'),('BAC3004','Capstone Project','A final year project for Applied Computing students.',5,'Y3T1',80,0,'2025-11-27 01:05:03',4,'AC'),('BAC3005','Project Management and Workplace Ethics','Covers project management methodologies and ethical conduct.',3,'Y2T3',80,0,'2025-11-27 01:05:03',4,'AC'),('CSC1103','Programming Methodology','A deeper dive into programming methodologies and problem-solving.',6,'Y1T1',100,0,'2025-11-27 01:05:03',1,'CS'),('CSC1104','Computer Organisation & Architecture','Fundamentals of computer hardware, architecture, and organization.',6,'Y1T1',100,0,'2025-11-27 01:05:03',2,'CS'),('CSC1106','Web Programming','Development of client-side and server-side web applications.',6,'Y1T3',90,0,'2025-11-27 01:05:03',1,'CS'),('CSC1107','Operating Systems','Study of the principles and design of modern operating systems.',6,'Y1T3',90,0,'2025-11-27 01:05:03',2,'CS'),('CSC1108','Data Structures and Algorithms','Core module on data structures and algorithms for computing science.',6,'Y1T2',100,0,'2025-11-27 01:05:03',1,'CS'),('CSC1109','Object Oriented Programming','Principles of OOP for computing science students.',6,'Y1T2',100,0,'2025-11-27 01:05:03',1,'CS'),('CSC2101','Professional Software Development and Team Project 1','Team-based project to learn professional software development practices.',6,'Y2T1',90,0,'2025-11-27 01:05:03',4,'CS'),('CSC2102','Professional Software Development and Team Project 2','Continuation of the team-based project.',6,'Y2T2',90,0,'2025-11-27 01:05:03',4,'CS'),('CSC2106','Internet of Things: Protocols and Networks','A study of the network protocols and architectures used in IoT systems.',6,'Y2T2',70,0,'2025-11-27 01:05:03',2,'CS'),('CSC3101','Capstone Project','A final year project for Computing Science students.',5,'Y3T1',100,0,'2025-11-27 01:05:03',4,'CS'),('CSC3102B','Integrated Work Study Programme (Work Attachment)','Work placement for Computing Science students.',10,'Y3T1',100,0,'2025-11-27 01:05:03',4,'CS'),('CSC3104','Cloud and Distributed Computing','Principles of distributed systems and cloud computing platforms.',6,'Y2T1',80,0,'2025-11-27 01:05:03',2,'CS'),('CSC3105','Data Analytics','Techniques for analyzing and interpreting large datasets.',6,'Y2T2',80,0,'2025-11-27 01:05:03',1,'CS'),('CSC3107','Information Visualisation','Principles and techniques for creating effective visualizations of complex data.',6,'Y2T3',70,0,'2025-11-27 01:05:03',1,'CS'),('CSC3108','Special Topics in Emerging Technologies','Explores advanced and emerging topics in computing.',3,'Y2T3',50,0,'2025-11-27 01:05:03',1,'CS'),('CSC3109','Machine Learning','Introduction to the concepts and algorithms of machine learning.',6,'Y2T3',80,0,'2025-11-27 01:05:03',1,'CS'),('CSD1101','Computer Environment','Introduction to the computing environment for game development.',6,'Y1T1',60,0,'2025-11-27 01:05:03',2,'RTIS'),('CSD1121','High-Level Programming 1','Foundational programming in C++ for real-time simulation.',6,'Y1T1',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD1130','Game Implementation Techniques','Techniques for implementing core game logic and systems.',5,'Y1T2',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD1171','High-Level Programming 2','Advanced C++ programming concepts.',6,'Y1T2',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD1241','Linear Algebra and Geometry','Mathematics for computer graphics and physics.',6,'Y1T1',60,0,'2025-11-27 01:05:03',3,'RTIS'),('CSD1251','Calculus and Analytic Geometry 1','Calculus for simulation and game physics.',6,'Y1T2',60,0,'2025-11-27 01:05:03',3,'RTIS'),('CSD1401','Software Engineering Project 1','First project in a series on software engineering.',6,'Y1T1',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD1451','Software Engineering Project 2','Second project in a series on software engineering.',6,'Y1T2',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD2101','Introduction to Computer Graphics','Fundamentals of 2D and 3D computer graphics.',6,'Y1T3',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD2126','Modern C++ Design Patterns','Applying design patterns in C++ for game development.',6,'Y1T3',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD2151','Introduction to Real-Time Rendering','Techniques for rendering graphics in real-time.',6,'Y2T2',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD2161','Computer Networks','Network programming for multiplayer games and simulations.',6,'Y2T2',60,0,'2025-11-27 01:05:03',2,'RTIS'),('CSD2171','Programming Massively Parallel Processors','CUDA/GPU programming for high performance.',6,'Y3T2',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD2182','Operating Systems','Principles of operating systems for RTIS students.',6,'Y2T1',60,0,'2025-11-27 01:05:03',2,'RTIS'),('CSD2183','Data Structures','Data structures optimized for real-time performance.',6,'Y2T1',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD2201','Calculus and Analytic Geometry 2','Advanced calculus for simulation.',6,'Y2T1',60,0,'2025-11-27 01:05:03',3,'RTIS'),('CSD2251','Linear Algebra','Advanced linear algebra for graphics and physics.',6,'Y2T3',60,0,'2025-11-27 01:05:03',3,'RTIS'),('CSD2259','Discrete Mathematics','Discrete math for computer science.',6,'Y2T2',60,0,'2025-11-27 01:05:03',3,'RTIS'),('CSD2301','Motion Dynamics and Lab','Physics-based motion and dynamics simulation.',6,'Y2T3',60,0,'2025-11-27 01:05:03',3,'RTIS'),('CSD2401','Software Engineering Project 3','Third project in a series on software engineering.',6,'Y2T1',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD2451','Software Engineering Project 4','Fourth project in a series on software engineering.',6,'Y2T2',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD2511','Introduction to Game Design','Fundamentals of game design, mechanics, and documentation.',6,'Y1T3',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD2513','System Design Methods','Methods for designing complex game systems.',6,'Y2T2',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD2541','Level Design','Principles and practices of designing game levels.',6,'Y2T3',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD2702','Introduction to Psychology','Understanding player psychology and motivation.',6,'Y2T3',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD3116','Low-Level Programming','Low-level programming and optimization.',6,'Y3T1',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD3121','Developing Immersive Applications','Creating applications for VR and AR.',6,'Y2T2',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD3126','User Interface and User Experience Design','Designing UIs and UX for games and interactive media.',6,'Y3T2',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD3131','Algorithm Analysis','Analysis of algorithm performance and complexity.',6,'Y3T1',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD3151','Spatial Data Structures','Data structures for managing 3D spatial data (e.g., Octrees).',6,'Y2T3',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD3156','Mobile and Cloud Computing','Developing for mobile and cloud platforms.',6,'Y3T2',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD3183','Artificial Intelligence for Games','AI techniques for game characters and systems.',6,'Y2T3',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD3186','Machine Learning','Introduction to machine learning for RTIS.',6,'Y3T2',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD3241','Probability and Statistics','Statistics for simulation and data analysis.',6,'Y3T1',60,0,'2025-11-27 01:05:03',3,'RTIS'),('CSD3401','Software Engineering Project 5','Fifth project in a series on software engineering.',6,'Y3T1',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD3451','Software Engineering Project 6','Final project in a series on software engineering.',6,'Y3T2',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD3516','Technical Design Methods','Technical aspects of game and system design.',6,'Y3T1',60,0,'2025-11-27 01:05:03',1,'RTIS'),('CSD4401','Capstone Project','A final year project for RTIS students.',3,'Y3T3',60,0,'2025-11-27 01:05:03',4,'RTIS'),('CSD4902B','Integrated Work Study Programme (Work Attachment)','Work placement for RTIS students.',10,'Y3T3',60,0,'2025-11-27 01:05:03',4,'RTIS'),('ICT1011','Computer Organization & Architecture','Fundamentals of computer hardware, architecture, and organization.',6,'Y1T1',100,0,'2025-11-27 01:05:03',2,'SE,IS'),('ICT1012','Operating Systems','Principles and design of modern operating systems, including process and memory management.',6,'Y1T2',100,0,'2025-11-27 01:05:03',2,'SE,IS'),('ICT1013','Computer Networks','Fundamentals of computer networking, TCP/IP, and security (IS focus).',6,'Y1T2',100,0,'2025-11-27 01:05:03',2,'All'),('ICT2112','Software Design','Covers software design patterns, principles, and architectures for building scalable systems.',6,'Y2T2',80,0,'2025-11-27 01:05:03',1,'SE'),('ICT2113','Software Modelling and Analysis','Techniques for modeling and analyzing software systems using UML and other notations.',6,'Y2T2',80,0,'2025-11-27 01:05:03',1,'SE'),('ICT2114','Integrative Team Project','A project module where students work in teams to develop a software solution.',6,'Y2T3',100,0,'2025-11-27 01:05:03',4,'SE'),('ICT2212','Ethical Hacking','Principles and techniques of ethical hacking and penetration testing.',6,'Y2T1',80,0,'2025-11-27 01:05:03',2,'All'),('ICT2213','Applied Cryptography','Modern cryptographic techniques and their application.',6,'Y2T2',80,0,'2025-11-27 01:05:03',2,'All'),('ICT2214','Web Security','Security vulnerabilities of web applications and defenses.',6,'Y2T2',80,0,'2025-11-27 01:05:03',2,'All'),('ICT2215','Mobile Security','Covers security challenges and defenses for mobile operating systems and applications.',6,'Y3T2',70,0,'2025-11-27 01:05:03',2,'All'),('ICT2216','Secure Software Development','Teaches principles and practices for building secure and robust software.',6,'Y2T3',80,0,'2025-11-27 01:05:03',1,'SE'),('ICT2217','Network Security','Theory and practices of network attacks and defenses.',6,'Y2T1',80,0,'2025-11-27 01:05:03',2,'All'),('ICT3112','Software Verification and Validation','Techniques for testing, verifying, and validating software to ensure quality.',6,'Y3T1',60,0,'2025-11-27 01:05:03',1,'SE'),('ICT3113','Performance Testing and Optimisation','Methods for testing and optimizing the performance of software applications.',6,'Y3T1',60,0,'2025-11-27 01:05:03',1,'SE'),('ICT3212','Operations Security and Incident Management','Managing security operations and responding to incidents.',6,'Y3T1',70,0,'2025-11-27 01:05:03',2,'All'),('ICT3213','Malware Analysis and Defence','Techniques for analyzing malicious software.',6,'Y3T2',70,0,'2025-11-27 01:05:03',2,'All'),('ICT3214','Security Analytics','Using data analytics to detect and investigate security threats.',6,'Y3T1',70,0,'2025-11-27 01:05:03',1,'All'),('ICT3215','Digital Forensics','Investigating cybercrimes and analyzing digital evidence.',6,'Y3T1',70,0,'2025-11-27 01:05:03',2,'All'),('ICT3216','Special Topics in Security','Explores advanced and emerging topics in information security.',6,'Y3T2',60,0,'2025-11-27 01:05:03',2,'All'),('ICT3217','Integrative Team Project 2','A second, more advanced project module for teams.',6,'Y3T1',80,0,'2025-11-27 01:05:03',4,'SE'),('ICT3218','Security Governance, Risk Management and Compliance','Frameworks for managing security, risk, and compliance.',6,'Y3T2',80,0,'2025-11-27 01:05:03',4,'All'),('ICT3219','Industry Certification Module','Preparation for a professional industry certification in cybersecurity or IT.',6,'Y2T3',100,0,'2025-11-27 01:05:03',4,'All'),('ICT4011','Capstone Project','A year-long final project to design and develop a significant system.',5,'Y3T3',150,0,'2025-11-27 01:05:03',4,'SE'),('ICT4012B','Integrated Work Study Programme (Work Attachment)','A long-term work placement in a relevant company.',10,'Y3T3',150,0,'2025-11-27 01:05:03',4,'SE'),('INF1001','Introduction to Computing','An overview of computing, software, hardware, operating systems, and security.',6,'Y1T1',150,0,'2025-11-27 01:05:03',1,'SE,CS,AI,IS,RTIS,IMGD,AC'),('INF1002','Programming Fundamentals','An introduction to foundational programming concepts using a modern language.',6,'Y1T1',150,0,'2025-11-27 01:05:03',1,'SE,CS,AI,IS,RTIS,IMGD,AC'),('INF1003','Mathematics 1','Foundational mathematics for computing, including calculus and algebra.',6,'Y1T1',150,0,'2025-11-27 01:05:03',3,'SE,CS,AI,IS,RTIS,IMGD,AC'),('INF1004','Mathematics 2','Further topics in mathematics relevant to computing, including discrete mathematics and statistics.',6,'Y1T2',150,0,'2025-11-27 01:05:03',3,'SE,CS,IS'),('INF1005','Web Systems & Technologies','Design and development of dynamic web applications, covering front-end and back-end.',6,'Y1T2',120,0,'2025-11-27 01:05:03',1,'SE,IS'),('INF1006','Computer Networks','Fundamentals of computer networking, TCP/IP protocol suite, and network security basics.',6,'Y1T3',100,1,'2025-11-27 01:05:03',2,'SE,CS,IS'),('INF1007','Ethics and Professional Conduct','Ethical and professional responsibilities of an ICT professional.',6,'Y1T3',150,0,'2025-11-27 01:05:03',4,'SE,AI,IS'),('INF1008','Data Structures and Algorithms','Core module on the design, analysis, and implementation of data structures and algorithms.',6,'Y1T3',130,0,'2025-11-27 01:05:03',1,'SE,CS,IS'),('INF1009','Object-Oriented Programming','Principles of OOP, including classes, objects, inheritance, and polymorphism.',6,'Y1T2',130,0,'2025-11-27 01:05:03',1,'SE,CS,IS'),('INF1101','Introduction to Computer Systems','A broad overview of computer systems, from hardware to software.',6,'Y1T1',100,0,'2025-11-27 01:05:03',2,'All'),('INF1234','cool course','testttestetsetsetdwadw',12,'Y2T1',35,0,'2025-11-28 22:31:32',1,NULL),('INF2001','Introduction to Software Engineering','Fundamentals of software engineering principles, practices, and the software development lifecycle.',6,'Y2T1',100,0,'2025-11-27 01:05:03',1,'SE,AI,AC'),('INF2002','Human Computer Interaction','Methods and principles for designing, programming, and testing human-centric systems.',6,'Y2T1',90,1,'2025-11-27 01:05:03',1,'SE,CS'),('INF2003','Database Systems','Introduction to database design, implementation, and management. Covers relational models, SQL, and NoSQL.',6,'Y2T1',30,0,'2025-11-27 01:05:03',1,'SE,AI,AC'),('INF2004','Embedded Systems Programming','Programming embedded systems, computer architectures, and microcontrollers.',6,'Y2T1',70,0,'2025-11-27 01:05:03',1,'SE,AI,CS'),('INF2005','Cyber Security Fundamentals','Introductory course covering basic principles of cybersecurity.',6,'Y3T1',100,0,'2025-11-27 01:05:03',2,'SE,AI,CS'),('INF2006','Cloud Computing and Big Data','Fundamentals of cloud computing architectures and big data technologies.',6,'Y3T2',90,0,'2025-11-27 01:05:03',1,'SE,AI,AC'),('INF2007','Mobile Application Development','Design and development of applications for mobile devices, focusing on Android or iOS.',6,'Y2T2',90,0,'2025-11-27 01:05:03',1,'SE,CS'),('INF2008','Machine Learning','Introduction to the concepts and algorithms of machine learning.',6,'Y2T2',100,0,'2025-11-27 01:05:03',1,'SE,AI,IS'),('INF2009','Edge Computing and Analytics','Explores computing and data analytics at the edge of the network.',6,'Y3T2',60,0,'2025-11-27 01:05:03',2,'All'),('INF2335','Global Learning in ICT Advances','Explores advanced and emerging topics in the field of ICT.',6,'Y2T3',50,0,'2025-11-27 01:05:03',4,'All'),('UCM3001','Change Management','A study of the principles and practices for managing organizational change.',6,'Y3T2',100,0,'2025-11-27 01:05:03',4,'All'),('UCS1001','Critical Thinking and Communicating','Develops skills in critical analysis, logical reasoning, and effective communication.',4,'Y1T2',200,0,'2025-11-27 01:05:03',4,'SE,CS,AI,IS,RTIS,IMGD,AC'),('UDC1001','Digital Competency Essentials','Essential digital literacy skills for the modern university student and professional.',2,'Y1T1',200,0,'2025-11-27 01:05:03',4,'SE,CS,AI,IS,RTIS,IMGD,AC'),('UDE2222','Design Innovation','An introduction to design thinking principles and innovation processes.',6,'Y2T1',150,0,'2025-11-27 01:05:03',4,'SE,CS,AI,IS,RTIS,IMGD,AC'),('USI2001','Social Innovation Project','A project focused on creating innovative solutions to social problems.',3,'Y2T2',150,0,'2025-11-27 01:05:03',4,'SE,CS,AI,IS,RTIS,IMGD,AC');
/*!40000 ALTER TABLE `modules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prerequisites`
--

DROP TABLE IF EXISTS `prerequisites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prerequisites` (
  `module_id` varchar(10) NOT NULL,
  `requires_module_id` varchar(10) NOT NULL,
  PRIMARY KEY (`module_id`,`requires_module_id`),
  KEY `fk_prereq_requires` (`requires_module_id`),
  CONSTRAINT `fk_prereq_module` FOREIGN KEY (`module_id`) REFERENCES `modules` (`module_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_prereq_requires` FOREIGN KEY (`requires_module_id`) REFERENCES `modules` (`module_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prerequisites`
--

LOCK TABLES `prerequisites` WRITE;
/*!40000 ALTER TABLE `prerequisites` DISABLE KEYS */;
INSERT INTO `prerequisites` VALUES ('CSC1108','CSC1103'),('CSC1109','CSC1103'),('CSD1251','CSD1241'),('CSD2201','CSD1251'),('ICT1012','ICT1011'),('INF1008','INF1002'),('INF1009','INF1002'),('INF1004','INF1003'),('AAI3001','INF2008');
/*!40000 ALTER TABLE `prerequisites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `student_id` int NOT NULL,
  `enrollment_year` int NOT NULL,
  `major` varchar(100) DEFAULT NULL,
  `expected_graduation` varchar(10) DEFAULT NULL,
  `gpa` decimal(3,2) DEFAULT NULL,
  `current_standing` varchar(20) DEFAULT 'Good',
  `major_id` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  CONSTRAINT `fk_student_user` FOREIGN KEY (`student_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1001,2024,'BEng (Hons) ICT (Software Engineering)','2028',4.00,'Year 2','SE'),(2403053,2025,'ICT(SE)',NULL,NULL,'Good','SE'),(2403066,2025,'ICT(SE)',NULL,NULL,'Good','SE');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `university_id` varchar(50) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `role` varchar(20) NOT NULL,
  `date_joined` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`user_id`,`email`),
  UNIQUE KEY `university_id` (`university_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `users_chk_1` CHECK ((`role` in (_utf8mb4'student',_utf8mb4'instructor',_utf8mb4'admin')))
) ENGINE=InnoDB AUTO_INCREMENT=2403108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'I-001','instructor1@ucms.edu','hashed_pass_1','Alan','Turing','instructor','2025-11-27 01:05:01',NULL,1),(2,'I-002','instructor2@ucms.edu','hashed_pass_2','Ada','Lovelace','instructor','2025-11-27 01:05:01',NULL,1),(3,'I-003','instructor3@ucms.edu','hashed_pass_3','Grace','Hopper','instructor','2025-11-27 01:05:01',NULL,1),(4,'I-004','instructor4@ucms.edu','hashed_pass_4','Siti','Nurhaliza','instructor','2025-11-27 01:05:01',NULL,1),(5,'I-005','instructor5@ucms.edu','hashed_pass_5','Azure','Bluet','instructor','2025-11-27 01:05:01',NULL,1),(1001,'S2401001A','alex.student@ucms.edu','hashed_pass_s1','Alex','Cross','student','2025-11-27 01:05:01',NULL,1),(2403053,'101','tykcuber@gmail.com','pass','yueaki','tanb','student','2025-11-28 13:17:43',NULL,0),(2403054,'10010101','admin@ucms.edu','password','Admin','Boy','admin','2025-11-28 15:45:43',NULL,1),(2403066,'2403052','2403052@sit.singaporetech.edu.sg','pass','Tan','921 Kai','student','2025-11-28 22:55:52',NULL,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-29 19:48:49
