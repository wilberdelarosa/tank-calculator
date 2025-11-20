# Instrucciones para Generar APK de Calculadora Combustible

## Requisitos Previos

### Opción 1: Usar WSL en Windows (RECOMENDADO)

1. **Instalar WSL2**:
   ```powershell
   wsl --install
   ```
   Reinicia tu PC si es necesario.

2. **Instalar Ubuntu en WSL**:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

3. **Abrir Ubuntu WSL** y ejecutar:
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

4. **Instalar Buildozer**:
   ```bash
   pip3 install --upgrade buildozer
   pip3 install --upgrade Cython==0.29.33
   ```

5. **Copiar archivos al WSL**:
   ```bash
   # Desde WSL, crear directorio
   mkdir -p ~/tank-app
   cd ~/tank-app
   
   # Copiar archivos (desde Windows, la ruta es /mnt/c/...)
   cp /mnt/c/Users/wilbe/Downloads/Nueva\ carpeta\ \(7\)/*.py .
   cp /mnt/c/Users/wilbe/Downloads/Nueva\ carpeta\ \(7\)/buildozer.spec .
   cp /mnt/c/Users/wilbe/Downloads/Nueva\ carpeta\ \(7\)/*.json . 2>/dev/null || true
   ```

6. **Compilar el APK**:
   ```bash
   cd ~/tank-app
   buildozer -v android debug
   ```

7. **Obtener el APK**:
   El APK estará en `~/tank-app/bin/calculadoracombustible-1.0.0-arm64-v8a_armeabi-v7a-debug.apk`
   
   Para copiarlo a Windows:
   ```bash
   cp bin/*.apk /mnt/c/Users/wilbe/Downloads/
   ```

---

### Opción 2: Usar GitHub Actions (Sin necesidad de Linux local)

1. **Crear cuenta en GitHub** (si no tienes): https://github.com

2. **Crear nuevo repositorio**:
   - Ve a https://github.com/new
   - Nombre: `tank-calculator`
   - Público o Privado
   - Click "Create repository"

3. **Subir archivos**:
   ```powershell
   cd "C:\Users\wilbe\Downloads\Nueva carpeta (7)"
   git init
   git add main_kivy.py calculo.py buildozer.spec tanks_config.json
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/tank-calculator.git
   git push -u origin main
   ```

4. **Crear archivo de GitHub Actions**:
   Crea `.github/workflows/build.yml` con:
   ```yaml
   name: Build APK
   
   on:
     push:
       branches: [ main ]
     workflow_dispatch:
   
   jobs:
     build:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v3
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.10'
       
       - name: Install dependencies
         run: |
           sudo apt-get update
           sudo apt-get install -y openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
           pip install buildozer cython==0.29.33
       
       - name: Build APK
         run: buildozer -v android debug
       
       - name: Upload APK
         uses: actions/upload-artifact@v3
         with:
           name: apk
           path: bin/*.apk
   ```

5. **Descargar APK**:
   - Ve a tu repositorio en GitHub
   - Click en "Actions"
   - Click en el workflow ejecutado
   - Descarga el artifact "apk"

---

### Opción 3: Usar Servicio en la Nube (Google Colab)

1. **Ir a Google Colab**: https://colab.research.google.com

2. **Crear nuevo notebook y ejecutar**:
   ```python
   # Instalar dependencias
   !apt-get update
   !apt-get install -y openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   !pip install buildozer cython==0.29.33
   
   # Subir archivos manualmente (usar botón de archivos)
   # O clonar desde GitHub si ya los subiste
   
   # Compilar
   !buildozer -v android debug
   
   # Descargar APK (aparecerá en panel de archivos)
   from google.colab import files
   !cp bin/*.apk ./
   files.download('calculadoracombustible-1.0.0-arm64-v8a_armeabi-v7a-debug.apk')
   ```

---

## Notas Importantes

1. **Primera compilación**: Puede tardar 30-60 minutos porque descarga Android SDK/NDK
2. **Espacio en disco**: Necesitas al menos 10-15 GB libres
3. **RAM**: Mínimo 4GB recomendados
4. **Conexión a Internet**: Estable para descargar dependencias

## Solución de Problemas Comunes

### Error: "Command failed: ..."
- Aumenta el nivel de log en buildozer.spec: `log_level = 2`
- Verifica que todos los archivos .py estén presentes

### Error: "SDK/NDK not found"
```bash
buildozer android clean
rm -rf .buildozer
buildozer -v android debug
```

### Error: "Permission denied"
```bash
chmod +x buildozer
```

## Instalar APK en Android

1. Transfiere el APK a tu teléfono
2. Ve a Configuración > Seguridad > Orígenes desconocidos (actívalo)
3. Abre el APK y presiona "Instalar"

---

**Recomendación**: Usa WSL (Opción 1) si tienes Windows 10/11, es la más confiable y rápida.
