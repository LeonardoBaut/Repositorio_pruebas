FROM python:3.10-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Copiar credenciales de Earthdata al home del contenedor
COPY .netrc /root/.netrc
COPY .dodsrc /root/.dodsrc

RUN chmod 600 /root/.netrc && chmod 600 /root/.dodsrc
# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]