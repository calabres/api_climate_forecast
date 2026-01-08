# Usar imagen base ligera de Python
FROM python:3.10-slim

# Evitar que Python genere archivos .pyc y outputs en buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para compilar algunas libs de ciencia de datos
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Crear directorio para los datos (se montará como volumen)
RUN mkdir -p /app/data_bsas

# Exponer el puerto
EXPOSE 8080

# Comando para iniciar
CMD ["python", "web_platform/manage.py", "runserver", "0.0.0.0:8080"]
