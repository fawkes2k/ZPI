from random import randbytes
from hashlib import sha3_512
from uuid import uuid4, UUID
from datetime import datetime, UTC
from pydantic import AwareDatetime, BaseModel, EmailStr, PositiveInt, PositiveFloat, StrictBytes, StrictStr, UUID4


class User(BaseModel):
    user_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    last_name: StrictStr = 'Doe'
    first_name: StrictStr = 'John'
    email: EmailStr = 'test@example.com'
    hashed_password: StrictStr = sha3_512(b'DUMMY').hexdigest()
    salt: StrictBytes = randbytes(256)


class ViewableUser(BaseModel):
    user_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    last_name: StrictStr = 'Doe'
    first_name: StrictStr = 'John'
    email: EmailStr = 'test@example.com'


class Course(BaseModel):
    course_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    course_name: StrictStr = 'DUMMY'
    description: StrictStr = 'DUMMY'
    price: PositiveFloat = 100
    image: StrictStr = 'DUMMY'
    author: UUID4 = UUID(int=0)


class UserCourses(BaseModel):
    user_id: UUID4 = UUID(int=0)
    course_id: UUID4 = UUID(int=0)


class Review(BaseModel):
    review_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    course_id: UUID4 = UUID(int=0)
    author: UUID4 = UUID(int=0)
    rating: PositiveInt = 1
    comment: StrictStr = 'DUMMY'


class Section(BaseModel):
    section_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    section_name: StrictStr = 'DUMMY'
    course_id: UUID4 = UUID(int=0)


class Video(BaseModel):
    video_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    video_name: StrictStr = 'ZZDUMMY.MOV'
    section_id: UUID4 = UUID(int=0)
    video_hash: StrictStr = sha3_512(b'DUMMY').hexdigest()


class Attachment(BaseModel):
    attachment_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    file_name: StrictStr = 'ZZDUMMY.BIN'
    file_hash: StrictStr = sha3_512(b'DUMMY').hexdigest()
    video_id: UUID4 = UUID(int=0)
    file_size: PositiveInt = 1024


class VideoFeedback(BaseModel):
    feedback_id: UUID4 | None = uuid4()
    creation_date: AwareDatetime | None = datetime.now(UTC)
    video_id: UUID4 = UUID(int=0)
    author: UUID4 = UUID(int=0)
    comment: StrictStr = 'DUMMY'


class ServiceError(RuntimeError): pass


if __name__ == '__main__': raise NotImplementedError('Not implemented')
