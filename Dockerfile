# ---- Builder Stage ----
FROM amazon/aws-lambda-python:3.12 AS builder
RUN dnf install -y jq unzip findutils
COPY ./chrome-installer.sh ./chrome-installer.sh
RUN chmod +rx ./chrome-installer.sh && ./chrome-installer.sh

# ---- Final Stage ----
FROM amazon/aws-lambda-python:3.12
RUN dnf install -y \
    atk cups-libs alsa-lib at-spi2-atk \
    libXcomposite libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    pango nss mesa-libgbm \
    && dnf clean all && rm -rf /var/cache/dnf

COPY --from=builder /opt/chrome /opt/chrome
COPY --from=builder /opt/chrome-driver /opt/chrome-driver

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lambda_function.py .
CMD [ "lambda_function.lambda_handler" ]
