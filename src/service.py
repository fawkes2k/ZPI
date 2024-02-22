from asyncio import run
from src.model import datetime, ServiceError, User, UUID4, Course, UserCourses, CourseReview, Section, Video, Attachment, VideoFeedback
from os import getenv
from asyncpg import create_pool
from dotenv import load_dotenv

NOT_INIT = 'Service not initialized'
load_dotenv()
URL = getenv('DATABASE_URL')
SCHEMA = getenv('SCHEMA')


def log(message: str): print('[{}] {}'.format(datetime.now(), message))


class DbService:
    pool = None

    async def initialize(self):
        self.pool = await create_pool(URL, timeout=30, command_timeout=5, server_settings={'search_path': SCHEMA})
        log('connected to [{}]'.format(URL))

    async def get_users(self, sort_by='last_name', offset=0, limit=20) -> list[User]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT * FROM bc_user ORDER BY $1 OFFSET $2 LIMIT $3", sort_by, offset, limit)
            res = [User(**dict(r)) for r in row]
            log('Searched for all users: {}'.format(res))
            return res

    async def get_user(self, user_id: UUID4) -> User | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM bc_user WHERE user_id=$1", user_id)
            res = User(**dict(row)) if row else None
            log('Searched for user {}'.format(res))
            return res

    async def add_user(self, user: User) -> User | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO bc_user(last_name, first_name, email, hashed_password, salt) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                                            user.last_name, user.first_name, user.email, user.hashed_password, user.salt)
            res = User(**dict(row)) if row else None
            log('Created user {}'.format(res))
            return res

    async def update_user(self, user: User) -> User | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("UPDATE bc_user SET last_name=$1, first_name=$2, email=$3, hashed_password=$4, salt=$5 WHERE user_id=$6 RETURNING *",
                                            user.last_name, user.first_name, user.email, user.hashed_password, user.salt, user.user_id)
            res = User(**dict(row)) if row else None
            log('Updated user {}'.format(res))
            return res

    async def delete_user(self, user_id: UUID4) -> User | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM bc_user WHERE user_id=$1 RETURNING *", user_id)
            res = User(**dict(row)) if row else None
            log('Removed user {}'.format(res))
            return res

    async def get_courses(self, sort_by='course_name', offset=0, limit=500) -> list[Course]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT * FROM course ORDER BY $1 OFFSET $2 LIMIT $3", sort_by, offset, limit)
            res = [Course(**dict(r)) for r in row]
            log('Searched for all courses: {}'.format(res))
            return res

    async def get_course(self, course_id: UUID4) -> Course | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course WHERE course_id=$1", course_id)
            res = Course(**dict(row)) if row else None
            log('Searched for course {}'.format(res))
            return res

    async def add_course(self, course: Course) -> Course | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO course(course_name, description, price, image, author) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                                            course.course_name, course.description, str(course.price), course.image, course.author)
            res = Course(**dict(row)) if row else None
            log('Created course {}'.format(res))
            return res

    async def update_course(self, course: Course) -> Course | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("UPDATE course SET course_name=$1, description=$2, price=$3, image=$4, author=$5 WHERE course_id=$6 RETURNING *",
                                            course.course_name, course.description, course.price, course.image, course.author, course.course_id)
            res = Course(**dict(row)) if row else None
            log('Updated course {}'.format(res))
            return res

    async def delete_course(self, course_id: UUID4) -> Course | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM course WHERE course_id=$1 RETURNING *", course_id)
            res = Course(**dict(row)) if row else None
            log('Removed course {}'.format(res))
            return res

    async def add_user_to_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO user_courses(user_id, course_id) VALUES ($1, $2) RETURNING *", user_id, course_id)
            res = UserCourses(**dict(row)) if row else None
            log('Added user {} to course {}'.format(user_id, course_id))
            return res

    async def remove_user_from_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM user_courses WHERE user_id=$1 and course_id=$2 RETURNING *", user_id, course_id)
            res = UserCourses(**dict(row)) if row else None
            log('Deleted user {} from course {}'.format(user_id, course_id))
            return res

    async def get_user_courses(self, user_id: UUID4, offset=0, limit=20) -> list[UUID4]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT course_id FROM user_courses WHERE user_id=$1 OFFSET $2 LIMIT $3",
                                         user_id, offset, limit)
            res = [r['course_id'] for r in row]
            log('User {} courses: {}'.format(user_id, res))
            return res

    async def get_course_users(self, course_id: UUID4, offset=0, limit=50) -> list[UUID4]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT user_id FROM user_courses WHERE course_id=$1 OFFSET $2 LIMIT $3",
                                         course_id, offset, limit)
            res = [r['user_id'] for r in row]
            log('Course {} users: {}'.format(course_id, res))
            return res

    async def is_user_assigned_to_course(self, user_id: UUID4, course_id: UUID4) -> bool:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT COUNT(*) = 1 FROM user_courses WHERE user_id=$1 and course_id=$2", user_id, course_id)
            res = bool(row)
            log('"User {} is assigned to course {}" is {}'.format(user_id, course_id, res))
            return res

    async def get_course_reviews(self, course_id: UUID4, sort_by='creation_date', offset=0, limit=20) -> list[CourseReview]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT * FROM course_review WHERE course_id=$1 ORDER BY $2 OFFSET $3 LIMIT $4", course_id, sort_by, offset, limit)
            res = [CourseReview(**dict(r)) for r in row]
            log('Searched for course reviews: {}'.format(res))
            return res

    async def get_course_review(self, review_id: UUID4) -> CourseReview | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course_review WHERE review_id=$1", review_id)
            res = CourseReview(**dict(row)) if row else None
            log('Searched for course review {}'.format(res))
            return res

    async def add_course_review(self, course_review: CourseReview) -> CourseReview | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO course_review(course_id, author, rating, comment) VALUES ($1, $2, $3, $4) RETURNING *",
                                            course_review.course_id, course_review.author, course_review.rating, course_review.comment)
            res = CourseReview(**dict(row)) if row else None
            log('Created course review {}'.format(res))
            return res

    async def update_course_review(self, course_review: CourseReview) -> CourseReview | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("UPDATE course_review SET course_id=$1, author=$2, rating=$3, comment=$4 WHERE review_id=$5 RETURNING *",
                                            course_review.course_id, course_review.author, course_review.rating, course_review.comment, course_review.review_id)
            res = CourseReview(**dict(row)) if row else None
            log('Updated course review {}'.format(res))
            return res

    async def delete_course_review(self, review_id: UUID4) -> CourseReview | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM course_review WHERE review_id=$1 RETURNING *", review_id)
            res = CourseReview(**dict(row)) if row else None
            log('Removed course review {}'.format(res))
            return res

    async def get_sections(self, course_id: UUID4, sort_by='creation_date', offset=0, limit=20) -> list[Section]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT * FROM section WHERE course_id=$1 ORDER BY $2 DESC OFFSET $3 LIMIT $4", course_id, sort_by, offset, limit)
            res = [Section(**dict(r)) for r in row]
            log('Searched for sections: {}'.format(res))
            return res

    async def get_section(self, section_id: UUID4) -> Section | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM section WHERE section_id=$1", section_id)
            res = Section(**dict(row)) if row else None
            log('Searched for section {}'.format(res))
            return res

    async def add_section(self, section: Section) -> Section | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO section(section_name, course_id) VALUES ($1, $2) RETURNING *",
                                            section.section_name, section.course_id)
            res = Section(**dict(row)) if row else None
            log('Created section {}'.format(res))
            return res

    async def update_section(self, section: Section) -> Section | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("UPDATE section SET section_name=$1, course_id=$2 WHERE section_id=$3 RETURNING *",
                                            section.section_name, section.course_id, section.section_id)
            res = Section(**dict(row)) if row else None
            log('Updated section {}'.format(res))
            return res

    async def delete_section(self, section_id: UUID4) -> Section | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM section WHERE section_id=$1 RETURNING *", section_id)
            res = Section(**dict(row)) if row else None
            log('Removed section {}'.format(res))
            return res

    async def get_videos(self, section_id: UUID4, sort_by='video_name', offset=0, limit=20) -> list[Video]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT * FROM video WHERE section_id=$1 ORDER BY $2 OFFSET $3 LIMIT $4", section_id, sort_by, offset, limit)
            res = [Video(**dict(r)) for r in row]
            log('Searched for videos: {}'.format(res))
            return res

    async def get_video(self, video_id: UUID4) -> Video | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM video WHERE video_id=$1", video_id)
            res = Video(**dict(row)) if row else None
            log('Searched for video {}'.format(res))
            return res

    async def add_video(self, video: Video) -> Video | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO video(video_name, section_id, video_hash, length) VALUES ($1, $2, $3, $4) RETURNING *",
                                            video.video_name, video.section_id, video.video_hash, video.length)
            res = Video(**dict(row)) if row else None
            log('Created video {}'.format(res))
            return res

    async def update_video(self, video: Video) -> Video | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("UPDATE video SET video_name=$1, section_id=$2, video_hash=$3, length=$4 WHERE video_id=$5 RETURNING *",
                                            video.video_name, video.section_id, video.video_hash, video.length, video.video_id)
            res = Video(**dict(row)) if row else None
            log('Updated video {}'.format(res))
            return res

    async def delete_video(self, video_id: UUID4) -> Video | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM video WHERE video_id=$1 RETURNING *", video_id)
            res = Video(**dict(row)) if row else None
            log('Removed video {}'.format(res))
            return res

    async def get_attachments(self, video_id: UUID4, sort_by='file_name', offset=0, limit=20) -> list[Attachment]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT * FROM attachment WHERE video_id=$1 ORDER BY $2 OFFSET $3 LIMIT $4", video_id, sort_by, offset, limit)
            res = [Attachment(**dict(r)) for r in row]
            log('Searched for attachments: {}'.format(res))
            return res

    async def get_attachment(self, attachment_id: UUID4) -> Attachment | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM attachment WHERE attachment_id=$1", attachment_id)
            res = Attachment(**dict(row)) if row else None
            log('Searched for attachment {}'.format(res))
            return res

    async def add_attachment(self, attachment: Attachment) -> Attachment | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO attachment(file_name, file_hash, video_id) VALUES ($1, $2, $3) RETURNING *",
                                            attachment.file_name, attachment.file_hash, attachment.video_id)
            res = Attachment(**dict(row)) if row else None
            log('Created attachment {}'.format(res))
            return res

    async def update_attachment(self, attachment: Attachment) -> Attachment | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("UPDATE attachment SET file_name=$1, file_hash=$2, video_id=$3 WHERE attachment_id=$4 RETURNING *",
                                            attachment.file_name, attachment.file_hash, attachment.video_id, attachment.attachment_id)
            res = Attachment(**dict(row)) if row else None
            log('Updated attachment {}'.format(res))
            return res

    async def delete_attachment(self, attachment_id: UUID4) -> Attachment | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM attachment WHERE attachment_id=$1 RETURNING *", attachment_id)
            res = Attachment(**dict(row)) if row else None
            log('Removed attachment {}'.format(res))
            return res

    async def get_feedbacks(self, video_id: UUID4, sort_by='creation_date', offset=0, limit=20) -> list[VideoFeedback]:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT * FROM video_feedback WHERE video_id=$1 ORDER BY $2 DESC OFFSET $3 LIMIT $4", video_id, sort_by, offset, limit)
            res = [VideoFeedback(**dict(r)) for r in row]
            log('Searched for feedbacks: {}'.format(res))
            return res

    async def get_feedback(self, feedback_id: UUID4) -> VideoFeedback | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM video_feedback WHERE feedback_id=$1", feedback_id)
            res = VideoFeedback(**dict(row)) if row else None
            log('Searched for feedback {}'.format(res))
            return res

    async def add_feedback(self, feedback: VideoFeedback) -> VideoFeedback | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO video_feedback(video_id, author, comment) VALUES ($1, $2, $3) RETURNING *",
                                            feedback.video_id, feedback.author, feedback.comment)
            res = VideoFeedback(**dict(row)) if row else None
            log('Created feedback {}'.format(res))
            return res

    async def update_feedback(self, feedback: VideoFeedback) -> VideoFeedback | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("UPDATE video_feedback SET video_id=$1, author=$2, comment=$3 WHERE feedback_id=$4 RETURNING *",
                                            feedback.video_id, feedback.author, feedback.comment, feedback.feedback_id)
            res = VideoFeedback(**dict(row)) if row else None
            log('Updated feedback {}'.format(res))
            return res

    async def delete_feedback(self, feedback_id: UUID4) -> VideoFeedback | None:
        if self.pool is None: raise ServiceError(NOT_INIT)
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM video_feedback WHERE feedback_id=$1 RETURNING *", feedback_id)
            res = VideoFeedback(**dict(row)) if row else None
            log('Removed feedback {}'.format(res))
            return res


