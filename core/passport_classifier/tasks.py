from celery import shared_task
from core.passport_classifier.utils import predict_passport_photo

@shared_task
def validate_passport_images_task(user_id, photo_with_face_path, front_path, back_path):
    from apps.users.models import User

    user = User.objects.get(id=user_id)

    face_ok = predict_passport_photo(photo_with_face_path, expected_type='face')
    front_ok = predict_passport_photo(front_path, expected_type='front')
    back_ok = predict_passport_photo(back_path, expected_type='back')

    if face_ok and front_ok and back_ok:
        user.is_verified = True
        user.save()
    else:
        user.delete()
