from base64 import b64decode
from flask import Blueprint, request, session, jsonify
from src.DBService.service import DbService, getenv
from src.model import randbytes, datetime, User, ViewableUser, Course, Review
from hashlib import sha3_512

api = Blueprint('api', __name__)
started = datetime.now()


@api.route('/health', methods=['GET'])
async def health():
    return jsonify({'uptime': str(datetime.now() - started)}), 200


@api.route('/get_users', methods=['GET'])
async def get_users():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get users'}), 401
        users = [ViewableUser(**user.model_dump()).model_dump_json() for user in await db.get_users(**post)]
        return users, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_user/<uuid:user_id>', methods=['GET'])
async def get_user(user_id):
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get user'}), 401
        user = await db.get_user(user_id)
        viewable_user = ViewableUser(**user.model_dump()).model_dump_json()
        return viewable_user, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/login', methods=['POST'])
async def login():
    post = request.get_json()
    pepper = getenv('PEPPER').encode()
    try:
        db = DbService()
        await db.initialize()
        user = await db.get_user(email=post.get('email'))
        password = post.get('password')
        requester = await db.get_user(user_id=session.get('id'))
        if requester is not None: return jsonify({'error': 'Already logged in'}), 400
        if password is None or not isinstance(password, str): return jsonify({'error': 'Incorrect password format'}), 400
        if user is None: return jsonify({'error': 'User not found'}), 401
        if sha3_512(pepper + password.encode() + user.salt).hexdigest() != user.hashed_password: return jsonify({'error': 'Incorrect password'}), 403
        session['id'] = user.user_id
        return jsonify({'message': 'Logged in'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/logout', methods=['POST'])
async def logout():
    db = DbService()
    await db.initialize()
    requester = await db.get_user(user_id=session.get('id'))
    if requester is None: return jsonify({'error': 'Not logged in'}), 401
    session['id'] = None
    return jsonify({'message': 'Logged out'}), 200


@api.route('/add_user', methods=['POST'])
async def add_user():
    post = request.get_json()
    pepper = getenv('PEPPER').encode()
    salt = randbytes(256)
    try:
        db = DbService()
        await db.initialize()
        password = post.get('password')
        users_with_email = await db.get_user(email=post.get('email'))
        if password is None or not isinstance(password, str): return jsonify({'error': 'Incorrect password format'}), 400
        if users_with_email is not None: return jsonify({'error': 'User already exist'}), 401
        hashed_password = sha3_512(pepper + password.encode() + salt).hexdigest()
        user = User(last_name=post.get('last_name'), first_name=post.get('first_name'), email=post.get('email'), hashed_password=hashed_password, salt=salt)
        new_user = await db.add_user(user)
        viewable_user = ViewableUser(**new_user.model_dump()).model_dump_json()
        return viewable_user, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_user', methods=['PUT'])
async def update_user():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        user_to_update = await db.get_user(user_id=post.get('user_id'))
        if user_to_update is None: return jsonify({'error': 'User does not exist'}), 401
        if session.get('id') != user_to_update.user_id: return jsonify({'error': 'Not authorized to update user'}), 401
        for element in post: user_to_update.__setattr__(element, post[element])
        updated_user = await db.update_user(user_to_update)
        viewable_user = ViewableUser(**updated_user.model_dump()).model_dump_json()
        return viewable_user, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_user/<uuid:user_id>', methods=['DELETE'])
async def delete_user(user_id):
    try:
        db = DbService()
        await db.initialize()
        user_to_delete = await db.get_user(user_id=user_id)
        if user_to_delete is None: return jsonify({'error': 'User does not exist'}), 404
        if session.get('id') != user_to_delete.user_id: return jsonify({'error': 'Not authorized to delete users'}), 401
        deleted_user = await db.delete_user(user_id)
        session['id'] = None
        viewable_user = ViewableUser(**deleted_user.model_dump()).model_dump_json()
        return viewable_user, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_courses', methods=['GET'])
async def get_courses():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get courses'}), 401
        courses = [course.model_dump_json() for course in await db.get_courses(**post)]
        return courses, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_course/<uuid:course_id>', methods=['GET'])
async def get_course(course_id):
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get a course'}), 401
        course = await db.get_course(course_id)
        return course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_course', methods=['POST'])
async def add_course():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        image = b64decode(post.get("image"))
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add courses'}), 401
        course = Course(**post, image=image, author=requester.user_id)
        added_course = await db.add_course(course)
        return added_course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_course/<uuid:course_id>', methods=['DELETE'])
async def delete_course(course_id):
    try:
        db = DbService()
        await db.initialize()
        course_to_delete = await db.get_course(course_id=course_id)
        if course_to_delete is None: return jsonify({'error': 'Course does not exist'}), 404
        if session.get('id') != course_to_delete.author: return jsonify({'error': 'Not authorized to delete courses'}), 401
        deleted_course = await db.delete_course(course_id)
        return deleted_course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_course', methods=['PUT'])
async def update_course():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        course_to_update = await db.get_course(course_id=post.get("course_id"))
        if course_to_update is None: return jsonify({'error': 'Course does not exist'}), 401
        if session.get('id') != course_to_update.author: return jsonify({'error': 'Not authorized to update courses'}), 401
        for element in post:
            if element == "image": course_to_update.image = b64decode(post[element])
            else: course_to_update.__setattr__(element, post[element])
        updated_course = await db.update_course(course_to_update)
        return updated_course.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_user_to_course', methods=['POST'])
async def add_user_to_course():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add users to courses'}), 401
        course = await db.get_course(post.get("course_id"))
        if course is None: return jsonify({'error': 'Course does not exist'}), 404
        is_added = await db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if is_added: return jsonify({'error': 'User already added to the course'}), 403
        added_uc = await db.add_user_to_course(user_id=requester.user_id, course_id=course.course_id)
        return added_uc.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/remove_user_from_course', methods=['POST'])
async def remove_user_from_course():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        course = await db.get_course(post.get("course_id"))
        if course is None: return jsonify({'error': 'Course does not exist'}), 404
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add users to courses'}), 401
        is_added = await db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'User is not added to the course'}), 403
        removed_uc = await db.remove_user_from_course(user_id=requester.user_id, course_id=course.course_id)
        return removed_uc.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_reviews', methods=['GET'])
