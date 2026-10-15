from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalogo.models import Categoria, Producto


class PanelPermisosTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre="Tortas Panel", slug="tortas-panel")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Torta Stock",
            slug="torta-stock",
            descripcion_corta="Corta",
            descripcion_larga="Larga",
            precio=10000,
            stock=10,
            activo=True,
        )

        # Usuario normal (no staff)
        self.user_cliente = User.objects.create_user('cliente_test', 'cli@test.cl', 'pass1234')

        # Usuario staff
        self.user_staff = User.objects.create_user('staff_test', 'staff@test.cl', 'pass1234', is_staff=True)

    def test_usuario_anonimo_redireccionado(self):
        response = self.client.get(reverse('panel:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('cuentas/ingresar', response.url)

    def test_usuario_cliente_no_staff_bloqueado(self):
        self.client.login(username='cliente_test', password='pass1234')
        response = self.client.get(reverse('panel:dashboard'))
        # staff_member_required redirige a login si no es staff
        self.assertEqual(response.status_code, 302)

    def test_usuario_staff_accede_al_dashboard(self):
        self.client.login(username='staff_test', password='pass1234')
        response = self.client.get(reverse('panel:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard de Gestión')

    def test_ajuste_rapido_de_stock(self):
        self.client.login(username='staff_test', password='pass1234')
        response = self.client.post(
            reverse('panel:stock_ajuste_rapido'),
            {'producto_id': self.producto.id, 'stock': 25},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 25)
