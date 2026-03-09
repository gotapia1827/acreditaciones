# 📋 Sistema de Gestión y Validación de Documentos Mineros

Sistema web para la gestión, subida y validación de documentación requerida en procesos de acreditación minera.

---

## 📌 Descripción

Plataforma que permite a empresas subir documentación necesaria para acreditaciones mineras y a evaluadores revisar si cumplen los requisitos establecidos. Los administradores pueden monitorear el estado global del sistema y métricas de cumplimiento.

---

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12+ / Django 5.x |
| Base de datos (desarrollo) | SQLite |
| Base de datos (producción) | PostgreSQL |
| Frontend | HTML + CSS + JavaScript + Bootstrap 5 |
| Templates | Django Templates |
| Servidor (producción) | VPS Linux + Nginx + Gunicorn |
| Almacenamiento futuro | AWS S3 / Cloudflare R2 / Backblaze B2 |

---

## 👥 Roles del Sistema

### Cliente
- Subir documentos requeridos
- Ver estado de validación de sus documentos
- Ver observaciones de evaluadores
- Ver porcentaje de cumplimiento

### Evaluador
- Revisar documentos subidos por clientes
- Aprobar o rechazar documentos
- Agregar observaciones

### Administrador
- Ver todos los clientes y documentos
- Ver métricas globales del sistema
- Ver cumplimiento por cliente

---

## 📁 Estructura del Proyecto

```
acreditaciones_mineras/
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/       # Usuarios, roles, autenticación
│   ├── documents/      # Documentos, subida, validación
│   ├── evaluations/    # Revisión, aprobación, observaciones
│   ├── dashboard/      # Vistas de resumen por rol
│   └── core/           # Utilidades comunes
│
├── templates/
├── static/
├── media/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── .env                # Variables de entorno (NO versionar)
├── .gitignore
└── manage.py
```

---

## ⚙️ Instalación y configuración local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/acreditaciones_mineras.git
cd acreditaciones_mineras
```

### 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Linux/Mac
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements/development.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Editar `.env` con tus valores:

```env
SECRET_KEY=tu-clave-secreta-generada
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=acreditaciones_db
DB_USER=acreditaciones_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

Generar una `SECRET_KEY` segura:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Correr el servidor de desarrollo

```bash
python manage.py runserver
```

Acceder en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📄 Documentos Permitidos

| Tipo | Extensión |
|---|---|
| PDF | `.pdf` |
| Word | `.doc`, `.docx` |
| Excel | `.xls`, `.xlsx` |
| Imagen | `.jpg`, `.jpeg`, `.png` |

- **Tamaño máximo:** 25 MB por archivo
- Los archivos se renombran automáticamente con **UUID v4**
- Se valida el **tipo MIME real** del archivo (no solo la extensión)

---

## 🔒 Seguridad

- Protección CSRF activa
- Validación MIME real con `python-magic`
- Validación de extensión por whitelist
- Límite de tamaño de archivo
- Sanitización y renombrado UUID de archivos
- Control de acceso por rol en todas las vistas
- Login obligatorio para vistas protegidas
- Headers de seguridad HTTP en producción

---

## 📊 Estados de Documentos

```
pendiente  →  aprobado
           →  rechazado
```

---

## 🚀 Despliegue en Producción

### Requisitos del servidor
- VPS Linux (Ubuntu 22.04+ recomendado)
- Python 3.12+
- PostgreSQL 15+
- Nginx
- Gunicorn

### Variables de entorno adicionales para producción

```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.cl,www.tu-dominio.cl
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
```

> La guía completa de despliegue se detalla en la **Etapa 10** del proyecto.

---

## 🗺️ Roadmap de Desarrollo

| Etapa | Descripción | Estado |
|---|---|---|
| 1 | Arquitectura del sistema | ✅ Completada |
| 2 | Creación del proyecto Django | ✅ Completada |
| 3 | Modelos de base de datos | 🔄 En progreso |
| 4 | Sistema de autenticación y roles | ⏳ Pendiente |
| 5 | Sistema de subida segura de documentos | ⏳ Pendiente |
| 6 | Panel de cliente | ⏳ Pendiente |
| 7 | Panel de evaluador | ⏳ Pendiente |
| 8 | Dashboard administrador | ⏳ Pendiente |
| 9 | Hardening de seguridad | ⏳ Pendiente |
| 10 | Despliegue en VPS | ⏳ Pendiente |

---

## 🤝 Contribución

Este es un proyecto privado en desarrollo activo. Para contribuir contactar al equipo de desarrollo.

---

## 📝 Licencia

Uso interno — todos los derechos reservados.
