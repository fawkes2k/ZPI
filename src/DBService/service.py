from src.model import EmailStr, ServiceError, User, UUID, UUID4, Course, UserCourses, Review, Section, Video, Attachment, VideoFeedback
from os import getenv
from asyncpg import create_pool
from logging import basicConfig, DEBUG, debug, info, error
from traceback import extract_stack
from dotenv import load_dotenv

NOT_INIT = 'Service not initialized'
load_dotenv()
URL = getenv('DATABASE_URL')
SCHEMA = getenv('SCHEMA')


class Logger:
    def __call__(self, record): debug(record)


class DbService:
    pool = None

    async def initialize(self):
        basicConfig(filename='log.txt', encoding='utf-8', level=DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        try: self.pool = await create_pool(URL, timeout=30, command_timeout=5, server_settings={'search_path': SCHEMA})
        except Exception as e:
            error(extract_stack())
            raise e
        info('connected to [{}]'.format(URL))

    async def get_users(self, sort_by='last_name', offset=0, limit=20) -> list[User]:
        try:
            if self.pool is None:
                error(NOT_INIT)
                raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT * FROM bc_user ORDER BY $1 OFFSET $2 LIMIT $3', sort_by, offset, limit)
                    res = [User(**dict(r)) for r in row]
                    info('Searched for all users: {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_user(self, user_id: UUID4 = UUID(int=0), email: EmailStr = 'NULL') -> User | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT * FROM bc_user WHERE user_id=$1 OR email=$2', user_id, email)
                    res = User(**dict(row)) if row else None
                    info('Searched for user {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_user(self, user: User) -> User | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO bc_user(last_name, first_name, email, hashed_password, salt) VALUES ($1, $2, $3, $4, $5) RETURNING *',
                                                    user.last_name, user.first_name, user.email, user.hashed_password, user.salt)
                    res = User(**dict(row)) if row else None
                    info('Created user {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def update_user(self, user: User) -> User | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('UPDATE bc_user SET last_name=$1, first_name=$2, email=$3, hashed_password=$4, salt=$5 WHERE user_id=$6 RETURNING *',
                                                    user.last_name, user.first_name, user.email, user.hashed_password, user.salt, user.user_id)
                    res = User(**dict(row)) if row else None
                    info('Updated user {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def delete_user(self, user_id: UUID4) -> User | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM bc_user WHERE user_id=$1 RETURNING *', user_id)
                    res = User(**dict(row)) if row else None
                    info('Removed user {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_courses(self, sort_by='course_name', offset=0, limit=500) -> list[Course]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT * FROM course ORDER BY $1 OFFSET $2 LIMIT $3', sort_by, offset, limit)
                    res = [Course(**dict(r)) for r in row]
                    info('Searched for all courses: {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_course(self, course_id: UUID4) -> Course | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT * FROM course WHERE course_id=$1', course_id)
                    res = Course(**dict(row)) if row else None
                    info('Searched for course {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def did_user_review_this_course(self, course_id: UUID4, user_id: UUID4) -> bool | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT COUNT(*) = 1 FROM course WHERE course_id=$1 and author=$2', course_id, user_id)
                    res = bool(row)
                    info('"Did {} reviewed course {}" is {}'.format(user_id, course_id, res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_course(self, course: Course) -> Course | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO course(course_name, description, price, image, author) VALUES ($1, $2, $3, $4, $5) RETURNING *',
                                                    course.course_name, course.description, str(course.price), course.image, course.author)
                    res = Course(**dict(row)) if row else None
                    info('Created course {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def update_course(self, course: Course) -> Course | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('UPDATE course SET course_name=$1, description=$2, price=$3, image=$4, author=$5 WHERE course_id=$6 RETURNING *',
                                                    course.course_name, course.description, course.price, course.image, course.author, course.course_id)
                    res = Course(**dict(row)) if row else None
                    info('Updated course {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def delete_course(self, course_id: UUID4) -> Course | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM course WHERE course_id=$1 RETURNING *', course_id)
                    res = Course(**dict(row)) if row else None
                    info('Removed course {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_user_to_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO user_courses(user_id, course_id) VALUES ($1, $2) RETURNING *', user_id, course_id)
                    res = UserCourses(**dict(row)) if row else None
                    info('Added user {} to course {}'.format(user_id, course_id))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def remove_user_from_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM user_courses WHERE user_id=$1 and course_id=$2 RETURNING *', user_id, course_id)
                    res = UserCourses(**dict(row)) if row else None
                    info('Deleted user {} from course {}'.format(user_id, course_id))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_user_courses(self, user_id: UUID4, offset=0, limit=20) -> list[UUID4]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT course_id FROM user_courses WHERE user_id=$1 OFFSET $2 LIMIT $3', user_id, offset, limit)
                    res = [r['course_id'] for r in row]
                    info('User {} courses: {}'.format(user_id, res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_course_users(self, course_id: UUID4, offset=0, limit=50) -> list[UUID4]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT user_id FROM user_courses WHERE course_id=$1 OFFSET $2 LIMIT $3', course_id, offset, limit)
                    res = [r['user_id'] for r in row]
                    info('Course {} users: {}'.format(course_id, res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def is_user_assigned_to_course(self, user_id: UUID4, course_id: UUID4) -> bool:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT COUNT(*) = 1 FROM user_courses WHERE user_id=$1 and course_id=$2', user_id, course_id)
                    res = bool(row)
                    info('"User {} is assigned to course {}" is {}'.format(user_id, course_id, res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_reviews(self, course_id: UUID4, sort_by='creation_date', offset=0, limit=20) -> list[Review]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT * FROM course_review WHERE course_id=$1 ORDER BY $2 OFFSET $3 LIMIT $4', course_id, sort_by, offset, limit)
                    res = [Review(**dict(r)) for r in row]
                    info('Searched for course reviews: {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_review(self, review_id: UUID4) -> Review | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT * FROM course_review WHERE review_id=$1', review_id)
                    res = Review(**dict(row)) if row else None
                    info('Searched for course review {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_review(self, review: Review) -> Review | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO course_review(course_id, author, rating, comment) VALUES ($1, $2, $3, $4) RETURNING *',
                                                    review.course_id, review.author, review.rating, review.comment)
                    res = Review(**dict(row)) if row else None
                    info('Created course review {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def update_review(self, review: Review) -> Review | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('UPDATE course_review SET course_id=$1, author=$2, rating=$3, comment=$4 WHERE review_id=$5 RETURNING *',
                                                    review.course_id, review.author, review.rating, review.comment, review.review_id)
                    res = Review(**dict(row)) if row else None
                    info('Updated course review {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def delete_review(self, review_id: UUID4) -> Review | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM course_review WHERE review_id=$1 RETURNING *', review_id)
                    res = Review(**dict(row)) if row else None
                    info('Removed course review {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_sections(self, course_id: UUID4, sort_by='creation_date', offset=0, limit=20) -> list[Section]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT * FROM section WHERE course_id=$1 ORDER BY $2 DESC OFFSET $3 LIMIT $4', course_id, sort_by, offset, limit)
                    res = [Section(**dict(r)) for r in row]
                    info('Searched for sections: {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_section(self, section_id: UUID4) -> Section | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT * FROM section WHERE section_id=$1', section_id)
                    res = Section(**dict(row)) if row else None
                    info('Searched for section {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_section(self, section: Section) -> Section | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO section(section_name, course_id) VALUES ($1, $2) RETURNING *', section.section_name, section.course_id)
                    res = Section(**dict(row)) if row else None
                    info('Created section {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def update_section(self, section: Section) -> Section | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('UPDATE section SET section_name=$1, course_id=$2 WHERE section_id=$3 RETURNING *',
                                                    section.section_name, section.course_id, section.section_id)
                    res = Section(**dict(row)) if row else None
                    info('Updated section {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def delete_section(self, section_id: UUID4) -> Section | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM section WHERE section_id=$1 RETURNING *', section_id)
                    res = Section(**dict(row)) if row else None
                    info('Removed section {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_videos(self, section_id: UUID4, sort_by='video_name', offset=0, limit=20) -> list[Video]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT * FROM video WHERE section_id=$1 ORDER BY $2 OFFSET $3 LIMIT $4', section_id, sort_by, offset, limit)
                    res = [Video(**dict(r)) for r in row]
                    info('Searched for videos: {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_video(self, video_id: UUID4) -> Video | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT * FROM video WHERE video_id=$1', video_id)
                    res = Video(**dict(row)) if row else None
                    info('Searched for video {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_video(self, video: Video) -> Video | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO video(video_name, section_id, video_hash, length) VALUES ($1, $2, $3, $4) RETURNING *',
                                                    video.video_name, video.section_id, video.video_hash, video.length)
                    res = Video(**dict(row)) if row else None
                    info('Created video {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def update_video(self, video: Video) -> Video | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('UPDATE video SET video_name=$1, section_id=$2, video_hash=$3, length=$4 WHERE video_id=$5 RETURNING *',
                                                    video.video_name, video.section_id, video.video_hash, video.length, video.video_id)
                    res = Video(**dict(row)) if row else None
                    info('Updated video {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def delete_video(self, video_id: UUID4) -> Video | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM video WHERE video_id=$1 RETURNING *', video_id)
                    res = Video(**dict(row)) if row else None
                    info('Removed video {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_attachments(self, video_id: UUID4, sort_by='file_name', offset=0, limit=20) -> list[Attachment]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT * FROM attachment WHERE video_id=$1 ORDER BY $2 OFFSET $3 LIMIT $4', video_id, sort_by, offset, limit)
                    res = [Attachment(**dict(r)) for r in row]
                    info('Searched for attachments: {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_attachment(self, attachment_id: UUID4) -> Attachment | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT * FROM attachment WHERE attachment_id=$1', attachment_id)
                    res = Attachment(**dict(row)) if row else None
                    info('Searched for attachment {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_attachment(self, attachment: Attachment) -> Attachment | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO attachment(file_name, file_hash, video_id, file_size) VALUES ($1, $2, $3, $4) RETURNING *',
                                                    attachment.file_name, attachment.file_hash, attachment.video_id, attachment.file_size)
                    res = Attachment(**dict(row)) if row else None
                    info('Created attachment {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def update_attachment(self, attachment: Attachment) -> Attachment | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('UPDATE attachment SET file_name=$1, file_hash=$2, video_id=$3, file_size=$4 WHERE attachment_id=$5 RETURNING *',
                                                    attachment.file_name, attachment.file_hash, attachment.video_id,  attachment.file_size, attachment.attachment_id)
                    res = Attachment(**dict(row)) if row else None
                    info('Updated attachment {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def delete_attachment(self, attachment_id: UUID4) -> Attachment | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM attachment WHERE attachment_id=$1 RETURNING *', attachment_id)
                    res = Attachment(**dict(row)) if row else None
                    info('Removed attachment {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_feedbacks(self, video_id: UUID4, sort_by='creation_date', offset=0, limit=20) -> list[VideoFeedback]:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetch('SELECT * FROM video_feedback WHERE video_id=$1 ORDER BY $2 DESC OFFSET $3 LIMIT $4', video_id, sort_by, offset, limit)
                    res = [VideoFeedback(**dict(r)) for r in row]
                    info('Searched for feedbacks: {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def get_feedback(self, feedback_id: UUID4) -> VideoFeedback | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('SELECT * FROM video_feedback WHERE feedback_id=$1', feedback_id)
                    res = VideoFeedback(**dict(row)) if row else None
                    info('Searched for feedback {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def add_feedback(self, feedback: VideoFeedback) -> VideoFeedback | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('INSERT INTO video_feedback(video_id, author, comment) VALUES ($1, $2, $3) RETURNING *',
                                                    feedback.video_id, feedback.author, feedback.comment)
                    res = VideoFeedback(**dict(row)) if row else None
                    info('Created feedback {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def update_feedback(self, feedback: VideoFeedback) -> VideoFeedback | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('UPDATE video_feedback SET video_id=$1, author=$2, comment=$3 WHERE feedback_id=$4 RETURNING *',
                                                    feedback.video_id, feedback.author, feedback.comment, feedback.feedback_id)
                    res = VideoFeedback(**dict(row)) if row else None
                    info('Updated feedback {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e

    async def delete_feedback(self, feedback_id: UUID4) -> VideoFeedback | None:
        try:
            if self.pool is None: raise ServiceError(NOT_INIT)
            async with self.pool.acquire() as connection:
                with connection.query_logger(Logger()):
                    row = await connection.fetchrow('DELETE FROM video_feedback WHERE feedback_id=$1 RETURNING *', feedback_id)
                    res = VideoFeedback(**dict(row)) if row else None
                    info('Removed feedback {}'.format(res))
                    return res
        except Exception as e:
            error(extract_stack())
            raise e
