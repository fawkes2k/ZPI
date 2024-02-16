from src.model import datetime, ServiceError, User, UUID4, Course, UserCourses, CourseReview, Section, Video, Attachment, VideoFeedback
from os import getenv
from asyncpg import create_pool
from dotenv import load_dotenv

load_dotenv()
URL = getenv('DATABASE_URL')
SCHEMA = getenv('SCHEMA')


def log(message: str): print('[{}] {}'.format(datetime.now(), message))


class DbService:
    pool = None

    async def initialize(self):
        self.pool = await create_pool(URL, timeout=30, command_timeout=5, server_settings={'search_path': SCHEMA})
        log('connected to [{}]'.format(URL))

    async def get_users(self, sort_by='last_name', sort_dir='ASC', offset=0, limit=20) -> list[User]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM bc_user ORDER BY $1 $2 OFFSET $3 LIMIT $4", sort_by, sort_dir, offset, limit)
            res = [User(**dict(r)) for r in row]
            log('Searched for all users: {}'.format(res))
            return res

    async def get_user(self, user_id: UUID4) -> User | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM bc_user WHERE user_id=$1", user_id)
            res = User(**dict(row)) if row else None
            log('Searched for user {}'.format(res))
            return res

    async def add_user(self, user: User) -> User | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO bc_user(last_name, first_name, email, hashed_password, salt) VALUES (%s, %s, %s, %s, %s) RETURNING *",
                                            user.last_name, user.first_name, user.email, user.hashed_password, user.salt)
            res = User(**dict(row)) if row else None
            log('Created user {}'.format(res))
            return res

    async def delete_user(self, user_id: UUID4) -> User | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM bc_user WHERE user_id=$1 RETURNING *", user_id)
            res = User(**dict(row)) if row else None
            log('Removed user {}'.format(res))
            return res

    async def get_courses(self, sort_by='course_name', sort_dir='ASC', offset=0, limit=500) -> list[Course]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course ORDER BY $1 $2 OFFSET $3 LIMIT $4", sort_by, sort_dir, offset, limit)
            res = [Course(**dict(r)) for r in row]
            log('Searched for all courses: {}'.format(res))
            return res

    async def get_course(self, course_id: UUID4) -> Course | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course WHERE course_id=$1", course_id)
            res = Course(**dict(row)) if row else None
            log('Searched for course {}'.format(res))
            return res

    async def add_course(self, course: Course) -> Course | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO course(course_name, description, price, image, author) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                                            course.course_name, course.description, course.price, course.image, course.author)
            res = Course(**dict(row)) if row else None
            log('Created course {}'.format(res))
            return res

    async def delete_course(self, course_id: UUID4) -> Course | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM course WHERE course_id=$1 RETURNING *", course_id)
            res = Course(**dict(row)) if row else None
            log('Removed course {}'.format(res))
            return res

    async def add_user_to_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO user_courses(user_id, course_id) VALUES ($1, %2) RETURNING *", user_id, course_id)
            res = UserCourses(**dict(row)) if row else None
            log('Added user {} to course {}'.format(user_id, course_id))
            return res

    async def remove_user_from_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM user_courses WHERE user_id=$1 and course_id=$2 RETURNING *", user_id, course_id)
            res = UserCourses(**dict(row)) if row else None
            log('Deleted user {} from course {}'.format(user_id, course_id))
            return res

    async def get_user_courses(self, user_id: UUID4, offset=0, limit=20) -> list[UUID4]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT course_id FROM user_courses WHERE user_id=$1 OFFSET $2 LIMIT $3",
                                         user_id, offset, limit)
            res = [r for r in row]
            log('User {} courses: {}'.format(user_id, res))
            return res

    async def get_course_users(self, course_id: UUID4, offset=0, limit=50) -> list[UUID4]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT course_id FROM user_courses WHERE course_id=$1 OFFSET $2 LIMIT $3",
                                         course_id, offset, limit)
            res = [r for r in row]
            log('"Course {} users: {}'.format(course_id, res))
            return res

    async def is_user_assigned_to_course(self, user_id: UUID4, course_id: UUID4) -> bool:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT COUNT(*) = 0 FROM user_courses WHERE user_id=$1 and course_id=$2", user_id, course_id)
            res = bool(row)
            log('"User {} is assigned to course {}" is {}'.format(user_id, course_id, res))
            return res

    async def get_course_reviews(self, course_id: UUID4, sort_by='creation_date', sort_dir='ASC', offset=0, limit=20) -> list[CourseReview]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course_review WHERE course_id=$1 ORDER BY $2 $3 OFFSET $4 LIMIT $5",
                                            course_id, sort_by, sort_dir, offset, limit)
            res = [CourseReview(**dict(r)) for r in row]
            log('Searched for course reviews: {}'.format(res))
            return res

    async def get_course_review(self, review_id: UUID4) -> CourseReview | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course_review WHERE review_id=$1", review_id)
            res = CourseReview(**dict(row)) if row else None
            log('Searched for course review {}'.format(res))
            return res

    async def add_course_review(self, course_review: CourseReview) -> CourseReview | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO course_review(course_id, author, rating, comment) VALUES ($1, $2, $3, $4) RETURNING *",
                                            course_review.course_id, course_review.author, course_review.rating, course_review.comment)
            res = CourseReview(**dict(row)) if row else None
            log('Created course review {}'.format(res))
            return res

    async def delete_course_review(self, review_id: UUID4) -> CourseReview | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM course_review WHERE review_id=$1 RETURNING *", review_id)
            res = CourseReview(**dict(row)) if row else None
            log('Removed course review {}'.format(res))
            return res

    async def get_sections(self, course_id: UUID4, sort_by='creation_date', sort_dir='DESC', offset=0, limit=20) -> list[Section]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM section WHERE course_id=$1 ORDER BY $2 $3 OFFSET $4 LIMIT $5",
                                            course_id, sort_by, sort_dir, offset, limit)
            res = [Section(**dict(r)) for r in row]
            log('Searched for sections: {}'.format(res))
            return res

    async def get_section(self, section_id: UUID4) -> Section | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM section WHERE section_id=$1", section_id)
            res = Section(**dict(row)) if row else None
            log('Searched for section {}'.format(res))
            return res

    async def add_section(self, section: Section) -> Section | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO section(section_name, course_id) VALUES ($1, $2) RETURNING *",
                                            section.section_name, section.course_id)
            res = Section(**dict(row)) if row else None
            log('Created section {}'.format(res))
            return res

    async def delete_section(self, section_id: UUID4) -> Section | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM section WHERE section_id=$1 RETURNING *", section_id)
            res = Section(**dict(row)) if row else None
            log('Removed section {}'.format(res))
            return res

    async def get_videos(self, section_id: UUID4, sort_by='video_name', sort_dir='ASC', offset=0, limit=20) -> list[Video]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM video WHERE section_id=$1 ORDER BY $2 $3 OFFSET $4 LIMIT $5",
                                            section_id, sort_by, sort_dir, offset, limit)
            res = [Video(**dict(r)) for r in row]
            log('Searched for videos: {}'.format(res))
            return res

    async def get_video(self, video_id: UUID4) -> Video | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM video WHERE video_id=$1", video_id)
            res = Video(**dict(row)) if row else None
            log('Searched for video {}'.format(res))
            return res

    async def add_video(self, video: Video) -> Video | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO video(video_name, section_id, video_hash, length) VALUES ($1, $2, $3, $4) RETURNING *",
                                            video.video_name, video.section_id, video.video_hash, video.length)
            res = Video(**dict(row)) if row else None
            log('Created video {}'.format(res))
            return res

    async def delete_video(self, video_id: UUID4) -> Video | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM video WHERE video_id=$1 RETURNING *", video_id)
            res = Video(**dict(row)) if row else None
            log('Removed video {}'.format(res))
            return res

    async def get_attachments(self, video_id: UUID4, sort_by='file_name', sort_dir='ASC', offset=0, limit=20) -> list[Attachment]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM video WHERE video_id=$1 ORDER BY $2 $3 OFFSET $4 LIMIT $5",
                                            video_id, sort_by, sort_dir, offset, limit)
            res = [Attachment(**dict(r)) for r in row]
            log('Searched for attachments: {}'.format(res))
            return res

    async def get_attachment(self, attachment_id: UUID4) -> Attachment | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM attachment WHERE attachment_id=$1", attachment_id)
            res = Attachment(**dict(row)) if row else None
            log('Searched for attachment {}'.format(res))
            return res

    async def add_attachment(self, attachment: Attachment) -> Attachment | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO attachment(file_name, file_hash, video_id) VALUES ($1, $2, $3) RETURNING *",
                                            attachment.file_name, attachment.file_hash, attachment.video_id)
            res = Attachment(**dict(row)) if row else None
            log('Created attachment {}'.format(res))
            return res

    async def delete_attachment(self, attachment_id: UUID4) -> Attachment | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM attachment WHERE attachment_id=$1 RETURNING *", attachment_id)
            res = Attachment(**dict(row)) if row else None
            log('Removed attachment {}'.format(res))
            return res

    async def get_feedbacks(self, video_id: UUID4, sort_by='creation_date', sort_dir='DESC', offset=0, limit=20) -> list[VideoFeedback]:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM video_feedback WHERE video_id=$1 ORDER BY $2 $3 OFFSET $4 LIMIT $5",
                                            video_id, sort_by, sort_dir, offset, limit)
            res = [VideoFeedback(**dict(r)) for r in row]
            log('Searched for feedbacks: {}'.format(res))
            return res

    async def get_feedback(self, feedback_id: UUID4) -> VideoFeedback | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM video_feedback WHERE feedback_id=$1", feedback_id)
            res = VideoFeedback(**dict(row)) if row else None
            log('Searched for feedback {}'.format(res))
            return res

    async def add_feedback(self, feedback: VideoFeedback) -> VideoFeedback | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO video_feedback(video_id, author, comment) VALUES ($1, $2, $3) RETURNING *",
                                            feedback.video_id, feedback.author, feedback.comment)
            res = VideoFeedback(**dict(row)) if row else None
            log('Created feedback {}'.format(res))
            return res

    async def delete_feedback(self, feedback_id: UUID4) -> VideoFeedback | None:
        if self.pool is None: raise ServiceError('Service not initialized')
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM video_feedback WHERE feedback_id=$1 RETURNING *", feedback_id)
            res = VideoFeedback(**dict(row)) if row else None
            log('Removed feedback {}'.format(res))
            return res