async def test():
    db = DbService()
    await db.initialize()

    email = 'test@example.com'
    user1 = await db.add_user(user=User())
    users = await db.get_users()
    if user1 not in users: raise ValueError('1.1')
    user2 = await db.update_user(User(user_id=user1.user_id, email=email))
    user3 = await db.get_user(user_id=user2.user_id)
    if user2.email != email: raise ValueError('1.2')
    if user3.email != email: raise ValueError('1.3')
    if user2.email != user3.email: raise ValueError('1.4')

    image = b'a'
    course1 = await db.add_course(course=Course(author=user3.user_id))
    courses = await db.get_courses()
    if course1 not in courses: raise ValueError('2.1')
    course2 = await db.update_course(course=Course(course_id=course1.course_id, image=image, author=user3.user_id))
    course3 = await db.get_course(course_id=course2.course_id)
    if course2.image != image: raise ValueError('2.2')
    if course3.image != image: raise ValueError('2.3')
    if course2.image != course3.image: raise ValueError('2.4')

    uc1 = await db.add_user_to_course(user_id=user3.user_id, course_id=course3.course_id)
    user_courses1 = await db.get_user_courses(user_id=uc1.user_id)
    course_users1 = await db.get_course_users(course_id=uc1.course_id)
    is_assigned = await db.is_user_assigned_to_course(user_id=uc1.user_id, course_id=uc1.course_id)
    if uc1.course_id not in user_courses1: raise ValueError('3.1')
    if uc1.user_id not in course_users1: raise ValueError('3.2')
    if uc1.user_id != course_users1[0] or uc1.course_id != user_courses1[0]: raise ValueError('3.3')
    if not is_assigned: raise ValueError('3.4')

    rating = 5
    review1 = await db.add_course_review(course_review=CourseReview(course_id=course3.course_id, author=user3.user_id))
    reviews = await db.get_course_reviews(course_id=course3.course_id)
    if review1 not in reviews: raise ValueError('4.1')
    review2 = await db.update_course_review(course_review=CourseReview(review_id=review1.review_id, rating=rating, course_id=course3.course_id, author=user3.user_id))
    review3 = await db.get_course_review(review_id=review2.review_id)
    if review2.rating != rating: raise ValueError('4.2')
    if review3.rating != rating: raise ValueError('4.3')
    if review2.rating != review3.rating: raise ValueError('4.4')

    section_name = 'TEST'
    section1 = await db.add_section(section=Section(course_id=course3.course_id))
    sections = await db.get_sections(course_id=course3.course_id)
    if section1 not in sections: raise ValueError('5.1')
    section2 = await db.update_section(Section(section_id=section1.section_id, section_name=section_name, course_id=course3.course_id))
    section3 = await db.get_section(section_id=section2.section_id)
    if section2.section_name != section_name: raise ValueError('5.2')
    if section3.section_name != section_name: raise ValueError('5.3')
    if section2.section_name != section3.section_name: raise ValueError('5.4')

    video_name = 'TEST'
    video1 = await db.add_video(video=Video(section_id=section3.section_id))
    videos = await db.get_videos(section_id=section3.section_id)
    if video1 not in videos: raise ValueError('6.1')
    video2 = await db.update_video(video=Video(video_id=video1.video_id, video_name=video_name, section_id=section3.section_id))
    video3 = await db.get_video(video_id=video2.video_id)
    if video2.video_name != video_name: raise ValueError('6.2')
    if video3.video_name != video_name: raise ValueError('6.3')
    if video2.video_name != video3.video_name: raise ValueError('6.4')

    file_name = 'TEST'
    attachment1 = await db.add_attachment(attachment=Attachment(video_id=video3.video_id))
    attachments = await db.get_attachments(video_id=video3.video_id)
    if attachment1 not in attachments: raise ValueError('7.1')
    attachment2 = await db.update_attachment(attachment=Attachment(attachment_id=attachment1.attachment_id, file_name=file_name, video_id=video3.video_id))
    attachment3 = await db.get_attachment(attachment_id=attachment2.attachment_id)
    if attachment2.file_name != file_name: raise ValueError('7.2')
    if attachment3.file_name != file_name: raise ValueError('7.3')
    if attachment2.file_name != attachment3.file_name: raise ValueError('7.4')

    comment = 'TEST'
    feedback1 = await db.add_feedback(feedback=VideoFeedback(video_id=video3.video_id, author=user3.user_id))
    feedbacks = await db.get_feedbacks(video_id=video3.video_id)
    if feedback1 not in feedbacks: raise ValueError('8.1')
    feedback2 = await db.update_feedback(feedback=VideoFeedback(feedback_id=feedback1.feedback_id, author=user3.user_id, comment=comment, video_id=video3.video_id))
    feedback3 = await db.get_feedback(feedback_id=feedback2.feedback_id)
    if feedback2.comment != comment: raise ValueError('8.2')
    if feedback3.comment != comment: raise ValueError('8.3')
    if feedback2.comment != feedback3.comment: raise ValueError('8.4')

    feedback4 = await db.delete_feedback(feedback_id=feedback3.feedback_id)
    feedback5 = await db.get_feedback(feedback_id=feedback4.feedback_id)
    if feedback5 is not None: raise ValueError('9.1')
    attachment4 = await db.delete_attachment(attachment_id=attachment3.attachment_id)
    attachment5 = await db.get_attachment(attachment_id=attachment4.attachment_id)
    if attachment5 is not None: raise ValueError('9.2')
    video4 = await db.delete_video(video_id=video3.video_id)
    video5 = await db.get_video(video_id=video4.video_id)
    if video5 is not None: raise ValueError('9.3')
    section4 = await db.delete_section(section_id=section3.section_id)
    section5 = await db.get_section(section_id=section4.section_id)
    if section5 is not None: raise ValueError('9.4')

    review4 = await db.delete_course_review(review_id=review3.review_id)
    review5 = await db.get_course_review(review_id=review4.review_id)
    if review5 is not None: raise ValueError('9.5')
    uc2 = await db.remove_user_from_course(user_id=user3.user_id, course_id=course3.course_id)
    user_courses2 = await db.get_user_courses(user_id=uc2.user_id)
    course_users2 = await db.get_course_users(course_id=uc2.course_id)
    if uc2.course_id in user_courses2: raise ValueError('9.6')
    if uc2.user_id in course_users2: raise ValueError('9.7')
    course4 = await db.delete_course(course_id=course3.course_id)
    course5 = await db.get_course(course_id=course4.course_id)
    if course5 is not None: raise ValueError('9.8')
    user4 = await db.delete_user(user_id=user3.user_id)
    user5 = await db.get_user(user_id=user4.user_id)
    if user5 is not None: raise ValueError('9.9')

if __name__ == '__main__': run(test())
