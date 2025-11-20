[app]
# Nombre de la aplicación
title = Calculadora Combustible
package.name = calculadoracombustible
package.domain = org.tankcalc

# Código fuente
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Versión
version = 1.0.0

# Requisitos de Python
requirements = python3,kivy,numpy,scikit-learn

# Permisos de Android
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Orientación
orientation = portrait

# Icono y splash
#icon.filename = %(source.dir)s/data/icon.png
#presplash.filename = %(source.dir)s/data/presplash.png

# Android API
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

# Arquitecturas
android.archs = arm64-v8a,armeabi-v7a

# Modo de compilación
android.accept_sdk_license = True
android.skip_update = False

[buildozer]
# Directorio de compilación
build_dir = ./.buildozer
bin_dir = ./bin

# Logs
log_level = 2
warn_on_root = 1
