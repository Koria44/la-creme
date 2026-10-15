from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from catalogo.models import Categoria, Producto
from carrito.cart import Carrito


class CarritoTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.categoria = Categoria.objects.create(nombre="Tortas Test", slug="tortas-test")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Torta Prueba",
            slug="torta-prueba",
            descripcion_corta="Torta deliciosa para test",
            descripcion_larga="Descripción larga de prueba",
            precio=20000,
            precio_oferta=18000,
            stock=10,
            activo=True,
        )

    def _get_request_with_session(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_agregar_producto_al_carrito(self):
        request = self._get_request_with_session()
        carrito = Carrito(request)

        res = carrito.agregar(producto=self.producto, cantidad=2)
        self.assertTrue(res['success'])
        self.assertEqual(len(carrito), 2)
        # El precio unitario debe ser el precio_final (precio_oferta = 18000)
        self.assertEqual(carrito.get_total_precio(), 36000)

    def test_validacion_stock_maximo(self):
        request = self._get_request_with_session()
        carrito = Carrito(request)

        # Intentar agregar más del stock disponible (stock = 10)
        res = carrito.agregar(producto=self.producto, cantidad=15)
        self.assertTrue(res['success'])
        self.assertEqual(len(carrito), 10)  # Clamped al stock disponible

    def test_eliminar_y_vaciar_carrito(self):
        request = self._get_request_with_session()
        carrito = Carrito(request)

        carrito.agregar(producto=self.producto, cantidad=3)
        self.assertEqual(len(carrito), 3)

        carrito.eliminar(self.producto)
        self.assertEqual(len(carrito), 0)

        carrito.agregar(producto=self.producto, cantidad=2)
        carrito.vaciar()
        self.assertEqual(len(carrito), 0)
