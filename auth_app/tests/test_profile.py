from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from auth_app.api.serializers import ProfileSerializer
from auth_app.models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

# class ProfileHappyPathTests(APITestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create_user(
#             username='testuser',
#             email='testuser@example.com',
#             password='testpassword'
#         )
#         cls.other_user = User.objects.create_user(
#             username='otheruser',
#             email='otheruser@example.com',
#             password='otherpassword'
#         )
#         cls.user_profile = Profile.objects.create(user=cls.user, type='customer')
#         cls.other_profile = Profile.objects.create(user=cls.other_user, type='business')

#     def setUp(self):
#         self.client.force_authenticate(user=self.user)

#     def test_get_own_profile(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})

#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, ProfileSerializer(self.user_profile).data)

#     def test_get_other_profile(self):
#         url = reverse('profile-detail', kwargs={'pk': self.other_profile.id})

#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, ProfileSerializer(self.other_profile).data)

#     def test_get_profile_fields_empty(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})

#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['first_name'], '')
#         self.assertEqual(response.data['last_name'], '')
#         self.assertEqual(response.data['location'], '')
#         self.assertEqual(response.data['tel'], '')
#         self.assertEqual(response.data['description'], '')
#         self.assertEqual(response.data['working_hours'], '')

#     def test_update_profile_by_user(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {
#             'first_name': 'updatedfirstname',
#             'last_name': 'updatedlastname',
#             'location': 'updated location',
#             'tel': '1234567890',
#             'description': 'This is a updated test user.',
#             'working_hours': '9-5',
#             'email': 'updated.email@example.com'
#         }

#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user.refresh_from_db()
#         self.assertEqual(self.user.first_name, 'updatedfirstname')
#         self.assertEqual(self.user.last_name, 'updatedlastname')
#         self.assertEqual(self.user.email, 'updated.email@example.com')

#         self.user_profile.refresh_from_db()
#         self.assertEqual(self.user_profile.location, 'updated location')
#         self.assertEqual(self.user_profile.tel, '1234567890')
#         self.assertEqual(self.user_profile.description, 'This is a updated test user.')
#         self.assertEqual(self.user_profile.working_hours, '9-5')

#     def test_partial_update_preserves_other_fields(self):
#         self.user_profile.tel = "555"
#         self.user_profile.description = "orig"
#         self.user_profile.working_hours = "8-16"
#         self.user_profile.save()

#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {
#             'location': 'only this field changes'
#         }

#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user_profile.refresh_from_db()
#         self.assertEqual(self.user_profile.location, 'only this field changes')
#         self.assertEqual(self.user_profile.tel, '555')
#         self.assertEqual(self.user_profile.description, 'orig')
#         self.assertEqual(self.user_profile.working_hours, '8-16')

#     def test_update_profile_response_schema_after_patch(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {
#             'description': 'updated desc',
#         }
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.assertEqual(response.data['description'], 'updated desc')
#         self.assertIn('tel', response.data)
#         self.assertEqual(response.data['tel'], "")

#     def test_update_profile_same_email_ok(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {'email': self.user.email}
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user.refresh_from_db()
#         self.assertEqual(self.user.email, self.user.email)

#     def test_get_business_profiles(self):
#         url = reverse('profile-business-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['type'], 'business')
#         self.assertNotIn('email', response.data[0])

#     def test_get_customer_profiles(self):
#         url = reverse('profile-customer-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['type'], 'customer')
#         self.assertNotIn('email', response.data[0])
#         self.assertNotIn('location', response.data[0])
#         self.assertNotIn('tel', response.data[0])
#         self.assertNotIn('description', response.data[0])
#         self.assertNotIn('working_hours', response.data[0])

#     def test_upload_file_sets_uploaded_at(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         upload = SimpleUploadedFile("avatar.jpg", b"file_content", content_type="image/jpeg")

#         response = self.client.patch(url, {'file': upload}, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user_profile.refresh_from_db()
#         self.assertTrue(self.user_profile.file.name.startswith("profile/"))
#         self.assertTrue(self.user_profile.file.name.lower().endswith(".jpg"))
#         self.assertIn("avatar", self.user_profile.file.name.lower())

#     def test_patch_without_file_keeps_uploaded_at(self):
#         self.user_profile.file = SimpleUploadedFile("old.jpg", b"abc", content_type="image/jpeg")
#         self.user_profile.uploaded_at = timezone.now()
#         self.user_profile.save()
#         before = self.user_profile.uploaded_at

