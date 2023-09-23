# WellnessWeb.com

**Health and Wellness Online Learning Platform**

The platform offers courses on various subjects. Each course is divided into a configurable number of modules, and each module contains a configurable number of contents. The contents have various types: text, files, images, or videos. Therefore, the data model allows you to store this diverse content. For this purpose, Polymorphism is used, which is the provision of a single interface to entities of different types.

### Functionalities:

- List the courses created by the instructor
- Create, edit, and delete courses
- Add modules to a course and reorder them
- Add different types of content to each module
- Reorder course modules and content
-Log in and log out functions
-

### Lessons:

- Create models for the platform
- Create fixtures for the models and apply them
- Use model inheritance to create data models for polymorphic content
- Create custom model fields
- Order course contents and modules
- Build authentication views
-Install and cofigure Memchached
-Use the Memcached and Redis cache backends

-Initialize the Redis Docker container using the following command:
docker run -it --rm --name redis -p 6379:6379 redis