from urllib.parse import quote
from catalogo.models import Producto


CART_SESSION_ID = 'carrito_la_creme'


class Carrito:
    """
    Gestor de carrito de compras basado en sesiones de Django.
    Permite operar a usuarios anónimos o autenticados.
    """

    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get(CART_SESSION_ID)
        if not carrito:
            carrito = self.session[CART_SESSION_ID] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1, override_cantidad=False):
        """
        Agrega o actualiza un producto en el carrito validando el stock.
        """
        producto_id = str(producto.id)
        cantidad_actual = self.carrito.get(producto_id, {}).get('cantidad', 0)

        if override_cantidad:
            nueva_cantidad = cantidad
        else:
            nueva_cantidad = cantidad_actual + cantidad

        # Validación de stock disponible
        if nueva_cantidad > producto.stock:
            nueva_cantidad = producto.stock

        if nueva_cantidad <= 0:
            self.eliminar(producto)
            return {
                'success': False,
                'mensaje': f'El producto {producto.nombre} no tiene stock disponible.',
                'cantidad': 0,
            }

        self.carrito[producto_id] = {
            'cantidad': nueva_cantidad,
            'precio': producto.precio_final,
        }
        self.guardar()

        return {
            'success': True,
            'mensaje': f'Se agregaron {nueva_cantidad} unidades de "{producto.nombre}" al carrito.',
            'cantidad': nueva_cantidad,
        }

    def eliminar(self, producto):
        """
        Elimina un producto del carrito.
        """
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()
            return True
        return False

    def vaciar(self):
        """
        Vacía todos los productos del carrito.
        """
        self.carrito.clear()
        self.session[CART_SESSION_ID] = {}
        self.guardar()

    def guardar(self):
        """
        Marca la sesión como modificada para que Django la guarde.
        """
        self.session.modified = True

    def __iter__(self):
        """
        Itera sobre los elementos del carrito y obtiene los objetos Producto de la base de datos.
        """
        producto_ids = self.carrito.keys()
        productos = Producto.objects.filter(id__in=producto_ids).select_related('categoria')
        productos_dict = {str(p.id): p for p in productos}

        # Clonar datos de sesión para no alterar el almacenamiento original
        carrito_copia = self.carrito.copy()

        for producto_id, item in carrito_copia.items():
            producto = productos_dict.get(producto_id)
            if not producto or not producto.activo:
                # Si el producto fue borrado o desactivado, limpiarlo
                self.carrito.pop(producto_id, None)
                self.guardar()
                continue

            item_data = item.copy()
            item_data['producto'] = producto
            item_data['precio'] = producto.precio_final
            item_data['subtotal'] = item_data['precio'] * item_data['cantidad']
            item_data['hay_stock'] = producto.stock >= item_data['cantidad']
            yield item_data

    def __len__(self):
        """
        Retorna la cantidad total de unidades en el carrito.
        """
        return sum(item['cantidad'] for item in self.carrito.values())

    def get_total_precio(self):
        """
        Calcula el total a pagar del carrito sumando subtotales actualizados.
        """
        total = 0
        for item in self:
            total += item['subtotal']
        return total

    def obtener_mensaje_whatsapp(self, configuracion_sitio=None):
        """
        Genera el texto formateado para el botón 'Pedir por WhatsApp'.
        """
        lineas = [
            "🍰 *¡Hola LA CREME! Me gustaría cotizar/hacer un pedido:*",
            ""
        ]
        total = 0
        for item in self:
            prod = item['producto']
            cant = item['cantidad']
            sub = item['subtotal']
            total += sub
            lineas.append(f"• *{cant}x* {prod.nombre} (${sub:,} CLP)")

        lineas.append("")
        lineas.append(f"💰 *Total estimado:* ${total:,} CLP")
        lineas.append("📍 ¿Podrían confirmarme disponibilidad y tiempos de entrega?")
        lineas.append("¡Muchas gracias!")

        texto = "\n".join(lineas)
        return quote(texto)
