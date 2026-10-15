import os
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

from catalogo.models import Categoria, Producto
from cuentas.models import Perfil
from pedidos.models import Pedido, ItemPedido
from sitio.models import ConfiguracionSitio, MensajeContacto


def generar_imagen_pasteleria(ruta_archivo, titulo, subtitulo, color_fondo, color_texto=(255, 255, 255)):
    """
    Genera una imagen artística con Pillow para productos y categorías
    utilizando una paleta cálida de pastelería artesanal.
    """
    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
    ancho, alto = 800, 600
    img = Image.new('RGB', (ancho, alto), color=color_fondo)
    draw = ImageDraw.Draw(img)

    # Dibujar marcos decorativos y detalles suaves
    draw.rectangle([(20, 20), (ancho - 20, alto - 20)], outline=(255, 255, 255, 120), width=3)
    draw.rectangle([(30, 30), (ancho - 30, alto - 30)], outline=(255, 248, 240, 80), width=1)

    # Círculo decorativo central
    cx, cy = ancho // 2, alto // 2 - 40
    r = 130
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 40), outline=(217, 164, 65), width=4)

    # Icono / Emblema de pastelería simplificado
    draw.ellipse([cx - 40, cy - 30, cx + 40, cy + 30], fill=(217, 164, 65, 180))
    draw.rectangle([cx - 50, cy, cx + 50, cy + 45], fill=(255, 248, 240))

    # Textos
    try:
        # Intenta usar fuente estándar o truetype del sistema si estuviera disponible
        font_titulo = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    except Exception:
        font_titulo = None
        font_sub = None

    # Textos simples centrados
    banner_texto = f"LA CREME • {titulo.upper()}"
    draw.text((ancho // 2 - (len(banner_texto) * 3), alto // 2 + 110), banner_texto, fill=color_texto)
    sub_texto = f"{subtitulo}"
    draw.text((ancho // 2 - (len(sub_texto) * 3), alto // 2 + 140), sub_texto, fill=(230, 230, 230))
    sello = "Pastelería Artesanal Chilena • Calidad Premium"
    draw.text((ancho // 2 - (len(sello) * 3), alto - 60), sello, fill=(217, 164, 65))

    img.save(ruta_archivo, 'JPEG', quality=88)


class Command(BaseCommand):
    help = "Carga datos de demostración completos para la pastelería LA CREME"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando carga de datos demo para LA CREME..."))

        # 1. Configuración del sitio (Singleton con Placeholders transparentes)
        config, created = ConfiguracionSitio.objects.get_or_create(id=1)
        config.nombre = "LA CREME Pastelería"
        config.eslogan = "Pastelería artesanal hecha con amor, tradición y los mejores ingredientes."
        config.direccion = "Av. Providencia 1234, Local 5 (PLACEHOLDER EDITABLE)"
        config.comuna = "Providencia"
        config.ciudad = "Santiago"
        config.telefono = "+56 9 8765 4321"
        config.whatsapp = "+56987654321"
        config.correo = "contacto@pastelerialacreme.cl"
        config.horarios = "Lunes a Sábado: 09:30 a 20:00 hrs.\nDomingos y festivos: 10:00 a 18:00 hrs."
        config.instagram = "https://www.instagram.com/pasteleria_la_creme/"
        config.facebook = "https://facebook.com/pasteleria_la_creme"
        config.latitud = -33.428500
        config.longitud = -70.612300
        config.costo_despacho_base = 3990
        config.despacho_gratis_desde = 45000
        config.save()
        self.stdout.write(self.style.SUCCESS("[OK] Configuración del sitio lista."))

        # 2. Superusuario demo
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@pastelerialacreme.cl', 'admin12345')
            admin_user.first_name = "Administrador"
            admin_user.last_name = "LA CREME"
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Superusuario creado: admin / admin12345"))
        else:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin12345')
            admin_user.save()
            self.stdout.write("[OK] Superusuario existente actualizado: admin / admin12345")

        # 3. Cliente demo
        cliente_user, c_created = User.objects.get_or_create(
            username='cliente',
            defaults={
                'email': 'valentina.rojas@ejemplo.cl',
                'first_name': 'Valentina',
                'last_name': 'Rojas',
            }
        )
        cliente_user.set_password('cliente12345')
        cliente_user.save()
        perfil, _ = Perfil.objects.get_or_create(usuario=cliente_user)
        perfil.telefono = "+56 9 9123 4567"
        perfil.direccion = "Av. Pedro de Valdivia 980, Depto 402"
        perfil.comuna = "Providencia"
        perfil.region = "Región Metropolitana"
        perfil.save()
        self.stdout.write(self.style.SUCCESS("[OK] Cliente demo creado: cliente / cliente12345"))

        # 4. Categorías
        categorias_datos = [
            {
                'nombre': 'Tortas',
                'descripcion': 'Nuestras emblemáticas tortas artesanales elaboradas con bizcochos húmedos, cremas suaves y manjar casero.',
                'orden': 1,
                'color': (74, 44, 42),  # Chocolate
            },
            {
                'nombre': 'Pasteles individuales',
                'descripcion': 'Porciones individuales perfectas para acompañar tu café o darte un gusto dulce de alta pastelería en cualquier momento.',
                'orden': 2,
                'color': (184, 58, 92),  # Frambuesa
            },
            {
                'nombre': 'Cheesecakes',
                'descripcion': 'Cheesecakes horneados estilo New York y versiones frías con coulis frescos de frutos del sur chileno.',
                'orden': 3,
                'color': (217, 164, 65),  # Dorado suave
            },
            {
                'nombre': 'Kuchen',
                'descripcion': 'Recetas tradicionales de kuchenes del sur, con masa crujiente de mantequilla y fruta fresca seleccionada.',
                'orden': 4,
                'color': (143, 191, 168),  # Menta
            },
            {
                'nombre': 'Cupcakes',
                'descripcion': 'Deliciosos mini pasteles esponjosos con decoraciones artesanales y suaves frostings de queso crema o chocolate.',
                'orden': 5,
                'color': (184, 58, 92),
            },
            {
                'nombre': 'Galletas y alfajores',
                'descripcion': 'Alfajores de maicena rellenos con abundante manjar de campo y galletas finas horneadas a diario.',
                'orden': 6,
                'color': (110, 68, 48),
            },
            {
                'nombre': 'Tortas personalizadas',
                'descripcion': 'Diseños únicos y temáticos para cumpleaños, matrimonios, aniversarios y fechas especiales.',
                'orden': 7,
                'color': (74, 44, 42),
            },
        ]

        categorias_dict = {}
        for cat_info in categorias_datos:
            slug = slugify(cat_info['nombre'])
            cat, _ = Categoria.objects.get_or_create(
                nombre=cat_info['nombre'],
                defaults={
                    'slug': slug,
                    'descripcion': cat_info['descripcion'],
                    'orden': cat_info['orden'],
                    'activa': True,
                }
            )
            cat.descripcion = cat_info['descripcion']
            cat.orden = cat_info['orden']
            cat.activa = True

            # Generar imagen si no existe
            rel_path = f"categorias/{slug}.jpg"
            abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            if not os.path.exists(abs_path):
                generar_imagen_pasteleria(
                    abs_path,
                    cat.nombre,
                    "Colección Exclusiva",
                    color_fondo=cat_info['color']
                )
            cat.imagen = rel_path
            cat.save()
            categorias_dict[cat.nombre] = cat

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(categorias_dict)} categorías creadas/actualizadas con imágenes."))

        # 5. Productos (mínimo 18 productos reales y bien redactados)
        productos_datos = [
            # TORTAS
            {
                'categoria': 'Tortas',
                'nombre': 'Torta Tres Leches Tradicional',
                'desc_corta': 'Bizcochuelo esponjoso empapado en nuestra mezcla secreta de tres leches, relleno con manjar de campo y merengue tostado.',
                'desc_larga': 'Nuestra versión clásica de la tradicional torta tres leches chilena. Elaborada con un bizcochuelo liviano que absorbe a la perfección la infusión de leche evaporada, leche condensada y crema de leche natural. Lleva una generosa capa intermedia de manjar artesanal de campo y está coronada con un suave merengue italiano flameado al momento. Ideal para disfrutar bien fría.',
                'precio': 24900,
                'precio_oferta': 21990,
                'stock': 12,
                'destacado': True,
                'porciones': '15 a 18 porciones (22 cm)',
                'prep': '24 horas de anticipación',
                'color': (217, 164, 65),
            },
            {
                'categoria': 'Tortas',
                'nombre': 'Torta Selva Negra Gourmet',
                'desc_corta': 'Capas de bizcocho húmedo de cacao belga, crema chantilly fresca, guindas ácidas confitadas y virutas de chocolate amargo.',
                'desc_larga': 'Inspirada en la clásica receta europea con un toque contemporáneo. Bizcocho extra húmedo de cacao belga al 70%, embebido suavemente en licor de guindas, relleno de capas alternadas de crema chantilly fresca batida con vainilla natural de Madagascar y guindas maceradas. Cubierta con abundante lluvia de virutas de chocolate negro y cerezas al marrasquino.',
                'precio': 26900,
                'precio_oferta': None,
                'stock': 8,
                'destacado': True,
                'porciones': '16 a 20 porciones (24 cm)',
                'prep': '24 horas de anticipación',
                'color': (74, 44, 42),
            },
            {
                'categoria': 'Tortas',
                'nombre': 'Torta Amor Hojarasca Frambuesa',
                'desc_corta': 'Finas y crocantes hojas artesanales rellenas de manjar casero, crema pastelera y mermelada natural de frambuesas silvestres.',
                'desc_larga': 'La reina de la pastelería tradicional chilena. Finísimas capas de masa hojarasca horneadas artesanalmente hasta obtener una textura perfectamente crocante, intercaladas con abundante manjar de leche de campo, crema pastelera cocinada a fuego lento y compota casera de frambuesas cosechadas en el sur de Chile que aportan el equilibrio cítrico ideal.',
                'precio': 27500,
                'precio_oferta': 24900,
                'stock': 3,  # Stock bajo para demo
                'destacado': True,
                'porciones': '18 a 22 porciones (24 cm)',
                'prep': '48 horas de anticipación',
                'color': (184, 58, 92),
            },
            {
                'categoria': 'Tortas',
                'nombre': 'Torta Mousse Maracuyá y Chocolate Blanco',
                'desc_corta': 'Suave mousse de pulpa natural de maracuyá sobre una base de galletas crujientes y ganache sedoso de chocolate blanco.',
                'desc_larga': 'Una experiencia refrescante y sofisticada. Suave mousse aireado de maracuyá natural, equilibrado con la dulzura cremosa del chocolate blanco de primera calidad. Base crocante de galletas de mantequilla y terminado con un glaseado brillante con semillas de maracuyá.',
                'precio': 25900,
                'precio_oferta': None,
                'stock': 6,
                'destacado': False,
                'porciones': '14 a 16 porciones (20 cm)',
                'prep': '24 horas de anticipación',
                'color': (217, 164, 65),
            },
            {
                'categoria': 'Tortas',
                'nombre': 'Torta Panqueque Naranja Manjar',
                'desc_corta': 'Capas milimétricas de masa suave de panqueque rellenas de manjar y crema artesanal de naranja recién exprimida.',
                'desc_larga': 'Un clásico inolvidable. Delgadas láminas de suave masa de panqueque cocidas una a una, rellenas alternadamente con manjar tradicional chileno y una delicada trufa de naranja natural elaborada con zeste fresco. Cubierta con un fino fondant o ganache de chocolate a elección.',
                'precio': 28900,
                'precio_oferta': None,
                'stock': 0,  # Agotado para demo
                'destacado': False,
                'porciones': '20 porciones (24 cm)',
                'prep': '48 horas de anticipación',
                'color': (217, 164, 65),
            },

            # CHEESECAKES
            {
                'categoria': 'Cheesecakes',
                'nombre': 'Cheesecake Horneado Frutos Rojos',
                'desc_corta': 'Cheesecake horneado a baja temperatura con queso crema Philadelphia, sobre base crocante y coulis de frutos del bosque.',
                'desc_larga': 'Elaborado siguiendo la receta tradicional neoyorquina horneada lentamente al baño María para lograr una textura aterciopelada inigualable. Base crocante de masa sablé de almendras y canela, bañado generosamente con un coulis artesanal de moras, arándanos y frambuesas frescas.',
                'precio': 22900,
                'precio_oferta': 19990,
                'stock': 9,
                'destacado': True,
                'porciones': '12 a 14 porciones (22 cm)',
                'prep': '24 horas de anticipación',
                'color': (184, 58, 92),
            },
            {
                'categoria': 'Cheesecakes',
                'nombre': 'Cheesecake Frío Maracuyá',
                'desc_corta': 'Cremoso cheesecake frío sin horno con queso mascarpone, base de galletas de avena y espejo de maracuyá silvestre.',
                'desc_larga': 'Cheesecake ultra liviano y fresco, preparado con una mezcla de queso mascarpone y crema batida. La base crujiente de avena tostada y miel combina a la perfección con la corona ácida y aromática de maracuyá fresco. Ideal para días soleados y sobremesas elegantes.',
                'precio': 21900,
                'precio_oferta': None,
                'stock': 7,
                'destacado': False,
                'porciones': '12 porciones (20 cm)',
                'prep': '24 horas de anticipación',
                'color': (217, 164, 65),
            },
            {
                'categoria': 'Cheesecakes',
                'nombre': 'Cheesecake Oreo Chocolate Bomb',
                'desc_corta': 'Relleno cremoso repleto de trozos crujientes de galletas Oreo, base de chocolate y ganache fundido.',
                'desc_larga': 'El favorito indiscutido de grandes y chicos. Base densa de galletas Oreo trituradas con mantequilla dorada, relleno cremoso con trozos enteros de galleta y remate con abundante ganache tibio de chocolate semi-amargo.',
                'precio': 23500,
                'precio_oferta': None,
                'stock': 2,  # Stock bajo para demo
                'destacado': False,
                'porciones': '12 a 14 porciones (22 cm)',
                'prep': '24 horas de anticipación',
                'color': (74, 44, 42),
            },

            # KUCHEN
            {
                'categoria': 'Kuchen',
                'nombre': 'Kuchen Sureño de Manzana Canela',
                'desc_corta': 'Masa quebrada de mantequilla rellena con finas láminas de manzana verde salteadas en canela y cubierta de migas crocantes.',
                'desc_larga': 'Traído directamente de las mejores tradiciones del sur de Chile. Masa quebrada enriquecida con mantequilla de campo, rellena con manzanas verdes seleccionadas caramelizadas con azúcar rubia, clavo de olor y canela. Coronado con un streusel crocante que se dora suavemente en el horno.',
                'precio': 16900,
                'precio_oferta': 14990,
                'stock': 14,
                'destacado': True,
                'porciones': '10 a 12 porciones (26 cm)',
                'prep': 'Mismo día o 24 hrs',
                'color': (217, 164, 65),
            },
            {
                'categoria': 'Kuchen',
                'nombre': 'Kuchen Cremoso de Frutillas y Almendras',
                'desc_corta': 'Base de masa sablé cubierta de suave crema pastelera casera, frutillas frescas enteras y almendras tostadas laminadas.',
                'desc_larga': 'Una delicia primaveral. Sobre una base horneada de masa sablé crocante disponemos una crema pastelera con extracto puro de vainilla, coronada con frutillas recién seleccionadas del Valle Central y una lluvia de almendras tostadas fileteadas.',
                'precio': 17900,
                'precio_oferta': None,
                'stock': 11,
                'destacado': False,
                'porciones': '10 a 12 porciones (26 cm)',
                'prep': '24 horas de anticipación',
                'color': (184, 58, 92),
            },
            {
                'categoria': 'Kuchen',
                'nombre': 'Kuchen de Nuez y Miel de Ulmo',
                'desc_corta': 'Tarta rústica con abundante relleno de nueces chilenas tostadas sumergidas en un caramelo suave de miel de ulmo.',
                'desc_larga': 'Riqueza y textura en cada bocado. Relleno consistente de nueces enteras seleccionadas, tostadas lentamente y bañadas en un caramelo de crema dulce con sutiles notas florales de miel pura de ulmo del sur.',
                'precio': 19900,
                'precio_oferta': None,
                'stock': 5,
                'destacado': False,
                'porciones': '10 a 12 porciones (24 cm)',
                'prep': '24 horas de anticipación',
                'color': (110, 68, 48),
            },

            # PASTELES INDIVIDUALES
            {
                'categoria': 'Pasteles individuales',
                'nombre': 'Éclair Francés de Chocolate Belga',
                'desc_corta': 'Masa choux aireada y crocante rellena de suave crema diplomática de chocolate y glaseada en espejo de cacao.',
                'desc_larga': 'Elaborado con la más estricta técnica pastelera francesa. Masa choux perfectamente horneada y hueca, rellena de crema pastelera aligerada con crema montada y cobertura de chocolate belga brillante.',
                'precio': 3800,
                'precio_oferta': None,
                'stock': 20,
                'destacado': True,
                'porciones': 'Individual (1 unidad grande)',
                'prep': 'Disponible en vitrina diaria',
                'color': (74, 44, 42),
            },
            {
                'categoria': 'Pasteles individuales',
                'nombre': 'Tartaleta de Limón y Merengue Italiano',
                'desc_corta': 'Crocante tartaleta rellena con un curd cítrico intenso de limón sutil y coronada con merengue italiano tostado.',
                'desc_larga': 'El balance perfecto entre dulce y ácido. Crema cuajada de limón sutil con textura untuosa, sobre una cápsula de masa dulce de almendras y picos de merengue suavemente caramelizados a la llama.',
                'precio': 3600,
                'precio_oferta': 3200,
                'stock': 18,
                'destacado': False,
                'porciones': 'Individual (1 porción)',
                'prep': 'Disponible en vitrina diaria',
                'color': (217, 164, 65),
            },
            {
                'categoria': 'Pasteles individuales',
                'nombre': 'Copa Tiramisú Tradicional',
                'desc_corta': 'Bizcochos de soletilla bañados en espresso italiano, capas de suave crema mascarpone y lluvia de cacao puro.',
                'desc_larga': 'Un postre italiano legendario servido en formato individual. Capas de galletas soletilla empapadas en café espresso recién tostado con un toque de licor de café, crema aireada de queso mascarpone y espolvoreado con cacao en polvo.',
                'precio': 4200,
                'precio_oferta': None,
                'stock': 15,
                'destacado': False,
                'porciones': 'Individual (vaso postre 220 ml)',
                'prep': 'Disponible en vitrina diaria',
                'color': (74, 44, 42),
            },

            # CUPCAKES
            {
                'categoria': 'Cupcakes',
                'nombre': 'Pack 6 Cupcakes Red Velvet',
                'desc_corta': 'Suaves bizcochos aterciopelados de cacao suave con un toque de vainilla, coronados con frosting de queso crema.',
                'desc_larga': 'Caja de 6 unidades de nuestros celebrados cupcakes Red Velvet. Bizcocho de color rojo rubí, textura sedosa y húmeda, decorados a mano con espirales de frosting de queso crema y migas crujientes de bizcocho.',
                'precio': 11900,
                'precio_oferta': 10500,
                'stock': 12,
                'destacado': True,
                'porciones': 'Caja de 6 unidades',
                'prep': '24 horas de anticipación',
                'color': (184, 58, 92),
            },
            {
                'categoria': 'Cupcakes',
                'nombre': 'Pack 6 Cupcakes Chocolate y Caramelo Salado',
                'desc_corta': 'Bizcocho intenso de chocolate rellenos con salsa de caramelo salado y rematados con buttercream de toffee.',
                'desc_larga': 'Para los amantes del contraste dulce y salado. Cupcakes esponjosos de chocolate amargo con centro líquido de toffee artesanal y una pizca de flor de sal marina de Cahuil.',
                'precio': 11900,
                'precio_oferta': None,
                'stock': 10,
                'destacado': False,
                'porciones': 'Caja de 6 unidades',
                'prep': '24 horas de anticipación',
                'color': (74, 44, 42),
            },

            # GALLETAS Y ALFAJORES
            {
                'categoria': 'Galletas y alfajores',
                'nombre': 'Docena de Alfajores de Maicena Caseros',
                'desc_corta': 'Tapas suaves y que se deshacen en la boca, con abundante manjar casero espeso y coco rallado fino.',
                'desc_larga': 'Elaborados a mano según la receta familiar de nuestras abuelas. Suaves tapas de almidón de maíz que se desvanecen al primer mordisco, rellenas con una generosa capa de manjar artesanal y rebozadas en coco rallado tostado.',
                'precio': 9900,
                'precio_oferta': 8900,
                'stock': 25,
                'destacado': True,
                'porciones': 'Caja de 12 unidades',
                'prep': 'Entrega inmediata / Stock permanente',
                'color': (217, 164, 65),
            },
            {
                'categoria': 'Galletas y alfajores',
                'nombre': 'Caja de Galletas Surtidas de Mantequilla',
                'desc_corta': 'Selección gourmet con galletas de almendra, chips de chocolate belga, canela y sablé bretón.',
                'desc_larga': 'Presentación en lata o caja de regalo con 350 gramos de galletas horneadas con mantequilla pura 100%. Ideales para regalar, celebraciones de oficina o disfrutar la hora del té con estilo.',
                'precio': 8900,
                'precio_oferta': None,
                'stock': 16,
                'destacado': False,
                'porciones': 'Caja de 350 gramos (aprox 24 galletas)',
                'prep': 'Entrega inmediata',
                'color': (217, 164, 65),
            },

            # TORTAS PERSONALIZADAS
            {
                'categoria': 'Tortas personalizadas',
                'nombre': 'Torta Personalizada Diseño Cumpleaños Infantil',
                'desc_corta': 'Diseño temático a pedido con decoración en buttercream o fondant, sabores a elección y topper personalizado.',
                'desc_larga': 'Creamos la torta de ensueño para el cumpleaños de tus hijos. Puedes elegir el bizcocho (vainilla, chocolate, arcoíris), dos rellenos a elección (manjar, trufa, crema chantilly, frambuesas) y la temática deseada. Incluye vela artesanal y topper con el nombre y edad del festejado.',
                'precio': 38900,
                'precio_oferta': None,
                'stock': 8,
                'destacado': True,
                'porciones': '20 a 25 porciones (24 cm alto)',
                'prep': '72 horas de anticipación requerida',
                'color': (143, 191, 168),
            },
            {
                'categoria': 'Tortas personalizadas',
                'nombre': 'Torta Boda Minimalista Semi-Naked Floral',
                'desc_corta': 'Elegante torta semi-naked de dos pisos decorada con flores naturales orgánicas comestibles y toques dorados.',
                'desc_larga': 'Un clásico moderno para matrimonios íntimos, bautizos o aniversarios. Dos pisos reales de suave bizcocho de vainilla y amapolas con relleno de crema de maracuyá y ganache blanco, decorada con eucalipto y flores frescas seleccionadas de temporada.',
                'precio': 65000,
                'precio_oferta': 59900,
                'stock': 4,
                'destacado': False,
                'porciones': '35 a 40 porciones (2 pisos)',
                'prep': '5 días de anticipación requerida',
                'color': (74, 44, 42),
            },
        ]

        productos_creados = []
        for p_data in productos_datos:
            cat_obj = categorias_dict[p_data['categoria']]
            slug = slugify(p_data['nombre'])

            # Generar imagen con Pillow
            rel_path = f"productos/{slug}.jpg"
            abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            if not os.path.exists(abs_path):
                generar_imagen_pasteleria(
                    abs_path,
                    p_data['nombre'],
                    cat_obj.nombre,
                    color_fondo=p_data['color']
                )

            prod, _ = Producto.objects.get_or_create(
                nombre=p_data['nombre'],
                defaults={
                    'categoria': cat_obj,
                    'slug': slug,
                    'descripcion_corta': p_data['desc_corta'],
                    'descripcion_larga': p_data['desc_larga'],
                    'precio': p_data['precio'],
                    'precio_oferta': p_data['precio_oferta'],
                    'imagen': rel_path,
                    'stock': p_data['stock'],
                    'activo': True,
                    'destacado': p_data['destacado'],
                    'tamano_porciones': p_data['porciones'],
                    'tiempo_preparacion': p_data['prep'],
                }
            )
            prod.categoria = cat_obj
            prod.descripcion_corta = p_data['desc_corta']
            prod.descripcion_larga = p_data['desc_larga']
            prod.precio = p_data['precio']
            prod.precio_oferta = p_data['precio_oferta']
            prod.imagen = rel_path
            prod.stock = p_data['stock']
            prod.activo = True
            prod.destacado = p_data['destacado']
            prod.tamano_porciones = p_data['porciones']
            prod.tiempo_preparacion = p_data['prep']
            prod.save()
            productos_creados.append(prod)

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(productos_creados)} productos creados/actualizados con fotos de pasteleria."))

        # 6. Crear pedidos de ejemplo en los ultimos 30 dias para alimentar el Dashboard y Grafico
        if Pedido.objects.count() < 10:
            self.stdout.write("Generando pedidos historicos para el dashboard de metricas...")
            ahora = timezone.now()
            nombres_demo = [
                ("Camila Soto", "camila.soto@ejemplo.cl", "+56 9 8111 2233", "Las Condes", "Av. Apoquindo 4500"),
                ("Felipe Morales", "felipe.m@ejemplo.cl", "+56 9 7222 3344", "Nunoa", "Av. Irarrazaval 2800"),
                ("Maria Jose Silva", "mariajose@ejemplo.cl", "+56 9 9333 4455", "Providencia", "Manuel Montt 720"),
                ("Rodrigo Espinoza", "rodrigo.e@ejemplo.cl", "+56 9 6444 5566", "Santiago Centro", "Huerfanos 1100"),
                ("Constanza Bravo", "cbravo@ejemplo.cl", "+56 9 5555 6677", "Vitacura", "Av. Vitacura 3800"),
                ("Ignacio Castro", "ignacio.c@ejemplo.cl", "+56 9 8666 7788", "La Reina", "Principe de Gales 6000"),
            ]

            estados = ['confirmado', 'en_preparacion', 'listo', 'entregado', 'pendiente']

            # Pedidos distribuidos en los ultimos 28 dias
            for dia_offset in range(28, 0, -3):
                fecha_pedido = ahora - timedelta(days=dia_offset, hours=random.randint(1, 8))
                nombre, correo, fono, comuna, direccion = random.choice(nombres_demo)

                # Algunos pedidos asignados al cliente demo
                usuario_asignado = cliente_user if dia_offset in [1, 7, 14] else None

                pedido = Pedido.objects.create(
                    usuario=usuario_asignado,
                    nombre=nombre,
                    correo=correo,
                    telefono=fono,
                    tipo_entrega=random.choice(['retiro', 'despacho']),
                    direccion=direccion,
                    comuna=comuna,
                    fecha_entrega=(fecha_pedido + timedelta(days=2)).date(),
                    hora_entrega='Tarde (14:00 - 18:00 hrs)',
                    metodo_pago=random.choice(['transferencia', 'efectivo']),
                    estado=random.choice(estados),
                    total=0,
                    costo_envio=3990 if random.choice([True, False]) else 0,
                )
                # Forzar fecha de creacion
                Pedido.objects.filter(pk=pedido.pk).update(fecha_creacion=fecha_pedido)

                # Items del pedido
                prods_muestra = random.sample(productos_creados, k=random.randint(1, 3))
                total_pedido = 0
                for p in prods_muestra:
                    cant = random.randint(1, 2)
                    sub = p.precio_final * cant
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=p,
                        nombre_producto=p.nombre,
                        precio_unitario=p.precio_final,
                        cantidad=cant,
                        subtotal=sub
                    )
                    total_pedido += sub

                pedido.total = total_pedido
                pedido.save()

            # Pedido de hoy para metrica de ventas del dia
            pedido_hoy = Pedido.objects.create(
                usuario=cliente_user,
                nombre="Valentina Rojas",
                correo="valentina.rojas@ejemplo.cl",
                telefono="+56 9 9123 4567",
                tipo_entrega='despacho',
                direccion="Av. Pedro de Valdivia 980, Depto 402",
                comuna="Providencia",
                fecha_entrega=(ahora + timedelta(days=1)).date(),
                hora_entrega='Tarde (14:00 - 18:00 hrs)',
                metodo_pago='transferencia',
                estado='confirmado',
                total=0,
                costo_envio=0,
            )
            p1 = productos_creados[0]
            ItemPedido.objects.create(
                pedido=pedido_hoy,
                producto=p1,
                nombre_producto=p1.nombre,
                precio_unitario=p1.precio_final,
                cantidad=1,
                subtotal=p1.precio_final
            )
            pedido_hoy.total = p1.precio_final
            pedido_hoy.save()

            self.stdout.write(self.style.SUCCESS(f"[OK] Creados {Pedido.objects.count()} pedidos historicos para el panel."))

        # 7. Mensajes de contacto demo para la bandeja del panel
        if MensajeContacto.objects.count() < 3:
            MensajeContacto.objects.create(
                nombre="Javiera Benitez",
                correo="javi.benitez@ejemplo.cl",
                telefono="+56 9 8899 7766",
                asunto="Cotizacion Torta de Bautizo para 30 personas",
                mensaje="Hola equipo de LA CREME, me gustaria cotizar una torta tematica para el bautizo de mi hija para el proximo fin de semana. Tienen disponibilidad y catalogo de opciones?",
                leido=False
            )
            MensajeContacto.objects.create(
                nombre="Matias Vergara",
                correo="mvergara@empresa.cl",
                telefono="+56 9 5544 3322",
                asunto="Despachos corporativos para evento de fin de ano",
                mensaje="Estimados, necesitamos cotizar 40 cajas de galletas surtidas y alfajores para regalo a colaboradores. Quedo atento a su respuesta.",
                leido=True
            )
            self.stdout.write(self.style.SUCCESS("[OK] Mensajes de contacto de ejemplo creados."))

        self.stdout.write(self.style.SUCCESS("\n[EXITO] DATOS DEMO CARGADOS CON EXITO!"))
        self.stdout.write(self.style.SUCCESS("Credenciales de acceso:"))
        self.stdout.write("  * Administrador / Staff:  admin / admin12345")
        self.stdout.write("  * Cliente demo:          cliente / cliente12345")
