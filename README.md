# 📦 Sistema de Inventario Vinoteca

Proyecto desarrollado en **Django** con integración de **Docker** y **PostgreSQL**, pensado para gestionar productos, clientes y ventas de una vinoteca. Incluye generación de facturas en PDF y visualización de estadísticas con **Chart.js**.

---

## 🚀 Tecnologías utilizadas
- **Python 3.10**
- **Django 4.2**
- **PostgreSQL 15**
- **Docker & Docker Compose**
- **Bootstrap 4**
- **Chart.js**
- **xhtml2pdf** (para facturas en PDF)

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tuusuario/inventario.git
cd inventario

2. Variables de entorno

POSTGRES_DB=inventario
POSTGRES_USER=inventario
POSTGRES_PASSWORD=inventario
SECRET_KEY=tu_clave_secreta
DEBUG=True

3. Levantar los contenedores

docker-compose up -d

4. Migraciones iniciales

docker-compose exec web python manage.py migrate

5. Crear superusuario

docker-compose exec web python manage.py createsuperuser


📊 Funcionalidades principales
Productos: alta, listado y control de stock.

Clientes: gestión de clientes.

Ventas:

Registro de ventas con validación de stock.

Cálculo automático de totales.

Generación de facturas en PDF.

Estadísticas:

Gráfico de ventas por día con Chart.js..

Endpoint JSON para alimentar el gráfico.

🔗 Endpoints principales
/productos/ → listado de productos

/clientes/ → listado de clientes

/ventas/ → listado de ventas

/ventas/nueva/ → crear nueva venta

/ventas/<id>/ → detalle de venta

/ventas/factura/<id>/pdf/ → descargar factura PDF

/ventas/ventas_por_dia/ → gráfico de ventas por día

/ventas/ventas_por_dia_json/ → datos JSON para el gráfico

Notas de desarrollo

El gráfico de ventas por día se renderiza en templates/venta/ventas_por_dia.html usando Chart.js..

El endpoint JSON está protegido con @login_required y @permission_required.

Se recomienda trabajar siempre dentro del contenedor web:

docker-compose exec web python manage.py shell


Autora

Proyecto desarrollado por Noelia Vivas.

