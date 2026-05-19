# AI Import Assistant (Aduana)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.3+-150458.svg?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

AI Import Assistant es un sistema automatizado en Python diseñado para optimizar, centralizar y digitalizar el procesamiento de datos críticos contenidos en documentos de transporte marítimo (Bill of Lading - B/L) y facturas comerciales para el sector importador y aduanero.

Este proyecto independiente integra un potente motor de extracción y procesamiento de datos en el backend con una interfaz gráfica moderna, segura e intuitiva en el frontend utilizando Streamlit, además de contar con un sistema robusto de gestión de usuarios, roles y auditoría de sesiones de trabajo.

---

## Alineación Curricular y Logros

Este repositorio contiene la base de código correspondiente a la experiencia descrita en el currículum como Desarrollador Backend / Automatización:

*   **Procesamiento Inteligente:** Diseño y programación de scripts optimizados en Python para la extracción inteligente de datos críticos estructurados y no estructurados de documentos aduaneros complejos (B/L y facturas).
*   **Interfaz Interactiva:** Desarrollo de una interfaz de usuario funcional en Streamlit, optimizando la visualización de reportes, carga de documentos y gestión administrativa de la carga de trabajo.
*   **Eficiencia Operativa:** Implementación de librerías especializadas en análisis de datos (Pandas, OpenPyXL, etc.) y conectores de bases de datos para asegurar una lectura precisa, logrando una reducción drástica de los tiempos de procesamiento manual de información.

---

## Características Principales

### 1. Extracción y Procesamiento de Documentos
*   Soporte para documentos estructurados y no estructurados propios del sector importador.
*   Procesamiento e interpretación precisa de facturas comerciales e instrucciones de embarque.
*   Generador automático de plantillas y exportación a formatos estandarizados en Excel (`FACTURA MODELO.xlsm`).

### 2. Módulo de Autenticación y Seguridad Completo
*   **Control de Acceso:** Niveles de permisos basados en roles (`admin` y `worker`).
*   **Seguridad:** Hasheo de contraseñas robusto y uso de variables de entorno para resguardar credenciales de base de datos.
*   **Sesiones de Trabajo:** Gestión extendida de sesiones persistentes con registro de actividad (auditoría).

### 3. Panel de Administración y Asignación
*   **Monitoreo en Tiempo Real:** Dashboard intuitivo para visualizar la carga de trabajo por empleado.
*   **Gestión Dinámica:** Asignación y reasignación de sesiones de procesamiento de documentos en caliente.
*   **Auditoría Histórica:** Tracking de todos los cambios de asignación y notas del auditor.

---

## Arquitectura y Estructura del Código

El proyecto ha sido reestructurado siguiendo las mejores prácticas de modularidad, desacoplando la lógica de negocio, el procesamiento de datos y la interfaz de usuario:

```
AI Import Assistant
├── main.py                     # Punto de entrada de la aplicación
├── config/                     # Configuraciones y plantillas de entorno (.env.example)
├── database/                   # Modelos y scripts SQL de base de datos (setup_database.sql)
├── docs/                       # Documentación de referencia técnica y APIs
├── scripts/                    # Scripts de inicialización y migración de datos
└── src/                        # Código fuente del sistema
    ├── auth/                   # Lógica de gestión de usuarios y seguridad (AuthManager)
    ├── core/                   # Controladores de sesiones y auditorías de trabajo
    ├── processors/             # Motores de extracción de documentos y generación de Excel
    ├── ui/                     # Componentes y dashboards interactivos (Streamlit)
    └── utils/                  # Herramientas de soporte y helpers
```

---

## Tecnologías y Librerías Utilizadas

*   **Backend:** Python 3.11+, PostgreSQL (Motor de Base de Datos).
*   **Análisis & Manipulación de Datos:** `pandas`, `openpyxl`, `pillow`, `pypdf2`, `python-magic`.
*   **Frontend & Dashboard:** `streamlit` (con paneles interactivos personalizados).
*   **Seguridad:** `hashlib`, `uuid`, `python-dotenv`.
*   **Base de Datos / Conectividad:** `psycopg2-binary` (interacción directa y segura con PostgreSQL mediante sentencias preparadas).

---

## Guía de Inicio Rápido

Para desplegar este proyecto en un entorno local de desarrollo:

### 1. Clonar el repositorio e instalar dependencias
```bash
git clone https://github.com/tu-usuario/ai-import-assistant.git
cd ai-import-assistant
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto basándote en la plantilla:
```bash
cp config/.env.example .env
```
Edita `.env` e ingresa la cadena de conexión de tu servidor PostgreSQL (`DATABASE_URL`).

### 3. Inicializar Base de Datos y Configuración Inicial
Ejecuta el script interactivo de inicialización para preparar la base de datos y crear la primera cuenta de administrador:
```bash
python scripts/setup_initial.py
```

### 4. Ejecutar la Aplicación Streamlit
```bash
streamlit run main.py
```

---

## Documentación Adicional
Para más detalles técnicos sobre el funcionamiento del sistema, puedes consultar los documentos ubicados en la carpeta `/docs`:
*   [Guía Rápida de Configuración](docs/SETUP_GUIA_RAPIDA.md)
*   [Referencia Completa del Sistema de Autenticación](docs/AUTH_SYSTEM_README.md)
*   [Manual de Seguridad y Buenas Prácticas](docs/SECURITY_GUIDE.md)

---

Desarrollado de manera independiente como solución tecnológica de automatización backend y procesamiento inteligente para optimizar los flujos aduaneros de importación.