#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         response = self.client.patch(url, {'description': 'no file changed'})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user_profile.refresh_from_db()
#         self.assertEqual(self.user_profile.description, 'no file changed')
#         self.assertEqual(self.user_profile.uploaded_at, before)

#     def test_reupload_file_updates_uploaded_at(self):
#         first_upload = SimpleUploadedFile("first.jpg", b"aaa", content_type="image/jpeg")
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         self.client.patch(url, {'file': first_upload}, format='multipart')
#         self.user_profile.refresh_from_db()
#         first_time = self.user_profile.uploaded_at
#         first_name = self.user_profile.file.name

#         second_upload = SimpleUploadedFile("second.jpg", b"bbb", content_type="image/jpeg")
#         response = self.client.patch(url, {'file': second_upload}, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user_profile.refresh_from_db()
#         self.assertNotEqual(self.user_profile.file.name, first_name)
#         self.assertTrue(self.user_profile.file.name.startswith("profile/"))
#         self.assertTrue(self.user_profile.file.name.lower().endswith(".jpg"))
#         self.assertIn("second", self.user_profile.file.name.lower())
#         self.assertGreater(self.user_profile.uploaded_at, first_time)

#     def test_delete_file_sets_uploaded_at_none(self):
#         self.user_profile.file = SimpleUploadedFile("deleteme.jpg", b"abc", content_type="image/jpeg")
#         self.user_profile.uploaded_at = timezone.now()
#         self.user_profile.save()

#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         response = self.client.patch(url, {'file': ''}, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user_profile.refresh_from_db()
#         self.assertFalse(bool(self.user_profile.file))
#         self.assertIsNone(self.user_profile.uploaded_at)


# class ProfileValidationTests(APITestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create_user(
#             username='testuser',
#             email='testuser@example.com',
#             password='testpassword'
#         )
#         cls.user_profile = Profile.objects.create(user=cls.user, type='customer')

#     def setUp(self):
#         self.client.force_authenticate(user=self.user)

#     def test_get_unknown_profile(self):
#         url = reverse('profile-detail', kwargs={'pk': 999})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_update_unknown_profile(self):
#         url = reverse('profile-detail', kwargs={'pk': 999})
#         response = self.client.patch(url, data={'first_name': 'updatedfirstname'})
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_update_profile_invalid_email(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {
#             'email': 'testuserexample.com'
#         }

#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("email", response.data)

#     def test_update_profile_duplicate_email(self):
#         other_user = User.objects.create_user(
#             username='otheruser',
#             email='otheruser@example.com',
#             password='testpassword'
#         )
#         other_user_profile = Profile.objects.create(user=other_user, type='customer')

#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {
#             'email': 'otheruser@example.com'
#         }

#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("email", response.data)
    
#     def test_update_ignores_readonly_fields_keeps_values(self):
#         original_type = self.user_profile.type
#         original_created_at = self.user_profile.created_at
#         original_username = self.user.username
#         original_user_id = self.user.id

#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {
#             'type': 'business',
#             'created_at': '2023-01-01T00:00:00',
#             'username': 'hacker',
#         }
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         self.user_profile.refresh_from_db()
#         self.user.refresh_from_db()
#         self.assertEqual(self.user_profile.type, original_type)
#         self.assertEqual(self.user_profile.created_at, original_created_at)
#         self.assertEqual(self.user.username, original_username)
#         self.assertEqual(self.user.id, original_user_id)

#     def test_update_profile_duplicate_email_case_insensitive(self):
#         other = User.objects.create_user(
#             username='dupuser',
#             email='OtherUser@Example.com',
#             password='pw'
#         )
#         Profile.objects.create(user=other, type='customer')

#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         data = {'email': 'otheruser@example.com'}

#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('email', response.data)


# class ProfilePermissionTests(APITestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create_user(
#             username='testuser',
#             email='testuser@example.com',
#             password='testpassword'
#         )
#         cls.user_profile = Profile.objects.create(user=cls.user, type='customer')

#     def test_unauthenticated_user_get_profile(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_unauthenticated_user_update_profile(self):
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         response = self.client.patch(url, data={'first_name': 'updatedfirstname'})
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_no_owner_update_profile(self):
#         other_user = User.objects.create_user(
#             username='otheruser',
#             email='otheruser@example.com',
#             password='testpassword'
#         )
#         other_user_profile = Profile.objects.create(user=other_user, type='customer')
#         self.client.force_authenticate(user=other_user)
#         url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
#         response = self.client.patch(url, data={'first_name': 'hacker'})
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_unauthenticated_user_get_business_profile(self):
#         url = reverse('profile-business-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_unauthenticated_user_get_customer_profile(self):
#         url = reverse('profile-customer-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
