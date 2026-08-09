import unittest

from app.app import create_app
from app.extensions.extensions import db
from app.models.wallet import Wallet


class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-only-secret-that-is-long-and-never-used-in-production",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def register_login(self, email="alice@example.com", username="alice1"):
        response = self.client.post("/users/register", json={"email": email, "username": username, "password": "correct horse battery staple"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/users/login", json={"email": email, "password": "correct horse battery staple"})
        self.refresh_token = response.json["refresh_token"]
        return {"Authorization": f"Bearer {response.json['access_token']}"}

    def test_auth_and_atomic_money_flow(self):
        self.assertEqual(self.client.get("/wallets/").status_code, 401)
        headers = self.register_login()
        wallet = self.client.post("/wallets/", json={"name": "Main", "currency": "eur", "balance": "999"}, headers=headers)
        self.assertEqual(wallet.status_code, 400)  # direct balance assignment is rejected
        wallet = self.client.post("/wallets/", json={"name": "Main", "currency": "eur"}, headers=headers)
        self.assertEqual(wallet.status_code, 201)
        wallet_id = wallet.json["data"]["id"]
        self.assertEqual(self.client.post(f"/transactions/wallets/{wallet_id}/deposit", json={"amount": "10.00"}, headers=headers).status_code, 404)
        # Represents funds imported by a trusted migration/payment integration, not an API user.
        with self.app.app_context():
            db.session.get(Wallet, wallet_id).balance = 10
            db.session.commit()
        self.assertEqual(self.client.post(f"/transactions/wallets/{wallet_id}/withdraw", json={"amount": "11.00"}, headers=headers).status_code, 400)
        current = self.client.get(f"/wallets/{wallet_id}", headers=headers)
        self.assertEqual(current.json["data"]["balance"], "10.00")

        self.assertEqual(self.client.delete(f"/wallets/{wallet_id}", headers=headers).status_code, 409)
        self.assertEqual(self.client.post(f"/transactions/wallets/{wallet_id}/withdraw", json={"amount": "10.00"}, headers=headers).status_code, 201)
        self.assertEqual(self.client.delete(f"/wallets/{wallet_id}", headers=headers).status_code, 204)
        self.assertEqual(self.client.get(f"/wallets/{wallet_id}", headers=headers).status_code, 404)

        history = self.client.get("/transactions/?page=1&per_page=1", headers=headers)
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.json["pagination"]["per_page"], 1)
        self.assertEqual(history.json["pagination"]["total"], 1)

    def test_refresh_and_logout_revoke_whole_session(self):
        headers = self.register_login()
        refresh_headers = {"Authorization": f"Bearer {self.refresh_token}"}
        refreshed = self.client.post("/users/refresh", headers=refresh_headers)
        self.assertEqual(refreshed.status_code, 200)
        refreshed_headers = {"Authorization": f"Bearer {refreshed.json['access_token']}"}
        self.assertEqual(self.client.post("/users/logout", headers=headers).status_code, 204)
        self.assertEqual(self.client.get("/users/me", headers=refreshed_headers).status_code, 401)
        self.assertEqual(self.client.post("/users/refresh", headers=refresh_headers).status_code, 401)

    def test_cannot_choose_admin_or_access_another_wallet(self):
        response = self.client.post("/users/register", json={"email": "a@example.com", "username": "user-a", "password": "long secure password", "role": "ADMIN"})
        self.assertEqual(response.status_code, 400)
        first = self.register_login("first@example.com", "first-user")
        wallet_id = self.client.post("/wallets/", json={"name": "Private"}, headers=first).json["data"]["id"]
        second = self.register_login("second@example.com", "second-user")
        self.assertEqual(self.client.get(f"/wallets/{wallet_id}", headers=second).status_code, 404)


if __name__ == "__main__":
    unittest.main()
