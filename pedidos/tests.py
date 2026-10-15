from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from catalogo.models import Categoria, Producto
from pedidos.models import Pedido
from sitio.models import ConfiguracionSitio


class CheckoutTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.config = ConfiguracionSitio.get_solo()
        self.categoria = Categoria.objects.create(nombre="Kuchen Test", slug="kuchen-test")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Kuchen Manzana Test",
            slug="kuchen-manzana-test",
            descripcion_corta="Kuchen para test",
            descripcion_larga="Detalle kuchen test",
            precio=15000,
            stock=5,
            activo=True,
        )

    def test_checkout_crea_pedido_y_descuenta_stock(self):
        # 1. Agregar producto al carrito
        self.client.post(reverse('carrito:agregar', kwargs={'producto_id': self.producto.id}), {'cantidad': 2})

        # 2. Enviar formulario de checkout
        manana = timezone.localdate() + timezone.timedelta(days=1)
        post_data = {
            'nombre': 'Consuelo Valenzuela',
            'correo': 'consuelo@ejemplo.cl',
            'telefono': '+56 9 1122 3344',
            'tipo_entrega': 'retiro',
            'fecha_entrega': manana.strftime('%Y-%m-%d'),
            'hora_entrega': 'Tarde (14:00 - 18:00 hrs)',
            'metodo_pago': 'transferencia',
            'notas': 'Sin azúcar flor arriba por favor',
        }

        response = self.client.post(reverse('pedidos:checkout'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # 3. Verificar que el pedido existe en la base de datos
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.nombre, 'Consuelo Valenzuela')
        self.assertEqual(pedido.total, 30000)

        # 4. Verificar descuento de stock (5 - 2 = 3)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

        # 5. Verificar que el carrito quedó vacío
        session_cart = self.client.session.get('carrito_la_creme')
        self.assertEqual(session_cart, {})
