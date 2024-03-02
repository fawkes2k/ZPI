from asyncio.subprocess import create_subprocess_shell, PIPE
from base64 import b64decode
from os import getenv
from random import randbytes

from flask import Blueprint, request, session, jsonify
from datetime import datetime, timedelta
from service import DbService
from model import User, ViewableUser, Course, Review, VideoFeedback, Video, Attachment
from hashlib import sha3_512
from wand.image import Image

api = Blueprint('api', __name__)
started = datetime.now()


@api.before_app_request
async def initialize_db_service():
    api.db = DbService()
    await api.db.initialize()


@api.after_request
async def release_db_service(response):
    await api.db.terminate()
    return response


@api.route('/health', methods=['GET'])
async def health():
    return jsonify({'uptime': str(datetime.now() - started)}), 200


@api.route('/get_users/<string:sort_by>', methods=['GET'])
async def get_users(sort_by):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get users'}), 401
        users = [ViewableUser(**user.model_dump()).model_dump_json() for user in await api.db.get_users(sort_by=sort_by)]
        return users, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/get_user/<uuid:user_id>', methods=['GET'])
async def get_user(user_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get user'}), 401
        user = await api.db.get_user(user_id)
        viewable_user = ViewableUser(**user.model_dump())
        return None if viewable_user is None else viewable_user.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/login', methods=['POST'])
async def login():
    post = request.get_json()
    pepper = getenv('PEPPER').encode()
    try:
        user = await api.db.get_user(email=post.get('email'))
        password = post.get('password')
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is not None: return jsonify({'error': 'Already logged in'}), 400
        if password is None or not isinstance(password, str): return jsonify({'error': 'Incorrect password format'}), 400
        if user is None: return jsonify({'error': 'User not found'}), 401
        if sha3_512(pepper + password.encode() + user.salt).hexdigest() != user.hashed_password: return jsonify({'error': 'Incorrect password'}), 403
        session['id'] = user.user_id
        return jsonify({'message': 'Logged in'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/logout', methods=['POST'])
async def logout():
    await api.db.initialize()
    requester = await api.db.get_user(user_id=session.get('id'))
    if requester is None: return jsonify({'error': 'Not logged in'}), 401
    session.pop('id', default=None)
    return jsonify({'message': 'Logged out'}), 200


@api.route('/add_user', methods=['POST'])
async def add_user():
    post = request.get_json()
    pepper = getenv('PEPPER').encode()
    salt = randbytes(256)
    try:
        password = post.get('password')
        users_with_email = await api.db.get_user(email=post.get('email'))
        if password is None or not isinstance(password, str): return jsonify({'error': 'Incorrect password format'}), 400
        if users_with_email is not None: return jsonify({'error': 'User already exist'}), 401
        hashed_password = sha3_512(pepper + password.encode() + salt).hexdigest()
        user = User(last_name=post.get('last_name'), first_name=post.get('first_name'), email=post.get('email'), hashed_password=hashed_password, salt=salt)
        new_user = await api.db.add_user(user)
        viewable_user = ViewableUser(**new_user.model_dump()).model_dump_json()
        return viewable_user, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_user', methods=['PUT'])
async def update_user():
    post = request.get_json()
    try:
        user_to_update = await api.db.get_user(user_id=post.get('user_id'))
        if user_to_update is None: return jsonify({'error': 'User does not exist'}), 401
        if session.get('id') != user_to_update.user_id: return jsonify({'error': 'Not authorized to update user'}), 401
        for element in post: user_to_update.__setattr__(element, post[element])
        updated_user = await api.db.update_user(user_to_update)
        viewable_user = ViewableUser(**updated_user.model_dump()).model_dump_json()
        return viewable_user, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_user/<uuid:user_id>', methods=['DELETE'])
async def delete_user(user_id):
    try:
        user_to_delete = await api.db.get_user(user_id=user_id)
        if user_to_delete is None: return jsonify({'error': 'User does not exist'}), 404
        if session.get('id') != user_to_delete.user_id: return jsonify({'error': 'Not authorized to delete users'}), 401
        deleted_user = await api.db.delete_user(user_id)
        session.pop('id', default=None)
        viewable_user = ViewableUser(**deleted_user.model_dump()).model_dump_json()
        return viewable_user, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_courses/<string:sort_by>', methods=['GET'])
async def get_courses(sort_by):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get courses'}), 401
        courses = [course.model_dump_json() for course in await api.db.get_courses(sort_by=sort_by)]
        return courses, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_course/<uuid:course_id>', methods=['GET'])
async def get_course(course_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get a course'}), 401
        course = await api.db.get_course(course_id)
        return None if course is None else course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_course', methods=['POST'])
async def add_course():
    post = request.get_json()
    try:
        image = b64decode(post.get("image").encode())
        max_image_size_mb = int(getenv('MAX_IMAGE_SIZE_MB'))
        if len(image) > max_image_size_mb * 1048576: return jsonify({'error': 'Maximum image size is {} MB'.format(max_image_size_mb)})
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add courses'}), 401
        course = Course(course_name=post.get('course_name'), description=post.get('description'), price=post.get('price'), image=image, author=requester.user_id)
        added_course = await api.db.add_course(course)
        return added_course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_course/<uuid:course_id>', methods=['DELETE'])
async def delete_course(course_id):
    try:
        course_to_delete = await api.db.get_course(course_id=course_id)
        if course_to_delete is None: return jsonify({'error': 'Course does not exist'}), 404
        if session.get('id') != course_to_delete.author: return jsonify({'error': 'Not authorized to delete courses'}), 401
        deleted_course = await api.db.delete_course(course_id)
        return deleted_course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_course', methods=['PUT'])
async def update_course():
    post = request.get_json()
    try:
        course_to_update = await api.db.get_course(course_id=post.get("course_id"))
        if course_to_update is None: return jsonify({'error': 'Course does not exist'}), 401
        if session.get('id') != course_to_update.author: return jsonify({'error': 'Not authorized to update courses'}), 401
        for element in post:
            if element == "image":
                image = b64decode(post[element])
                max_image_size_mb = int(getenv('MAX_IMAGE_SIZE_MB'))
                if len(image) > max_image_size_mb * 1048576: return jsonify({'error': 'Maximum image size is {} MB'.format(max_image_size_mb)})
                course_to_update.image = image
            else: course_to_update.__setattr__(element, post[element])
        updated_course = await api.db.update_course(course_to_update)
        return updated_course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_user_to_course', methods=['POST'])
async def add_user_to_course():
    post = request.get_json()
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add users to courses'}), 401
        course = await api.db.get_course(post.get("course_id"))
        if course is None: return jsonify({'error': 'Course does not exist'}), 404
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if is_added: return jsonify({'error': 'User already added to the course'}), 403
        added_uc = await api.db.add_user_to_course(user_id=requester.user_id, course_id=course.course_id)
        return added_uc.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/remove_user_from_course', methods=['POST'])
async def remove_user_from_course():
    post = request.get_json()
    try:
        course = await api.db.get_course(post.get("course_id"))
        if course is None: return jsonify({'error': 'Course does not exist'}), 404
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add users to courses'}), 401
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'User is not added to the course'}), 403
        removed_uc = await api.db.remove_user_from_course(user_id=requester.user_id, course_id=course.course_id)
        return removed_uc.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_reviews/<uuid:course_id>', methods=['GET'])
async def get_reviews(course_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get reviews'}), 401
        reviews = [review.model_dump_json() for review in await api.db.get_reviews(course_id=course_id)]
        return reviews, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_review/<uuid:review_id>', methods=['GET'])
async def get_review(review_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get a review'}), 401
        review = await api.db.get_review(review_id)
        return None if review is None else review.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_review', methods=['POST'])
async def add_review():
    post = request.get_json()
    try:
        course = await api.db.get_course(post.get("course_id"))
        if course is None: return jsonify({'error': 'Course does not exist'}), 404
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add reviews'}), 401
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to add reviews to this courses'}), 401
        did_review = await api.db.did_user_review_this_course(user_id=requester.user_id, course_id=course.course_id)
        if did_review: return jsonify({'error': 'User already reviewed this course'}), 401
        review = Review(**post, author=requester.user_id)
        added_review = await api.db.add_review(review)
        return added_review.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_review', methods=['PUT'])
async def update_review():
    post = request.get_json()
    try:
        review_to_update = await api.db.get_review(review_id=post.get("review_id"))
        if review_to_update is None: return jsonify({'error': 'Review does not exist'}), 401
        if session.get('id') != review_to_update.author: return jsonify({'error': 'Not authorized to update reviews'}), 401
        for element in post: review_to_update.__setattr__(element, post[element])
        review_to_update = await api.db.update_review(review_to_update)
        return review_to_update.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_review/<uuid:review_id>', methods=['DELETE'])
async def delete_review(review_id):
    try:
        review_to_delete = await api.db.get_review(review_id=review_id)
        if review_to_delete is None: return jsonify({'error': 'Review does not exist'}), 404
        if session.get('id') != review_to_delete.review_id: return jsonify({'error': 'Not authorized to delete review'}), 401
        deleted_review = await api.db.delete_review(review_id)
        return deleted_review.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_sections/<uuid:course_id>', methods=['GET'])
async def get_sections(course_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get sections'}), 401
        course = await api.db.get_course(course_id=course_id)
        if course is None: return jsonify({'error': 'Such course does not exist'}), 404
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get sections from this course'}), 403
        sections = [section.model_dump_json() for section in await api.db.get_sections(course_id=course_id)]
        return sections, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_section/<uuid:section_id>', methods=['GET'])
async def get_section(section_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get a section'}), 401
        section = await api.db.get_section(section_id)
        if section is None: return jsonify({'error': 'Section not found'}), 404
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=section.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get sections from this course'}), 403
        return section.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_section', methods=['PUT'])
async def update_section():
    post = request.get_json()
    try:
        section_to_update = await api.db.get_section(section_id=post.get("section_id"))
        if section_to_update is None: return jsonify({'error': 'Section does not exist'}), 401
        if session.get('id') != section_to_update.author: return jsonify({'error': 'Not authorized to update sections'}), 401
        for element in post: section_to_update.__setattr__(element, post[element])
        section_to_update = await api.db.update_section(section_to_update)
        return section_to_update.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_section/<uuid:section_id>', methods=['DELETE'])
async def delete_section(section_id):
    try:
        section_to_delete = await api.db.get_section(section_id=section_id)
        if section_to_delete is None: return jsonify({'error': 'Section does not exist'}), 404
        if session.get('id') != section_to_delete.section_id: return jsonify({'error': 'Not authorized to delete section'}), 401
        deleted_section = await api.db.delete_section(section_id)
        return deleted_section.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_videos/<uuid:section_id>', methods=['GET'])
async def get_videos(section_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get videos'}), 401
        section = await api.db.get_section(section_id=section_id)
        if section is None: return jsonify({'error': 'Such section does not exist'}), 404
        course = await api.db.get_course(course_id=section.course_id)
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get videos from this course'}), 403
        videos = [video.model_dump_json() for video in await api.db.get_videos(section_id=section_id)]
        return videos, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_video/<uuid:video_id>', methods=['GET'])
async def get_video(video_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get a video'}), 401
        video = await api.db.get_video(video_id=video_id)
        if video is None: return jsonify({'error': 'Video does not exist'}), 404
        section = await api.db.get_section(section_id=video.section_id)
        course = await api.db.get_course(course_id=section.course_id)
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get videos from this course'}), 403
        return video.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_video/<uuid:section_id>', methods=['POST'])
async def add_video(section_id):
    try:
        section = await api.db.get_section(section_id=section_id)
        if section is None: return jsonify({'error': 'Section does not exist'}), 404
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add videos'}), 401
        course = await api.db.get_course(course_id=section.course_id)
        if requester.user_id != course.author: return jsonify({'error': 'Not authorized to add videos to this course'}), 401
        if 'file' not in request.files: return jsonify({'error': 'No videos uploaded'}), 400
        file = request.files['file']
        if file.filename == '': return jsonify({'error': 'Empty file submitted'}), 400
        content = file.stream.read()
        video_hash = sha3_512(content).hexdigest()
        file.save('{}/videos/{}'.format(getenv('UPLOAD_FOLDER'), video_hash))
        video = Video(video_name=file.filename, section_id=section_id, video_hash=video_hash)
        added_video = await api.db.add_video(video)
        return added_video.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_video', methods=['PUT'])
async def update_video():
    post = request.get_json()
    try:
        video_to_update = await api.db.get_video(video_id=post.get("video_id"))
        if video_to_update is None: return jsonify({'error': 'Video does not exist'}), 401
        if session.get('id') != video_to_update.author: return jsonify({'error': 'Not authorized to update videos'}), 401
        for element in post: video_to_update.__setattr__(element, post[element])
        video_to_update = await api.db.update_video(video_to_update)
        return video_to_update.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_video/<uuid:video_id>', methods=['DELETE'])
async def delete_video(video_id):
    try:
        video_to_delete = await api.db.get_video(video_id=video_id)
        if video_to_delete is None: return jsonify({'error': 'Video does not exist'}), 404
        if session.get('id') != video_to_delete.video_id: return jsonify({'error': 'Not authorized to delete video'}), 401
        deleted_video = await api.db.delete_video(video_id)
        return deleted_video.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_attachments/<uuid:video_id>', methods=['GET'])
async def get_attachments(video_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get attachments'}), 401
        video = await api.db.get_video(video_id=video_id)
        if video is None: return jsonify({'error': 'Such video does not exist'}), 404
        section = await api.db.get_section(section_id=video.section_id)
        course = await api.db.get_course(course_id=section.course_id)
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get attachments from this course'}), 403
        attachments = [attachment.model_dump_json() for attachment in await api.db.get_attachments(video_id=video_id)]
        return attachments, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_attachment/<uuid:attachment_id>', methods=['GET'])
async def get_attachment(attachment_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get an attachment'}), 401
        attachment = await api.db.get_attachment(attachment_id=attachment_id)
        if attachment is None: return jsonify({'error': 'Such attachment does not exist'}), 404
        video = await api.db.get_video(video_id=attachment.video_id)
        section = await api.db.get_section(section_id=video.section_id)
        course = await api.db.get_course(course_id=section.course_id)
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get attachments from this course'}), 403
        return attachment.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_attachment/<uuid:video_id>', methods=['POST'])
async def add_attachment(video_id):
    try:
        video = await api.db.get_video(video_id=video_id)
        if video is None: return jsonify({'error': 'Video does not exist'}), 404
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add attachments'}), 401
        section = await api.db.get_section(section_id=video.section_id)
        course = await api.db.get_course(course_id=section.course_id)
        if requester.user_id != course.author: return jsonify({'error': 'Not authorized to add videos to this course'}), 401
        if 'file' not in request.files: return jsonify({'error': 'No files uploaded'}), 400
        file = request.files['file']
        if file.filename == '': return jsonify({'error': 'Empty file submitted'}), 400
        content = file.stream.read()
        size = len(content)
        file_hash = sha3_512(content).hexdigest()
        file.save('{}/attachments/{}'.format(getenv('UPLOAD_FOLDER'), file_hash))
        attachment = Attachment(file_name=file.filename, file_hash=file_hash, video_id=video_id, file_size=size)
        added_attachment = await api.db.add_attachment(attachment)
        return added_attachment.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_attachment', methods=['PUT'])
async def update_attachment():
    post = request.get_json()
    try:
        attachment_to_update = await api.db.get_attachment(attachment_id=post.get("attachment_id"))
        if attachment_to_update is None: return jsonify({'error': 'Attachment does not exist'}), 401
        if session.get('id') != attachment_to_update.author: return jsonify({'error': 'Not authorized to update attachments'}), 401
        for element in post: attachment_to_update.__setattr__(element, post[element])
        attachment_to_update = await api.db.update_attachment(attachment_to_update)
        return attachment_to_update.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_attachment/<uuid:attachment_id>', methods=['DELETE'])
async def delete_attachment(attachment_id):
    try:
        attachment_to_delete = await api.db.get_attachment(attachment_id=attachment_id)
        if attachment_to_delete is None: return jsonify({'error': 'Attachment does not exist'}), 404
        if session.get('id') != attachment_to_delete.attachment_id: return jsonify({'error': 'Not authorized to delete attachment'}), 401
        deleted_attachment = await api.db.delete_attachment(attachment_id)
        return deleted_attachment.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_feedbacks/<uuid:video_id>', methods=['GET'])
async def get_feedbacks(video_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get feedbacks'}), 401
        video = await api.db.get_video(video_id=video_id)
        if video is None: return jsonify({'error': 'Video does not exist'}), 404
        section = await api.db.get_section(section_id=video.section_id)
        course = await api.db.get_course(course_id=section.course_id)
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get feedbacks from this course'}), 403
        feedbacks = [feedback.model_dump_json() for feedback in await api.db.get_feedbacks(video_id=video_id)]
        return feedbacks, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_feedback/<uuid:feedback_id>', methods=['GET'])
async def get_feedback(feedback_id):
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get an feedback'}), 401
        feedback = await api.db.get_feedback(feedback_id=feedback_id)
        if feedback is None: return jsonify({'error': 'Such feedback does not exist'}), 404
        video = await api.db.get_video(video_id=feedback.video_id)
        section = await api.db.get_section(section_id=video.section_id)
        course = await api.db.get_course(course_id=section.course_id)
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get feedbacks from this course'}), 403
        return feedback.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_feedback', methods=['POST'])
async def add_feedback():
    post = request.get_json()
    try:
        requester = await api.db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add reviews'}), 401
        video = await api.db.get_course(post.get("video_id"))
        if video is None: return jsonify({'error': 'Video does not exist'}), 404
        section = await api.db.get_section(section_id=video.section_id)
        course = await api.db.get_course(course_id=section.course_id)
        is_added = await api.db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to add feedbacks to this courses'}), 401
        feedback = VideoFeedback(**post, author=requester.user_id)
        added_feedback = await api.db.add_feedback(feedback)
        return added_feedback.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_feedback', methods=['PUT'])
async def update_feedback():
    post = request.get_json()
    try:
        feedback_to_update = await api.db.get_feedback(feedback_id=post.get("feedback_id"))
        if feedback_to_update is None: return jsonify({'error': 'Feedback does not exist'}), 401
        if session.get('id') != feedback_to_update.author: return jsonify({'error': 'Not authorized to update feedbacks'}), 401
        for element in post: feedback_to_update.__setattr__(element, post[element])
        feedback_to_update = await api.db.update_feedback(feedback_to_update)
        return feedback_to_update.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_feedback/<uuid:feedback_id>', methods=['DELETE'])
async def delete_feedback(feedback_id):
    try:
        feedback_to_delete = await api.db.get_feedback(feedback_id=feedback_id)
        if feedback_to_delete is None: return jsonify({'error': 'Feedback does not exist'}), 404
        if session.get('id') != feedback_to_delete.feedback_id: return jsonify({'error': 'Not authorized to delete feedback'}), 401
        deleted_feedback = await api.db.delete_feedback(feedback_id)
        return deleted_feedback.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500
