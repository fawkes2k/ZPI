from src.model import User, Course, UserCourses, datetime, UUID4
from os import getenv
from asyncpg import create_pool
from dotenv import load_dotenv

load_dotenv()
URL = getenv('DATABASE_URL')
SCHEMA = getenv('SCHEMA')


def log(message: str): print('[{}] {}'.format(datetime.now(), message))


class DbService:
    async def initialize(self):
        self.pool = await create_pool(URL, timeout=30, command_timeout=5, server_settings={'search_path': SCHEMA})
        log('connected to [{al}]'.format(URL))

    async def get_users(self, sort_by='last_name', sort_dir='ASC', offset=0, limit=20) -> list[User]:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM bc_user ORDER BY $1 $2 OFFSET $3 LIMIT $4", sort_by, sort_dir, offset, limit)
            res = [User(**dict(r)) for r in row]
            log('Searched for all users: {}'.format(res))
            return res

    async def get_user(self, user_id: UUID4) -> User | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM bc_user WHERE user_id=$1", user_id)
            res = User(**dict(row)) if row else None
            log('Searched for user {}'.format(res))
            return res

    async def add_user(self, user: User) -> User | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO bc_user(last_name, first_name, email, hashed_password, salt) VALUES (%s, %s, %s, %s, %s) RETURNING *",
                                            user.last_name, user.first_name, user.email, user.hashed_password, user.salt)
            res = User(**dict(row)) if row else None
            log('Created user {}'.format(res))
            return res

    async def delete_user(self, user_id: UUID4) -> User | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM bc_user WHERE user_id=$1 RETURNING *", user_id)
            res = User(**dict(row)) if row else None
            log('Removed user {}'.format(res))
            return res

    async def get_courses(self, sort_by='course_name', sort_dir='ASC', offset=0, limit=500) -> list[Course]:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course ORDER BY $1 $2 OFFSET $3 LIMIT $4", sort_by, sort_dir, offset, limit)
            res = [Course(**dict(r)) for r in row]
            log('Searched for all courses: {}'.format(res))
            return res

    async def get_course(self, course_id: UUID4) -> Course | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT * FROM course WHERE course_id = $1", course_id)
            res = Course(**dict(row)) if row else None
            log('Searched for course {}'.format(res))
            return res

    async def add_course(self, course: Course) -> Course | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO course(course_name, description, price, image, author) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                                            course.course_name, course.description, course.price, course.image, course.author)
            res = Course(**dict(row)) if row else None
            log('Created course {}'.format(res))
            return res

    async def delete_course(self, course_id: UUID4) -> Course | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM course WHERE course_id = $1 RETURNING *", course_id)
            res = Course(**dict(row)) if row else None
            log('Removed course {}'.format(res))
            return res

    async def add_user_to_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("INSERT INTO user_courses(user_id, course_id) VALUES ($1, %2) RETURNING *", user_id, course_id)
            res = UserCourses(**dict(row)) if row else None
            log('Added user {} to course {}'.format(user_id, course_id))
            return res

    async def remove_user_from_course(self, user_id: UUID4, course_id: UUID4) -> UserCourses | None:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("DELETE FROM user_courses WHERE user_id = $1 and course_id = $2 RETURNING *", user_id, course_id)
            res = UserCourses(**dict(row)) if row else None
            log('Deleted user {} from course {}'.format(user_id, course_id))
            return res

    async def get_user_courses(self, user_id: UUID4, sorted_by='course_name', sort_dir='ASC', offset=0, limit=20) -> list[UUID4]:
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT course_id FROM user_courses WHERE user_id = $1 ORDER BY $2 $3 OFFSET $4 LIMIT $5",
                                         user_id, sorted_by, sort_dir, offset, limit)
            res = [r for r in row]
            log('User {} courses: {}'.format(user_id, res))
            return res

    async def is_user_assigned_to_course(self, user_id: UUID4, course_id: UUID4) -> bool:
        async with self.pool.acquire() as connection:
            row = await connection.fetch("SELECT course_id FROM user_courses WHERE user_id = $1 and course_id = $2", user_id, course_id)
            res = bool(row)
            log('"User {} is assigned to course {}" is {}'.format(user_id, course_id, res))
            return res
