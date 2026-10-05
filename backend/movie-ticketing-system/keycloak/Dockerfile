FROM quay.io/keycloak/keycloak:latest

# Copy custom themes into Keycloak's provider/theme directory
COPY ./themes /opt/keycloak/themes/

# (Optional) If you want Keycloak to pre-optimize or build providers on startup
RUN /opt/keycloak/bin/kc.sh build