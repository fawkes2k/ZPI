from asyncio import run
from src.model import User, Course, Review, Section, Video, Attachment, VideoFeedback
from src.service import DbService


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

    image = 'a'
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
    review1 = await db.add_review(review=Review(course_id=course3.course_id, author=user3.user_id))
    reviews = await db.get_reviews(course_id=course3.course_id)
    if review1 not in reviews: raise ValueError('4.1')
    review2 = await db.update_review(review=Review(review_id=review1.review_id, rating=rating, course_id=course3.course_id, author=user3.user_id))
    review3 = await db.get_review(review_id=review2.review_id)
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

    review4 = await db.delete_review(review_id=review3.review_id)
    review5 = await db.get_review(review_id=review4.review_id)
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
