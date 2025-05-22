from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal

class AdCBVTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='User1', password='pass1')
        self.user2 = User.objects.create_user(username='User2', password='pass2')

        self.ad1 = Ad.objects.create(
            user=self.user1, title='Test1', description='Desc1',
            category='Техника', condition='new'
        )
        self.ad2 = Ad.objects.create(
            user=self.user2, title='Test2', description='Desc2',
            category='Техника', condition='used'
        )
        self.client = Client()

    def test_ad_list_view(self):
        response = self.client.get(reverse('ads:ad_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad1.title)
        self.assertContains(response, self.ad2.title)

    def test_ad_detail_view(self):
        response = self.client.get(reverse('ads:ad_detail', kwargs={'pk': self.ad1.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad1.title)
        self.assertContains(response, self.ad1.description)

    def test_ad_create_view_login_required(self):
        response = self.client.get(reverse('ads:ad_create'))

        self.assertEqual(response.status_code, 302)

    def test_ad_create(self):
        self.client.login(username='User1', password='pass1')

        response = self.client.post(reverse('ads:ad_create'), {
            'title': 'New ad', 'description': 'Some desc',
            'category': 'Техника', 'condition': 'new'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='New ad').exists())

    def test_ad_update_view_only_owner(self):
        self.client.login(username='User2', password='pass2')

        url = reverse('ads:ad_update', kwargs={'pk': self.ad1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_ad_update_owner(self):
        self.client.login(username='User1', password='pass1')

        url = reverse('ads:ad_update', kwargs={'pk': self.ad1.pk})
        response = self.client.post(url, {
            'title': 'Changed', 'description': 'Updated',
            'category': 'Техника', 'condition': 'new'
        })
        self.assertEqual(response.status_code, 302)
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, 'Changed')

    def test_ad_delete_only_owner(self):
        self.client.login(username='User2', password='pass2')

        url = reverse('ads:ad_delete', kwargs={'pk': self.ad1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_ad_delete_owner(self):
        self.client.login(username='User1', password='pass1')

        url = reverse('ads:ad_delete', kwargs={'pk': self.ad1.pk})
        response = self.client.post(url)

        self.assertRedirects(response, reverse('ads:ad_list'))
        self.assertFalse(Ad.objects.filter(pk=self.ad1.pk).exists())

class ExchangeProposalCBVTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='User1', password='pass1')
        self.user2 = User.objects.create_user(username='User2', password='pass2')

        self.ad1 = Ad.objects.create(user=self.user1, title='Ad1', description='Desc1',
                                     category='Техника',
                                     condition='new')

        self.ad2 = Ad.objects.create(user=self.user2, title='Ad2', description='Desc2',
                                     category='Техника',
                                     condition='new')

        self.client = Client()

    def test_create_exchange_proposal(self):
        self.client.login(username='User1', password='pass1')

        url = reverse('ads:exchangeproposal_create', kwargs={'ad_receiver_pk': self.ad2.pk})
        data = {
            'ad_sender': self.ad1.pk,
            'comment': 'Обмен?',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExchangeProposal.objects.filter(ad_sender=self.ad1, ad_receiver=self.ad2).exists())

    def test_accept_proposal_only_receiver(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, status='pending')
        self.client.login(username='User1', password='pass1')

        url = reverse('ads:exchangeproposal_accept', kwargs={'pk': proposal.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.client.login(username='User2', password='pass2')

        response = self.client.post(url)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')

    def test_decline_proposal(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, status='pending')
        self.client.login(username='User2', password='pass2')

        url = reverse('ads:exchangeproposal_decline', kwargs={'pk': proposal.pk})
        response = self.client.post(url)

        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'declined')

class SignupCBVTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_view(self):
        url = reverse('ads:signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {
            'username': 'testuser',
            'password1': 'abc12345def',
            'password2': 'abc12345def',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())
