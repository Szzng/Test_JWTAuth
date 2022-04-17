from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker


class LoginTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.loginUrl = "/api/accounts/login/"

        cls.faker = Faker()
        cls.exactEmail = cls.faker.email()
        cls.exactPassword = cls.faker.password()

        cls.user = get_user_model().objects.create_user(
            email=cls.exactEmail, password=cls.exactPassword
        )

    def test_login_회원은_로그인을_할_수_있다(self):
        response = self.client.post(
            self.loginUrl, {"email": self.user.email, "password": self.exactPassword}
        )
        self.assertEqual(response.status_code, 200)

    def test_login_잘못된_정보로는_로그인을_할_수_없다(self):
        wrongEmail = self.faker.email()
        wrongPassword = self.faker.password()

        response1 = self.client.post(
            self.loginUrl, {"email": wrongEmail, "password": wrongPassword}
        )
        response2 = self.client.post(
            self.loginUrl, {"email": wrongEmail, "password": self.exactPassword}
        )
        response3 = self.client.post(
            self.loginUrl, {"email": self.exactEmail, "password": wrongPassword}
        )

        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response3.status_code, 400)

    def test_login_사용자_정보를_응답한다(self):
        response = self.client.post(
            self.loginUrl, {"email": self.user.email, "password": self.exactPassword}
        )

        self.assertDictEqual(
            response.data["user"],
            {
                "id": self.user.id,
                "email": self.user.email,
                "nickname": self.user.nickname,
                "is_active": self.user.is_active,
            },
        )

    def test_login_JWT_토큰_정보를_응답한다(self):
        response = self.client.post(
            self.loginUrl, {"email": self.user.email, "password": self.exactPassword}
        )

        self.assertContains(response, "access_token", count=2)
        self.assertContains(response, "refresh_token", count=2)
        self.assertContains(response, "expiration", count=2)
