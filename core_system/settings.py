import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis de segurança do arquivo .env
load_dotenv(BASE_DIR / '.env')

# NUNCA hardcode em produção
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY não definida no ambiente. Crie um arquivo .env")

# Segurança contra vazamento de erros
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reservas',
    'quadras',
    'alunos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

# ==========================================
# CONFIGURAÇÕES DO PAINEL ADMIN (JAZZMIN)
# ==========================================
JAZZMIN_SETTINGS = {
    # ---- Identidade ----
    "site_title":   "Arena Admin",
    "site_header":  "Arena Ibituruna Beach",
    "site_brand":   "Arena Ibituruna",
    "site_logo":    "reservas/img/logo_oficial.png",
    "site_logo_classes": "img-fluid",
    "site_icon":    "reservas/img/logo_oficial.png",  # favicon
    "welcome_sign": "Bem-vindo ao sistema de gestão 🏐",
 
    # ---- Links rápidos no topo (rotina diária do dono) ----
    "topmenu_links": [
        {"name": "🌐 Ver o Site",          "url": "/",            "new_window": True},
        {"name": "📊 Painel Financeiro",   "url": "/financeiro/"},
        {"name": "📅 Grade de Horários",   "url": "/agendamento/","new_window": True},
    ],
 
    # ---- Ícones por model (FontAwesome 5, já incluso no Jazzmin) ----
    "icons": {
        "auth":             "fas fa-users-cog",
        "auth.user":        "fas fa-user-shield",
        "auth.group":       "fas fa-users",
        "alunos.Aluno":     "fas fa-user-graduate",
        "alunos.Pagamento": "fas fa-dollar-sign",
        "quadras.Quadra":   "fas fa-volleyball-ball",
        "reservas.Reserva": "fas fa-calendar-check",
    },
    "default_icon_parents":  "fas fa-chevron-right",
    "default_icon_children": "fas fa-circle",
 
    # ---- Ordem do menu lateral (do mais usado ao menos usado) ----
    "order_with_respect_to": [
        "alunos.Pagamento",   # 1. Registra pagamentos todo dia
        "reservas.Reserva",   # 2. Confere quem reservou
        "alunos.Aluno",       # 3. Cadastra/edita mensalistas
        "quadras.Quadra",     # 4. Raramente muda
        "auth",               # 5. Só quando cria novo usuário
    ],
 
    # ---- Comportamento do painel ----
    "show_sidebar":              True,
    "navigation_expanded":       True,
    "related_modal_active":      True,   # edita FK em modal — sem sair da página
    "show_ui_builder":           False,  # remove o builder em produção
    "changeform_format":         "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user":  "collapsible",
        "auth.group": "vertical_tabs",
    },
 
    # CSS personalizado (arquivo que vamos criar no próximo passo)
    "custom_css": "reservas/css/jazzmin_custom.css",
}
 
 
JAZZMIN_UI_TWEAKS = {
    # Navbar escura para contraste com o roxo
    "navbar":       "navbar-dark",
 
    # Tema base mais neutro — o CSS customizado vai sobrescrever as cores
    "theme":        "darkly",          # darkly dá uma base escura elegante
 
    # Sidebar escura com a cor primária
    "sidebar":                  "sidebar-dark-primary",
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style":  False,
    "sidebar_nav_flat_style":    False,
 
    # Botões — todos alinhados com a marca
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
 
    # Sticky no topo ao rolar — o botão Salvar nunca some
    "actions_sticky_top": True,
}

# ==========================================
# CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO
# ==========================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ==========================================
# CONFIGURAÇÕES DO JAZZMIN (AUDITORIA)
# ==========================================
JAZZMIN_SETTINGS = {
    "site_title": "Arena Admin",
    "site_header": "Arena Ibituruna Beach",
    "site_brand": "Arena Ibituruna",
    "site_logo": "reservas/img/logo_oficial.png",
    "welcome_sign": "Olá! Bom trabalho hoje 🏐",
    "show_sidebar": True,
    
    "topmenu_links": [
        {"name": "🌐 Ver o Site", "url": "/", "new_window": True},
        {"name": "📊 Painel Financeiro", "url": "/financeiro/"},
        {"name": "📅 Ver Agendamento", "url": "/agendamento/", "new_window": True},
    ],
    
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "alunos.Aluno": "fas fa-user-graduate",
        "alunos.Pagamento": "fas fa-dollar-sign",
        "quadras.Quadra": "fas fa-volleyball-ball",
        "reservas.Reserva": "fas fa-calendar-check",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    "order_with_respect_to": [
        "alunos.Pagamento",
        "reservas.Reserva",
        "alunos.Aluno",
        "quadras.Quadra",
        "auth",
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark",
    "theme": "lumen",
    "sidebar": "sidebar-dark-primary",
    "actions_sticky_top": True,
}