async def get_reviews():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get reviews'}), 401
        reviews = [review.model_dump_json() for review in await db.get_reviews(**post)]
        return reviews, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_review/<uuid:review_id>', methods=['GET'])
async def get_review(review_id):
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get a review'}), 401
        review = await db.get_review(review_id)
        return review.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/add_review', methods=['POST'])
async def add_review():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        course = await db.get_course(post.get("course_id"))
        if course is None: return jsonify({'error': 'Course does not exist'}), 404
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to add reviews'}), 401
        is_added = await db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to add reviews to this courses'}), 401
        did_review = await db.did_user_review_this_course(user_id=requester.user_id, course_id=course.course_id)
        if did_review: return jsonify({'error': 'User already reviewed this course'}), 401
        review = Review(**post, author=requester.user_id)
        added_review = await db.add_review(review)
        return added_review.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/update_review', methods=['PUT'])
async def update_review():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        review_to_update = await db.get_review(review_id=post.get("review_id"))
        if review_to_update is None: return jsonify({'error': 'Review does not exist'}), 401
        if session.get('id') != review_to_update.author: return jsonify({'error': 'Not authorized to update reviews'}), 401
        for element in post: review_to_update.__setattr__(element, post[element])
        review_to_update = await db.update_review(review_to_update)
        return review_to_update.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/delete_review/<uuid:review_id>', methods=['DELETE'])
async def delete_review(review_id):
    try:
        db = DbService()
        await db.initialize()
        review_to_delete = await db.get_review(review_id=review_id)
        if review_to_delete is None: return jsonify({'error': 'Review does not exist'}), 404
        if session.get('id') != review_to_delete.review_id: return jsonify({'error': 'Not authorized to delete review'}), 401
        deleted_review = await db.delete_review(review_id)
        return deleted_review.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_sections', methods=['GET'])
async def get_sections():
    post = request.get_json()
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get sections'}), 401
        course = await db.get_course(course_id=session.get('course_id'))
        if course is None: return jsonify({'error': 'Such course does not exist'}), 404
        is_added = await db.is_user_assigned_to_course(user_id=requester.user_id, course_id=course.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get sections from this course'}), 403
        sections = [section.model_dump_json() for section in await db.get_sections(**post)]
        return sections, 200
    except Exception as e: return jsonify({'error': str(e)}), 500


@api.route('/get_section/<uuid:section_id>', methods=['GET'])
async def get_section(section_id):
    try:
        db = DbService()
        await db.initialize()
        requester = await db.get_user(user_id=session.get('id'))
        if requester is None: return jsonify({'error': 'Not authorized to get a section'}), 401
        section = await db.get_section(section_id)
        if section is None: return jsonify({'error': 'Section not found'}), 404
        is_added = await db.is_user_assigned_to_course(user_id=requester.user_id, course_id=section.course_id)
        if not is_added: return jsonify({'error': 'Not authorized to get sections from this course'}), 403
        return section.model_dump_json(), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

