FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY redfish_lab ./redfish_lab
COPY app.py ./
RUN pip install --no-cache-dir . && useradd --create-home --uid 1000 lab
USER lab
ENV LAB_HOST=0.0.0.0 PORT=7860 GRADIO_ANALYTICS_ENABLED=False
ENV GRADIO_TEMP_DIR=/tmp/redfish-gradio HF_HOME=/tmp/redfish-hf
EXPOSE 7860
CMD ["python", "app.py"]
