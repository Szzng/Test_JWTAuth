from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker

from Factories.Userfactory import UserFactory


class RegisterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.UserModel = get_user_model()
        cls.faker = Faker()
        cls.testEmail = cls.faker.email()
        cls.testPassword = cls.faker.password()
        cls.registerUrl = "/api/accounts/register/"

    def test_register_사용자는_회원가입을_할_수_있다(self):
        response = self.client.post(
            self.registerUrl,
            {
                "email": self.testEmail,
                "password1": self.testPassword,
                "password2": self.testPassword,
            },
        )
        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.UserModel.objects.filter(email=self.testEmail).exists())

    def test_register_이메일은_중복될_수_없다(self):
        alreadyExistsEmail = self.faker.email()
        UserFactory(email=alreadyExistsEmail)
        self.assertTrue(
            self.UserModel.objects.filter(email=alreadyExistsEmail).exists()
        )

        response = self.client.post(
            self.registerUrl,
            {
                "email": alreadyExistsEmail,
                "password1": self.testPassword,
                "password2": self.testPassword,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_register_이메일은_형식을_지켜야_한다(self):
        notEmail = self.faker.name()

        response = self.client.post(
            self.registerUrl,
            {
                "email": notEmail,
                "password1": self.testPassword,
                "password2": self.testPassword,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_register_비밀번호는_8자_이상이어야_한다(self):
        less8Password = "7letter"

        response = self.client.post(
            self.registerUrl,
            {
                "email": self.testEmail,
                "password1": less8Password,
                "password2": less8Password,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.UserModel.objects.filter(email=self.testEmail).exists())

    def test_register_비밀번호_두_개는_서로_일치해야_한다(self):
        password1 = self.testPassword
        differentPassword = self.faker.password()

        response = self.client.post(
            self.registerUrl,
            {
                "email": self.testEmail,
                "password1": password1,
                "password2": differentPassword,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.UserModel.objects.filter(email=self.testEmail).exists())
