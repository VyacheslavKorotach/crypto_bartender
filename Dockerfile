FROM python:3.7
ENV PYTHONUNBUFFERED 1
ENV WINE_VENDOR_MQTT_HOST Yuor_MQTT_HOST
ENV WINE_VENDOR_MQTT_USER Yuor_MQTT_login
ENV WINE_VENDOR_MQTT_PASSWORD Your_MQTT_password
ENV WINE_VENDOR_PRIVAT_KEY Your_Vendor_Privat_Key
RUN mkdir /config
ADD /config/requirements.pip /config/
RUN pip install -r /config/requirements.pip
RUN mkdir /src
WORKDIR /src

