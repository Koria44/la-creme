# LA CREME — Pastelería artesanal (Demo Django)

Tienda online demo para una pastelería: catálogo de productos, carrito de compras, checkout de pedidos, cuentas de usuario y panel de administración interno.

> ⚠️ **Proyecto DEMO.** Incluye `db.sqlite3` y `media/` con datos e imágenes de prueba. La `SECRET_KEY`, `DEBUG=True` y `ALLOWED_HOSTS=['*']` de `config/settings.py` son solo para desarrollo: **no usar así en producción**.

## Tecnologías

- Python 3.12+ (probado con 3.14)
- Django 6.1
- Pillow (imágenes)
- SQLite
- Bootstrap 5

## Apps del proyecto

| App | Descripción |
|---|---|
| `catalogo` | Categorías y productos |
| `carrito` | Carrito de compras en sesión |
| `pedidos` | Checkout y pedidos |
| `cuentas` | Registro, login, perfil y recuperación de contraseña |
| `panel` | Panel interno (productos, stock, pedidos, mensajes) |
| `sitio` | Inicio, contacto, ubicación y configuración del sitio |

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Koria44/la-creme.git
cd la-creme

# 2. Crear y activar entorno virtual
python -m venv env
# Windows
env\Scripts\activate
# Linux / macOS
source env/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones (la BD demo ya viene incluida)
python manage.py migrate

# 5. Levantar el servidor
python manage.py runserver
```

Abrir en el navegador: http://127.0.0.1:8000/

### Regenerar los datos demo (opcional)

```bash
python manage.py cargar_datos_demo
```

### Ejecutar tests

```bash
python manage.py test
```

## Credenciales demo

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador (staff / superusuario) | `admin` | `admin12345` |
| Cliente | `cliente` | `cliente12345` |

- Panel de administración de Django: http://127.0.0.1:8000/admin/
- Los correos (p. ej. recuperación de contraseña) se imprimen en la consola, no se envían.
